# Referencia de la API Interna — Plataforma de Gestión del Conocimiento

Versión: 1.4.2  
Fecha de actualización: Febrero 2026  
Responsable: Equipo de Plataforma e Integración

---

## Introducción

Esta documentación describe la API REST proporcionada por la Plataforma de Gestión del Conocimiento Corporativo. La API permite integrar las capacidades de búsqueda semántica y consulta de documentos en aplicaciones externas o automatizar flujos de trabajo relacionados con la gestión documental.

La API sigue los principios REST: recursos identificados por URLs, uso semántico de verbos HTTP (GET, POST, PUT, DELETE, PATCH), respuestas en JSON y uso de códigos de estado HTTP estándar.

**URL base:** `https://plataforma.empresa.com/api/v1`

---

## Autenticación

### API Key

Incluye la clave en la cabecera de every petición:

```
Authorization: Bearer <tu_api_key>
```

Las API Keys se gestionan en Perfil → Desarrollador → API Keys. Cada clave puede tener scopes limitados: `read`, `write`, `admin`.

### JWT Token

Para sesiones de usuario puedes obtener un token JWT:

**Endpoint:** `POST /auth/token`

**Body:**
```json
{
  "email": "usuario@empresa.com",
  "password": "contraseña_segura"
}
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJS...",
  "token_type": "Bearer",
  "expires_in": 28800
}
```

Los tokens expiran a las 8 horas. Para renovar sin re-autenticarse usa `POST /auth/refresh` con el token actual en la cabecera.

---

## Endpoints de Consulta

### POST /query

Realiza una consulta semántica a la base de conocimiento y devuelve una respuesta generada por el LLM junto con los fragmentos de documentación más relevantes.

**Cabeceras requeridas:**
```
Authorization: Bearer <api_key>
Content-Type: application/json
```

**Body:**
```json
{
  "query": "¿Cómo se configura el timeout en el cliente HTTP?",
  "collection_ids": ["col_tech_docs", "col_apis"],
  "top_k": 5,
  "model": "llama3-8b",
  "language": "es",
  "include_sources": true
}
```

**Parámetros del body:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `query` | string | Sí | Pregunta o consulta en lenguaje natural (máx. 2000 caracteres) |
| `collection_ids` | array[string] | No | IDs de colecciones a consultar. Si se omite, consulta todas las accesibles |
| `top_k` | integer | No | Número de fragmentos a recuperar (1-20, default: 5) |
| `model` | string | No | Modelo LLM a usar: `llama3-8b`, `llama3-70b`, `mistral-7b` (default: configurado por admin) |
| `language` | string | No | Idioma de la respuesta: `es`, `en` (default: `es`) |
| `include_sources` | boolean | No | Incluir fuentes en la respuesta (default: `true`) |

**Respuesta exitosa (200):**
```json
{
  "answer": "Para configurar el timeout en el cliente HTTP se debe...",
  "sources": [
    {
      "document_id": "doc_a3f9c1",
      "document_title": "Manual Técnico Cliente HTTP v2.3",
      "page": 14,
      "chunk_text": "El timeout de conexión se configura mediante el parámetro connection_timeout...",
      "relevance_score": 0.94
    }
  ],
  "model_used": "llama3-8b",
  "query_id": "qry_7b2d34",
  "processing_time_ms": 1842
}
```

**Códigos de error:**

| Código | Descripción |
|--------|-------------|
| 400 | Query vacía o demasiado larga |
| 401 | Token inválido o expirado |
| 403 | Sin permisos sobre la colección solicitada |
| 429 | Límite de peticiones superado |
| 500 | Error interno del servidor |
| 503 | Modelo LLM no disponible |

---

### GET /query/{query_id}

Recupera el resultado de una consulta previamente realizada.

**Parámetros de ruta:**
- `query_id` (string): Identificador único de la consulta.

**Respuesta exitosa (200):** Mismo formato que POST /query.

**Nota:** Los resultados de consultas se almacenan durante 30 días.

---

## Endpoints de Documentos

### GET /documents

Lista los documentos accesibles para el usuario autenticado.

