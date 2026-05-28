import os, re, json, base64, shutil
from pathlib import Path
from typing import Optional

import fitz  # pymupdf
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# ─── Config ───────────────────────────────────────────
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "sublime2024")
DATA_FILE      = Path("data/drawings.json")
DUCT_RE        = re.compile(r'^\d{2}-\d{4}[A-Z]?(-[A-Z0-9]+)*$')
RENDER_SCALE   = 1.5
JPEG_QUALITY   = 75

app = FastAPI()
security = HTTPBasic()

DATA_FILE.parent.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps([]))


# ─── Auth ─────────────────────────────────────────────
def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    ok = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not ok:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})
    return credentials.username


# ─── PDF Processing ───────────────────────────────────
def process_pdf(pdf_bytes: bytes, name: str) -> dict:
    doc  = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    mat  = fitz.Matrix(RENDER_SCALE, RENDER_SCALE)
    pix  = page.get_pixmap(matrix=mat)
    PW, PH = page.rect.width, page.rect.height

    markers = {}
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                t = span["text"].strip()
                if not DUCT_RE.match(t) or t in markers:
                    continue
                b = span["bbox"]
                markers[t] = {
                    "x": round((b[0]+b[2])/2/PW, 4),
                    "y": round((b[1]+b[3])/2/PH, 4)
                }

    img_b64 = base64.b64encode(pix.tobytes("jpeg", jpg_quality=JPEG_QUALITY)).decode()
    return {
        "name":    name,
        "img":     f"data:image/jpeg;base64,{img_b64}",
        "markers": markers,
        "count":   len(markers)
    }


def load_drawings():
    return json.loads(DATA_FILE.read_text())

def save_drawings(drawings):
    DATA_FILE.write_text(json.dumps(drawings))


