import os, json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_FILE = Path("data/drawings.json")

@app.get("/api/drawings")
def get_drawings():
    if not DATA_FILE.exists():
        return {"drawings": [], "markers": {}}
    drawings = json.loads(DATA_FILE.read_text())
    all_markers = {}
    for di, d in enumerate(drawings):
        for duct_id, pos in d["markers"].items():
            if duct_id not in all_markers:
                all_markers[duct_id] = []
            all_markers[duct_id].append({"x": pos["x"], "y": pos["y"], "di": di})
    return {
        "drawings": [{"name": d["name"], "img": d["img"], "count": d["count"]} for d in drawings],
        "markers":  all_markers
    }

@app.get("/", response_class=HTMLResponse)
def viewer_page():
    return open("static/index.html").read()
