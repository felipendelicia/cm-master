# Aprobar, publicar y comprobar

Lee esta referencia antes de aprobar, enviar, programar o reconciliar una pieza. Usa el [contrato CLI](local-tools.md) y comprueba las capacidades del [host](hosts.md).

## Preparar una decisión concreta

El paquete revisable muestra ID y versión, marca, red, URL exacta de cuenta, formato, texto final completo, medios finales visibles, alt text y horario con zona. Ejecuta `review` para obtener la huella actual. El usuario puede aprobar una pieza o una tanda numerada cuyas versiones, destinos y horarios estén visibles. Conserva como evidencia el mensaje o referencia de conversación que expresa ese consentimiento y quién lo dio.

Registra el consentimiento mediante `approve ... --review-sha ... --evidence ... --by ...`. La CLI comprueba coherencia; no autentica a la persona. Una casilla heredada, la aprobación del manual o la aceptación del calendario no identifica por sí sola una pieza final autorizada. Si el usuario pide un cambio, actualiza los archivos y manifiesto, vuelve a `review` y presenta la nueva versión para aprobar. `revoke` cancela la autorización local antes de ejecutar; no retira automáticamente una publicación o programación ya enviada al servicio.

## Vía de publicación

Para **LinkedIn, Instagram, Facebook y X**, evalúa el navegador autenticado y autorizado del host. Verifica si permite abrir el editor, adjuntar los archivos, completar el texto y ejecutar la acción aprobada en la cuenta elegida. Considera también la programación nativa y Meta Business Suite cuando estén disponibles. No impongas una API ni el trabajo manual como modo predeterminado para LinkedIn o X.

La capacidad de controlar una página no resuelve los requisitos concretos del servicio, cuenta y host. Atiende los controles de autorización que aparezcan; no supongas una excepción contractual por ser una operación supervisada. Si aparece una restricción concreta, sesión vencida, CAPTCHA, 2FA o editor inaccesible, conserva el paquete y pide la intervención específica necesaria. Ofrece el paquete para publicación manual si la vía disponible no puede completarse. No cambies de cuenta o canal para eludir ese impedimento.

## Envío con reserva persistente

1. Verifica la cuenta visible contra el manifiesto, marca, destino, adjuntos, texto y horario aprobados. El borrador en el editor debe coincidir con la vista revisada. Confirma la vigencia de las afirmaciones sensibles a la fecha.
2. Ejecuta `check ID POST --mode publish` para publicación inmediata, o `--mode schedule` para solicitar programación nativa. `publish` admite desde la hora aprobada hasta 60 minutos después; `schedule` exige una fecha futura. Si la pieza venció, reprograma y vuelve a aprobar antes de ejecutar.
3. Inmediatamente antes del envío o de confirmar la programación, ejecuta `begin` con el mismo modo. Sólo continúa si obtiene la reserva. Esta comprobación persistente evita que otra ejecución envíe el mismo paquete. La aprobación del usuario y cualquier autorización final del host deben estar resueltas para la acción concreta.
4. Ejecuta la acción final en el navegador una vez. Observa la respuesta del servicio y recoge fecha, URL, identificador, entrada de la lista de publicaciones programadas o comprobante equivalente. Registra `published` o `scheduled` con esa evidencia mediante `record`. Para `scheduled`, verifica que el servicio aceptó la cuenta, pieza y fecha elegidas.

Si el proceso se interrumpe después de `begin`, la reserva sigue vigente. `begin` tampoco debe repetirse ante un estado `scheduled`, `published`, `uncertain` o `blocked`. Un calendario local, una tarea del host, la carga de un adjunto o un editor cerrado no prueban envío ni programación.

## Reconciliar incertidumbre o bloqueo

Si no está claro si el servicio recibió el envío, registra `uncertain` con lo observado y examina el perfil, historial o cola de programación de la cuenta correcta antes de cualquier reintento. Si encuentras la pieza, registra el resultado real y su evidencia. Si no puedes determinarlo, conserva el estado incierto y comunica la verificación pendiente.

Sólo si existe evidencia suficiente de que la pieza no fue publicada ni programada, utiliza `resolve ... --outcome not-published --evidence ...`. Si la huella permanece idéntica, conserva la aprobación ya otorgada; si cambió, queda pendiente de aprobación. Repasa la versión y la ventana horaria antes de una nueva reserva. Una página que no cargó no acredita ausencia.

Cuando un impedimento confirmado detiene una operación ya reservada, registra `blocked` con su causa. Si detectas el impedimento antes de reservar, conserva la pieza y documenta la limitación en su historial, sin iniciar un envío. Para retomar un paquete reservado, resuelve primero la ausencia de publicación con evidencia.

Si ya hay una programación remota y el usuario la revoca, retírala del servicio mediante una acción autorizada y comprueba el resultado. Sólo entonces usa `cancel-scheduled ID POST --evidence TEXT` para dejarla cancelada y sin aprobación local. Ese comando no borra nada del servicio. Si no puedes confirmar la cancelación, conserva la evidencia del problema y comunica que la salida remota aún puede ocurrir.

## Seguimiento y entrega

Guarda en el historial la versión, aprobación, reserva, operación y evidencia. Comunica si quedó preparado, aprobado, programado, publicado, bloqueado o incierto, con enlace cuando exista. Revisa las programaciones después de su horario: si se publicó, usa `record ... --status published --evidence ...` con su enlace o comprobación; esa actualización no necesita otra reserva. Si falló, conserva la evidencia del fallo y reconcilia la situación antes de cualquier nueva ejecución. Los avisos o tareas para hacerlo se configuran por marca como explica [hosts](hosts.md); no son garantía de ejecución continua.
