"""Zero-dependency development server for Knowledge in Bloom."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import secrets
import shutil
import tempfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
USERS = ROOT / "users"
ACTIVE_USER = ROOT / ".active-user"
DRAFTS = ROOT / ".pack-drafts"

def safe_user_id(value):
    return value if value.startswith("usr_") and value.replace("_", "").isalnum() else None

def user_path(user_id):
    return USERS / user_id / "user.json"

def users():
    USERS.mkdir(exist_ok=True)
    result = []
    for folder in sorted(USERS.glob("usr_*")):
        path = folder / "user.json"
        if path.exists():
            data = json.loads(path.read_text())
            result.append({"user_id": folder.name,
                           "display_name": data.get("profile", {}).get("display_name", folder.name)})
    return result

def catalogue():
    def discover(folder):
        found = []
        candidates = sorted((ROOT / folder).glob("*/pack.json" if folder == "packs" else "*/icon.png"))
        # Keep supporting simple icon-only prototype folders as well as complete packs.
        if folder == "packs": candidates += [p for p in sorted((ROOT / folder).glob("*/icon.png")) if not (p.parent / "pack.json").exists()]
        for candidate in candidates:
            pack_folder = candidate.parent
            icon = pack_folder / "icon.png"
            entry = {"id": pack_folder.name, "icon": icon.relative_to(ROOT).as_posix()}
            metadata_file = pack_folder / ("pack.json" if folder == "packs" else "manifest.json")
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                if folder == "minigames":
                    entry.update(metadata)
                    entry["id"] = metadata.get("game_id", entry["id"])
                    entry["icon"] = (pack_folder / metadata.get("icon", "icon.png")).relative_to(ROOT).as_posix()
                    entry["entrypoint"] = (pack_folder / metadata["entrypoint"]).relative_to(ROOT).as_posix()
                    found.append(entry)
                    continue
                entry.update({key: metadata.get(key) for key in
                              ("pack_id", "title", "subtitle", "description", "author", "version",
                               "language", "tags", "license", "credits")})
                items = []
                for item_file in metadata.get("item_files", []):
                    items.extend(json.loads((pack_folder / item_file).read_text()))
                entry["items"] = items
            found.append(entry)
        return found
    furniture = []
    for image in sorted((ROOT / "assets/furniture").glob("level_*/*.png")):
        furniture.append({"id": image.stem, "level": int(image.parent.name.split("_")[-1]),
                          "image": image.relative_to(ROOT).as_posix()})
    flowers = [{"id": p.stem, "image": p.relative_to(ROOT).as_posix()}
               for p in sorted((ROOT / "assets/flowers").glob("*.png"))]
    backgrounds = [{"id": p.stem, "image": p.relative_to(ROOT).as_posix()}
                   for p in sorted((ROOT / "assets/backgrounds").glob("*"))
                   if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}]
    return {"packs": discover("packs"), "minigames": discover("minigames"),
            "furniture": furniture, "flowers": flowers, "backgrounds": backgrounds}

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = super().translate_path(path)
        return str(ROOT / Path(path).relative_to(Path.cwd())) if Path.cwd() != ROOT else path

    def do_GET(self):
        if self.path == "/api/catalogue": return self.send_json(catalogue())
        if self.path == "/api/users":
            return self.send_json({"users": users(), "active_user_id": ACTIVE_USER.read_text().strip() if ACTIVE_USER.exists() else None})
        if self.path.startswith("/api/save"):
            user_id = safe_user_id(self.path.partition("user=")[2])
            path = user_path(user_id) if user_id else None
            return self.send_json(json.loads(path.read_text()) if path and path.exists() else None)
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/pack-drafts":
            return self.create_pack_draft()
        match = re.fullmatch(r"/api/pack-drafts/([a-f0-9]+)/media", self.path)
        if match: return self.upload_pack_media(match.group(1))
        match = re.fullmatch(r"/api/pack-drafts/([a-f0-9]+)/save", self.path)
        if match: return self.save_pack_draft(match.group(1))
        if self.path == "/api/backgrounds":
            return self.import_background()
        if self.path == "/api/users":
            return self.create_user()
        if not self.path.startswith("/api/save"): return self.send_error(404)
        user_id = safe_user_id(self.path.partition("user=")[2])
        if not user_id: return self.send_error(400, "Invalid user ID")
        size = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(size))
        if data.get("save_version") != 1: return self.send_error(400, "Unsupported save version")
        data["user_id"] = user_id
        path = user_path(user_id); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n")
        ACTIVE_USER.write_text(user_id + "\n")
        self.send_json({"saved": True})

    def create_user(self):
        size = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(size))
        display_name = str(payload.get("display_name", "")).strip()[:60]
        if not display_name: return self.send_error(400, "Display name is required")
        import secrets
        user_id = "usr_" + secrets.token_hex(4)
        data = payload.get("save") or {}
        data.update({"user_id": user_id, "profile": {"display_name": display_name}})
        path = user_path(user_id); path.parent.mkdir(parents=True)
        path.write_text(json.dumps(data, indent=2) + "\n")
        ACTIVE_USER.write_text(user_id + "\n")
        self.send_json({"user_id": user_id, "display_name": display_name})

    def import_background(self):
        filename = Path(unquote(self.headers.get("X-Filename", "background.png"))).name
        suffix = Path(filename).suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            return self.send_error(400, "Unsupported image type")
        size = int(self.headers.get("Content-Length", 0))
        if not 0 < size <= 15 * 1024 * 1024:
            return self.send_error(400, "Image must be between 1 byte and 15 MB")
        destination = ROOT / "assets/backgrounds" / filename
        stem, counter = destination.stem, 2
        while destination.exists():
            destination = destination.with_name(f"{stem}_{counter}{suffix}")
            counter += 1
        destination.write_bytes(self.rfile.read(size))
        self.send_json({"id": destination.stem,
                        "image": destination.relative_to(ROOT).as_posix()})

    def read_json_body(self, maximum=5 * 1024 * 1024):
        size = int(self.headers.get("Content-Length", 0))
        if not 0 < size <= maximum: raise ValueError("Request is empty or too large")
        return json.loads(self.rfile.read(size))

    def create_pack_draft(self):
        try:
            payload = self.read_json_body()
            source_id = payload.get("source_id")
            if source_id:
                if not re.fullmatch(r"[A-Za-z0-9_-]+", source_id): raise ValueError("Invalid pack ID")
                source = ROOT / "packs" / source_id
                manifest = json.loads((source / "pack.json").read_text())
                items = []
                for item_file in manifest.get("item_files", []): items.extend(json.loads((source / item_file).read_text()))
                data = {"manifest": manifest, "items": items}
            else:
                raw = payload.get("data", {})
                if isinstance(raw, list): data = {"manifest": {}, "items": raw}
                elif "manifest" in raw: data = {"manifest": raw.get("manifest", {}), "items": raw.get("items", [])}
                elif "pack" in raw: data = {"manifest": raw.get("pack", {}), "items": raw.get("items", [])}
                else: data = {"manifest": raw, "items": raw.get("items", [])}
                if payload.get("name"):
                    data["manifest"]["title"] = payload["name"].strip()[:100]
                    data["manifest"]["pack_id"] = re.sub(r"[^a-z0-9_-]+", "_", payload["name"].lower()).strip("_")[:64]
            if not isinstance(data["manifest"], dict) or not isinstance(data["items"], list): raise ValueError("Pack JSON must contain a manifest and an items list")
            manifest = data["manifest"]
            manifest.setdefault("schema_version", "1.0"); manifest.setdefault("version", "1.0.0")
            manifest["item_files"] = ["items.json"]
            draft_id = secrets.token_hex(12); draft = DRAFTS / draft_id; draft.mkdir(parents=True, exist_ok=False)
            if source_id: shutil.copytree(source / "assets", draft / "assets", dirs_exist_ok=True) if (source / "assets").exists() else None
            (draft / "draft.json").write_text(json.dumps(data, indent=2) + "\n")
            self.send_json({"draft_id": draft_id, "data": data})
        except (ValueError, OSError, json.JSONDecodeError) as error:
            self.send_error(400, str(error))

    def upload_pack_media(self, draft_id):
        draft = DRAFTS / draft_id
        if not draft.is_dir(): return self.send_error(404, "Draft not found")
        field_path = self.headers.get("X-Media-Path", "")
        match = re.fullmatch(r"items\.(\d+)\.(question|answer|explanation)\.(image|audio|video)", field_path)
        if not match: return self.send_error(400, "Invalid media target")
        filename = Path(unquote(self.headers.get("X-Filename", "media"))).name
        suffix = Path(filename).suffix.lower()
        allowed = {"image": {".png", ".jpg", ".jpeg", ".webp", ".gif"}, "audio": {".mp3", ".wav", ".ogg", ".m4a"}, "video": {".mp4", ".webm", ".ogv"}}
        kind = match.group(3)
        if suffix not in allowed[kind]: return self.send_error(400, f"Unsupported {kind} type")
        size = int(self.headers.get("Content-Length", 0))
        if not 0 < size <= 30 * 1024 * 1024: return self.send_error(400, "Media must be between 1 byte and 30 MB")
        media_dir = draft / "assets" / kind; media_dir.mkdir(parents=True, exist_ok=True)
        base = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(filename).stem).strip("_") or kind
        destination = media_dir / f"{base}{suffix}"; counter = 2
        while destination.exists(): destination = media_dir / f"{base}_{counter}{suffix}"; counter += 1
        destination.write_bytes(self.rfile.read(size))
        self.send_json({"path": destination.relative_to(draft).as_posix()})

    def save_pack_draft(self, draft_id):
        draft = DRAFTS / draft_id
        if not draft.is_dir(): return self.send_error(404, "Draft not found")
        try:
            data = self.read_json_body(); manifest = data.get("manifest", {}); items = data.get("items", [])
            pack_id = str(manifest.get("pack_id", "")).strip().lower()
            if not re.fullmatch(r"[a-z0-9_-]+", pack_id): raise ValueError("Pack ID must use lowercase letters, numbers, underscores, or hyphens")
            if not str(manifest.get("title", "")).strip(): raise ValueError("Display name is required")
            if not items or any(not i.get("item_id") or not i.get("question", {}).get("text") or not i.get("answer", {}).get("text") for i in items): raise ValueError("Every question needs an ID, question, and answer")
            ids = [i["item_id"] for i in items]
            if len(ids) != len(set(ids)): raise ValueError("Question IDs must be unique")
            manifest.update({"pack_id": pack_id, "schema_version": "1.0", "item_files": ["items.json"], "icon": "icon.png"})
            staging = Path(tempfile.mkdtemp(prefix=f".{pack_id}-", dir=ROOT / "packs"))
            if (draft / "assets").exists(): shutil.copytree(draft / "assets", staging / "assets")
            icon_source = ROOT / "assets/ui/new_pack_button.png"; shutil.copy2(icon_source, staging / "icon.png")
            (staging / "pack.json").write_text(json.dumps(manifest, indent=2) + "\n")
            (staging / "items.json").write_text(json.dumps(items, indent=2) + "\n")
            destination = ROOT / "packs" / pack_id; backup = ROOT / "packs" / f".{pack_id}.backup"
            if backup.exists(): shutil.rmtree(backup)
            if destination.exists(): destination.rename(backup)
            staging.rename(destination)
            if backup.exists(): shutil.rmtree(backup)
            shutil.rmtree(draft)
            self.send_json({"saved": True, "pack_id": pack_id})
        except (ValueError, OSError, json.JSONDecodeError) as error:
            self.send_error(400, str(error))

    def send_json(self, value):
        body = json.dumps(value).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body)); self.end_headers(); self.wfile.write(body)

if __name__ == "__main__":
    print("Knowledge in Bloom: http://localhost:8000")
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
