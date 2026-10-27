# Capacidades del host y continuidad

Lee esta referencia al iniciar una operación que dependa de navegador, archivos, generación, correo o tareas, y cuando cambie el entorno. Descubre las herramientas enumeradas en la sesión; la instalación de la skill no añade estas capacidades.

## Elegir herramientas disponibles

| Host | Cómo resolver la capacidad |
| --- | --- |
| Codex | Usa conectores, navegador/control de ordenador y herramientas de archivos o terminal realmente disponibles. Sigue sus instrucciones de descubrimiento y autorización. Un nombre de herramienta de otra sesión no acredita que esté instalada. |
| Claude Code | Usa su integración de navegador/Chrome, MCP y herramientas locales sólo si están habilitadas en esa sesión. Selecciona por capacidad y documentación presente; no invoques nombres de herramientas de Codex como si fueran de Claude. |
| ChatGPT dot u otro entorno conectado | Opera con las herramientas, archivos y sesiones propias de ese entorno, o mediante un ordenador conectado explícitamente disponible. Una sesión en la nube no tiene acceso implícito a las carpetas o al navegador local del usuario. |

Para cada operación comprueba el acceso concreto necesario:

- **Investigación:** búsqueda o lectura de fuentes actuales, con fecha y URL.
- **Archivos y CLI:** lectura/escritura en la carpeta de la marca y ejecución de Python local. Si el host no puede ejecutar scripts o acceder a esos archivos, conserva un paquete transferible e indica qué paso local falta, sin simular persistencia.
- **Visuales:** generador incluido y permisos de uso, o Python con Pillow y un encoder disponible para composiciones locales. No infieras una capacidad de video a partir de una suscripción o del acceso a imágenes.
- **Publicación:** navegador autenticado, cuenta correcta, editor funcional y acción permitida para la red y formato. Se evalúa en LinkedIn, Instagram, Facebook y X conforme a [publishing](publishing.md).
- **Correo/tareas:** herramienta conectada, destinatario/alcance elegidos y autorización del usuario para esa marca.

Cuando haya un conector suficiente y admitido para una parte del trabajo, úsalo según las preferencias del host; el navegador sigue siendo una vía de publicación dentro del alcance. Si una capacidad falta, continúa el trabajo independiente y conserva archivos, estado y una explicación precisa de la intervención necesaria. El paquete manual es una alternativa ante ese impedimento real.

## Tres relojes distintos

| Mecanismo | Qué demuestra |
| --- | --- |
| Calendario editorial local | Qué se propone preparar o publicar y cuándo |
| Tarea o recordatorio del host | Que hay un mecanismo configurado para despertar al agente o avisar |
| Programación aceptada por la red | Que el servicio recibió la pieza y devolvió evidencia para ese destino y fecha |

Sólo la tercera situación permite registrar `scheduled`. Una tarea que ejecuta `due` o abre un chat no confirma publicación. El trabajo con carpetas y navegador locales requiere equipo encendido, sesión/aplicación disponible, conexión y permisos. La programación remota aceptada puede funcionar con la computadora apagada según el servicio; compruébalo para la vía utilizada.

## Configurar autonomía por marca

Si el usuario desea tareas reales, presenta una configuración concreta: marca, zona horaria, frecuencia/horarios, alcance y eventos de aviso. Usa el sistema nativo del host que exista en esa sesión; consulta su contrato actual en lugar de suponer una API compartida entre Codex, Claude y dots. La instalación no crea tareas ni cambia permisos o ajustes globales.

Una tarea autorizada puede revisar el calendario, preparar la próxima tanda, detectar aprobaciones pendientes, ejecutar piezas con versión aprobada dentro de su ventana y verificar resultados remotos. Guarda la raíz de datos y la marca correctas en su contexto. Antes de enviar sigue `check`/`begin` y los controles vigentes de [publishing](publishing.md). Si la tarea no dispone de navegador, archivos o autorización final requerida, conserva el trabajo pendiente y avisa.

Por defecto guarda silencio cuando no hay cambios accionables. Avisa en el host ante una aprobación pendiente, bloqueo, resultado listo, cambio relevante o fallo que requiera intervención. Para correo, exige elección de ese canal, destinatario confirmado y autorización explícita de crear/enviar el mensaje; utiliza una cuenta ya conectada. Si no hay herramienta, conserva el aviso local y explica la falta. Una autorización de tareas para una marca no configura otra marca.

Al informar capacidades distingue documentación, disponibilidad observada y prueba realizada. Un ejemplo local de PNG/MP4 no comprueba una publicación; instrucciones portables para Claude no equivalen a una sesión real de Claude.
