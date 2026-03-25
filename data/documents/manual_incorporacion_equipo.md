# Manual de Incorporación — Equipo de Ingeniería

Versión: 4.2  
Última actualización: Febrero 2026  
Responsable: People & Engineering / Tech Leads  
Destinatarios: Nuevos empleados del área de Ingeniería de Software

---

## Bienvenida

¡Bienvenido al equipo de Ingeniería! Este manual tiene como objetivo que tu incorporación sea lo más fluida posible. Lo hemos diseñado pensando en que puedas ser autónomo desde el primer día y tener respuesta a las siguientes preguntas: ¿qué herramientas necesito? ¿a quién pregunto? ¿qué se espera de mí en las primeras semanas?

Léelo con detenimiento y no dudes en hacer preguntas. Nadie espera que lo sepas todo desde el primer día.

---

## 1. Antes del Primer Día

### ¿Qué deberías tener antes de empezar?

Antes de tu primer día, el equipo de IT habrá enviado a tu correo personal:

- Credenciales de acceso a tu cuenta corporativa (correo `@empresa.com`).
- Instrucciones para configurar la MFA (autenticación multifactor).
- Enlace al portal de autoservicio de IT para solicitar hardware adicional si lo necesitas.
- Acceso VPN: instrucciones y certificado de cliente.

Si no has recibido alguno de estos elementos el día anterior a tu incorporación, contacta con `it-onboarding@empresa.com`.

### Equipo que se te asignará

El primer día recogerás en recepción:
- Portátil corporativo (MacBook Pro o ThinkPad según perfil).
- Periféricos básicos (monitor, teclado, ratón).
- Tarjeta de acceso a las instalaciones.

Si necesitas hardware específico (monitor adicional, webcam, auriculares profesionales), puedes solicitarlo en el portal de IT con justificación de negocio. El tiempo de entrega habitual es de 3-5 días.

---

## 2. Primera Semana: Configuración del Entorno

### 2.1 Accesos que debes solicitar

Solicita los siguientes accesos el primer día al equipo de IT (portal `it.empresa.com/accesos`):

| Sistema | Acceso requerido | Aprobado por |
|---------|-----------------|--------------|
| GitLab corporativo | Usuario con acceso a proyectos de tu equipo | Tech Lead |
| Jira | Acceso al proyecto de tu equipo | Product Manager |
| Confluence | Acceso al espacio de tu departamento | Tech Lead |
| Slack | Canales de equipo y generales | RR.HH. (automático) |
| AWS / GCP (si aplica) | Rol de acceso restringido | Responsable arquitectura |
| VPN | Certificado de cliente | IT (automático tras alta) |
| Plataforma de conocimiento | Perfil en plataforma interna | Automático |

### 2.2 Configuración del entorno de desarrollo

Sigue las instrucciones del repositorio de setup:
```bash
git clone gitlab.empresa.com/infrastructure/dev-setup.git
cd dev-setup
./setup.sh --profile backend   # o 'frontend', 'data', 'fullstack'
```

El script realiza automáticamente:
- Instalación de herramientas base (git, docker, nvm/pyenv, etc.).
- Configuración de Git con tus credenciales corporativas.
- Instalación de las extensiones de VS Code del equipo.
- Configuración del proxy corporativo si estás en oficina.
- Instalación de hooks de pre-commit (linting, detección de secretos).
- Acceso al registro de imágenes Docker interno.

Si algo falla durante el setup, abre un issue en el repositorio con el error completo. Hay un canal de Slack #dev-setup para ayuda durante las primeras semanas.

### 2.3 Primer acceso a los repositorios

Los repositorios principales de tu equipo están documentados en el Confluence de tu departamento (espacio `ENG > Equipos > [tu equipo]`). Los más comunes son:

- Repositorio principal del producto.
- Repositorio de infraestructura.
- Repositorio de documentación técnica.
- Repositorio de herramientas internas.

Solicita acceso a cada repositorio mediante una MR a `gitlab.empresa.com/infrastructure/access-requests`, siguiendo la plantilla disponible.

---

## 3. Estructura del Equipo y Comunicación

### 3.1 Organización de los equipos

La ingeniería está organizada en squads multidisciplinares, cada uno con:
- **Tech Lead (TL):** Responsable técnico, tu principal punto de contacto técnico.
- **Product Manager (PM):** Responsable de producto, priorización y roadmap.
- **Diseñador UX:** Colabora en funcionalidades con impacto en usuario (no todos los squads).
- **Ingenieros de Software:** Backend, frontend, full-stack o data según el squad.
- **QA Engineer:** Garantiza la calidad (en squads grandes; en squads pequeños la responsabilidad es compartida).

