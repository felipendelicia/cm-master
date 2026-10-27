"""Local editorial state. This module never opens a browser or sends messages."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class StateError(ValueError):
    pass


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value):
        raise StateError("El ID debe usar minúsculas, números y guiones (1–64 caracteres).")
    return value


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise StateError("Se esperaba un objeto JSON.")
    return value


def nonempty(value, field):
    if not isinstance(value, str) or not value.strip():
        raise StateError(f"Falta {field}.")
    return value


def url(value):
    parsed = urlparse(nonempty(value, "URL"))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
        raise StateError("Se requiere una URL http/https sin credenciales.")
    return value


def scheduled_time(post):
    try:
        value = datetime.fromisoformat(nonempty(post.get("scheduled_at"), "scheduled_at").replace("Z", "+00:00"))
        zone = ZoneInfo(nonempty(post.get("timezone"), "timezone"))
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise StateError("Fecha ISO 8601 o zona IANA inválida.") from exc
    if value.utcoffset() is None:
        raise StateError("scheduled_at necesita un offset explícito.")
    if value.utcoffset() != value.astimezone(zone).utcoffset():
        raise StateError("El offset de scheduled_at no corresponde a timezone.")
    return value


def merge(base, patch):
    result = dict(base)
    for key, value in patch.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else value
    return result


class Store:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()

    def safe(self, base, relative):
        """Forbid traversal and every symlink below the selected private root."""
        relative = Path(relative)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise StateError("La ruta debe ser relativa a la marca y no puede escapar de su carpeta.")
        target = base / relative
        current = self.root
        try:
            parts = target.relative_to(self.root).parts
        except ValueError as exc:
            raise StateError("Ruta fuera de la raíz de datos.") from exc
        for part in parts:
            current = current / part
            if current.is_symlink():
                raise StateError("No se admiten symlinks dentro de los datos de marca.")
        if not target.resolve().is_relative_to(base.resolve()):
            raise StateError("Ruta fuera de la marca.")
        return target

    @contextmanager
    def transaction(self):
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        lockpath = self.root / ".state.lock"
        if lockpath.is_symlink():
            raise StateError("El lock de estado no puede ser un symlink.")
        descriptor = os.open(lockpath, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(descriptor, "r+b") as stream:
            try:
                if os.name == "nt":
                    import msvcrt
                    if os.fstat(stream.fileno()).st_size == 0:
                        stream.write(b"0")
                        stream.flush()
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise StateError("Otra operación está modificando el estado; reintentar después.") from exc
            try:
                yield
            finally:
                if os.name == "nt":
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def write(self, path, content):
        self.safe(self.root, path.relative_to(self.root))
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix=".cm-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)

    def write_json(self, path, value):
        self.write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")

    def brand_path(self, brand):
        return self.safe(self.root, Path("brands") / identifier(brand))

    def brand(self, brand):
        base = self.brand_path(brand)
        if not self.safe(base, "profile.json").is_file():
            raise StateError(f"No existe la marca {brand}.")
        return base

    def init_brand(self, brand, name, website=""):
        base = self.brand_path(brand)
        if base.exists():
            raise StateError("La carpeta de marca ya existe; no se sobrescribió.")
        nonempty(name, "nombre de marca")
        if website:
            url(website)
        for part in ("assets", "posts", "sources", "reports", "history"):
            (base / part).mkdir(mode=0o700, parents=True)
        profile = {
            "id": brand, "name": name, "website": website,
            "market": "Argentina", "language": "es-AR", "timezone": "America/Argentina/Buenos_Aires",
            "business": {}, "identity": {}, "voice": {}, "contact": {}, "keywords": [],
            "forbidden_words": [], "objectives": [], "social_accounts": {}, "competitors": [],
            "sources": [], "schedule": {"feed_days": ["monday", "wednesday", "friday"], "review": "weekly"},
            "notifications": {"channel": "host", "configured": False},
        }
        return self.save_profile(brand, profile, initial=True)

    def list_brands(self):
        directory = self.safe(self.root, "brands")
        if not directory.exists():
            return {"brands": []}
        entries = []
        for folder in sorted(directory.iterdir()):
            if not folder.is_dir():
                continue
            base = self.brand(folder.name)
            data = read_json(self.safe(base, "profile.json"))
            entries.append({"id": folder.name, "name": data["name"], "path": str(base)})
        return {"brands": entries}

    def profile(self, brand):
        return read_json(self.safe(self.brand(brand), "profile.json"))

    def save_profile(self, brand, patch, initial=False):
        base = self.brand_path(brand) if initial else self.brand(brand)
        current = {} if initial else self.profile(brand)
        if patch.get("id", brand) != brand:
            raise StateError("El perfil pertenece a otra marca.")
        data = merge(current, patch)
        nonempty(data.get("name"), "nombre de marca")
        try:
            ZoneInfo(data.get("timezone", ""))
        except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
            raise StateError("Zona horaria de perfil inválida.") from exc
        data.update(id=brand, revision=current.get("revision", 0) + 1, updated_at=timestamp())
        self.write_json(self.safe(base, f"history/profile-{data['revision']:04d}.json"), data)
        self.write_json(self.safe(base, "profile.json"), data)
        lines = [f"# Manual de {data['name']}", "", f"Revisión {data['revision']} · {data['updated_at']}", ""]

        def render(value, depth=2):
            if isinstance(value, dict):
                for key, child in value.items():
                    lines.extend([f"{'#' * min(depth, 6)} {key.replace('_', ' ')}", ""])
                    render(child, depth + 1)
            elif isinstance(value, list):
                if not value:
                    lines.extend(["Por completar.", ""])
                for child in value:
                    if isinstance(child, (dict, list)):
                        render(child, depth)
                    else:
                        lines.append(f"- {child}")
                lines.append("")
            else:
                lines.extend([str(value) if value not in (None, "") else "Por completar.", ""])

        render({k: v for k, v in data.items() if k not in {"revision", "updated_at", "id", "name"}})
        self.write(self.safe(base, "manual.md"), "\n".join(lines))
        return data

    def post_paths(self, brand, post):
        base = self.brand(brand)
        folder = self.safe(base, Path("posts") / identifier(post))
        return base, self.safe(base, folder.relative_to(base) / "post.json"), self.safe(base, folder.relative_to(base) / "state.json")

    def validate_post(self, base, post):
        network = post.get("network")
        if network not in {"linkedin", "instagram", "facebook", "x"}:
            raise StateError("Red no soportada.")
        url(post.get("account"))
        kind = post.get("format")
        if kind not in {"feed", "story", "reel", "carousel", "video"}:
            raise StateError("Formato no soportado.")
        if kind in {"story", "reel"} and network not in {"instagram", "facebook"}:
            raise StateError("Historias y reels sólo se planifican para Instagram/Facebook.")
        scheduled_time(post)
        if not isinstance(post.get("text"), str) or not isinstance(post.get("alt_text"), str):
            raise StateError("text y alt_text deben ser strings.")
        media = post.get("media")
        if not isinstance(media, list) or any(not isinstance(item, str) for item in media):
            raise StateError("media debe ser una lista de rutas relativas.")
        if not media and not post["text"].strip():
            raise StateError("La pieza no tiene contenido.")
        if (network == "instagram" or kind in {"reel", "video", "carousel", "story"}) and not media:
            raise StateError("Este destino/formato requiere archivos finales.")
        if kind in {"reel", "video"} and not any(Path(item).suffix.lower() in {".mp4", ".mov"} for item in media):
            raise StateError("El video requiere un archivo MP4/MOV final.")
        for item in media:
            path = self.safe(base, item)
            if not path.is_file() or path.stat().st_size == 0:
                raise StateError(f"Falta el archivo final: {item}.")

    def validate_draft(self, brand, data):
        """Persist known facts without inventing an account or publication date."""
        base = self.brand(brand)
        if data.get("network") and data["network"] not in {"linkedin", "instagram", "facebook", "x"}:
            raise StateError("Red no soportada.")
        if data.get("account"):
            url(data["account"])
        if data.get("format") and data["format"] not in {"feed", "story", "reel", "carousel", "video"}:
            raise StateError("Formato no soportado.")
        if data.get("format") in {"story", "reel"} and data.get("network") in {"linkedin", "x"}:
            raise StateError("Historias y reels sólo se planifican para Instagram/Facebook.")
        for key in ("text", "alt_text", "brief", "objective"):
            if key in data and not isinstance(data[key], str):
                raise StateError(f"{key} debe ser texto.")
        media = data.get("media", [])
        if not isinstance(media, list) or any(not isinstance(item, str) for item in media):
            raise StateError("media debe ser una lista de rutas relativas.")
        for relative in media:
            self.safe(base, relative)
        for field in ("scheduled_at", "delivery_due_at"):
            if data.get(field):
                scheduled_time({"scheduled_at": data[field],
                                "timezone": data.get("timezone") or self.profile(brand)["timezone"]})

    def load(self, brand, post, validate=True):
        base, manifest, statefile = self.post_paths(brand, post)
        if not manifest.is_file():
            raise StateError("No existe esa pieza.")
        data = read_json(manifest)
        if validate:
            self.validate_post(base, data)
        return base, data, read_json(statefile)

    def digest(self, base, data):
        assets = []
        for relative in data["media"]:
            sha = hashlib.sha256()
            with self.safe(base, relative).open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    sha.update(chunk)
            assets.append({"path": relative, "sha256": sha.hexdigest()})
        canonical = json.dumps({"post": data, "media": assets}, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def save_state(self, brand, post, state, action, **details):
        _, _, path = self.post_paths(brand, post)
        state.setdefault("events", []).append({"at": timestamp(), "action": action, **details})
        state["updated_at"] = timestamp()
        self.write_json(path, state)
        return state

    def stage(self, brand, post, data):
        self.validate_post(self.brand(brand), data)
        return self.save_package(brand, post, data, complete=True)

    def draft(self, brand, post, data):
        self.validate_draft(brand, data)
        return self.save_package(brand, post, data, complete=False)

    def save_package(self, brand, post, data, complete):
        base, manifest, statefile = self.post_paths(brand, post)
        previous = read_json(statefile) if statefile.exists() else {"events": []}
        if previous.get("state") in {"in_flight", "published", "scheduled", "uncertain", "blocked"}:
            raise StateError("Resolver el estado anterior antes de reemplazar esa pieza; usar otro ID para otra publicación.")
        self.write_json(manifest, data)
        previous.update(state="pending_approval" if complete else "draft", approval=None)
        self.save_state(brand, post, previous, "stage" if complete else "draft")
        if complete:
            return self.review(brand, post)
        return {"brand_id": brand, "post_id": post, "state": "draft", "post": data,
                "path": str(manifest), "notice": "Borrador local; completar y ejecutar stage antes de revisar y aprobar."}

    def review(self, brand, post):
        base, data, state = self.load(brand, post)
        return {"brand_id": brand, "post_id": post, "review_sha": self.digest(base, data),
                "post": data, "state": state["state"], "path": str(base / "posts" / post)}

    def approve(self, brand, post, review_sha, evidence, by):
        nonempty(evidence, "evidencia del mensaje humano")
        nonempty(by, "persona que aprobó")
        base, data, state = self.load(brand, post)
        if state["state"] not in {"pending_approval", "approved", "cancelled"}:
            raise StateError("La pieza tiene una operación sin resolver o ya ejecutada.")
        current = self.digest(base, data)
        if review_sha != current:
            raise StateError("La vista revisada cambió; presentar la versión actual al usuario.")
        state.update(state="approved", approval={"review_sha": current, "by": by, "evidence": evidence, "at": timestamp()})
        return self.save_state(brand, post, state, "approve", review_sha=current)

    def revoke(self, brand, post, reason):
        nonempty(reason, "motivo")
        _, _, state = self.load(brand, post, validate=False)
        if state["state"] in {"published", "scheduled", "in_flight", "uncertain", "blocked"}:
            raise StateError("La operación ya fue enviada o está en curso; comprobar/cancelar en la red primero.")
        state.update(state="cancelled", approval=None)
        return self.save_state(brand, post, state, "revoke", reason=reason)

    def cancel_scheduled(self, brand, post, evidence):
        nonempty(evidence, "evidencia de cancelación en la plataforma")
        _, _, state = self.load(brand, post, validate=False)
        if state["state"] != "scheduled":
            raise StateError("No hay una programación remota confirmada para cancelar.")
        state.update(state="cancelled", approval=None)
        return self.save_state(brand, post, state, "cancel-scheduled", evidence=evidence)

    def check(self, brand, post, mode="publish"):
        base, data, state = self.load(brand, post)
        if state["state"] != "approved" or not state.get("approval"):
            raise StateError(f"La pieza no está disponible para ejecutar: {state['state']}.")
        if self.digest(base, data) != state["approval"]["review_sha"]:
            raise StateError("La pieza o sus archivos cambiaron después de aprobarse.")
        at = scheduled_time(data)
        now = datetime.now(timezone.utc)
        if mode == "schedule":
            if at <= now:
                raise StateError("La programación remota requiere una fecha futura.")
        elif mode == "publish":
            if not at <= now <= at + timedelta(minutes=60):
                raise StateError("Fuera de la ventana aprobada (horario hasta +60 minutos); reprogramar y aprobar.")
        else:
            raise StateError("Modo inválido.")
        return {"ready": True, "brand_id": brand, "post_id": post, "mode": mode,
                "review_sha": state["approval"]["review_sha"], "post": data}

    def begin(self, brand, post, mode):
        ready = self.check(brand, post, mode)
        _, _, state = self.load(brand, post)
        state.update(state="in_flight", attempt={"at": timestamp(), "mode": mode, "review_sha": ready["review_sha"]})
        self.save_state(brand, post, state, "begin", mode=mode)
        return {**ready, "state": "in_flight", "notice": "Reserva local: todavía no se publicó ni programó en la red."}

    def record(self, brand, post, status, evidence, result_url=None, reconciled=False):
        nonempty(evidence, "evidencia externa")
        if result_url:
            url(result_url)
        base, data, state = self.load(brand, post, validate=False)
        if reconciled and (state["state"] != "uncertain" or status not in {"published", "scheduled"}):
            raise StateError("--reconciled sólo cierra un resultado incierto tras verificar publicación/programación remota.")
        if status not in {"published", "scheduled", "uncertain", "blocked"}:
            raise StateError("Resultado inválido.")
        verifying_schedule = state["state"] == "scheduled" and status in {"published", "uncertain"}
        verifying_block = state["state"] == "blocked" and status in {"published", "scheduled", "uncertain"}
        if state["state"] not in {"in_flight", "uncertain"} and not verifying_schedule and not verifying_block:
            raise StateError("No hay una operación reservada para registrar ese resultado.")
        attempt = state.get("attempt", {})
        if status == "scheduled" and attempt.get("mode") != "schedule" and not reconciled:
            raise StateError("La operación no reservó programación remota.")
        # A scheduled item may have appeared immediately, so published is valid for either mode.
        try:
            changed = self.digest(base, data) != attempt.get("review_sha")
        except (StateError, OSError, KeyError, TypeError):
            changed = True
        result = {"status": status, "evidence": evidence, "url": result_url, "at": timestamp(),
                  "local_changed": changed, "attempt_review_sha": attempt.get("review_sha"), "reconciled": reconciled}
        if changed and status in {"published", "scheduled"} and not reconciled:
            result["reported_status"] = status
            result["status"] = "uncertain"
            result["warning"] = "El paquete cambió durante la operación; reconciliar la versión enviada."
        if changed:
            state["approval"] = None
        if changed and reconciled:
            result["warning"] = "Resultado remoto verificado; el paquete local modificado no quedó aprobado."
        state.update(state=result["status"], result=result)
        return self.save_state(brand, post, state, "record", result=result)

    def resolve(self, brand, post, outcome, evidence):
        nonempty(evidence, "evidencia de reconciliación")
        base, data, state = self.load(brand, post, validate=False)
        if outcome != "not-published" or state["state"] not in {"in_flight", "uncertain", "blocked"}:
            raise StateError("Sólo se reconcilian operaciones pendientes con evidencia de que no se enviaron.")
        approval = state.get("approval")
        try:
            unchanged = approval and approval["review_sha"] == self.digest(base, data)
        except (StateError, OSError, KeyError, TypeError):
            unchanged = False
        state.update(state="approved" if unchanged else "pending_approval",
                     approval=approval if unchanged else None, attempt=None)
        return self.save_state(brand, post, state, "resolve", outcome=outcome, evidence=evidence)

    def due(self, brand=None):
        brands = [brand] if brand else [entry["id"] for entry in self.list_brands()["brands"]]
        items = []
        now = datetime.now(timezone.utc)
        for name in brands:
            base = self.brand(name)
            for directory in sorted(self.safe(base, "posts").iterdir()):
                if not directory.is_dir():
                    continue
                try:
                    _, data, state = self.load(name, directory.name, validate=False)
                    if state["state"] == "draft":
                        self.validate_draft(name, data)
                        items.append({"brand_id": name, "post_id": directory.name, "state": "draft", "ready": False,
                                      "reason": "Borrador pendiente; ejecutar stage con cuenta, archivos finales y fecha de publicación para revisión.",
                                      "delivery_due_at": data.get("delivery_due_at")})
                        continue
                    self.validate_post(base, data)
                    if state["state"] == "published":
                        continue
                    at = scheduled_time(data)
                    if at > now and state["state"] == "approved":
                        continue
                    item = {"brand_id": name, "post_id": directory.name, "state": state["state"],
                            "scheduled_at": data["scheduled_at"], "ready": False}
                    try:
                        item["ready"] = self.check(name, directory.name)["ready"]
                    except StateError as exc:
                        item["reason"] = str(exc)
                    items.append(item)
                except (StateError, OSError, ValueError) as exc:
                    items.append({"brand_id": name, "post_id": directory.name, "ready": False, "state": "invalid", "reason": str(exc)})
        return {"items": items, "notice": "Lectura local; no publica ni crea tareas programadas."}
