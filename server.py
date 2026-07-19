"""Zero-dependency development server for Knowledge in Bloom."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
SAVE = ROOT / "garden-save.json"

def catalogue():
    def discover(folder):
        return [{"id": p.parent.name, "icon": p.relative_to(ROOT).as_posix()}
                for p in sorted((ROOT / folder).glob("*/icon.png"))]
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
        if self.path == "/api/save":
            return self.send_json(json.loads(SAVE.read_text()) if SAVE.exists() else None)
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/backgrounds":
            return self.import_background()
        if self.path != "/api/save": return self.send_error(404)
        size = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(size))
        if data.get("save_version") != 1: return self.send_error(400, "Unsupported save version")
        SAVE.write_text(json.dumps(data, indent=2) + "\n")
        self.send_json({"saved": True})

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