### 3.2 Ceremonias ágiles

Todos los squads siguen metodología Scrum con sprints de 2 semanas:

| Ceremonia | Frecuencia | Duración | Participantes |
|-----------|-----------|----------|---------------|
| Sprint Planning | Inicio de sprint | 2h | Squad completo |
| Daily Standup | Cada día laborable | 15 min | Squad completo |
| Sprint Review | Fin de sprint | 1h | Squad + stakeholders |
| Sprint Retrospective | Fin de sprint | 1h | Squad completo |
| Refinement | Mitad de sprint | 1h | Squad completo |

### 3.3 Canales de comunicación

**Slack** es la herramienta de comunicación principal. Canales obligatorios:
- `#general`: Comunicaciones de toda la empresa.
- `#ingenieria`: Anuncios y debates técnicos de todo el departamento.
- `#[tu-squad]`: Canal de tu equipo (daily async, preguntas rápidas).
- `#incidencias`: Alertas de sistemas y comunicación de incidentes.
- `#dev-standards`: Consultas sobre estándares de desarrollo.

**Correo electrónico:** Para comunicaciones formales, contratos o comunicaciones con personas externas a la empresa.

**Documentación permanente:** Todo lo que necesite perdurar va a Confluence o al repositorio de documentación. No uses Slack para archivar decisiones importantes.

---

## 4. Proceso de Desarrollo y Flujo de Trabajo

### 4.1 Ciclo de una tarea

1. **Backlog refinement:** La tarea está en el backlog de Jira con descripción, criterios de aceptación y story points estimados.
2. **Sprint Planning:** La tarea se incluye en el sprint y se asigna a un developer.
3. **Desarrollo:** Crea una rama `feature/JIRA-XXX-descripcion-corta` desde `develop`. Desarrolla siguiendo los estándares de código (ver Guía de Desarrollo).
4. **Pull Request:** Abre un PR en GitLab con el título en formato Conventional Commits. Incluye la referencia al ticket de Jira en la descripción.
5. **Code Review:** Dos compañeros revisan el código. Las observaciones deben resolverse antes de mergear.
6. **CI/CD:** El pipeline verifica que los tests pasan y que no hay regresión de cobertura.
7. **Merge y deploy a develop:** Una vez aprobado, el PR se mergea y se despliega automáticamente al entorno de desarrollo.
8. **QA:** El QA Engineer (o el developer en squads pequeños) verifica el funcionamiento en el entorno de desarrollo.
9. **Release:** En el sprint end, las features validadas se incluyen en la release a producción.

### 4.2 Estimación de tareas

El equipo usa puntos de historia de Fibonacci (1, 2, 3, 5, 8, 13). La referencia:
- **1 punto:** Una tarea claramente definida, menos de 2 horas.
- **2 puntos:** Algo claro pero con algo de trabajo, medio día.
- **3 puntos:** Un día de trabajo.
- **5 puntos:** 2-3 días de trabajo.
- **8 puntos:** Una semana. Si es más, debería dividirse.
- **13 puntos:** Demasiado grande; dividir obligatoriamente antes de comprometerse.

---

## 5. Cultura de Equipo y Expectativas

### 5.1 Code Review: cultura constructiva

El code review es una herramienta de mejora colectiva, no de evaluación individual. Principios:
- Revisar el código, no a la persona. Los comentarios van sobre las decisiones técnicas, no sobre quien las tomó.
- Explicar el *por qué* de las sugerencias, no solo el *qué*.
- Distinguir entre bloqueos ("esto tiene un bug de seguridad") y sugerencias ("podrías simplificar esto con X, aunque funciona igual").
- El autor siempre tiene la última palabra en decisiones de estilo que no violan estándares. El revisor puede reiterar su sugerencia, pero no bloquear por preferencias personales.
- Responder a los comentarios de revisión en un plazo máximo de 1 día laborable.

### 5.2 Documentación como ciudadano de primera clase

Documentar no es una tarea opcional para cuando sobre tiempo. En nuestro equipo:
- Toda tarea que modifique el comportamiento del sistema incluye actualización de documentación como criterio de aceptación.
- Los ADRs (Architecture Decision Records) se escriben cuando se toma una decisión técnica relevante.
- Las postmortems de incidentes se documentan dentro de las 48 horas posteriores a la resolución.

