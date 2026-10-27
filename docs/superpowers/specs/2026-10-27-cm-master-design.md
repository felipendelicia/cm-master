# CM Master: diseño de la primera versión

Fecha: 27 de octubre de 2026. Estado: propuesta para revisión; la skill todavía no está implementada.

## Propósito

Crear una skill reutilizable de Community Manager para Codex y Claude Code. Debe administrar varias marcas, entender cada negocio, generar contenido final coherente, organizar su calendario, publicar las piezas aprobadas por el usuario cuando exista una vía disponible y analizar resultados y competidores para mejorar la visibilidad.

La inspiración en Google Pomelli es su perfil de marca persistente y corregible, construido desde la web, conversación y materiales propios, y su creación de campañas coherentes. CM Master agrega gestión de varias marcas, calendario, aprobación editorial, seguimiento y análisis. No requiere ni integra Pomelli.

## Decisiones expresas del usuario

- Compatibilidad con Codex y Claude Code.
- Gestión de varias marcas, con LinkedIn, Instagram, Facebook y X como destinos iniciales.
- Publicación por la IA, con aprobación humana del contenido antes de cada publicación. El usuario entiende por complemento de navegador el control de un navegador autenticado.
- Archivos finales de imagen y video; buscar logos y fotos en la web de la marca o solicitarlos cuando hagan falta.
- Usar inicialmente las capacidades de las suscripciones, sin contratar APIs ni servicios adicionales.
- Guardar manual, material e historial en carpetas locales.
- Argentina como mercado inicial, configurable en la entrevista de cada marca.
- Analizar resultados y competidores para mejorar visibilidad.
- Repositorio público `felipendelicia/cm-master`.
- El usuario delegó la propuesta de calendario y preguntó por recordatorios por mail y ejecución autónoma.
- El usuario aclaró que ya publica en X y LinkedIn mediante GPT dots. La publicación mediante control de navegador forma parte del alcance solicitado también para esas redes; esta experiencia fue informada por el usuario, no comprobada en cuentas reales durante el diseño.

## Propuestas que requieren revisar el alcance

### Publicación mediante el navegador del host

La primera versión incluye publicación en LinkedIn, Instagram, Facebook y X mediante las herramientas disponibles en el host, incluido el control de un navegador autenticado. No requiere desarrollar un bot independiente ni contratar una API social para intentar ese flujo. Comprobar la capacidad real de abrir el editor, cargar los archivos finales, completar el texto y ejecutar la acción aprobada en cada cuenta.

Las condiciones de LinkedIn y X restringen ciertas formas de automatización. Esas condiciones no son una prueba de imposibilidad técnica ni una razón para eliminar por defecto redes expresamente solicitadas. A su vez, poder controlar el navegador no demuestra autorización de la plataforma: conservar esta distinción y atender los requisitos concretos del servicio, la cuenta y las herramientas disponibles. No asumir que una publicación supervisada tiene una excepción contractual ni que todas las operaciones estarán disponibles.

Antes del envío o de confirmar una programación, verificar la aprobación humana del texto y medios finales, la cuenta y el destino. Respetar los controles de autorización del host y comprobar el resultado en la red. Evaluar también Meta Business Suite y la programación nativa cuando estén disponibles. Si aparece un impedimento concreto de acceso, cuenta, herramienta o servicio, conservar el paquete y explicar la intervención necesaria; ofrecer publicación manual cuando no pueda completarse la operación por la vía disponible. No convertirla en el modo obligatorio de LinkedIn o X ni incorporar APIs pagas como requisito oculto.

La documentación de OpenAI describe el navegador y las sesiones de dots, y la extensión de ChatGPT menciona expresamente operaciones en sitios con sesión iniciada como LinkedIn. Esto respalda incluir el flujo en el diseño; no equivale a haber probado una publicación en las cuentas del usuario ni a garantizar idénticas capacidades en Claude Code.

### Videos e imágenes con la suscripción

La skill no aporta por sí sola un motor de generación audiovisual. Detectará herramientas realmente disponibles en el host y plan actuales.

