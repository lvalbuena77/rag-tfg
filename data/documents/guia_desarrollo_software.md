# Guía de Desarrollo de Software — Estándares y Buenas Prácticas

Versión: 2.0  
Vigencia: Enero 2026 — Diciembre 2026  
Responsable: Equipo de Arquitectura y Calidad  
Alcance: Todos los equipos de desarrollo de la organización

---

## Propósito

Este documento establece los estándares, convenciones y buenas prácticas que deben seguir todos los equipos de desarrollo de software de la empresa. Su objetivo es garantizar la coherencia del código, facilitar la colaboración, reducir la deuda técnica y mejorar la calidad y mantenibilidad de los productos.

El cumplimiento de estas guías es obligatorio para todo el código que se integre en las ramas principales de los repositorios corporativos.

---

## 1. Entorno de Desarrollo

### 1.1 Requisitos mínimos

- **Sistema operativo:** Linux (Ubuntu 22.04+), macOS (Ventura+), o Windows 11 con WSL2.
- **IDE recomendado:** Visual Studio Code con las extensiones del pack corporativo (ver `extensions.json` en el repositorio de plantillas).
- **Gestión de versiones:** Git 2.40+. Obligatorio configurar nombre y correo corporativo: `git config --global user.email "nombre@empresa.com"`.
- **Contenedores:** Docker Desktop 4.x o Docker Engine + Docker Compose v2.

### 1.2 Configuración inicial

Clona el repositorio de plantillas de entorno de desarrollo:
```bash
git clone gitlab.empresa.com/infrastructure/dev-setup.git
cd dev-setup
./setup.sh --profile <backend|frontend|data>
```

Este script configura: hooks de Git, alias de comandos frecuentes, certificados corporativos, acceso al registro de imágenes Docker interno y configuración del proxy si corresponde.

---

## 2. Control de Versiones (Git)

### 2.1 Estrategia de ramas (Git Flow)

| Rama | Propósito | Protección |
|------|-----------|-----------|
| `main` | Código en producción | Push directo prohibido, requiere PR revisado |
| `develop` | Integración de features | Push directo prohibido, requiere PR |
| `feature/descripcion-corta` | Nuevas funcionalidades | Sin protección |
| `fix/descripcion-corta` | Corrección de bugs | Sin protección |
| `hotfix/descripcion-corta` | Parches urgentes a producción | Sin protección, PR con review express |
| `release/vX.Y.Z` | Preparación de versión | Rama temporal |

### 2.2 Convención de commits (Conventional Commits)

Todos los commits deben seguir el estándar Conventional Commits:

```
<tipo>(<scope>): <descripción corta>

[cuerpo opcional]

[footer opcional: referencias a issues/tickets]
```

**Tipos permitidos:**
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `docs`: cambios en documentación
- `style`: formateo, espacios (sin cambio de lógica)
- `refactor`: refactorización sin cambio funcional
- `test`: adición o modificación de tests
- `chore`: cambios en build, CI, dependencias
- `perf`: mejoras de rendimiento

**Ejemplos válidos:**
```
feat(auth): añadir soporte para login con OAuth2
fix(api): corregir timeout en cliente HTTP cuando la respuesta es lenta
docs(readme): actualizar instrucciones de instalación
test(ingesta): añadir tests unitarios para el parser de PDFs
chore(deps): actualizar langchain a 0.3.1
```

**Reglas adicionales:**
- Descripción corta en imperativo en español, sin punto final, máx. 72 caracteres.
- El cuerpo del commit debe explicar el *qué* y el *por qué*, no el *cómo*.
- Referencia siempre el ticket de Jira cuando corresponda: `Closes PLAT-1234`.

### 2.3 Pull Requests

- El título del PR debe seguir la misma convención de commits.
- Todo PR debe incluir: descripción del cambio, tipo de cambio (feature/fix/etc.), cómo probar los cambios, capturas de pantalla si aplica (para cambios de UI).
- Mínimo **2 aprobaciones** de revisores para PR a `develop`; **3 aprobaciones** para PR a `main`.
- Los PRs no deben superar los 400 líneas de cambio. Si es mayor, dividirlo en PRs más pequeños.
- Está prohibido mergear el propio PR sin aprobaciones, incluso para hotfixes.

---

## 3. Estándares de Código

