import asyncio
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

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
    "/v1/eval/predict",
    summary="Распознать вино по фотографии бутылки",
)
async def analyze(
    image: UploadFile = File(
        ...,
        description="Фотография бутылки",
    ),
) -> dict:

    result = await _analyze_full(image)

    return {
        "slug": detector.resolve_slug(result),
    }


async def _analyze_full(image: UploadFile) -> dict:
    """
    Полный результат анализа изображения.

    Используется интеграционным слоем; публичный endpoint
    /v1/eval/predict возвращает только slug.
    """

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

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