**Parámetros de query:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `collection_id` | string | Filtrar por colección |
| `type` | string | Tipo de archivo: `pdf`, `docx`, `md`, `txt` |
| `page` | integer | Página de resultados (default: 1) |
| `per_page` | integer | Resultados por página (1-100, default: 20) |
| `sort` | string | Campo de ordenación: `created_at`, `title`, `updated_at` |
| `order` | string | Dirección: `asc`, `desc` |

**Ejemplo de petición:**
```
GET /documents?collection_id=col_tech_docs&type=pdf&per_page=10
```

**Respuesta exitosa (200):**
```json
{
  "documents": [
    {
      "document_id": "doc_a3f9c1",
      "title": "Manual Técnico Cliente HTTP v2.3",
      "type": "pdf",
      "collection_id": "col_tech_docs",
      "size_bytes": 2457600,
      "created_at": "2025-11-14T10:32:00Z",
      "updated_at": "2026-01-20T09:15:00Z",
      "indexed": true,
      "author": "Equipo Backend",
      "tags": ["http", "cliente", "configuracion"]
    }
  ],
  "total": 142,
  "page": 1,
  "per_page": 10
}
```

---

### POST /documents

Sube un nuevo documento a la plataforma para su indexación.

**Content-Type:** `multipart/form-data`

**Campos del formulario:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `file` | file | Sí | Archivo a subir (PDF, DOCX, MD, TXT) |
| `collection_id` | string | Sí | Colección destino |
| `title` | string | No | Título del documento (default: nombre del archivo) |
| `description` | string | No | Descripción breve del contenido |
| `tags` | string | No | Etiquetas separadas por coma |
| `confidentiality` | string | No | Nivel: `public`, `internal`, `confidential` (default: `internal`) |

**Respuesta exitosa (202 Accepted):**
```json
{
  "document_id": "doc_n8x2v4",
  "title": "Guia Despliegue Microservicio A",
  "status": "processing",
  "estimate_seconds": 45,
  "status_url": "/documents/doc_n8x2v4/status"
}
```

La respuesta es 202 porque el procesamiento (extracción, chunking, embedding) es asíncrono.

---

### GET /documents/{document_id}

Obtiene los metadatos y estado de un documento específico.

**Respuesta exitosa (200):**
```json
{
  "document_id": "doc_a3f9c1",
  "title": "Manual Técnico Cliente HTTP v2.3",
  "type": "pdf",
  "collection_id": "col_tech_docs",
  "size_bytes": 2457600,
  "pages": 48,
  "chunks_count": 312,
  "created_at": "2025-11-14T10:32:00Z",
  "updated_at": "2026-01-20T09:15:00Z",
  "indexed": true,
  "indexing_completed_at": "2026-01-20T09:17:32Z",
  "author": "Equipo Backend",
  "tags": ["http", "cliente", "configuracion"],
  "confidentiality": "internal",
  "version": 3
}
```

---

### DELETE /documents/{document_id}

Elimina un documento y sus embeddings asociados.

**Respuesta exitosa (204 No Content).**

La eliminación es lógica durante 30 días (el documento va a la papelera). Pasado ese plazo se elimina permanentemente. Para eliminar inmediatamente, añade el query param `?permanent=true` (requiere scope `admin`).

---

### GET /documents/{document_id}/status

Consulta el estado del procesamiento de un documento.

**Respuesta:**
```json
{
  "document_id": "doc_n8x2v4",
  "status": "indexed",
  "chunks_generated": 87,
  "embeddings_computed": 87,
  "indexing_completed_at": "2026-02-10T14:23:11Z",
  "errors": []
}
```

**Valores de `status`:** `pending`, `processing`, `indexed`, `error`.

---

## Endpoints de Colecciones

### GET /collections

Lista todas las colecciones accesibles para el usuario.

**Respuesta (200):**
```json
{
  "collections": [
    {
      "collection_id": "col_tech_docs",
      "name": "Documentación Técnica",
      "description": "Manuales técnicos y guías de desarrollo",
      "document_count": 142,
      "created_at": "2025-05-01T00:00:00Z",
      "owner": "Equipo Arquitectura"
    }
  ]
}
```

