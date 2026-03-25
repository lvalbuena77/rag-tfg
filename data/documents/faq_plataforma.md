# FAQ Plataforma — Gestión del Conocimiento Corporativo

Documento de preguntas frecuentes (versión 3.1 — Marzo 2026).  
Destinado a todos los empleados y colaboradores que utilicen la plataforma interna de gestión del conocimiento.

---

## 1. Acceso y autenticación

### ¿Cómo accedo al sistema por primera vez?
Para acceder por primera vez debes recibir un correo de bienvenida con un enlace de activación. Haz clic en el enlace, establece tu contraseña (mínimo 12 caracteres, al menos una mayúscula, un número y un símbolo especial) y acepta la política de uso. Tras esto podrás iniciar sesión con tu correo corporativo y la nueva contraseña.

### ¿Cómo inicio sesión?
Accede a la URL interna de la plataforma (disponible en la intranet corporativa). Introduce tu correo electrónico corporativo y tu contraseña en el formulario de inicio de sesión. Si la empresa tiene SSO (Single Sign-On) habilitado, serás redirigido automáticamente al proveedor de identidad corporativo (Azure AD o Okta según el entorno).

### ¿Qué hago si olvido mi contraseña?
En la pantalla de inicio de sesión, haz clic en "¿Olvidaste tu contraseña?". Introduce tu correo electrónico corporativo y recibirás un enlace de recuperación válido durante 30 minutos. Si no recibes el correo en 5 minutos, revisa la carpeta de spam. Si el problema persiste, contacta con el equipo de IT a través del portal de soporte.

### ¿Puedo acceder desde fuera de la red corporativa?
Sí, la plataforma es accesible desde Internet siempre que dispongas de las credenciales correctas. Para acceso desde redes externas se requiere autenticación multifactor (MFA). Es recomendable conectarse previamente a la VPN corporativa para acceso a recursos adicionales integrados con la plataforma.

### ¿Qué es la autenticación multifactor (MFA) y cómo la configuro?
La MFA añade una capa adicional de seguridad. Tras introducir tu contraseña, el sistema solicitará un segundo factor. Opciones disponibles: aplicación de autenticación (Google Authenticator, Microsoft Authenticator), código SMS al número corporativo registrado, o llave de seguridad física (FIDO2). Para configurarla, ve a Perfil → Seguridad → Autenticación multifactor.

### ¿Durante cuánto tiempo permanece activa mi sesión?
Las sesiones tienen una duración máxima de 8 horas de inactividad. Las sesiones activas se renuevan automáticamente mientras navegas. Puedes cerrar sesión manualmente desde el menú de perfil (esquina superior derecha). Por seguridad, se recomienda cerrar sesión al finalizar la jornada laboral.

### ¿Qué hago si mi cuenta ha sido bloqueada?
Las cuentas se bloquean automáticamente tras 5 intentos fallidos de inicio de sesión consecutivos. Para desbloquearla contacta con el administrador del sistema o el equipo de IT, quien podrá restablecer el acceso y verificar si existió algún intento de acceso no autorizado.

---

## 2. Funcionalidades principales

### ¿Qué puedo hacer en la plataforma?
La plataforma permite: (1) consultar documentos internos de la empresa mediante búsqueda semántica en lenguaje natural, (2) hacer preguntas al asistente de IA que responde basándose en la documentación indexada, (3) subir y gestionar documentos internos si tienes permisos de editor, (4) ver el historial de consultas realizadas, (5) marcar documentos como favoritos, y (6) exportar respuestas y fragmentos relevantes.

### ¿Cómo realizo una búsqueda?
Escribe tu pregunta o consulta en el campo de búsqueda principal. El sistema analiza semánticamente el texto y recupera los fragmentos de documentación más relevantes. No es necesario usar palabras clave exactas; puedes escribir en lenguaje natural como si hablaras con una persona. Ejemplo: "¿Cómo se configura el timeout en el cliente HTTP?" obtendrá mejores resultados que "timeout config HTTP".

### ¿Cómo funciona el asistente de IA?
El asistente utiliza un modelo de lenguaje ejecutado en local (sin enviar datos a servicios externos). Cuando realizas una pregunta, el sistema primero recupera los fragmentos de documentación más relevantes de la base de datos vectorial y luego el modelo genera una respuesta contextualizada basada exclusivamente en esa información. Cada respuesta incluye las fuentes documentales en las que se ha basado.

### ¿Qué tipos de archivos puedo subir a la plataforma?
La plataforma admite: PDF (hasta 50 MB), DOCX / DOC (hasta 25 MB), Markdown (.md, hasta 10 MB), texto plano (.txt, hasta 10 MB). Los archivos subidos son procesados automáticamente: se extraen, fragmentan, generan embeddings y se indexan. Este proceso puede tardar entre 30 segundos y 5 minutos dependiendo del tamaño.