# ─── Admin Routes ─────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse)
def admin_page(user=Depends(check_admin)):
    drawings = load_drawings()
    rows = ""
    for i, d in enumerate(drawings):
        rows += f"""
        <tr>
          <td>{d['name']}</td>
          <td>{d['count']} ducts</td>
          <td>
            <form method="post" action="/admin/delete/{i}" style="display:inline">
              <button class="btn-del" onclick="return confirm('Delete {d[\'name\']}?')">Delete</button>
            </form>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Duct Viewer — Admin</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:system-ui,sans-serif;background:#0f172a;color:#f1f5f9;min-height:100vh;}}
.hdr{{background:#1e293b;padding:16px 24px;border-bottom:1px solid #334155;display:flex;align-items:center;gap:12px;}}
.hdr h1{{font-size:18px;font-weight:600;}}
.badge{{background:#1D9E75;color:#fff;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;}}
.container{{max-width:800px;margin:32px auto;padding:0 24px;}}
.card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px;margin-bottom:24px;}}
.card h2{{font-size:15px;font-weight:600;margin-bottom:16px;color:#94a3b8;letter-spacing:0.05em;}}
.upload-area{{border:2px dashed #334155;border-radius:8px;padding:32px;text-align:center;cursor:pointer;transition:border-color 0.2s;}}
.upload-area:hover{{border-color:#1D9E75;}}
.upload-area p{{color:#64748b;font-size:14px;margin-top:8px;}}
input[type=file]{{display:none;}}
input[type=text]{{width:100%;padding:10px 14px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#f1f5f9;font-size:14px;outline:none;margin-bottom:12px;}}
input[type=text]:focus{{border-color:#1D9E75;}}
.btn{{padding:10px 20px;border-radius:8px;border:none;cursor:pointer;font-size:14px;font-weight:600;}}
.btn-primary{{background:#1D9E75;color:#fff;width:100%;}}
.btn-del{{background:#7f1d1d;color:#fca5a5;border:none;padding:5px 12px;border-radius:6px;cursor:pointer;font-size:12px;}}
.btn-del:hover{{background:#ef4444;color:#fff;}}
table{{width:100%;border-collapse:collapse;}}
th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #334155;font-size:13px;}}
th{{color:#64748b;font-weight:500;font-size:11px;letter-spacing:0.05em;}}
.empty{{color:#475569;font-size:13px;padding:16px 0;}}
#status{{margin-top:12px;font-size:13px;color:#1D9E75;display:none;}}
.progress{{width:100%;height:4px;background:#334155;border-radius:2px;margin-top:12px;display:none;}}
.progress-bar{{height:100%;background:#1D9E75;border-radius:2px;width:0%;transition:width 0.3s;}}
</style>
</head>
<body>
<div class="hdr">
  <h1>Duct Viewer</h1>
  <span class="badge">ADMIN</span>
</div>
<div class="container">
  <div class="card">
    <h2>UPLOAD NEW DRAWING</h2>
    <div class="upload-area" onclick="document.getElementById('pdfFile').click()">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      <p>Click to select PDF</p>
      <p id="fileName" style="color:#1D9E75;margin-top:4px;"></p>
      <input type="file" id="pdfFile" accept=".pdf" onchange="document.getElementById('fileName').textContent=this.files[0]?.name||''">
    </div>
    <br>
    <input type="text" id="drawingName" placeholder="Drawing name, e.g. L2 Zone 1" />
    <button class="btn btn-primary" onclick="upload()">Process & Upload</button>
    <div class="progress" id="progress"><div class="progress-bar" id="bar"></div></div>
    <div id="status"></div>
  </div>

  <div class="card">
    <h2>DRAWINGS ({len(drawings)} total)</h2>
    {'<table><tr><th>NAME</th><th>DUCTS</th><th></th></tr>'+rows+'</table>' if drawings else '<p class="empty">No drawings uploaded yet.</p>'}
  </div>

  <div class="card" style="text-align:center;">
    <a href="/" style="color:#1D9E75;text-decoration:none;font-size:14px;">→ Open Viewer (installer view)</a>
  </div>
</div>

<script>
async function upload() {{
  const file = document.getElementById('pdfFile').files[0];
  const name = document.getElementById('drawingName').value.trim();
  if (!file) {{ alert('Select a PDF first'); return; }}
  if (!name) {{ alert('Enter a drawing name'); return; }}

  const status = document.getElementById('status');
  const progress = document.getElementById('progress');
  const bar = document.getElementById('bar');

  status.style.display = 'block';
  status.textContent = 'Processing PDF...';
  progress.style.display = 'block';
  bar.style.width = '30%';

  const fd = new FormData();
  fd.append('file', file);
  fd.append('name', name);

  try {{
    bar.style.width = '60%';
    const res = await fetch('/admin/upload', {{ method: 'POST', body: fd }});
    bar.style.width = '100%';
    const data = await res.json();
    if (res.ok) {{
      status.textContent = '✓ ' + data.count + ' ducts extracted from ' + name;
      setTimeout(() => location.reload(), 1500);
    }} else {{
      status.style.color = '#ef4444';
      status.textContent = 'Error: ' + (data.detail || 'Unknown error');
    }}
  }} catch(e) {{
    status.style.color = '#ef4444';
    status.textContent = 'Upload failed: ' + e.message;
  }}
}}
</script>
</body>
</html>"""


@app.post("/admin/upload")
async def upload_drawing(
    file: UploadFile = File(...),
    name: str = Form(...),
    user=Depends(check_admin)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted")
    pdf_bytes = await file.read()
    drawing   = process_pdf(pdf_bytes, name)
    drawings  = load_drawings()
    # Replace if same name exists
    drawings = [d for d in drawings if d["name"] != name]
    drawings.append(drawing)
    save_drawings(drawings)
    return {"count": drawing["count"], "name": name}


@app.post("/admin/delete/{index}")
def delete_drawing(index: int, user=Depends(check_admin)):
    drawings = load_drawings()
    if 0 <= index < len(drawings):
        drawings.pop(index)
        save_drawings(drawings)
    return RedirectResponse("/admin", status_code=303)


# ─── Viewer (installer) ───────────────────────────────
@app.get("/api/drawings")
def get_drawings():
    drawings = load_drawings()
    # Build global marker lookup
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
