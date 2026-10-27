# Marca, manual y configuración

Lee esta referencia al incorporar una marca o cambiar su identidad, cuentas, avisos o modo de trabajo. Los comandos disponibles están en [local-tools](local-tools.md).

## Entrevista y evidencia

Lista las marcas y elige el identificador antes de leer activos u operar cuentas. Al crear una marca pide primero su web; si no tiene, trabaja con entrevista y documentos. Revisa páginas útiles del sitio, como inicio, productos/servicios, nosotros y contacto, y los activos vinculados. Recoge logos y fotos autorizados, o solicita los que falten. Guarda su procedencia y condiciones de uso conocidas; una imagen encontrada en buscadores no acredita permiso de reutilización.

Completa por conversación sólo los campos que falten o necesiten una decisión:

| Área | Información para el manual |
| --- | --- |
| Negocio | Nombre comercial, rubro, propuesta de valor, oferta, diferenciadores, ubicación y contactos confirmados |
| Público | Clientes prioritarios, necesidades, mercado, idioma y alcance geográfico |
| Objetivos | Visibilidad, consultas u otro resultado observable; prioridad y forma de medirlo |
| Voz | Tono, vocabulario, palabras prohibidas, temas sensibles, afirmaciones que requieren validación y ejemplos aprobados |
| Visual | Logos, variantes, colores, tipografías, estilo fotográfico, activos disponibles y derechos conocidos |
| Operación | Redes activas, URL exacta de cada perfil/página/cuenta, zona horaria, capacidad de producción/revisión y presupuesto disponible |
| Avisos | Canal elegido, destinatario, anticipación, horario y eventos que merecen aviso |
| Autonomía | Qué puede preparar, qué piezas están aprobadas y si el usuario desea configurar tareas reales para esa marca |

Propón Argentina, español rioplatense y `America/Argentina/Buenos_Aires` como valores iniciales corregibles. No completes precios, promociones, direcciones o teléfonos por intuición.

Para cada afirmación útil registra valor, origen, fecha de consulta y una categoría: **observado en fuente**, **aportado/confirmado por el usuario** o **hipótesis pendiente**. Distingue fecha de publicación del material, fecha del hecho y fecha de consulta cuando difieran. Si hay conflicto entre fuentes, conserva ambas y resuelve la afirmación antes de usarla en publicidad. No hace falta interrumpir el resto del onboarding por una hipótesis que todavía no se utilizará.

## Manual persistente y corregible

Presenta un manual legible que reúna las áreas de la tabla, fuentes y dudas pendientes. Incluye criterios concretos para evaluar piezas: promesa principal, voz, recursos visuales, llamados a la acción y límites de afirmaciones. La aprobación del manual define identidad; cada publicación mantiene su revisión propia.

Conserva el perfil estructurado mediante `profile ID --file JSON`: la CLI combina diccionarios, reemplaza listas, incrementa la revisión, guarda `history/profile-<revision>.json` y regenera `manual.md`. Incluye allí el contenido completo del manual, las fuentes y las dudas, para que la versión legible generada sea útil. Actualiza el perfil en lugar de editar únicamente el manual que luego se regenerará.

Estas rutas reúnen los archivos generados y las convenciones documentales que mantiene la skill; no implican comandos adicionales de la CLI:

| Ruta dentro de `brands/<id>/` | Contenido |
| --- | --- |
| `profile.json` y `manual.md` | Perfil y versión legible vigentes, generados por la CLI |
| `history/profile-<revision>.json` | Historial estructurado generado por la CLI; permite recuperar el manual de cada revisión |
| `history/manual-<fecha-version>.md` | Copia legible adicional cuando sea útil para comparar revisiones |
| `history/decisions.md` | Fecha, cambio, motivo y referencia al consentimiento o fuente |
| `sources/` | Evidencia y notas de procedencia |
| `assets/` | Activos de la propia marca |
| `calendar/` | Plan de cuatro semanas y tanda de siete días |
| `reports/` | Snapshots, reportes y experimentos |

Registra qué cambió, por qué y qué piezas pendientes quedan afectadas. Una decisión conversada puede corregir la identidad sin repetir toda la entrevista. Evita copiar datos o activos entre carpetas de marcas; si un recurso es compartido, verifica su uso para ambas y guarda una copia autorizada dentro de la marca que lo necesita.

## Cuentas, correo y tareas

Guarda las URL de las cuentas y el estado de acceso, sin contraseñas, cookies ni tokens de sesión. El navegador y sus sesiones pertenecen al host. Revalida la cuenta visible al publicar.

Ofrece aviso en el host cuando haya aprobación pendiente, bloqueo, resultado listo o un fallo que requiera atención. Correo y tareas persistentes son opciones por marca: recoge la elección del usuario, destinatario confirmado, anticipación y horario antes de configurarlos. Usa una cuenta/herramienta de correo ya conectada y autorización explícita para crear o enviar mensajes. La instalación de la skill no configura avisos ni crea tareas. Consulta [hosts](hosts.md) para capacidades y condiciones de ejecución.
