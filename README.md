# CM Master

Skill de Community Manager para **Codex y Claude Code**, inspirada en el perfil de marca editable de Google Pomelli. Administra varias marcas, produce contenido final, organiza el calendario y coordina publicación mediante navegador con aprobación humana de cada pieza.

**Primera versión implementada.** Incluye instrucciones operativas, estado editorial local, instalador y renderer PNG/MP4. La publicación se ejecuta con las herramientas disponibles en el host; la CLI del proyecto administra estado y no es un bot de redes.

## Qué hace

- Entrevista inicial desde la web o materiales de la marca; manual editable con identidad, tono, público, negocio, contactos y fuentes.
- Carpetas separadas por marca con perfil, historial, medios, paquetes, aprobaciones y reportes.
- Plan mensual orientativo y preparación semanal. Punto de partida configurable: tres publicaciones principales e historias de Instagram/Facebook tres días por semana.
- Investigación de tendencias y competidores, con Argentina y español rioplatense como valores iniciales configurables.
- Texto, imágenes y archivos MP4 finales. Usa generación de la suscripción cuando existe; como alternativa produce composiciones y montajes animados locales.
- Publicación en **LinkedIn, Instagram, Facebook y X** usando navegador autenticado del host cuando esté disponible, tras aprobar texto, archivos, cuenta y horario.
- Huellas que detectan cambios posteriores a la aprobación, reserva persistente para evitar doble envío y registro de resultados comprobados.
- Análisis semanal con métricas fechadas, denominadores identificados y propuestas de mejora.
- Avisos en el host o por mail y tareas recurrentes cuando se configuran y autorizan para la marca.

## Instalación

Python **3.10 o posterior**. Cloná el repositorio y elegí uno o ambos hosts:

```bash
git clone https://github.com/felipendelicia/cm-master.git
cd cm-master
python3 scripts/install.py --host codex
python3 scripts/install.py --host claude
```

El instalador copia la misma skill a `~/.agents/skills/cm-master` para Codex y `~/.claude/skills/cm-master` para Claude Code. Rechaza destinos existentes para conservar modificaciones locales. Para una instalación acotada al proyecto o una prueba, indicá la carpeta final con `--destination /ruta/al/proyecto/.agents/skills/cm-master` o `.claude/skills/cm-master` según el host.

En Windows, usá `python` o `py -3` si ése es el intérprete instalado y ejecutá `python -m pip install -r requirements.txt` para los datos IANA de zona horaria. El código de estado no necesita Pillow ni FFmpeg.

La instalación no cambia permisos, sesiones, cuentas, tareas ni correo. Para actualizar, preservá tus cambios locales y reemplazá deliberadamente la carpeta instalada por la nueva versión. Los datos de las marcas están en una ubicación distinta de la instalación.

### Invocación

En Codex:

```text
Usá $cm-master para dar de alta mi marca y preparar la primera semana de contenido.
```

En Claude Code:

```text
/cm-master
```

También puede activarse cuando el pedido coincide con su descripción. Si el host no detecta la instalación, abrí una sesión nueva. En el primer uso pedirá la web o materiales del negocio, los objetivos y las cuentas exactas.

## Archivos finales de imagen y video

Las herramientas de generación de la suscripción se detectan en cada entorno. Para la alternativa local, instalá las dependencias en un entorno virtual:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-media.txt
.venv/bin/python skills/cm-master/scripts/render_media.py examples/demo-media.json --output /tmp/cm-demo.png --kind image
.venv/bin/python skills/cm-master/scripts/render_media.py examples/demo-media.json --output /tmp/cm-demo.mp4 --kind video
```

En Windows, el intérprete del entorno suele ser `.venv\Scripts\python.exe`; elegí rutas de salida locales en lugar de `/tmp`. Se usa FFmpeg del sistema o el ejecutable incluido con `imageio-ffmpeg`. Estos paquetes funcionan localmente y no consumen una API paga.

El renderer admite fotos locales PNG/JPEG/WebP y textos en español, colores configurables, varias slides y animaciones. Entrega PNG o MP4 H.264 sin audio; sin fotos genera una composición abstracta. Rechaza texto que no cabe legible, contraste insuficiente, rutas fuera del spec o dimensiones inválidas. Los MP4 son montajes animados; no escenas generadas por un modelo de video.

## Datos y aprobación

Por defecto se guardan en `~/.cm-master/brands/<id>/`; `CM_MASTER_HOME` o `cm.py --root DIR` permite otra raíz. Usá una carpeta fuera del repositorio público.

```text
brands/mi-marca/
  profile.json   manual.md
  assets/        sources/
  history/       reports/
  posts/mi-pieza/
    post.json    state.json