### POST /collections

Crea una nueva colección.

**Body:**
```json
{
  "name": "Documentación Proyecto Alpha",
  "description": "Documentos del proyecto de migración de infraestructura",
  "visibility": "team",
  "team_ids": ["team_backend", "team_devops"]
}
```

---

## Endpoints de Feedback

### POST /query/{query_id}/feedback

Envía valoración sobre la calidad de una respuesta.

**Body:**
```json
{
  "rating": 1,
  "comment": "La respuesta era correcta y las fuentes relevantes"
}
```

El campo `rating` acepta `1` (positiva) o `-1` (negativa). El comentario es opcional (máx. 500 caracteres).

---

## Rate Limiting y Buenas Prácticas

El sistema aplica rate limiting por API Key:

- **Plan estándar:** 1.000 req/hora, 10.000 req/día
- **Plan premium:** 10.000 req/hora
- **Burst máximo:** 50 req/10 segundos

Cabeceras de respuesta relevantes:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1735689600
```

**Recomendaciones:**
- Implementa backoff exponencial cuando recibas errores 429.
- Almacena en caché los resultados de consultas idénticas.
- Usa `collection_ids` para acotar el alcance de las búsquedas y mejorar tiempos de respuesta.
- El endpoint `POST /query` admite hasta 10 peticiones concurrentes por API Key.

---

## Webhooks

Puedes configurar webhooks para recibir notificaciones de eventos asíncronate.

**Eventos disponibles:**

| Evento | Descripción |
|--------|-------------|
| `document.indexed` | Un documento ha sido procesado e indexado correctamente |
| `document.error` | Error durante el procesamiento de un documento |
| `document.deleted` | Un documento ha sido eliminado |
| `collection.created` | Se ha creado una nueva colección |

**Configuración:** Perfil → Desarrollador → Webhooks → "Añadir endpoint".

**Payload de ejemplo (document.indexed):**
```json
{
  "event": "document.indexed",
  "timestamp": "2026-02-10T14:23:11Z",
  "data": {
    "document_id": "doc_n8x2v4",
    "title": "Guia Despliegue Microservicio A",
    "collection_id": "col_devops"
  }
}
```

Los webhooks incluyen la cabecera `X-Platform-Signature` con una firma HMAC-SHA256 del payload usando el secreto configurado. Siempre verifica esta firma antes de procesar el evento.

---

## SDKs disponibles

| Lenguaje | Repositorio | Estado |
|----------|-------------|--------|
| Python | `gitlab.empresa.com/platform/sdk-python` | Estable (v1.2.0) |
| JavaScript / TypeScript | `gitlab.empresa.com/platform/sdk-js` | Estable (v1.1.3) |
| Java | `gitlab.empresa.com/platform/sdk-java` | Beta (v0.9.0) |
| Go | `gitlab.empresa.com/platform/sdk-go` | Planificado |

**Ejemplo de uso con SDK Python:**
```python
from platform_sdk import KnowledgeClient

client = KnowledgeClient(api_key="tu_api_key")

response = client.query(
    "¿Cómo configurar la autenticación OAuth2?",
    collection_ids=["col_tech_docs"],
    top_k=5
)

print(response.answer)
for source in response.sources:
    print(f"- {source.document_title} (score: {source.relevance_score:.2f})")
```

---

## Changelog

### v1.4.2 (Febrero 2026)
- Añadido soporte para modelo `llama3-70b` en `POST /query`.
- Nuevo campo `processing_time_ms` en respuestas de consulta.
- Mejora de rendimiento en la búsqueda semántica (~30% más rápida).

### v1.4.0 (Enero 2026)
- Nuevo endpoint `POST /query/{query_id}/feedback`.
- Soporte para webhooks.
- SDK Python actualizado a v1.2.0.

### v1.3.0 (Noviembre 2025)
- Añadidos parámetros `language` y `model` en `POST /query`.
- Nuevo endpoint `GET /documents/{document_id}/status`.
- Rate limiting por burst añadido.
