# Arquitectura del Sistema — Plataforma de Gestión del Conocimiento

Versión del documento: 1.3  
Fecha: Enero 2026  
Autores: Equipo de Arquitectura  
Estado: Aprobado

---

## 1. Visión general

La Plataforma de Gestión del Conocimiento es un sistema distribuido basado en microservicios diseñado para indexar, almacenar y recuperar documentación corporativa mediante búsqueda semántica y generación de texto con modelos de lenguaje ejecutados en local.

El sistema sigue una arquitectura RAG (Retrieval-Augmented Generation): los documentos son fragmentados, convertidos en representaciones vectoriales (embeddings) y almacenados en una base de datos vectorial. Ante una consulta, el sistema recupera los fragmentos más relevantes semánticamente y los proporciona como contexto al modelo de lenguaje, que genera una respuesta fundamentada.

**Principios de diseño:**
- **Privacidad por diseño:** ningún dato sale de la infraestructura corporativa.
- **Modularidad:** cada componente es reemplazable independientemente.
- **Observabilidad:** logging, métricas y trazas distribuidas desde el primer día.
- **Escalabilidad horizontal:** diseñado para escalar cada componente según la carga.

---

## 2. Diagrama de componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE                                 │
│    Web App (React)  ·  App Móvil  ·  API Clients externos       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST
┌────────────────────────────▼────────────────────────────────────┐
│                       API GATEWAY                               │
│         Nginx + autenticación JWT + rate limiting               │
└──────────┬──────────────────────────────────────────────────────┘
           │ Routing interno
    ┌──────▼──────────────────────────────┐
    │                                     │
┌───▼────────────┐           ┌────────────▼────────────┐
│  Ingestion     │           │   Query Service          │
│  Service       │           │   (RAG Pipeline)         │
│  (FastAPI)     │           │   (FastAPI)              │
└───┬────────────┘           └────────┬────────────────┘
    │                                 │
    │ Publica eventos                 │ Búsqueda semántica
┌───▼────────┐              ┌─────────▼──────────┐
│  Message   │              │  Vector Store       │
│  Queue     │              │  (ChromaDB /        │
│  (Redis)   │              │   Qdrant)           │
└───┬────────┘              └─────────────────────┘
    │                                 │
┌───▼────────────┐           ┌────────▼────────────────┐
│  Processing    │           │   LLM Service            │
│  Workers       ├──────────►│   (Ollama)               │
│  (Celery)      │           │   Llama3 / Mistral       │
└───┬────────────┘           └─────────────────────────┘
    │
┌───▼────────────┐
│  Document      │
│  Store         │
│  (MinIO S3)    │
└────────────────┘
           │
