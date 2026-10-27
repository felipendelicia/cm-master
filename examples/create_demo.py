#!/usr/bin/env python3
"""Build a fictional pending package locally. Never approve or publish."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/cm-master/scripts"


def run(script, *args):
    result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Raíz de datos para una marca ficticia nueva.")
    parser.add_argument("--video", action="store_true", help="Crear también MP4; requiere FFmpeg o imageio-ffmpeg.")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    brand = root / "brands/taller-rio-demo"
    try:
        run("cm.py", "--root", root, "init-brand", "taller-rio-demo", "--name", "Taller Río (marca ficticia)")
        spec = brand / "assets/demo-media.json"
        spec.write_text((REPO / "examples/demo-media.json").read_text(encoding="utf-8"), encoding="utf-8")
        image = run("render_media.py", spec, "--output", brand / "assets/demo.png", "--kind", "image")
        video = run("render_media.py", spec, "--output", brand / "assets/demo.mp4", "--kind", "video") if args.video else None
        zone = ZoneInfo("America/Argentina/Buenos_Aires")
        tomorrow = (datetime.now(zone) + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0)
        manifest = {
            "network": "instagram", "account": "https://www.instagram.com/taller_rio_ficticio/",
            "format": "feed", "scheduled_at": tomorrow.isoformat(), "timezone": zone.key,
            "text": "Las manos crean. La pausa inspira. Una invitación ficticia a volver a lo simple.",
            "alt_text": "Composición geométrica abstracta en verde y terracota con texto de una marca ficticia.",
            "media": ["assets/demo.png"], "objective": "Ejemplo de visibilidad", "sources": [],
            "brief": "Demostración local ficticia; la URL de cuenta no fue comprobada y no debe usarse para publicar.",
        }
        source = brand / "assets/demo-post.json"
        source.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        review = run("cm.py", "--root", root, "stage", "taller-rio-demo", "demo-feed", "--file", source)
        print(json.dumps({"root": str(root), "image": image, "video": video, "review": review,
                          "published": False, "notice": "Ejemplo ficticio pendiente de revisión, sin aprobación ni acciones remotas."},
                         ensure_ascii=False, indent=2))
        return 0
    except (RuntimeError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