### ¿Puedo buscar en documentos específicos?
Sí. En el panel lateral puedes filtrar la búsqueda por: colección o carpeta, tipo de documento, fecha de publicación, autor o departamento. También puedes anclar colecciones favoritas para acceso rápido.

### ¿Cómo puedo ver el historial de mis consultas?
Ve a tu perfil (ícono superior derecho) → Historial de consultas. Verás las últimas 500 consultas con fecha, hora y la respuesta generada. Puedes buscar dentro del historial, exportarlo en CSV o eliminar entradas específicas.

### ¿Qué es una "colección"?
Una colección es un agrupamiento lógico de documentos, similar a una carpeta inteligente. Los administradores pueden crear colecciones por proyecto, departamento o temática. Los usuarios con los permisos adecuados pueden añadir y quitar documentos de colecciones existentes.

---

## 3. Gestión de documentos

### ¿Cómo subo un documento nuevo?
Dispones de dos opciones: (1) Arrastrar y soltar el archivo en la zona de carga de la pantalla principal, o (2) hacer clic en el botón "Subir documento" (ícono de nube con flecha). Selecciona el archivo, elige la colección destino, añade etiquetas opcionales y confirma. Recibirás una notificación cuando el documento esté indexado y disponible para búsquedas.

### ¿Puedo actualizar un documento existente?
Sí, accede al documento desde la vista de colección, haz clic en el menú de tres puntos (⋮) y selecciona "Nueva versión". Sube el archivo actualizado. El sistema mantendrá las versiones anteriores en el historial del documento y actualizará el índice con el contenido nuevo.

### ¿Cómo elimino un documento?
Navega hasta el documento, abre el menú (⋮) y selecciona "Eliminar". Se requiere confirmación explícita. La eliminación es lógica durante 30 días (recuperable desde la papelera), tras lo cual se elimina permanentemente junto con sus embeddings asociados. Solo pueden eliminar documentos los editores propietarios y los administradores.

### ¿Qué ocurre si subo un documento duplicado?
El sistema detecta duplicados mediante un hash del contenido. Si el archivo es idéntico a uno existente, se te notificará y podrás decidir si crear una nueva versión, reemplazar el existente o cancelar la operación.

### ¿Puedo establecer permisos de acceso para un documento?
Sí. En las propiedades del documento puedes definir: visibilidad (toda la empresa, departamentos específicos, usuarios específicos), permiso de descarga, y permiso de comentarios. Los documentos clasificados como confidenciales solo son visibles para los grupos autorizados.

### ¿Se pueden añadir metadatos a los documentos?
Sí. Durante la subida o posteriormente en las propiedades del documento puedes añadir: título, descripción, etiquetas, autor, departamento, proyecto asociado, fecha de vigencia y nivel de confidencialidad. Los metadatos mejoran la relevancia de las búsquedas y permiten filtrar resultados.

---

## 4. Integraciones y API

### ¿La plataforma se integra con otras herramientas?
Sí. Integraciones disponibles: Confluence (sincronización bidireccional de páginas), Jira (vinculación de documentos a tickets), Slack (bot para consultas desde canales), Microsoft Teams (pestaña embebida), SharePoint (importación de documentos), GitHub/GitLab (indexación de READMEs y wikis de repositorios).

### ¿Existe una API para acceder programáticamente?
Sí. La plataforma expone una API REST documentada en `/api/v1/docs` (Swagger UI). Requiere autenticación mediante API Key o token JWT. Endpoints principales: `POST /api/v1/query` para consultas, `POST /api/v1/documents` para subida, `GET /api/v1/documents/{id}` para recuperación. También hay una API de webhooks para recibir notificaciones de eventos.

### ¿Cómo obtengo una API Key?
Ve a Perfil → Desarrollador → API Keys → "Generar nueva clave". Asigna un nombre descriptivo e indica los permisos necesarios (lectura, escritura, administración). La clave solo se muestra una vez al generarla, guárdala en un lugar seguro. Puedes revocarla en cualquier momento desde el mismo panel.

### ¿Qué límites tiene la API?
Plan estándar: 1.000 peticiones/hora, 10.000 peticiones/día. Plan premium: 10.000 peticiones/hora. Los límites se pueden ampliar contactando con el equipo de plataforma. Las respuestas incluyen cabeceras `X-RateLimit-Remaining` y `X-RateLimit-Reset` para monitorizar el consumo.

---

## 5. Seguridad y privacidad

### ¿Mis consultas y documentos están seguros?
Todos los datos se procesan en infraestructura interna de la empresa. Ningún documento ni consulta es enviado a servicios externos o de terceros (incluidos proveedores de IA cloud). El tráfico entre cliente y servidor está cifrado con TLS 1.3. Los datos en reposo están cifrados con AES-256.

### ¿Quién puede ver mis consultas?
Las consultas son privadas por defecto. Solo tú puedes ver tu historial. Los administradores de la plataforma tienen acceso en modo anonimizado a estadísticas de uso agregadas para mejora del servicio. El acceso a consultas individuales identificadas requiere autorización explícita del Delegado de Protección de Datos (DPD), únicamente en casos de investigación de incidentes de seguridad.