### 3.1 Python

- **Versión mínima:** Python 3.11.
- **Estilo:** PEP 8. Usar `ruff` como linter y formateador (`ruff format` + `ruff check`).
- **Tipado:** Obligatorio uso de type hints en funciones públicas (mypy en modo estricto para módulos críticos).
- **Docstrings:** Formato Google para funciones y clases públicas.
- **Gestión de dependencias:** `uv` o `pip-tools`. Siempre `requirements.txt` con versiones fijadas ([`pip-compile`](https://github.com/jazzband/pip-tools)).
- **Testing:** `pytest` con cobertura mínima del 80% para módulos nuevos.

Ejemplo de función bien documentada y tipada:
```python
def split_documents(
    documents: list[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[Document]:
    """Divide documentos en fragmentos para procesamiento RAG.

    Args:
        documents: Lista de documentos LangChain a fragmentar.
        chunk_size: Tamaño máximo de cada fragmento en caracteres.
        chunk_overlap: Solapamiento entre fragmentos consecutivos.

    Returns:
        Lista de fragmentos (chunks) con metadatos preservados.

    Raises:
        ValueError: Si chunk_size <= chunk_overlap.
    """
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size debe ser mayor que chunk_overlap")
    ...
```

### 3.2 JavaScript / TypeScript

- **Versión:** Node.js LTS (actualmente 20.x). TypeScript 5.x obligatorio (sin `any` implícito).
- **Estilo:** ESLint con config corporativa (`@empresa/eslint-config`). Prettier para formato.
- **Módulos:** ESM (import/export), no CommonJS para código nuevo.
- **Testing:** Vitest para unit tests; Playwright para tests E2E.
- **Cobertura mínima:** 75%.

### 3.3 Reglas generales (todos los lenguajes)

- Sin código comentado en el repositorio (usar git para recuperar versiones anteriores).
- Sin `TODO` o `FIXME` sin ticket de Jira asociado: `// TODO(PLAT-456): refactorizar cuando...`.
- Longitud máxima de línea: 120 caracteres.
- Funciones con una única responsabilidad; longitud máxima orientativa: 50 líneas.
- Sin magic numbers: usar constantes con nombre descriptivo.
- Nombres en inglés para variables, funciones y clases; comentarios y documentación en español.

---

## 4. Testing

### 4.1 Pirámide de tests

Se debe respetar la pirámide de testing:
- **Tests unitarios (70%):** Prueban funciones/clases aisladas con dependencias mockeadas. Deben ser rápidos (<1ms por test) y sin I/O real.
- **Tests de integración (20%):** Prueban la interaction entre componentes reales (base de datos, servicios internos). Se ejecutan en CI con contenedores Docker.
- **Tests E2E (10%):** Prueban flujos completos desde la interfaz. Se ejecutan pre-deploy en staging.

### 4.2 Nomenclatura de tests

```
test_<qué_se_prueba>_<condición>_<resultado_esperado>
```

Ejemplo: `test_split_documents_empty_list_returns_empty_list`

### 4.3 Ejecución

```bash
# Tests unitarios
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Tests de integración (requiere Docker)
pytest tests/integration/ -v --docker

# Todos los tests con reporte HTML
pytest --cov=src --cov-report=html:reports/coverage
```

### 4.4 CI/CD y tests

- Los tests unitarios se ejecutan en cada push (pipeline CI de GitLab).
- Los tests de integración se ejecutan en cada PR a `develop` y `main`.
- Un pipeline fallido **bloquea** el merge del PR.
- La cobertura no puede disminuir más de un 2% respecto a la rama base.

---

## 5. Seguridad en el Desarrollo

### 5.1 Gestión de secretos

- **Nunca** commitear credenciales, API keys, contraseñas o certificados en el repositorio.
- Usar variables de entorno para todos los secretos en desarrollo local (archivo `.env`, nunca commiteado; añadir al `.gitignore`).
- En producción, usar el sistema de secretos corporativo (HashiCorp Vault o Kubernetes Secrets cifrados).
- Activar el hook `pre-commit` de detección de secretos: incluido en el script de setup.

### 5.2 Dependencias

- Revisar vulnerabilidades con `pip audit` (Python) o `npm audit` (JS) antes de cada release.
- Las dependencias con vulnerabilidades críticas deben actualizarse en un máximo de 72 horas.
- Usar Dependabot configurado en GitLab para alertas automáticas.

### 5.3 OWASP Top 10

Todo el código que maneje entrada de usuario debe contemplar:
- **Inyección:** Usar ORMs o queries parametrizadas; nunca concatenar SQL.
- **XSS:** Escapar salidas HTML; usar librerías de sanitización.
- **SSRF:** Validar y restringir URLs externas; usar allowlists.
- **Autenticación:** No implementar crypto o auth propias; usar librerías auditadas.

---

## 6. Documentación

### 6.1 README de repositorio

Todo repositorio debe tener un `README.md` con: descripción del proyecto, arquitectura de alto nivel, requisitos e instrucciones de instalación, instrucciones de ejecución (dev, test, producción), variables de entorno necesarias, y enlace a documentación detallada.

### 6.2 ADRs (Architecture Decision Records)

Las decisiones arquitectónicas relevantes deben documentarse como ADR en la carpeta `docs/adr/` del repositorio. Usar la plantilla disponible en `gitlab.empresa.com/infrastructure/templates/adr-template.md`. Ejemplos de decisiones que requieren ADR: elección de base de datos, estrategia de autenticación, elección de framework principal, cambios en la estrategia de versionado de API.

### 6.3 Documentación de API

Las APIs REST deben estar documentadas con OpenAPI 3.x. Usar anotaciones en el código cuando sea posible (FastAPI genera la especificación automáticamente). La documentación debe estar disponible en `/api/docs` en entornos de desarrollo e integración.

---

## 7. Proceso de Deploy

### 7.1 Entornos

| Entorno | Rama | Deploy | Propósito |
|---------|------|--------|-----------|
| Local | cualquier | Manual | Desarrollo |
| Dev | `develop` | Automático post-merge | Pruebas internas |
| Staging | `release/*` | Automático | QA y UAT |
| Producción | `main` | Manual con aprobación | Usuarios finales |

### 7.2 Versioning semántico

Los proyectos siguen [Semantic Versioning 2.0](https://semver.org/): `MAYOR.MENOR.PARCHE`.
- **MAYOR:** cambios incompatibles con versiones anteriores.
- **MENOR:** nuevas funcionalidades compatibles hacia atrás.
- **PARCHE:** correcciones de bugs compatibles.

### 7.3 Checklist pre-release

Antes de crear una release:
- [ ] Todos los tests pasan en staging.
- [ ] Revisión de seguridad completada (SAST en CI).
- [ ] `CHANGELOG.md` actualizado.
- [ ] Versión actualizada en archivos de configuración.
- [ ] Revisión de rendimiento si hay cambios en rutas críticas.
- [ ] Documentación actualizada.
- [ ] Aprobación del Tech Lead y Product Manager.

---

## 8. Monitorización y Logging

### 8.1 Niveles de log

Usar siempre logs estructurados (JSON) con los niveles estándar:
- `DEBUG`: Información detallada para desarrollo. Desactivado en producción.
- `INFO`: Eventos operacionales normales (inicio de proceso, operación completada).
- `WARNING`: Situación inesperada pero recuperable.
- `ERROR`: Error que impide completar una operación.
- `CRITICAL`: Fallo grave que requiere intervención inmediata.

### 8.2 Qué incluir en cada log

```python
logger.info(
    "Documento indexado correctamente",
    extra={
        "document_id": doc_id,
        "chunks_generated": chunk_count,
        "duration_ms": elapsed_ms,
        "user_id": user_id,
    }
)
```

Nunca loguear: contraseñas, tokens, datos personales sensibles, contenido de documentos confidenciales.

### 8.3 Métricas

Instrumentar con Prometheus las métricas clave de cada servicio:
- Latencia de operaciones (histograma).
- Tasa de errores (contador).
- Throughput de peticiones (contador).
- Estado de dependencias (gauge).

---

## Apéndice: Recursos internos

- Plantillas de repositorio: `gitlab.empresa.com/infrastructure/templates`
- Configuración de linters: `gitlab.empresa.com/infrastructure/linting-configs`
- Imágenes Docker base: `registry.empresa.com/base-images`
- Portal de documentación: `docs.empresa.com`
- Canal de consultas: #dev-standards en Slack
