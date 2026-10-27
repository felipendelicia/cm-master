# Contratos de los helpers locales

Lee esta referencia al persistir perfiles, operar paquetes o generar una composición. Los comandos son locales y no autentican personas ni controlan cuentas sociales.

## Rutas y raíz de datos

En los ejemplos, `SKILL_DIR` representa el directorio donde está instalado `SKILL.md`; resuélvelo antes de ejecutar. Los nombres `ID`, `POST`, `DIR`, `JSON`, `SHA`, `TEXT`, `NAME`, `URL` y `PATH` son argumentos que debes reemplazar por valores concretos y entrecomillar cuando corresponda. Los ejemplos usan `python3`, versión 3.10 o posterior. En Windows puede ser `python` si ese intérprete corresponde a la versión requerida; con un entorno virtual usa su propio intérprete.

```text
python3 SKILL_DIR/scripts/cm.py --root DIR <command> ...
```

`--root` es opcional: toma `CM_MASTER_HOME` o, por defecto, `~/.cm-master`. Cada marca queda en `brands/<id>/` y cada manifiesto en `posts/<post>/post.json` dentro de esa marca. Usa IDs válidos y una raíz fuera del repositorio público para datos operativos. Las rutas de medios son relativas a la carpeta de su marca; un archivo o symlink que escape hacia otra marca o fuera de ella se rechaza.

## CLI de estado editorial

```text
init-brand ID --name NAME [--website URL]
list-brands
profile ID [--file JSON]
stage ID POST --file JSON
review ID POST
approve ID POST --review-sha SHA --evidence TEXT --by NAME
revoke ID POST --reason TEXT
cancel-scheduled ID POST --evidence TEXT
check ID POST [--mode publish|schedule]
begin ID POST [--mode publish|schedule]
record ID POST --status published|scheduled|uncertain|blocked --evidence TEXT [--url URL]
resolve ID POST --outcome not-published --evidence TEXT
due [--brand ID]
```

Todos son subcomandos de `cm.py`; la salida es JSON y un estado inválido produce código de salida no cero. Interpreta el resultado antes de continuar. `profile` consulta el perfil sin `--file`, o combina desde un JSON los diccionarios y reemplaza las listas; regenera `manual.md` y guarda una revisión del perfil. `stage` guarda el manifiesto de una pieza; `review` devuelve detalles revisables y la huella canónica actual sin cambiar el estado.

Los paquetes persistidos forman el calendario operativo. `due` inspecciona la cola local, sin efectos en redes: cada item informa `brand_id`, `post_id`, `state`, `ready` y, cuando no está listo, `reason`. Omite piezas aprobadas con fecha futura; las programadas pueden permanecer como no listas para que se verifique su resultado remoto. Los planes, fuentes y reportes se guardan con las herramientas de archivos del host; no hay comandos adicionales de analíticas o calendario global.

Ejemplo de manifiesto ficticio completo; el archivo visual debe existir dentro de la marca elegida antes de revisar/aprobar:

```json
{
  "network": "instagram",
  "account": "https://www.instagram.com/marca_ficticia/",
  "format": "feed",
  "scheduled_at": "2026-11-02T12:00:00-03:00",
  "timezone": "America/Argentina/Buenos_Aires",
  "text": "Conocé nuestra nueva colección. Consultanos para elegir tu próxima pieza.",
  "alt_text": "Composición con productos de la colección ficticia.",
  "media": ["assets/coleccion.png"],
  "objective": "Generar consultas",
  "sources": [],
  "brief": "Presentación de colección ficticia con identidad de la marca."
}
```

Campos obligatorios: `network` (`linkedin|instagram|facebook|x`), `account` (URL exacta), `format` (`feed|story|reel|carousel|video`), `scheduled_at` (ISO 8601 con offset), `timezone` (IANA), `text`, `alt_text` y `media` (lista de rutas relativas a la marca). Opcionales: `objective`, `sources`, `brief`. La presencia de un formato en el esquema no implica que toda red o herramienta lo admita.

## Huellas, ventanas y reconciliación