- Imágenes: preferir generación o edición de imagen disponible en la suscripción. Alternativa: composición original con fotos y activos autorizados de la marca, tipografía y diseños renderizados localmente a PNG/JPEG.
- Videos: usar un generador conectado incluido si existe. Alternativa propuesta: MP4 con composición animada de fotos, textos y transiciones, mediante herramientas locales como FFmpeg. Describirlo como montaje animado; no como video de escenas generado por IA.
- Entregar archivos visualmente comprobados. Un prompt, un guion o una promesa no cuentan como archivo final. Si falta el motor o la dependencia necesaria, informar la carencia y pedir la decisión mínima para resolverla, conservando el resto del trabajo.
- No contratar herramientas, introducir costos por consumo ni automatizar interfaces de generación ajenas a los permisos disponibles.

## Experiencia de uso

### 1. Selección y entrevista de marca

Listar marcas existentes o crear una nueva. Cada marca tiene un identificador y carpeta independientes; elegir explícitamente la marca antes de operar en una cuenta.

En el primer uso pedir la web. Si falta, admitir entrevista y documentos. Revisar páginas útiles del negocio y los activos vinculados desde ellas. Extraer el rubro, propuesta de valor, productos y servicios, público, ubicación, contactos, slogans, tono, colores, tipografías y estilo fotográfico. Registrar fuentes y fecha; distinguir datos observados, aportados por el usuario e hipótesis.

Completar con objetivos, mercado e idioma, zona horaria, presupuesto disponible, palabras clave y prohibidas, temas sensibles, ejemplos aprobados y activos. El valor inicial sugerido es español rioplatense y `America/Argentina/Buenos_Aires`, corregible por marca. No inferir una dirección, teléfono, precio o promoción que no conste en una fuente válida.

Presentar el manual para correcciones. Conservar una versión legible y datos estructurados consistentes. Cambiar el manual por conversación y mantener historial de decisiones; solicitar confirmación de afirmaciones inciertas antes de usarlas en publicidad.

### 2. Redes, objetivos y competencia

Pedir los enlaces y el destino exacto en cada red: perfil, página o cuenta. Verificar qué acceso, herramientas y sesiones están disponibles, sin guardar contraseñas o cookies en los archivos de marca.

Auditar los contenidos accesibles, consistencia y llamados a la acción mediante herramientas admitidas o datos aportados/exportados por el usuario. Proponer entre tres y cinco competidores relevantes por rubro, mercado y objetivo. No dar por confirmado un competidor homónimo ni necesitar datos privados de otros negocios.

Investigar tendencias recientes con fecha, fuente y relación con el negocio. Obtener patrones, preguntas, formatos y oportunidades; producir conceptos originales en lugar de copiar piezas ajenas. La ausencia de métricas de un competidor debe aparecer como ausencia, no como una estimación inventada.

### 3. Plan y calendario propuestos

Decisión propuesta por el constructor, delegada por el usuario:

- Plan orientativo de cuatro semanas con objetivos y temas.
- Preparación y revisión semanal de la próxima tanda de siete días.
- Punto de partida: tres temas principales por semana, lunes, miércoles y viernes, adaptados a cada red activa. La marca puede reducir redes o frecuencia; no se exige publicar lo mismo en todos los destinos.
- Historias de Instagram y Facebook en tres días de la semana, con posibilidad de reutilizar material aprobado en formatos adecuados. No crear entradas de historias para redes que no las ofrecen.
- Horarios provisionales según zona horaria y disponibilidad del usuario, ajustados al obtener evidencia propia. No presentar un horario como óptimo sin datos.
- Preparar con al menos 48 horas de anticipación cuando sea posible; revisar novedades y afirmaciones sensibles a la fecha antes de publicar.

Cada entrada vincula objetivo, red, cuenta, formato, fecha/hora/zona, brief, texto, archivos finales, fuentes relevantes y estado. Evitar comprometer una cadencia sin capacidad de generar, revisar y publicar las piezas.

### 4. Producción y aprobación

Crear un paquete por destino: imagen o video final, texto/caption, hashtags pertinentes, llamada a la acción, texto alternativo cuando aplique y una vista previa que el usuario pueda revisar. Mantener el idioma, voz y manual de la marca. Verificar especificaciones actuales de la red en vez de tratar tamaños o límites como reglas eternas.

