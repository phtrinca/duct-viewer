import os, json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def find_data():
    candidates = [
        Path("data/drawings.json"),
        Path("/opt/render/project/src/data/drawings.json"),
        Path(os.path.dirname(os.path.abspath(__file__))) / "data" / "drawings.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

@app.get("/debug")
def debug():
    return {
        "cwd": os.getcwd(),
        "file_location": os.path.abspath(__file__),
        "data_exists": Path("data/drawings.json").exists(),
        "all_json": [str(p) for p in Path(".").rglob("*.json")]
    }

@app.get("/api/drawings")
def get_drawings():
    path = find_data()
    if not path:
        return JSONResponse({"drawings": [], "markers": {}})
    drawings = json.loads(path.read_text())
    all_markers = {}
    for di, d in enumerate(drawings):
        for duct_id, pos in d["markers"].items():
            if duct_id not in all_markers:
                all_markers[duct_id] = []
            all_markers[duct_id].append({"x": pos["x"], "y": pos["y"], "di": di})
    return {
        "drawings": [{"name": d["name"], "img": d["img"], "count": d["count"]} for d in drawings],
        "markers": all_markers
    }

@app.get("/", response_class=HTMLResponse)
def viewer_page():
    return open("static/index.html").read()