┌──────────▼──────────────────────────────────────────┐
│                  OBSERVABILIDAD                      │
│   Prometheus + Grafana  ·  Loki  ·  Jaeger (trazas) │
└─────────────────────────────────────────────────────┘
```

---

## 3. Descripción de los componentes

### 3.1 API Gateway

**Tecnología:** Nginx con configuración personalizada.

**Responsabilidades:**
- Terminación TLS (certificados gestionados por cert-manager).
- Autenticación y validación de tokens JWT.
- Rate limiting por IP y por API Key.
- Routing de peticiones a los microservicios internos.
- Logging de acceso centralizado.

**Configuración destacada:**
- Timeout de conexión: 10 segundos.
- Timeout de lectura: 120 segundos (necesario para respuestas del LLM).
- Buffer de respuesta: 64KB.

---

### 3.2 Ingestion Service

**Tecnología:** Python 3.11 + FastAPI + LangChain Community.

**Responsabilidades:**
- Recibir documentos vía API (multipart/form-data).
- Validar el formato y tamaño del archivo.
- Almacenar el archivo original en el Document Store (MinIO).
- Publicar un mensaje en la cola (Redis) para procesamiento asíncrono.
- Gestionar el ciclo de vida de los documentos (versiones, estados, eliminación).

**Flujo de ingesta de documento:**
1. Cliente envía `POST /documents` con el archivo.
2. El servicio valida formato (PDF/DOCX/MD/TXT) y tamaño (máx. 50 MB).
3. Se guarda el archivo en MinIO con un UUID único.
4. Se registra el documento en la base de datos PostgreSQL con estado `pending`.
5. Se publica mensaje `document.uploaded` en Redis con el ID del documento.
6. Se devuelve respuesta 202 con el ID del documento y URL de seguimiento de estado.

---

### 3.3 Processing Workers

**Tecnología:** Python 3.11 + Celery + LangChain.

**Responsabilidades:**
- Consumir mensajes de la cola de documentos pendientes.
- Extraer texto de los documentos (PDF: PyPDF2 / pdfplumber; DOCX: python-docx; MD/TXT: lectura directa).
- Fragmentar el texto en chunks usando `RecursiveCharacterTextSplitter`.
- Generar embeddings para cada chunk usando el modelo de embeddings configurado.
- Almacenar los chunks y sus embeddings en el Vector Store.
- Actualizar el estado del documento en PostgreSQL a `indexed` o `error`.
- Publicar evento `document.indexed` si el proceso fue exitoso.

**Parámetros de chunking (configurables por colección):**
- `chunk_size`: 512 caracteres (default).
- `chunk_overlap`: 64 caracteres (default).
- `separators`: `["\n\n", "\n", ".", " ", ""]`.

**Modelo de embeddings:** `sentence-transformers/all-MiniLM-L6-v2` ejecutado en local (salida: vectores de 384 dimensiones).

**Escalabilidad:** Los workers escalan horizontalmente. En picos de carga se pueden levantar instancias adicionales con `docker compose scale worker=N`.

---

### 3.4 Vector Store

**Tecnología:** ChromaDB (entorno de pruebas / desarrollo) o Qdrant (producción).

**Responsabilidades:**
- Almacenar los vectores de embeddings junto con los metadatos de cada chunk.
- Responder a consultas de similitud semántica (búsqueda kNN aproximada).
- Permitir filtrado por metadatos (colección, tipo de documento, fecha, etc.).

**Metadatos almacenados por chunk:**
```json
{
  "document_id": "doc_a3f9c1",
  "collection_id": "col_tech_docs",
  "chunk_index": 14,
  "source_file": "manual_tecnico_http.pdf",
  "page": 7,
  "created_at": "2026-01-20T09:17:32Z",
  "confidentiality": "internal"
}
```

**Configuración de ChromaDB:**
- Colección por organización con particionamiento por `collection_id`.
- Función de distancia: coseno.
- Índice HNSW para búsqueda aproximada eficiente.

**Configuración de Qdrant (producción):**
- Colección única con payload indexado.
- Replicación a 2 nodos para alta disponibilidad.
- Cuantización de vectores a int8 para reducción de memoria.

---

### 3.5 Query Service (Pipeline RAG)

**Tecnología:** Python 3.11 + FastAPI + LangChain.

**Responsabilidades:**
- Recibir consultas en lenguaje natural.
- Generar el embedding de la consulta con el mismo modelo usado en la ingesta.
- Recuperar del Vector Store los `top_k` fragmentos más relevantes semánticamente.
- Construir el prompt con el contexto recuperado.
- Enviar el prompt al LLM Service y devolver la respuesta generada.
- Almacenar el historial de consultas en PostgreSQL.
- Exponer el endpoint de feedback para valoración de respuestas.

**Construcción del prompt:**
```
Eres un asistente de gestión del conocimiento corporativo.
Responde a la siguiente pregunta basándote EXCLUSIVAMENTE en el contexto proporcionado.
Si la información no está en el contexto, responde que no tienes información suficiente.
No inventes datos ni utilices conocimiento externo al contexto.

CONTEXTO:
{fragmento_1}

{fragmento_2}

{fragmento_3}

PREGUNTA:
{consulta_del_usuario}

RESPUESTA:
```

**Estrategia de recuperación:** Se recuperan `top_k * 2` candidatos del vector store y se re-rankea con un cross-encoder (`cross-encoder/ms-marco-en-MiniLM-L-6-v2`) para seleccionar los `top_k` más relevantes finales. Esto mejora la precisión de la recuperación frente a la búsqueda vectorial directa.

---

### 3.6 LLM Service (Ollama)

**Tecnología:** Ollama ejecutado en contenedor Docker con acceso a GPU si disponible.

**Modelos disponibles:**
| Modelo | Tamaño en disco | RAM requerida | Calidad |
|--------|----------------|---------------|---------|
| `llama3:8b` | 4.7 GB | 8 GB | Buena |
| `llama3:70b` | 40 GB | 48 GB | Excelente |
| `mistral:7b` | 4.1 GB | 6 GB | Buena |
| `nomic-embed-text` | 274 MB | 1 GB | — (solo embeddings) |

**Comunicación:** El Query Service y los Processing Workers se comunican con Ollama via API HTTP local (`http://ollama:11434`). La comunicación nunca sale de la red privada de Docker.

**Configuración de generación:**
- `temperature`: 0.1 (respuestas más deterministas y fieles al contexto).
- `top_p`: 0.9.
- `max_tokens`: 1024.
- `context_window`: 8192 tokens.

---

### 3.7 Document Store (MinIO)

**Tecnología:** MinIO, compatible con la API de S3.

**Responsabilidades:**
- Almacenar los archivos originales de los documentos.
- Proporcionar URLs presignadas para descarga de documentos por usuarios autorizados.
- Gestionar el ciclo de vida de los archivos (retención, eliminación).