### ¿Cómo se cumple con GDPR?
La plataforma cumple con el Reglamento General de Protección de Datos (GDPR). Los datos personales almacenados se limitan a lo estrictamente necesario. Tienes derecho de acceso, rectificación, supresión, portabilidad y oposición. Para ejercer estos derechos contacta con el DPD mediante el formulario disponible en la intranet.

### ¿Qué ocurre con los documentos cuando un empleado abandona la empresa?
Al desactivar una cuenta de usuario, sus documentos privados pasan a un estado de custodia administrado por el responsable del departamento durante 90 días, tras los cuales se eliminan según la política de retención de datos. Los documentos compartidos con la organización permanecen accesibles.

---

## 6. Rendimiento y disponibilidad

### ¿Cuál es el SLA de disponibilidad?
La plataforma tiene un SLA del 99,5% de disponibilidad mensual, excluyendo ventanas de mantenimiento planificado. Las ventanas de mantenimiento se comunican con al menos 48 horas de antelación y se realizan en horario de baja actividad (domingos entre 02:00 y 06:00 UTC).

### ¿Por qué tarda en responder el asistente de IA?
El tiempo de respuesta depende de la longitud y complejidad de la consulta y el modelo de LLM utilizado. Tiempos orientativos: consultas simples 2-5 segundos, consultas complejas con mucho contexto 8-20 segundos. Si el tiempo de respuesta supera los 30 segundos consistentemente, reporta el problema al equipo de soporte.

### ¿Puedo usar la plataforma en dispositivos móviles?
La interfaz web es responsive y se adapta a dispositivos móviles. Hay una aplicación nativa disponible para iOS (App Store corporativo) y Android (Play Store o APK de distribución interna). Las apps permiten consultas por voz y notificaciones push.

---

## 7. Soporte técnico

### ¿Cómo contacto con soporte?
Canales disponibles: (1) Portal de soporte interno en `soporte.empresa.com`, crea un ticket con categoría "Plataforma Conocimiento"; (2) Chat en la propia plataforma (botón flotante "Soporte" en la esquina inferior derecha); (3) Correo electrónico: `soporte-plataforma@empresa.com`; (4) Canal de Slack #soporte-plataforma para incidencias urgentes.

### ¿Cuál es el tiempo de respuesta del soporte?
Prioridad crítica (plataforma caída o datos inaccesibles): respuesta en 1 hora, resolución en 4 horas. Prioridad alta (funcionalidad principal afectada): respuesta en 4 horas, resolución en 24 horas. Prioridad media (problema puntual sin bloqueo): respuesta en 1 día laborable. Prioridad baja (consulta o mejora): respuesta en 3 días laborables.

### ¿Dónde encuentro la documentación técnica de la plataforma?
La documentación técnica completa está disponible en el portal de documentación interno (`docs.empresa.com/plataforma`). Incluye: guías de usuario, guías de administración, referencia de la API, guías de integración y notas de versión (changelog).

### ¿Cómo reporto un fallo de seguridad?
Los fallos de seguridad deben reportarse siguiendo el proceso de divulgación responsable: envía un correo a `seguridad@empresa.com` con el asunto "SECURITY REPORT". Incluye descripción del problema, pasos para reproducirlo y su impacto potencial. No reportes vulnerabilidades de seguridad a través de los canales normales de soporte. El equipo de seguridad responderá en un máximo de 24 horas.

---

## 8. Preguntas sobre el modelo de IA

### ¿Qué modelo de lenguaje usa el asistente?
El asistente utiliza modelos open-source ejecutados localmente mediante Ollama. Los modelos disponibles actualmente son Llama 3 (8B y 70B) y Mistral 7B. El administrador de la plataforma puede configurar qué modelo está activo. Los modelos no envían datos a servidores externos.

### ¿El asistente puede equivocarse?
Sí. El asistente puede cometer errores, especialmente si la documentación disponible es incompleta, ambigua o contradictoria. Siempre verifica las respuestas importantes consultando directamente la fuente citada. Las respuestas incluyen siempre las fuentes documentales para facilitar la verificación.

### ¿Por qué el asistente dice que no tiene información sobre un tema?
Si el asistente responde que no tiene información suficiente, significa que no existen documentos indexados que cubran ese tema. Soluciones: (1) sube los documentos relevantes a la plataforma, (2) consulta directamente las fuentes originales, o (3) contacta con el experto del área correspondiente.

### ¿Pueden los usuarios valorar las respuestas del asistente?
Sí. Debajo de cada respuesta del asistente hay botones de valoración (pulgar arriba/abajo) y un campo opcional de comentario. Este feedback se usa para mejorar la relevancia del sistema de recuperación y detectar respuestas incorrectas o incompletas.