El usuario puede aprobar una pieza o una tanda enumerada cuyas versiones finales, destinos y horarios estén visibles. La aprobación debe identificar qué autorizó y de dónde surge su consentimiento. La aprobación del manual, del plan o de esta skill no autoriza automáticamente publicaciones futuras.

Conservar una huella del texto, medios, cuenta y programación aprobados. Si cambia alguno, devolver la pieza a revisión. Permitir cancelar o revocar una aprobación antes de ejecutar. Los helpers locales validan coherencia, pero no autentican una identidad ni sustituyen el consentimiento expresado en la conversación.

Estados conceptuales: borrador, pendiente de aprobación, aprobado, programado, publicado, cancelado, bloqueado y resultado incierto. Programado significa que la plataforma devolvió evidencia de programación, no que hay una fecha en un JSON.

### 5. Publicación y seguimiento

Antes de publicar o programar: comprobar marca, cuenta visible, destino, archivos, versión aprobada y horario. Validar también las capacidades del host y la vía elegida, incluido el navegador autenticado para cualquiera de las cuatro redes. La skill respeta los controles de autorización del host; un manual no los desactiva.

Después de ejecutar, recoger enlace, identificador o comprobación de que la pieza fue publicada o aceptada para programación. Registrar evidencia y fecha. Si se interrumpe la operación después de enviar, comprobar el destino antes de reintentar para evitar duplicados; conservar resultado incierto cuando no pueda verificarse. No generar pruebas de publicación ficticias.

Ante sesión vencida, CAPTCHA, 2FA, restricciones de cuenta o interfaz inaccesible, guardar el progreso y solicitar la intervención concreta necesaria. No cambiar de marca, cuenta o canal para resolver una falla sin autorización.

### 6. Autonomía y avisos

Propuesta inicial: revisión periódica local que prepara contenido, detecta piezas que requieren aprobación, ejecuta las ya aprobadas cuando corresponde y verifica publicaciones programadas. Usar el sistema nativo de tareas del host cuando exista, sin asumir que Claude y Codex comparten una API de programación.

Separar tres funciones: calendario editorial persistido, tarea del host que despierta a la IA y programación nativa de la red social. La última, si está disponible y verificada, puede publicar aun con la computadora del usuario apagada.

En la entrevista preguntar canal, destinatario, anticipación y horario de avisos. Por defecto avisar en el host únicamente cuando haya aprobación pendiente, bloqueo, resultado listo o fallo que requiera atención; no producir mensajes periódicos sin cambios.

Mail es una opción mediante una cuenta/herramienta ya conectada y destinatario confirmado. Crear o enviar un mail y dar de alta tareas reales requieren que el usuario elija esa configuración para su marca; este diseño no crea tareas ni envía correos. Si no hay herramienta de correo, conservar aviso local y explicar qué falta.

La primera versión no incorpora un servidor. El trabajo sobre carpetas y navegador locales necesita el equipo encendido, la aplicación/sesión correspondiente disponible, conexión y los permisos de cuenta necesarios. No prometer ejecución 24/7 ni tratar un recordatorio como garantía de publicación.

### 7. Medición y aprendizaje

Propuesta: reporte semanal, evaluación inicial a 30 días y ajustes graduales. Priorizar visibilidad y consultas medibles según los objetivos de cada marca. Guardar snapshots con fuente, fecha, ventana y definiciones de las métricas disponibles: alcance, impresiones, interacciones, clics, seguidores o consultas.

Comparar piezas de antigüedad y formato comparables. Calcular tasas sólo con denominadores identificados y explicar limitaciones. No mezclar alcance con impresiones ni tratar la falta de datos como cero. Usar exportaciones o carga manual cuando no exista acceso permitido a estadísticas.

El reporte muestra qué funcionó, qué no puede concluirse, ejemplos y un cambio concreto para probar. Evitar promesas de viralidad o crecimiento garantizado. Cambios de calendario y nuevas creatividades siguen sujetos a aprobación antes de publicarse.

## Estructura y compatibilidad

