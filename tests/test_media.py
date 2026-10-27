"""End-to-end checks for the independent, offline media renderer."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

try:
    from PIL import Image
except ImportError:
    Image = None


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "skills/cm-master/scripts/render_media.py"


def ffmpeg_executable():
    executable = shutil.which("ffmpeg")
    if executable:
        return executable
    if importlib.util.find_spec("imageio_ffmpeg"):
        import imageio_ffmpeg
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except RuntimeError:
            return None
    return None


@unittest.skipUnless(Image, "Pillow is optional: install requirements-media.txt")
class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.spec = {
            "brand_name": "Taller Río · marca ficticia",
            "headline": "Diseñá una pausa para vos.",
            "body": "Cerámica, café y pequeños rituales. Una propuesta ficticia para crear sin apuro.",
            "cta": "Descubrí tu próximo ritual",
            "background": "#122E2A",
            "foreground": "#FFF4DA",
            "accent": "#EAA47C",
            "size": [640, 800],
            "seconds_per_slide": 0.5,
        }

    def render(self, spec=None, *, kind="image", suffix=None, cwd=None):
        source = self.directory / "spec.json"
        source.write_text(json.dumps(self.spec if spec is None else spec, ensure_ascii=False), encoding="utf-8")
        output = self.directory / ("result" + (suffix or (".png" if kind == "image" else ".mp4")))
        result = subprocess.run(
            [sys.executable, str(RENDERER), str(source), "--output", str(output), "--kind", kind],
            cwd=cwd, text=True, capture_output=True, timeout=90,
        )
        return result, output

    def test_png_has_requested_dimensions_and_visible_composition(self):
        result, output = self.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        with Image.open(output) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (640, 800))
            self.assertGreater(len(image.getcolors(1000000)), 20)
        self.assertEqual(json.loads(result.stdout)["kind"], "image")

    def test_long_spanish_copy_is_rendered_without_ellipsis_or_silent_loss(self):
        self.spec["size"] = [1080, 1350]
        self.spec["headline"] = "Volvé a encontrar tu ritmo: una invitación a crear con las manos y compartir lo simple."
        self.spec["body"] = ("Diseñamos encuentros de cerámica para disfrutar cada proceso. "
                             "Elegí tus colores, probá nuevas formas y llevate una pieza con tu historia. "
                             "No necesitás experiencia; sólo curiosidad y ganas de compartir. "
                             "Esta marca y esta propuesta son ficticias.")
        result, output = self.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.is_file())

    def test_copy_too_large_to_remain_legible_is_an_explicit_error(self):
        self.spec["body"] = "Una descripción extensa con acentos y sentido. " * 250
        result, output = self.render()
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr.lower(), "texto|text|cabe|fit|largo")
        self.assertFalse(output.exists())

    def test_local_photo_is_resolved_relative_to_spec_not_working_directory(self):
        assets = self.directory / "assets"
        assets.mkdir()
        Image.new("RGB", (400, 200), (250, 20, 40)).save(assets / "photo.png")
        self.spec["slides"] = [{"text": "Una pieza única.", "image": "assets/photo.png"}]
        result, output = self.render(cwd="/tmp")
        self.assertEqual(result.returncode, 0, result.stderr)
        with Image.open(output) as image:
            colors = image.convert("RGB").getcolors(image.width * image.height)
            red_pixels = sum(count for count, (r, g, b) in colors if r > 200 and g < 60 and b < 80)
            red, green, blue = image.convert("RGB").split()
            mask = red.point(lambda channel: 255 if channel > 200 else 0)
            mask.paste(0, mask=green.point(lambda channel: 255 if channel >= 60 else 0))
            mask.paste(0, mask=blue.point(lambda channel: 255 if channel >= 80 else 0))
            left, top, right, bottom = mask.getbbox()
            self.assertAlmostEqual((right - left) / (bottom - top), 2.0, delta=0.03)
        self.assertGreater(red_pixels, 2000)

    def test_invalid_specs_fail_clearly_without_creating_output(self):
        cases = [
            ({}, "brand|marca|headline|titular"),
            ({**self.spec, "size": [0, 800]}, "size|tamaño|dimensi"),
            ({**self.spec, "size": [640.0, 800]}, "size|tamaño|entero|integer"),
            ({**self.spec, "background": "not-a-color"}, "color|background"),
            ({**self.spec, "headline": ["wrong"]}, "headline|texto|text"),
            ({**self.spec, "slides": []}, "slides|diapositiva"),
            ({**self.spec, "slides": ["wrong"]}, "slide|diapositiva"),
            ({**self.spec, "seconds_per_slide": float("nan")}, "seconds|segundo|finite|finito"),
        ]
        for spec, error in cases:
            with self.subTest(spec=spec):
                result, output = self.render(spec)
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr.lower(), error)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(output.exists())

    def test_remote_and_outside_photo_paths_are_rejected_before_reading(self):
        for filename in ("https://example.com/photo.jpg", "/etc/passwd", "../photo.png"):
            with self.subTest(filename=filename):
                self.spec["slides"] = [{"image": filename}]
                result, output = self.render()
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr.lower(), "local|relativ|fuera|outside|ruta|path")
                self.assertFalse(output.exists())

    def test_symlink_photo_escaping_spec_directory_is_rejected(self):
        (self.directory / "photo.png").symlink_to("/etc/passwd")
        self.spec["slides"] = [{"image": "photo.png"}]
        result, output = self.render()
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr.lower(), "fuera|outside|ruta|path")
        self.assertFalse(output.exists())

    def test_missing_or_nonimage_photo_has_actionable_error(self):
        for filename in ("missing.png", "spec.json"):
            with self.subTest(filename=filename):
                self.spec["slides"] = [{"image": filename}]
                result, output = self.render()
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr.lower(), "imagen|image|foto")
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(output.exists())

    def test_multiple_slides_cannot_be_silently_discarded_in_one_png(self):
        self.spec["slides"] = [{"text": "Primera."}, {"text": "Segunda."}]
        result, output = self.render()
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr.lower(), "slide|diapositiva|video")
        self.assertFalse(output.exists())

    def test_video_requires_even_dimensions_for_h264(self):
        self.spec["size"] = [641, 800]
        result, output = self.render(kind="video")
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr.lower(), "par|even")
        self.assertFalse(output.exists())

    @unittest.skipUnless(ffmpeg_executable(), "MP4 integration needs FFmpeg or imageio-ffmpeg")
    def test_mp4_is_h264_decodable_and_contains_all_slides_with_animation(self):
        self.spec["size"] = [320, 400]
        self.spec["headline"] = "Creá tu pausa."
        self.spec["body"] = "Cerámica y pequeños rituales."
        self.spec["cta"] = "Descubrí más"
        Image.new("RGB", (400, 200), (250, 20, 40)).save(self.directory / "photo.png")
        self.spec["slides"] = [{"text": "Hecho a mano.", "image": "photo.png"}, {"text": "Para disfrutar."}]
        result, output = self.render(kind="video")
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["size"], [320, 400])
        self.assertEqual(metadata["frames"], 24)
        self.assertAlmostEqual(metadata["duration_seconds"], 1.0)
        decoded = subprocess.run(
            [ffmpeg_executable(), "-hide_banner", "-i", str(output), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            capture_output=True, timeout=30,
        )
        self.assertEqual(decoded.returncode, 0, decoded.stderr.decode(errors="replace"))
        self.assertIn("h264", decoded.stderr.decode(errors="replace").lower())
        self.assertEqual(len(decoded.stdout), 320 * 400 * 3 * 24)
        frame_bytes = 320 * 400 * 3
        self.assertNotEqual(decoded.stdout[4 * frame_bytes:5 * frame_bytes], decoded.stdout[8 * frame_bytes:9 * frame_bytes])


if __name__ == "__main__":
    unittest.main()