```

Los paquetes forman el calendario operativo. El usuario revisa el texto y archivos finales junto con cuenta, red y horario; después la IA registra el consentimiento con su huella. Un cambio de esos elementos invalida la aprobación. Aprobar la estrategia o el manual no aprueba las publicaciones futuras.

Antes de enviar se reserva el intento con `begin`; después se registra la evidencia real de la red. `scheduled` requiere confirmación del servicio. Si se corta el proceso, se comprueba el destino antes de reintentar. Una reserva local o una tarea del host no prueba que se publicó. La cancelación local tampoco retira una programación remota: primero se cancela y verifica en la red, después se registra ese resultado.

La CLI registra evidencia y versiones; no autentica criptográficamente al humano ni valida por sí sola un comprobante remoto. El navegador sigue los controles del host. Ver [publicación](skills/cm-master/references/publishing.md) y [contratos locales](skills/cm-master/references/local-tools.md).

### Ejemplo completo sin cuentas reales

```bash
.venv/bin/python examples/create_demo.py --root /tmp/cm-master-demo --video
```

Crea una marca y cuenta **ficticias**, un PNG, un MP4 y un paquete para mañana a las 11 de Buenos Aires, pendiente de revisión. No aprueba, publica ni programa nada. Elegí otra raíz si ya existe esa marca de ejemplo. El JSON de salida muestra las rutas de los archivos y la revisión del paquete.

## Navegador, autonomía y correo

Codex necesita una sesión con herramientas de navegador, como la aplicación de escritorio y su extensión; instalar la skill en un CLI no añade esas herramientas. Claude Code usa su integración de navegador configurada. Dots puede coordinar la skill cuando tiene acceso a su instalación y a los archivos necesarios; el navegador cloud tiene sesiones distintas de las de tu computadora. Ver [adaptadores y configuración](skills/cm-master/references/hosts.md).

El flujo de publicación por navegador contempla las cuatro redes. Las funciones concretas dependen del host, tipo de cuenta, adjuntos, permisos y estado del servicio. Ante un impedimento real conserva los archivos y solicita la intervención necesaria. No se exige una API ni se impone publicación manual por defecto para LinkedIn/X.

Las tareas nativas del host pueden preparar propuestas, pedir aprobación, ejecutar lo aprobado y verificar resultados. Los avisos por mail requieren herramienta de correo y destinatario configurados. La skill no instala un servidor ni un scheduler propio: para operar archivos o navegador locales, la computadora y la aplicación/sesión deben estar disponibles. La programación nativa de una red, si quedó confirmada, sigue las condiciones de esa plataforma.

Quedan fuera de esta versión la atención autónoma de mensajes privados, anuncios pagos y servicios adicionales por consumo.

## Verificación y desarrollo

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Los tests usan carpetas temporales y datos ficticios. Cubren aprobación ligada a archivos, aislamiento de marcas, fechas, reserva concurrente, resultados inciertos, programación/cancelación, instalación y medios reales. Las pruebas de video se omiten con una razón si falta el encoder; instalá `requirements-media.txt` para ejecutarlas. GitHub Actions ejecuta la suite con dependencias de medios en Python 3.10 y 3.12.

Ver [evidencia de validación](docs/validation.md), [diseño aprobado](docs/superpowers/specs/2026-10-27-cm-master-design.md) y [plan de implementación](docs/superpowers/plans/2026-10-27-cm-master-skill.md).
