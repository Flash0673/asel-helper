import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app import WineDetectionApp


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
}

CONTENT_TYPE_SUFFIX = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
}

MAX_IMAGE_BYTES = 15 * 1024 * 1024


class WineInfo(BaseModel):
    название: Optional[str] = None
    производитель: Optional[str] = None
    категория: Optional[str] = None
    виноград: Optional[str] = None
    крепость: Optional[str] = None
    регион: Optional[str] = None
    год: Optional[int] = None
    цвет: Optional[str] = None
    температура: Optional[str] = None
    характер: Optional[str] = None


class Recognition(BaseModel):
    name: Optional[str] = None
    grape_variety: Optional[str] = None


class AnalyzeResponse(BaseModel):
    recognition: Recognition
    match_type: str = Field(
        description="exact_match, same_grape или fallback_all"
    )
    основное: Optional[WineInfo] = None
    дополнительное: Optional[WineInfo] = None


app = FastAPI(
    title="Wine Detection API",
    version="1.0.0",
)

detector = WineDetectionApp()


def _image_suffix(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix.lower()

    if suffix in ALLOWED_EXTENSIONS:
        return suffix

    return CONTENT_TYPE_SUFFIX.get(
        (upload.content_type or "").lower(),
        "",
    )


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Распознать вино по фотографии бутылки",
)
async def analyze(
    image: UploadFile = File(
        ...,
        description="Фотография бутылки",
    ),
) -> AnalyzeResponse:

    suffix = _image_suffix(image)

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Нужно изображение JPG, PNG, WEBP или BMP",
        )

    data = await image.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Файл пустой",
        )

    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Файл больше 15 МБ",
        )

    fd, temp_name = tempfile.mkstemp(suffix=suffix)
    image_path = Path(temp_name)

    try:
        with os.fdopen(fd, "wb") as temp_file:
            temp_file.write(data)

        result = await asyncio.to_thread(
            detector.process,
            str(image_path),
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    finally:
        image_path.unlink(missing_ok=True)

    return AnalyzeResponse.model_validate(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