**Organización del almacenamiento:**
```
bucket: corporate-knowledge
├── documents/
│   ├── {organization_id}/
│   │   ├── {document_id}/
│   │   │   ├── v1_original.pdf
│   │   │   ├── v2_original.pdf
│   │   │   └── metadata.json
└── exports/
    └── {user_id}/
        └── {export_id}.zip
```

---

### 3.8 Base de datos relacional (PostgreSQL)

**Tecnología:** PostgreSQL 16.

**Tablas principales:**

- `organizations`: Datos de la organización.
- `users`: Cuentas de usuario con roles y permisos.
- `collections`: Agrupaciones lógicas de documentos.
- `documents`: Metadatos de documentos (título, tipo, estado, versiones).
- `query_history`: Historial de consultas con respuesta y fuentes.
- `query_feedback`: Valoraciones de respuestas por usuarios.
- `api_keys`: Claves de API generadas por usuarios.
- `audit_log`: Registro de auditoría de operaciones sensibles.

---

## 4. Infraestructura y despliegue

### 4.1 Contenedores Docker

Todos los servicios se despliegan como contenedores Docker. El archivo `docker-compose.yml` en la raíz del repositorio permite levantar el sistema completo en local:

```bash
docker compose up -d
```

Servicios que levanta:
- `api-gateway` (Nginx)
- `ingestion-service`
- `query-service`
- `processing-worker` (3 réplicas por defecto)
- `ollama`
- `chromadb` o `qdrant`
- `minio`
- `postgres`
- `redis`
- `prometheus` + `grafana`

### 4.2 Kubernetes (producción)

En producción el sistema se despliega en un clúster Kubernetes interno. Los manifests se gestionan con Helm charts en el repositorio `gitlab.empresa.com/infrastructure/k8s-charts`.

**Namespaces:**
- `knowledge-platform`: Servicios de la plataforma.
- `knowledge-infra`: Bases de datos y message brokers.
- `knowledge-observability`: Stack de monitorización.

**Autoscaling:** HPA (Horizontal Pod Autoscaler) configurado para los `processing-workers` y el `query-service` basado en uso de CPU y longitud de la cola.

---

## 5. Seguridad de la arquitectura

### 5.1 Red

- Comunicación entre microservicios exclusivamente en la red privada de Docker/Kubernetes.
- Únicamente el API Gateway expone puertos al exterior.
- Políticas de red Kubernetes (NetworkPolicy) restringen las conexiones a las mínimas necesarias.

### 5.2 Cifrado

- Tráfico externo: TLS 1.3 con certificados renovados automáticamente (Let's Encrypt o PKI corporativa).
- Tráfico interno: mTLS entre microservicios (implementado con Linkerd service mesh en producción).
- Datos en reposo: cifrado a nivel de volumen con LUKS (Kubernetes) y cifrado nativo de MinIO y PostgreSQL.

### 5.3 Gestión de secretos

- Secretos de aplicación almacenados en HashiCorp Vault.
- Los contenedores reciben los secretos como variables de entorno inyectadas por el agente de Vault al inicio.
- Ningún secreto está hardcodeado en imágenes Docker ni en repositorios.

---

## 6. Monitorización y observabilidad

### 6.1 Métricas (Prometheus + Grafana)

Dashboards disponibles en Grafana (`monitoring.empresa.com`):
- **Overview del sistema:** estado de todos los servicios, latencia p50/p95/p99.
- **Pipeline RAG:** tiempo medio de respuesta, distribución por modelo, tasa de errores.
- **Ingesta:** documentos procesados/día, tiempo medio de indexación, errores por tipo.
- **Vector Store:** tamaño del índice, latencia de búsqueda, uso de memoria.
- **LLM:** latencia de inferencia, tokens generados/segundo, uso de GPU.

### 6.2 Logs (Loki)

Todos los servicios envían logs estructurados JSON a Loki vía Promtail. Disponibles en Grafana con el explorer de Loki. Retención: 90 días.

### 6.3 Trazas distribuidas (Jaeger)

El Query Service instrumenta cada petición con OpenTelemetry, generando trazas que cubren todos los componentes involucrados: búsqueda vectorial, generación del prompt, inferencia del LLM. Esto permite identificar cuellos de botella con precisión.

---

## 7. Decisiones arquitectónicas relevantes (ADRs)

| ID | Decisión | Fecha |
|----|----------|-------|
| ADR-001 | Usar ChromaDB en dev y Qdrant en producción | 2025-04 |
| ADR-002 | Ollama como runtime de LLMs (vs. llama.cpp directo) | 2025-05 |
| ADR-003 | RecursiveCharacterTextSplitter como estrategia de chunking | 2025-06 |
| ADR-004 | Re-ranking con cross-encoder para mejorar precisión | 2025-09 |
| ADR-005 | MinIO como Object Store compatible con S3 | 2025-04 |
| ADR-006 | FastAPI como framework para microservicios Python | 2025-03 |

Los ADRs completos están en `docs/adr/` del repositorio principal.