### 5.3 Manejo de errores y fallos

Los fallos son oportunidades de aprendizaje, no motivos de penalización. Cuando ocurre un error:
1. **Primero, resuelve el problema** (no busques culpables mientras el sistema está caído).
2. **Documenta el incidente** en el canal #incidencias con impacto, causa raíz y acciones tomadas.
3. **Postmortem sin culpas:** Analiza el sistema, los procesos y las herramientas que permitieron que ocurriera. Detecta qué se puede mejorar estructuralmente.

### 5.4 Horario y disponibilidad

El equipo trabaja en modalidad híbrida: 3 días presenciales (martes, miércoles, jueves) y 2 en remoto. El horario es flexible dentro de la banda horaria de 9:00 a 19:00, siempre que la presencia en dailies y ceremonias quede garantizada.

Si un día no puedes asistir a la daily, comunícalo en el canal del squad con tu actualización escrita antes de las 10:00.

---

## 6. Herramientas Principales

| Herramienta | Propósito | URL / Instalación |
|-------------|-----------|-------------------|
| GitLab | Control de versiones, CI/CD, code review | `gitlab.empresa.com` |
| Jira | Gestión de tareas y sprints | `jira.empresa.com` |
| Confluence | Documentación y wiki | `confluence.empresa.com` |
| Slack | Comunicación en tiempo real | App de escritorio + móvil |
| VS Code | IDE (recomendado) | Descarga + pack de extensiones corporativo |
| Docker Desktop | Contenedores en local | `docker.empresa.com/setup` |
| Grafana | Monitorización y dashboards | `monitoring.empresa.com` |
| Vault (HashiCorp) | Gestión de secretos | Solo acceso desde CI/CD y con VPN |
| Sentry | Tracking de errores en producción | `sentry.empresa.com` |

---

## 7. Recursos de Formación

- **Documentación técnica interna:** Plataforma de Gestión del Conocimiento (acceso en `conocimiento.empresa.com`).
- **Formación en tecnologías:** Licencias de Udemy Business disponibles para todos los empleados (solicitar en IT).
- **Libros técnicos:** Biblioteca digital con acceso a O'Reilly Learning (solicitar acceso en IT).
- **1:1 con Tech Lead:** Reuniones quincenales para feedback técnico y plan de desarrollo. Se inician desde la segunda semana.
- **Buddy program:** Se te asignará un compañero de equipo como buddy durante los primeros 3 meses para resolver dudas del día a día.

---

## 8. Checklist de Incorporación — Primeros 30 días

### Semana 1
- [ ] Configurar entorno de desarrollo con el script de setup.
- [ ] Solicitar todos los accesos necesarios.
- [ ] Revisar y comprender la arquitectura del sistema (documento en Confluence).
- [ ] Participar en daily y ceremonias del sprint en curso (como observador).
- [ ] Primer 1:1 de bienvenida con el Tech Lead.
- [ ] Leer la Guía de Desarrollo de Software del equipo.
- [ ] Configurar MFA en todos los sistemas.

### Semana 2
- [ ] Primera tarea asignada (bug pequeño o task de documentación).
- [ ] Primer código commiteado y revisado.
- [ ] Revisión del primer PR de un compañero.
- [ ] Reunión 1:1 con el Product Manager para entender el roadmap del producto.
- [ ] Asistir a la Sprint Review y Retrospectiva.

### Semanas 3 y 4
- [ ] Feature completa entregada de forma autónoma.
- [ ] ADR redactado si tomaste una decisión técnica relevante.
- [ ] Feedback de 360 introductorio con el Tech Lead.
- [ ] Identificar áreas de mejora del proceso y proponerlas en la Retrospectiva.

---

## Contactos clave

| Rol | Nombre | Slack | Email |
|-----|--------|-------|-------|
| VP de Ingeniería | — | Perfil en directorio interno | — |
| Responsable de RRHH | — | #people-hr | `personas@empresa.com` |
| IT Helpdesk | — | #it-soporte | `it@empresa.com` |
| Seguridad | — | #seguridad | `seguridad@empresa.com` |
| Tu Tech Lead | Asignado por email previo | Directorio Slack | — |

> Los nombres concretos están en el directorio corporativo accesible desde la intranet con tu cuenta corporativa.