La huella une texto, medios, cuenta y programación; modificar archivos visuales también invalida la aprobación aunque el JSON permanezca igual. Usa el SHA devuelto por `review` en `approve` junto con evidencia humana. Una fecha sin offset o contradictoria con la zona IANA es inválida.

`check --mode publish` admite desde el horario aprobado hasta 60 minutos después. `check --mode schedule` exige una fecha futura. Pasada la ventana, actualiza fecha/versión y vuelve a aprobar. `begin` realiza la comprobación y crea una reserva exclusiva persistente **antes** de la acción externa. Una segunda reserva o los estados `scheduled`, `published`, `uncertain` y `blocked` impiden repetir.

`record` guarda lo observado tras una reserva; no efectúa la acción remota. `scheduled` requiere aceptación comprobada del servicio y `published` requiere prueba de publicación. Permite actualizar `scheduled` a `published` con evidencia tras verificar la salida, sin una nueva reserva. `uncertain` conserva una duda sobre el resultado del envío; `blocked` conserva un impedimento. Una interrupción tras reservar exige reconciliar el destino, incluso si no hubo tiempo de registrar el resultado. `resolve --outcome not-published` sólo se usa con evidencia de ausencia: conserva la aprobación si la huella sigue idéntica o devuelve la pieza a pendiente de aprobación si cambió.

`revoke` revoca la autorización local antes del envío. Si la pieza ya está programada en el servicio, cancélala allí mediante el navegador autorizado y comprueba el resultado; entonces `cancel-scheduled --evidence ...` registra `scheduled` → `cancelled` y elimina la aprobación local. Este comando no cancela nada remotamente. Sigue [publishing](publishing.md) para decidir la transición correcta; el envío incierto no se reintenta automáticamente.

Las huellas aportan integridad local de la versión y el historial aporta trazabilidad. Ninguno autentica criptográficamente al humano ni demuestra por sí mismo que el servicio social recibió la pieza.

## Renderer independiente

```text
python3 SKILL_DIR/scripts/render_media.py SPEC.json --output PATH [--kind image|video]
```

Lee un JSON y exporta un PNG o un MP4 real. No depende del módulo de estado ni publica nada. Requiere Pillow; para MP4 usa FFmpeg del sistema o imageio-ffmpeg, disponibles entre las dependencias opcionales de medios del proyecto. Si falta una dependencia falla claramente; conserva ese error como diagnóstico, sin tratarlo como un archivo terminado.

El spec admite `brand_name`, `headline`, `body`, `cta`, `background`, `foreground`, `accent`, `size: [w,h]`, `slides` y `seconds_per_slide`. `brand_name` y `headline` deben ser textos no vacíos; `body` y `cta` son opcionales. Cada slide es un objeto con `text` e `image` opcionales. Las imágenes PNG/JPEG/WebP se resuelven respecto del directorio del spec, sin escapes por `../` o symlinks. Mantén spec, imágenes y salida dentro de la carpeta de la marca al producir material operativo.

Para PNG admite exactamente una slide y salida `.png`; para MP4, de una a 30 slides y salida `.mp4`. `size` usa enteros de 256 a 4096 y dimensiones pares para video. `seconds_per_slide` admite de 0.5 a 30 segundos y un máximo total de 300 segundos. El renderer exige contraste de texto/fondo de al menos 4.5 y falla si el texto no cabe de forma legible, en lugar de recortarlo; ante ese error, reduce texto, redistribuye slides o ajusta el diseño.

```json
{
  "brand_name": "Marca ficticia",
  "headline": "Ideas para tu próxima visita",
  "body": "Una presentación de ejemplo.",
  "cta": "Consultanos",
  "background": "#F4EFE7",
  "foreground": "#192A32",
  "accent": "#D55A35",
  "size": [1080, 1080],
  "slides": [
    {"text": "Conocé la colección y elegí tu favorita"}
  ],
  "seconds_per_slide": 3
}
```

Usa `--kind image` o `--kind video` explícitamente al preparar el entregable. Comprueba visualmente el PNG y reproduce o inspecciona el MP4 generado como indica [editorial](editorial.md). El MP4 local es un montaje animado de fotos/textos, no evidencia de generación de escenas por IA.
