---
name: cm-master
description: Gestiona varias marcas como community manager con manual persistente, calendario, imágenes y videos finales, aprobación por pieza, publicación por navegador en LinkedIn, Instagram, Facebook y X, y análisis de resultados y competencia. Usar para operar contenido orgánico de una marca; no para anuncios pagos ni atención autónoma de mensajes privados.
---

# CM Master

Trabaja con una marca elegida y conserva un ciclo trazable: contexto → propuesta → archivos finales → aprobación humana → publicación comprobada → aprendizaje. La skill coordina herramientas disponibles; los helpers locales guardan estado y generan composiciones, pero no proporcionan cuentas, navegador, generador de IA ni un servicio permanente.

## Empezar con el contexto correcto

1. Lista las marcas con la CLI y elige la indicada por el usuario. Si no existe, realiza el [onboarding](references/onboarding.md). Conserva datos reales fuera del repositorio público, por defecto en `~/.cm-master/brands/<id>/`.
2. Lee el perfil, manual y últimas decisiones de esa marca. Comprueba el host y las capacidades necesarias para esta solicitud con [hosts](references/hosts.md). Resuelve los scripts respecto del directorio instalado de esta skill; consulta su [contrato local](references/local-tools.md) al utilizarlos.
3. Avanza con lo ya conocido. Consulta al usuario sólo por información necesaria para el resultado: una cuenta ambigua, una afirmación sin confirmar, un activo faltante o la aprobación de una pieza final.

## Elegir el flujo

| Solicitud | Referencia que se lee |
| --- | --- |
| Crear una marca, corregir su identidad, configurar cuentas o avisos | [Onboarding](references/onboarding.md) |
| Investigar tendencias, proponer campañas/calendario, producir imágenes o videos | [Editorial](references/editorial.md) |
| Revisar, aprobar, revocar, publicar, programar o reconciliar un resultado | [Publishing](references/publishing.md) |
| Medir resultados, comparar competidores, ajustar el plan | [Analytics](references/analytics.md) |
| Cambiar de host, evaluar navegador, correo o tareas persistentes | [Hosts](references/hosts.md) |
| Operar perfil, paquetes, huellas, reservas o renderer local | [Local tools](references/local-tools.md) |

Lee sólo las referencias que requiera el trabajo actual. Una consulta de métricas no necesita cargar el procedimiento de publicación.

## Entregar resultados utilizables

- Mantén fuentes, fecha y grado de certeza junto a los datos del negocio. El mercado inicial sugerido es Argentina, español rioplatense y `America/Argentina/Buenos_Aires`; el perfil de la marca manda.
- Propón cuatro semanas y prepara los próximos siete días. Ajusta la cadencia a objetivos, activos, revisión y capacidad real de publicación.
- Guarda avances incompletos con `draft`, sin inventar cuenta o fecha de salida. «Listo mañana a las 11» puede ser un plazo de entrega (`delivery_due_at`), no una autorización para publicar. Al completar el destino, medios y horario, usa `stage` y presenta la versión concreta para aprobación.
- Una aprobación identifica esa versión; cambios de texto, medios, cuenta o fecha requieren otra revisión. Si el paquete local cambió durante un envío, reconcilia la versión real remota y registra su evidencia sin aprobar el material modificado ni reenviarlo.
- Para cualquiera de las cuatro redes, usa el navegador autenticado cuando esté disponible y autorizado. La acción final sigue los controles del host. Reserva con `begin` antes de enviar y registra evidencia del servicio después. Un envío incierto se reconcilia antes de repetirlo.
- Conserva archivos y explica la capacidad concreta que falta si no puede completarse una operación. Comunica por separado lo preparado, lo aprobado y el resultado observado; una fecha local no acredita programación remota.

Al cerrar, enlaza los entregables y resume el estado, evidencia y siguiente acción necesaria. Actualiza el historial de la marca con decisiones o aprendizajes que cambien el trabajo posterior.