Una única fuente de la skill en `skills/cm-master/`, con `SKILL.md` portable y referencias breves por flujo. Adaptadores de instrucciones para las herramientas de Codex y Claude Code; no hardcodear una herramienta inexistente como si estuviera en ambos.

Helpers pequeños en Python para aislamiento de marcas, persistencia, calendario y validación de aprobaciones. Añadir helpers audiovisuales sólo donde aporten archivos finales verificables. Evitar un backend, panel web, base de datos remota o framework de agentes en esta versión.

Instalación documentada para cada host, con la ubicación de descubrimiento que corresponda a su versión. No cambiar configuraciones globales ni instalar la skill para todos los proyectos como efecto de crear el repositorio.

Datos operativos fuera del repositorio público: por defecto `~/.cm-master/brands/<id>/`, con raíz configurable. Dentro de cada marca: perfil/manual, fuentes, activos, calendario, paquetes, aprobaciones, publicaciones y reportes. Los archivos se pueden inspeccionar y respaldar. Evitar referencias cruzadas entre marcas o rutas de salida que escapen de su carpeta.

El repositorio contiene instrucciones, helpers, pruebas, documentación y ejemplos expresamente ficticios. Excluir datos reales, credenciales, sesiones del navegador, correo y contenido operativo. No extraer ni publicar datos de una marca real durante la construcción de la skill.

## Fuera de la primera versión

- Respuestas autónomas a mensajes privados o comentarios: no hubo una decisión específica del usuario sobre atención al cliente.
- Compra, administración o lanzamiento de anuncios pagos.
- APIs por consumo, suscripciones adicionales, integración de una API social nueva o servidor permanente.
- Generación de escenas de video por IA sin una herramienta disponible para ello.
- Dashboard web, colaboración multiusuario y sincronización con Drive/Notion.

Estas extensiones se pueden incorporar después de probar el flujo principal; no son requisitos ocultos para utilizar los modos locales.

## Validación requerida antes de presentar la skill como utilizable

- Validar metadata, rutas y referencias de la skill.
- Probar con agentes independientes solicitudes de onboarding, cambio de marca, aprobación de piezas y publicación con capacidad faltante; no usar cuentas reales ni efectos externos.
- Probar helpers con datos temporales: aislamiento, persistencia, zona horaria, revocación/cambios que invalidan aprobación, doble ejecución y resultado incierto.
- Comprobar un paquete final ficticio de imagen y, si se incluye un renderer, un MP4 reproducible, sin afirmar que es una prueba de publicación real.
- Documentar las funciones que se probaron localmente y las que requieren configuración y validación en una cuenta del usuario. La compatibilidad documental con Claude no equivale a haber ejecutado una sesión real de Claude.

## Fuentes consultadas el 27 de octubre de 2026

- [Pomelli: perfil de negocio](https://support.google.com/labs/answer/17090488?hl=en-GB).
- [Pomelli: identidad y Brand Books](https://blog.google/innovation-and-ai/models-and-research/google-labs/pomelli-agentic-capabilities/).
- [OpenAI: crear skills](https://learn.chatgpt.com/docs/build-skills).
- [OpenAI: tareas programadas](https://learn.chatgpt.com/docs/automations?surface=app).
- [OpenAI: dots, navegador, sesiones y aprobaciones](https://learn.chatgpt.com/docs/dots).
- [OpenAI: extensión de navegador y sitios con sesión iniciada](https://learn.chatgpt.com/docs/chrome-extension).
- [Claude Code: skills](https://code.claude.com/docs/en/skills).
- [Claude Code: navegador Chrome](https://code.claude.com/docs/en/chrome).
- [Claude Code: opciones de programación](https://code.claude.com/docs/en/scheduled-tasks).
- [LinkedIn: software y extensiones prohibidos](https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions).
- [X: reglas de automatización](https://help.x.com/en/rules-and-policies/x-automation).

## Pendiente de decisión del usuario

Revisar la propuesta y la alternativa de videos MP4 animados cuando no haya generador incluido. La publicación mediante navegador, incluida LinkedIn y X, permanece dentro del alcance solicitado y está sujeta a las herramientas disponibles, la aprobación de cada pieza y la verificación del resultado. Tras revisar el diseño se elaborará el plan de implementación y se construirá la skill.
