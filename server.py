"""Zero-dependency development server for Knowledge in Bloom."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
USERS = ROOT / "users"
ACTIVE_USER = ROOT / ".active-user"

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
        for icon in sorted((ROOT / folder).glob("*/icon.png")):
            entry = {"id": icon.parent.name, "icon": icon.relative_to(ROOT).as_posix()}
            metadata_file = icon.parent / ("pack.json" if folder == "packs" else "manifest.json")
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                if folder == "minigames":
                    entry.update(metadata)
                    entry["id"] = metadata.get("game_id", entry["id"])
                    entry["icon"] = (icon.parent / metadata.get("icon", "icon.png")).relative_to(ROOT).as_posix()
                    entry["entrypoint"] = (icon.parent / metadata["entrypoint"]).relative_to(ROOT).as_posix()
                    found.append(entry)
                    continue
                entry.update({key: metadata.get(key) for key in
                              ("pack_id", "title", "subtitle", "description", "author", "version",
                               "language", "tags", "license", "credits")})
                items = []
                for item_file in metadata.get("item_files", []):
                    items.extend(json.loads((icon.parent / item_file).read_text()))
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

    def send_json(self, value):
        body = json.dumps(value).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body)); self.end_headers(); self.wfile.write(body)

if __name__ == "__main__":
    print("Knowledge in Bloom: http://localhost:8000")
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
