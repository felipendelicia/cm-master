"""Contract tests using isolated data and the public CLI, never real accounts."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

CLI = Path(__file__).resolve().parents[1] / "skills/cm-master/scripts/cm.py"


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "private"
        self.call("init-brand", "faro", "--name", "Faro ficticio")
        self.brand = self.root / "brands/faro"
        (self.brand / "assets/test.png").write_bytes(b"fictional-image-v1")
        self.payload = {
            "network": "x", "account": "https://x.com/faro_ficticio",
            "format": "feed", "text": "Una idea para hoy", "alt_text": "Diseño de prueba",
            "scheduled_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
            "timezone": "UTC", "media": ["assets/test.png"],
        }

    def call(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(CLI), "--root", str(self.root), *args],
                           capture_output=True, text=True)
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr or p.stdout)
            return json.loads(p.stdout)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        return p.stderr + p.stdout

    def stage(self, **changes):
        self.payload.update(changes)
        spec = Path(self.tmp.name) / "post.json"
        spec.write_text(json.dumps(self.payload), encoding="utf-8")
        return self.call("stage", "faro", "p1", "--file", str(spec))

    def approve(self):
        review = self.call("review", "faro", "p1")
        self.call("approve", "faro", "p1", "--review-sha", review["review_sha"],
                  "--by", "Humano de prueba", "--evidence", "Mensaje ficticio: aprobada p1")
        return review

    def test_brand_isolation_and_manual_history(self):
        self.call("init-brand", "rio", "--name", "Río ficticio")
        patch = Path(self.tmp.name) / "profile.json"
        patch.write_text(json.dumps({"contact": {"phone": "TEL-FICTICIO"}}))
        self.call("profile", "faro", "--file", str(patch))
        self.assertNotIn("TEL-FICTICIO", json.dumps(self.call("profile", "rio")))
        self.assertIn("TEL-FICTICIO", (self.brand / "manual.md").read_text())
        self.assertTrue(list((self.brand / "history").glob("profile-*.json")))

    def test_needs_review_and_explicit_approval(self):
        self.stage()
        self.call("check", "faro", "p1", ok=False)
        self.approve()
        self.assertTrue(self.call("check", "faro", "p1")["ready"])

    def test_stale_review_cannot_be_approved(self):
        self.stage()
        sha = self.call("review", "faro", "p1")["review_sha"]
        self.stage(text="Texto distinto")
        self.call("approve", "faro", "p1", "--review-sha", sha,
                  "--by", "Humano", "--evidence", "Un mensaje viejo", ok=False)

    def test_asset_changes_invalidate_approval(self):
        self.stage()
        self.approve()
        (self.brand / "assets/test.png").write_bytes(b"fictional-image-v2")
        self.call("check", "faro", "p1", ok=False)

    def test_manifest_changes_invalidate_approval(self):
        self.stage()
        self.approve()
        path = self.brand / "posts/p1/post.json"
        item = json.loads(path.read_text())
        item["account"] = "https://x.com/otra_ficticia"
        path.write_text(json.dumps(item))
        self.call("check", "faro", "p1", ok=False)

    def test_revoke_prevents_execution(self):
        self.stage()
        self.approve()
        self.call("revoke", "faro", "p1", "--reason", "El usuario canceló")
        self.call("begin", "faro", "p1", ok=False)

    def test_begin_reserves_once_and_uncertain_requires_reconciliation(self):
        self.stage()
        self.approve()
        self.call("begin", "faro", "p1")
        self.call("begin", "faro", "p1", ok=False)
        self.call("record", "faro", "p1", "--status", "uncertain", "--evidence", "Corte tras enviar")
        self.call("begin", "faro", "p1", ok=False)
        self.call("resolve", "faro", "p1", "--outcome", "not-published",
                  "--evidence", "Se comprobó la cuenta y no existe la publicación")
        self.call("begin", "faro", "p1")

    def test_published_and_scheduled_cannot_repeat(self):
        self.stage()
        self.approve()
        self.call("begin", "faro", "p1")
        self.call("record", "faro", "p1", "--status", "published",
                  "--evidence", "Visible en perfil ficticio", "--url", "https://x.com/faro_ficticio/status/123")
        self.call("begin", "faro", "p1", ok=False)
        self.call("resolve", "faro", "p1", "--outcome", "not-published", "--evidence", "Incorrecto", ok=False)
        self.call("stage", "faro", "p1", "--file", str(Path(self.tmp.name) / "post.json"), ok=False)

    def test_scheduled_needs_external_evidence_and_claim(self):
        future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        self.stage(scheduled_at=future)
        self.approve()
        self.call("check", "faro", "p1", ok=False)
        self.call("record", "faro", "p1", "--status", "scheduled", "--evidence", "Hay una fecha", ok=False)
        self.call("begin", "faro", "p1", "--mode", "schedule")
        self.call("record", "faro", "p1", "--status", "scheduled", "--evidence", "Servicio confirmó id 123")
        self.call("begin", "faro", "p1", "--mode", "schedule", ok=False)

    def test_rejects_naive_dates_wrong_offsets_and_unsupported_formats(self):
        for changes in [
            {"scheduled_at": "2026-11-01T09:00:00"},
            {"scheduled_at": "2026-11-01T09:00:00+00:00", "timezone": "America/Argentina/Buenos_Aires"},
            {"format": "story", "network": "linkedin"},
        ]:
            data = dict(self.payload, **changes)
            spec = Path(self.tmp.name) / "invalid.json"
            spec.write_text(json.dumps(data))
            self.call("stage", "faro", "invalid", "--file", str(spec), ok=False)

    def test_expired_time_needs_reapproval(self):
        self.stage(scheduled_at=(datetime.now(timezone.utc) - timedelta(hours=2)).isoformat())
        self.approve()
        self.call("check", "faro", "p1", ok=False)
        due = self.call("due")
        self.assertTrue(any(x["post_id"] == "p1" and not x["ready"] for x in due["items"]))

    def test_rejects_traversal_and_cross_brand_symlink(self):
        self.call("init-brand", "../escape", "--name", "No", ok=False)
        outside = Path(self.tmp.name) / "outside.png"
        outside.write_bytes(b"private")
        (self.brand / "assets/link.png").symlink_to(outside)
        for path in ["../rio/private.png", "assets/link.png", str(outside)]:
            spec = Path(self.tmp.name) / "bad-path.json"
            spec.write_text(json.dumps(dict(self.payload, media=[path])))
            self.call("stage", "faro", "escape", "--file", str(spec), ok=False)

    def test_dry_queue_never_claims_remote_scheduling(self):
        self.stage()
        self.approve()
        items = self.call("due", "--brand", "faro")["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["state"], "approved")
        self.assertTrue(items[0]["ready"])

    def scheduled_post(self):
        self.stage(scheduled_at=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat())
        self.approve()
        self.call("begin", "faro", "p1", "--mode", "schedule")
        self.call("record", "faro", "p1", "--status", "scheduled", "--evidence", "Servicio confirmó id 123")

    def test_scheduled_post_can_be_verified_published_without_resending(self):
        self.scheduled_post()
        result = self.call("record", "faro", "p1", "--status", "published", "--evidence", "Se verificó id 123 publicado")
        self.assertEqual(result["state"], "published")

    def test_remote_cancellation_requires_its_own_evidence(self):
        self.stage()
        self.call("cancel-scheduled", "faro", "p1", "--evidence", "Todavía no se programó", ok=False)
        self.scheduled_post()
        self.call("revoke", "faro", "p1", "--reason", "No cancela remoto", ok=False)
        result = self.call("cancel-scheduled", "faro", "p1", "--evidence", "El servicio confirmó cancelación id 123")
        self.assertEqual(result["state"], "cancelled")
        self.call("begin", "faro", "p1", ok=False)

    def test_result_evidence_survives_missing_media_after_begin(self):
        self.stage()
        self.approve()
        self.call("begin", "faro", "p1")
        (self.brand / "assets/test.png").unlink()
        result = self.call("record", "faro", "p1", "--status", "uncertain", "--evidence", "Se cortó la red después de enviar")
        self.assertEqual(result["state"], "uncertain")
        self.assertIn("cortó", result["result"]["evidence"])

    def test_parallel_begin_only_one_process_can_reserve(self):
        self.stage()
        self.approve()
        command = [sys.executable, str(CLI), "--root", str(self.root), "begin", "faro", "p1"]
        children = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for child in children:
            child.communicate(timeout=15)
        self.assertEqual(sorted(child.returncode for child in children), [0, 1])

    def test_blocked_attempt_cannot_bypass_reconciliation_by_revoking(self):
        self.stage()
        self.approve()
        self.call("begin", "faro", "p1")
        self.call("record", "faro", "p1", "--status", "blocked", "--evidence", "Editor dejó de responder")
        self.call("revoke", "faro", "p1", "--reason", "Quiero volver a intentar", ok=False)
        self.call("approve", "faro", "p1", "--review-sha", self.call("review", "faro", "p1")["review_sha"],
                  "--by", "Humano", "--evidence", "No reconcilia por sí solo", ok=False)

    def test_verified_remote_result_can_close_changed_local_package(self):
        self.stage(scheduled_at=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat())
        self.approve()
        self.call("begin", "faro", "p1", "--mode", "schedule")
        (self.brand / "assets/test.png").unlink()
        first = self.call("record", "faro", "p1", "--status", "scheduled", "--evidence", "Servicio aceptó id 456")
        self.assertEqual(first["state"], "uncertain")
        closed = self.call("record", "faro", "p1", "--status", "scheduled", "--reconciled",
                           "--evidence", "Se abrió id 456 y se verificaron cuenta, medios, copy y fecha remotos")
        self.assertEqual(closed["state"], "scheduled")
        self.assertIsNone(closed["approval"])
        self.assertTrue(closed["result"]["local_changed"])
        self.call("cancel-scheduled", "faro", "p1", "--evidence", "El servicio confirmó cancelación id 456")

    def test_draft_can_preserve_delivery_deadline_without_inventing_account_or_publish_date(self):
        spec = Path(self.tmp.name) / "draft.json"
        spec.write_text(json.dumps({"network": "instagram", "format": "feed", "text": "Para revisar",
                                    "media": ["assets/test.png"], "delivery_due_at": "2026-11-01T11:00:00-03:00"}))
        draft = self.call("draft", "faro", "idea1", "--file", str(spec))
        self.assertEqual(draft["state"], "draft")
        saved = json.loads((self.brand / "posts/idea1/post.json").read_text())
        self.assertNotIn("account", saved)
        self.assertNotIn("scheduled_at", saved)
        self.assertEqual(self.call("due")["items"][0]["state"], "draft")
        self.call("begin", "faro", "idea1", ok=False)

    def test_unrelated_metadata_files_do_not_break_brand_and_post_listing(self):
        (self.root / "brands/.DS_Store").write_bytes(b"finder metadata")
        self.stage()
        (self.brand / "posts/.DS_Store").write_bytes(b"finder metadata")
        self.assertEqual(len(self.call("list-brands")["brands"]), 1)
        items = self.call("due")["items"]
        self.assertEqual([item["post_id"] for item in items], ["p1"])

    def test_blocked_attempt_can_close_a_later_verified_publication_without_retry(self):
        self.stage()
        self.approve()
        self.call("begin", "faro", "p1")
        self.call("record", "faro", "p1", "--status", "blocked", "--evidence", "No se pudo abrir el comprobante")
        result = self.call("record", "faro", "p1", "--status", "published", "--evidence", "Se encontró y verificó la pieza en la cuenta")
        self.assertEqual(result["state"], "published")
        self.call("begin", "faro", "p1", ok=False)


if __name__ == "__main__":
    unittest.main()
