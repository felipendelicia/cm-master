# Investigación, calendario y archivos finales

Lee esta referencia para producir contenido o proponer un plan. Usa el manual vigente; si falta contexto esencial, completa [onboarding](onboarding.md). Para medición y competencia recurrente, consulta [analytics](analytics.md).

## Investigar sin perder la voz de la marca

Busca tendencias actuales del rubro y mercado de la marca. Parte de Argentina sólo mientras el perfil no indique otro mercado. Recoge una muestra útil de conversaciones públicas, noticias, búsquedas, formatos y preguntas del público; el número de resultados no determina su relevancia.

Cada oportunidad propuesta incluye tema, fuente/URL, fecha de publicación o del hecho, fecha de consulta, mercado y relación con un objetivo de la marca. Comprueba actualidad y contexto antes de reutilizarla. Prioriza fuentes originales para hechos, cifras y anuncios; usa la observación pública de redes para describir patrones. Si no hay acceso a fuentes actuales, conserva ideas atemporales y señala qué tendencia queda pendiente de verificar.

Separa hechos comprobados, patrones observados e hipótesis creativas. Deriva conceptos originales con ejemplos y activos de la marca. Registra la fuente de inspiración sin copiar textos, diseños o piezas de competidores. Para afirmaciones comerciales sensibles a la fecha, como precio, stock o promoción, usa una fuente válida y confirma la versión antes de publicar.

## Plan de cuatro semanas y tanda de siete días

Propón cuatro semanas con objetivo, temas principales, audiencia, formato, red, llamado a la acción y criterio de éxito. Desarrolla para revisión la próxima tanda de siete días.

Punto de partida ajustable: tres temas semanales, lunes, miércoles y viernes, adaptados a las redes activas; historias de Instagram/Facebook en tres días de la semana cuando aporten valor. No hace falta replicar un tema en todos los destinos. Reduce o redistribuye la frecuencia según activos, revisión, equipo y capacidad real. Los horarios iniciales son provisionales en la zona de la marca, hasta obtener evidencia propia. Prepara con 48 horas de anticipación cuando sea posible.

El calendario conserva una fila por destino con:

| Campo | Uso |
| --- | --- |
| ID de pieza y versión | Vincular la fila con `posts/<post>/post.json` y sus archivos |
| Objetivo, tema, brief y CTA | Explicar qué intenta lograr |
| Red, URL de cuenta y formato | Identificar el lugar exacto de publicación |
| Plazo de preparación, cuando exista | Guardar `delivery_due_at` separado del horario de salida |
| Fecha/hora con offset y zona IANA | Evitar ambigüedad de ejecución |
| Texto, medios y fuentes | Localizar el paquete revisable |
| Estado y próxima acción | Distinguir preparación, aprobación y resultado externo |

«Dejalo listo mañana a las 11» puede indicar el plazo para entregar archivos o presentarlos a revisión; consérvalo como `delivery_due_at`, sin convertirlo en `scheduled_at` ni en permiso de publicación. Si todavía faltan cuenta, horario o archivos, guarda los campos conocidos mediante `draft` y continúa la preparación. Una fecha de publicación propuesta en el calendario sigue siendo una intención local. El estado programado exige evidencia del servicio como indica [publishing](publishing.md).

## Producir el paquete por destino

Comprueba las especificaciones actuales de la red o del editor disponible: formatos admitidos, dimensiones, duración, peso, recortes, límites de texto y texto alternativo. El formato `story` corresponde a Instagram/Facebook; el contrato de la CLI no sustituye esta comprobación de capacidad de cada destino.

Entrega texto/caption final, hashtags pertinentes, CTA, alt text cuando aplique, archivos finales y una vista previa. Adapta intención y voz al contexto de cada red. Guarda las fuentes usadas para los hechos y el brief con el paquete.

Elige la producción visual según herramientas verificadas del [host](hosts.md):

- **Imagen:** usa el generador/editor incluido en la suscripción cuando esté disponible. Como alternativa, crea una composición original con fotos y activos autorizados, textos y tipografía mediante el renderer local de [local-tools](local-tools.md).
- **Video:** usa un generador conectado incluido si existe y permite esta operación. La alternativa inicial aceptada es un MP4 con fotos, textos y animaciones locales. Preséntalo como montaje animado. El renderer genera un archivo real; un guion o prompt sirve para producirlo, pero no completa el entregable visual.

Abre la imagen para revisar legibilidad, acentos, contraste, logo, recortes y encuadre. En video comprueba reproducción, duración, dimensiones y fotogramas representativos, además de cualquier audio incorporado. Si una dependencia impide producir un archivo, guarda el trabajo terminado y explica qué falta. No agregues servicios pagos para resolverlo sin una decisión del usuario.

Conserva el avance mediante `draft` mientras falten datos o archivos finales. Cuando el paquete tenga cuenta exacta, medios y horario de publicación, ejecuta `stage` y `review` conforme a [local-tools](local-tools.md), muestra el resultado concreto y sigue el proceso de aprobación de [publishing](publishing.md).
