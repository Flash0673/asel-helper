"""Thin adapter that joins the original frontend and backend without changing them."""
import math
import sys
from pathlib import Path

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "wine_detection"
FRONTEND_PUBLIC = ROOT / "svoe-vino-scanner" / ".output" / "public"
sys.path.insert(0, str(BACKEND))

from api import app, analyze, detector  # noqa: E402
from config import (  # noqa: E402
    CATEGORY_COLUMN,
    COLOR_COLUMN,
    GRAPE_COLUMN,
    MANUFACTURER_COLUMN,
    REGION_COLUMN,
    STRENGTH_COLUMN,
    TEMPERATURE_COLUMN,
    TITLE_COLUMN,
)


def _clean(value) -> str:
    """Normalize catalog/model values for safe comparison."""
    if value is None:
        return ""
    try:
        if math.isnan(value):
            return ""
    except (TypeError, ValueError):
        pass
    return detector.catalog.normalize(str(value))


def _slug_for_wine(wine) -> str | None:
    """Resolve the exact catalog row selected by the original backend."""
    if wine is None or not getattr(wine, "название", None):
        return None

    catalog = detector.catalog
    title = wine.название
    matches = catalog.df[
        catalog.df["_normalized_title"] == catalog.normalize(title)
    ].copy()

    if matches.empty or "slug" not in matches.columns:
        return None

    # Titles are not unique in the catalog. Narrow the candidates using the
    # fields already returned by the original backend, without changing it.
    checks = (
        (MANUFACTURER_COLUMN, getattr(wine, "производитель", None)),
        (CATEGORY_COLUMN, getattr(wine, "категория", None)),
        (GRAPE_COLUMN, getattr(wine, "виноград", None)),
        (STRENGTH_COLUMN, getattr(wine, "крепость", None)),
        (REGION_COLUMN, getattr(wine, "регион", None)),
        (COLOR_COLUMN, getattr(wine, "цвет", None)),
        (TEMPERATURE_COLUMN, getattr(wine, "температура", None)),
    )

    for column, expected in checks:
        if not expected or column not in matches.columns or len(matches) <= 1:
            continue
        expected_normalized = _clean(expected)
        narrowed = matches[matches[column].apply(_clean) == expected_normalized]
        if not narrowed.empty:
            matches = narrowed

    slug = matches.iloc[0]["slug"]
    if slug is None or _clean(slug) in {"", "nan"}:
        return None
    return str(slug)


@app.post("/api/scan")
async def scan(image: UploadFile) -> dict:
    result = await analyze(image)

    # The original backend can return a usable primary recommendation for
    # exact_match, same_grape and fallback_all. The frontend only needs its
    # catalog slug to open the wine card.
    if result.основное is not None:
        primary = result.основное
        slug = _slug_for_wine(primary)
        if slug:
            return {"found": True, "wine": {"slug": slug}}

    grape = result.recognition.grape_variety
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
