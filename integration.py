"""Thin adapter that joins the original frontend and backend without changing them."""
import sys
from pathlib import Path

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "wine_detection"
FRONTEND_PUBLIC = ROOT / "svoe-vino-scanner" / ".output" / "public"
sys.path.insert(0, str(BACKEND))

from api import app, _analyze_full, detector  # noqa: E402


@app.post("/api/scan")
async def scan(image: UploadFile) -> dict:
    result = await _analyze_full(image)

    # Slug для найденного вина вычисляет backend (WineCatalog).
    slug = detector.resolve_slug(result)
    if slug:
        return {"found": True, "wine": {"slug": slug}}

    grape = (result.get("recognition") or {}).get("grape_variety")
    return {"found": False, "profile": {"grapes": [grape] if grape else []}}


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    index = FRONTEND_PUBLIC / "index.html"
    if not index.is_file():
        raise HTTPException(status_code=503, detail="Фронтенд не собран. Запустите python run.py")
    candidate = (FRONTEND_PUBLIC / path).resolve()
    try:
        candidate.relative_to(FRONTEND_PUBLIC.resolve())
    except ValueError:
        raise HTTPException(status_code=404)
    if candidate.is_file():
        return FileResponse(candidate)
    if path.startswith("api/") or Path(path).suffix:
        raise HTTPException(status_code=404)
    return FileResponse(index)
