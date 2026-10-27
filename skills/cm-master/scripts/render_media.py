#!/usr/bin/env python3
"""Render an offline PNG or an animated H.264 MP4 from a local JSON spec.

Usage: python render_media.py SPEC.json --output PATH [--kind image|video]
Images are relative to SPEC.json and must remain inside its directory. No network,
API keys or paid services are used. PNG accepts one slide; use MP4 for a sequence.
Dependencies are optional and separate from the editorial-state CLI.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import sys
import tempfile


FPS = 24


class MediaError(ValueError):
    """A readable input, dependency or rendering failure."""


def pillow():
    try:
        from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps
    except ImportError as error:
        raise MediaError("Falta Pillow. Instalá requirements-media.txt en un entorno virtual.") from error
    return Image, ImageColor, ImageDraw, ImageFont, ImageOps


def ffmpeg_executable():
    executable = shutil.which("ffmpeg")
    if executable:
        return executable
    try:
        import imageio_ffmpeg
        executable = imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError, OSError) as error:
        raise MediaError(
            "Falta FFmpeg para MP4 H.264. Instalá FFmpeg o imageio-ffmpeg "
            "(requirements-media.txt) en un entorno virtual."
        ) from error
    if not Path(executable).is_file():
        raise MediaError("No se encontró el ejecutable FFmpeg de imageio-ffmpeg.")
    return executable


def text_value(value, field, *, required=False):
    if not isinstance(value, str) or (required and not value.strip()):
        raise MediaError(f"{field} debe ser texto" + (" no vacío." if required else "."))
    if any(ord(character) < 32 and character not in "\n\t" for character in value):
        raise MediaError(f"{field} contiene caracteres de control no admitidos.")
    if len(value) > 20000:
        raise MediaError(f"El texto {field} es demasiado largo; dividilo en varias piezas.")
    return value.strip()


def luminance(color):
    channels = [channel / 255 for channel in color]
    channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return sum(channel * weight for channel, weight in zip(channels, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def load_spec(source, kind):
    Image, ImageColor, _, _, ImageOps = pillow()
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise MediaError(f"No se pudo leer el spec JSON: {error}") from error
    if not isinstance(data, dict):
        raise MediaError("El spec debe ser un objeto JSON con brand_name y headline.")
    spec = {field: text_value(data.get(field, ""), field, required=field in ("brand_name", "headline"))
            for field in ("brand_name", "headline", "body", "cta")}
    spec["size"] = data.get("size", [1080, 1350])
    if (not isinstance(spec["size"], list) or len(spec["size"]) != 2
            or any(type(side) is not int or not 256 <= side <= 4096 for side in spec["size"])):
        raise MediaError("size debe contener dos tamaños enteros entre 256 y 4096 píxeles.")
    if kind == "video" and any(side % 2 for side in spec["size"]):
        raise MediaError("Las dimensiones de video H.264 deben ser pares.")
    for field, default in (("background", "#123A32"), ("foreground", "#FFF4DA"), ("accent", "#EAA47C")):
        try:
            color = data.get(field, default)
            if not isinstance(color, str):
                raise ValueError("se esperaba un color de texto")
            spec[field] = ImageColor.getrgb(color)
            if len(spec[field]) != 3:
                raise ValueError("usá un color RGB opaco")
        except (ValueError, TypeError) as error:
            raise MediaError(f"Color {field} inválido: {error}") from error
    if contrast(spec["foreground"], spec["background"]) < 4.5:
        raise MediaError("Los colores foreground y background requieren contraste de al menos 4.5 para texto legible.")
    seconds = data.get("seconds_per_slide", 3)
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0.5 <= seconds <= 30:
        raise MediaError("seconds_per_slide debe ser un número finito entre 0.5 y 30 segundos.")
    spec["frames_per_slide"] = round(seconds * FPS)
    slides = data.get("slides", [{}])
    if not isinstance(slides, list) or not 1 <= len(slides) <= 30:
        raise MediaError("slides debe ser una lista de 1 a 30 diapositivas.")
    if kind == "image" and len(slides) != 1:
        raise MediaError("Un PNG admite una diapositiva; usá --kind video para varias slides.")
    if len(slides) * spec["frames_per_slide"] / FPS > 300:
        raise MediaError("El video supera 300 segundos; dividilo en varias piezas.")
    spec["slides"] = []
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict) or set(slide) - {"text", "image"}:
            raise MediaError(f"slides[{index}] debe ser un objeto con text e image opcionales.")
        item = {"text": text_value(slide.get("text", ""), f"slides[{index}].text"), "photo": None}
        if "image" in slide:
            filename = slide["image"]
            if (not isinstance(filename, str) or not filename.strip() or ":" in filename or "\\" in filename
                    or Path(filename).is_absolute() or PureWindowsPath(filename).is_absolute()):
                raise MediaError(f"La ruta image de slides[{index}] debe ser local y relativa al spec.")
            try:
                photo = (source.parent / filename).resolve()
                photo.relative_to(source.parent)
            except (ValueError, OSError, RuntimeError) as error:
                raise MediaError(f"La ruta de imagen en slides[{index}] queda fuera de la carpeta del spec.") from error
            try:
                with Image.open(photo) as opened:
                    if opened.format not in {"PNG", "JPEG", "WEBP"}:
                        raise MediaError("La imagen debe ser PNG, JPEG o WebP.")
                    item["photo"] = ImageOps.exif_transpose(opened).convert("RGB")
            except (OSError, ValueError, Image.DecompressionBombError) as error:
                raise MediaError(f"No se pudo abrir la imagen local de slides[{index}]: {error}") from error
            item["path"] = photo
        spec["slides"].append(item)
    return spec


def font(size, bold=False):
    _, _, _, ImageFont, _ = pillow()
    candidates = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=max(1, round(size)))
        except OSError:
            continue
    raise MediaError("Falta una tipografía TrueType con acentos: instalá DejaVu Sans, FreeSans o Arial.")


def wrap_text(text, typeface, width):
    """Wrap all copy, including long words, without truncating or adding ellipses."""
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}" if line else word
            if typeface.getlength(candidate) <= width:
                line = candidate
                continue
            if line:
                lines.append(line)
                line = ""
            for character in word:
                if line and typeface.getlength(line + character) > width:
                    lines.append(line)
                    line = ""
                line += character
        lines.append(line)
    return lines


def text_height(lines, typeface):
    return len(lines) * math.ceil(typeface.size * 1.30)


def draw_lines(draw, lines, typeface, position, fill):
    x, y = position
    for line in lines:
        draw.text((x, y), line, font=typeface, fill=fill, anchor="lt")
        y += math.ceil(typeface.size * 1.30)


def layout(spec, slide):
    width, height = spec["size"]
    margin = round(min(width, height) * 0.065)
    text_width = width - 2 * margin
    unit = min(width, height)
    brand_font = font(max(10, unit * 0.023), bold=True)
    brand_lines = wrap_text(spec["brand_name"], brand_font, text_width - unit * 0.04)
    brand_height = text_height(brand_lines, brand_font)
    header_bottom = margin + brand_height + unit * 0.035
    art_top = round(header_bottom + unit * 0.035)
    art_height = round(min(height * 0.22, width * 0.40))
    content_top = art_top + art_height + round(unit * 0.05)
    body = "\n\n".join(value for value in (spec["body"], slide["text"]) if value)
    for step in range(26):
        scale = 1 - step * 0.02
        title_font = font(max(21, min(width * 0.088, height * 0.078) * scale), bold=True)
        body_font = font(max(12, unit * 0.031 * scale))
        cta_font = font(max(11, unit * 0.027 * scale), bold=True)
        if body_font.size < max(12, round(unit * 0.021)):
            break
        title_lines = wrap_text(spec["headline"], title_font, text_width)
        body_lines = wrap_text(body, body_font, text_width) if body else []
        cta_lines = wrap_text(spec["cta"], cta_font, text_width - 2 * margin * 0.5) if spec["cta"] else []
        title_height = text_height(title_lines, title_font)
        body_height = text_height(body_lines, body_font)
        cta_height = text_height(cta_lines, cta_font) + unit * 0.035 if cta_lines else 0
        gaps = unit * 0.026 * bool(body_lines) + unit * 0.045 * bool(cta_lines)
        total = title_height + body_height + cta_height + gaps
        if total <= height - content_top - margin and header_bottom < height * 0.22:
            return locals()
    raise MediaError(
        "El texto no cabe con tamaño legible. Acortá headline/body/cta, "
        "dividí el contenido en slides o aumentá size. No se recortó el texto."
    )


def mix(first, second, weight):
    return tuple(round(a * (1 - weight) + b * weight) for a, b in zip(first, second))


def artwork(spec, slide, box, progress):
    Image, _, ImageDraw, _, ImageOps = pillow()
    width, height = box
    background, accent = spec["background"], spec["accent"]
    art = Image.new("RGB", box, background)
    draw = ImageDraw.Draw(art)
    muted = mix(background, accent, 0.12)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=height * 0.13, fill=muted)
    if slide["photo"] is not None:
        # Fit the complete photo, preserve its aspect ratio and animate within the panel.
        padding = max(5, round(height * (0.08 - 0.02 * progress)))
        photo = ImageOps.contain(slide["photo"], (width - 2 * padding, height - 2 * padding), Image.Resampling.LANCZOS)
        art.paste(photo, ((width - photo.width) // 2, (height - photo.height) // 2))
        return art
    # Neutral abstract composition; never infer a brand's product or industry.
    offset = progress * width * 0.014
    draw.polygon([(width * 0.43, height * 0.16), (width * 0.71, height * 0.16),
                  (width * 0.56, height * 0.84), (width * 0.28, height * 0.84)],
                 fill=mix(background, accent, 0.25))
    cx, cy, radius = width * 0.29 + offset, height * 0.50, height * 0.32
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=accent)
    cx = width * 0.70 - offset
    for proportion in (0.34, 0.24):
        radius = height * proportion
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                     outline=mix(spec["foreground"], accent, 0.35), width=max(1, round(height * 0.014)))
    for index in range(4):
        x = width * (0.83 + index * 0.025)
        draw.line((x, height * 0.63, x, height * 0.78),
                  fill=mix(background, accent, 0.65), width=max(1, round(height * 0.009)))
    return art


def prepare_slide(spec, slide):
    Image, _, ImageDraw, _, _ = pillow()
    info = layout(spec, slide)
    width, height = spec["size"]
    unit, margin = info["unit"], info["margin"]
    image = Image.new("RGB", (width, height), spec["background"])
    draw = ImageDraw.Draw(image)
    mark = round(unit * 0.018)
    draw.rectangle((margin, margin + 2, margin + mark, margin + 2 + mark), fill=spec["accent"])
    draw_lines(draw, info["brand_lines"], info["brand_font"], (margin + unit * 0.04, margin), spec["foreground"])
    draw.line((margin, info["header_bottom"], width - margin, info["header_bottom"]), fill=mix(spec["background"], spec["foreground"], 0.25), width=1)
    y = info["content_top"]
    draw_lines(draw, info["title_lines"], info["title_font"], (margin, y), spec["foreground"])
    y += info["title_height"]
    if info["body_lines"]:
        y += unit * 0.026
        draw_lines(draw, info["body_lines"], info["body_font"], (margin, y), spec["foreground"])
    if info["cta_lines"]:
        top = height - margin - info["cta_height"]
        draw.rounded_rectangle((margin, top, width - margin, height - margin), radius=unit * 0.015, fill=spec["accent"])
        ink = max(((0, 0, 0), (255, 255, 255)), key=lambda value: contrast(value, spec["accent"]))
        draw_lines(draw, info["cta_lines"], info["cta_font"], (margin * 1.5, top + unit * 0.0175), ink)
    return image, (margin, info["art_top"], width - 2 * margin, info["art_height"])


def frame(spec, slide, prepared, progress):
    image, (x, y, width, height) = prepared
    image = image.copy()
    image.paste(artwork(spec, slide, (width, height), progress), (x, y))
    return image


def write_video(spec, output, prepared, executable):
    Image, _, _, _, _ = pillow()
    width, height = spec["size"]
    command = [executable, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
               "-vcodec", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
               "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
               "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
    # A file for stderr prevents a full pipe from deadlocking the encoder.
    with tempfile.TemporaryFile() as diagnostics:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=diagnostics)
        previous = Image.new("RGB", tuple(spec["size"]), spec["background"])
        count = spec["frames_per_slide"]
        fade_frames = min(round(FPS * 0.20), max(2, count // 3))
        try:
            for slide, composition in zip(spec["slides"], prepared):
                for index in range(count):
                    current = frame(spec, slide, composition, index / max(1, count - 1))
                    if index < fade_frames:
                        current = Image.blend(previous, current, (index + 1) / fade_frames)
                    process.stdin.write(current.tobytes())
                previous = current
            process.stdin.close()
            returncode = process.wait(timeout=120)
        except BaseException:
            process.kill()
            process.wait()
            if process.stdin:
                process.stdin.close()
            diagnostics.seek(0)
            detail = diagnostics.read(4000).decode(errors="replace").strip()
            if sys.exc_info()[0] in (BrokenPipeError, subprocess.TimeoutExpired):
                raise MediaError(f"FFmpeg no pudo codificar H.264: {detail or 'tiempo agotado'}") from None
            raise
        diagnostics.seek(0)
        if returncode:
            raise MediaError("FFmpeg no pudo codificar H.264: " + diagnostics.read(4000).decode(errors="replace").strip())


def render(source, output, kind):
    Image, _, _, _, _ = pillow()
    source = Path(source).resolve()
    output = Path(output).absolute()
    suffix = ".png" if kind == "image" else ".mp4"
    if output.suffix.lower() != suffix:
        raise MediaError(f"La salida {kind} debe tener extensión {suffix}.")
    spec = load_spec(source, kind)
    input_paths = {source} | {slide["path"] for slide in spec["slides"] if "path" in slide}
    if output.resolve() in input_paths:
        raise MediaError("La ruta de salida no puede sobrescribir el spec ni una imagen de entrada.")
    # Validate all text before writing an output or starting FFmpeg.
    prepared = [prepare_slide(spec, slide) for slide in spec["slides"]]
    executable = ffmpeg_executable() if kind == "video" else None
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".cm-master-", suffix=suffix, dir=output.parent)
    os.close(descriptor)
    try:
        if kind == "image":
            frame(spec, spec["slides"][0], prepared[0], 0.5).save(temporary, format="PNG", optimize=True)
        else:
            write_video(spec, Path(temporary), prepared, executable)
        os.replace(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)
    result = {"kind": kind, "output": str(output), "size": spec["size"]}
    if kind == "video":
        total = spec["frames_per_slide"] * len(spec["slides"])
        result.update(codec="h264", fps=FPS, frames=total, duration_seconds=total / FPS)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--kind", choices=("image", "video"))
    arguments = parser.parse_args(argv)
    kind = arguments.kind or ("video" if arguments.output.suffix.lower() == ".mp4" else "image")
    try:
        result = render(arguments.spec, arguments.output, kind)
    except (MediaError, OSError, subprocess.SubprocessError) as error:
        print(f"Error de medios: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
