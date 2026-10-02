import json
import tempfile
from pathlib import Path

from gigachat import GigaChat
from PIL import Image

from config import (
    GIGACHAT_BASE_URL,
    GIGACHAT_CREDENTIALS,
    GIGACHAT_MODEL,
    GIGACHAT_SCOPE,
    GIGACHAT_VERIFY_SSL,
)
from models.wine import WineRecognition


SYSTEM_PROMPT = """
Ты эксперт по распознаванию вина по фотографии бутылки.

Твоя задача — определить:

1. Полное название вина.
2. Основной сорт винограда.

Внимательно изучи фотографию:

- переднюю этикетку;
- заднюю этикетку;
- название производителя;
- название вина;
- регион;
- appellation;
- сорт винограда;
- другие видимые надписи.

Если сорт винограда прямо не указан, можешь определить его
по названию вина, производителю, региону и appellation.

Не выдумывай информацию.

Если название вина определить невозможно — используй null.

Если сорт винограда определить невозможно — используй null.

ОБЯЗАТЕЛЬНО ВЕРНИ ТОЛЬКО JSON:

{
  "name": "название вина или null",
  "grape_variety": "сорт винограда или null"
}

Не добавляй Markdown.
Не добавляй ```json.
Не добавляй пояснения.
Не добавляй дополнительные поля.
"""


class GigaChatService:

    def __init__(self):
        self.client = GigaChat(
            base_url=GIGACHAT_BASE_URL,
            credentials=GIGACHAT_CREDENTIALS,
            scope=GIGACHAT_SCOPE,
            model=GIGACHAT_MODEL,
            verify_ssl_certs=GIGACHAT_VERIFY_SSL,
        )

    def recognize(self, image_path: Path) -> WineRecognition:

        if not image_path.exists():
            raise FileNotFoundError(
                f"Изображение не найдено: {image_path}"
            )

        # ----------------------------------------------------
        # Upload
        # ----------------------------------------------------

        # GigaChat принимает только JPEG, PNG и BMP.
        # WebP перекодируем в PNG.
        upload_path = image_path
        temp_dir = None

        if self._needs_upload_conversion(image_path):

            temp_dir = tempfile.TemporaryDirectory(
                prefix="wine_gigachat_"
            )

            upload_path = (
                Path(temp_dir.name)
                / f"{image_path.stem}.png"
            )

            with Image.open(image_path) as image:
                image.save(upload_path, format="PNG")

        try:

            with open(upload_path, "rb") as image_file:

                uploaded_file = self.client.upload_file(
                    image_file,
                    purpose="general"
                )

        finally:

            if temp_dir is not None:
                temp_dir.cleanup()

        file_id = uploaded_file.id_

        # ----------------------------------------------------
        # Request
        # ----------------------------------------------------

        payload = {
            "model": GIGACHAT_MODEL,

            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        "Проанализируй фотографию бутылки "
                        "и определи название вина и сорт винограда."
                    ),
                    "attachments": [
                        file_id
                    ],
                },
            ],

            "temperature": 0.1,
            "stream": False,
        }

        response = self.client.chat(payload)

        raw_response = response.choices[0].message.content

        if not raw_response:
            return WineRecognition()

        raw_response = raw_response.strip()

        # ----------------------------------------------------
        # Убираем Markdown
        # ----------------------------------------------------

        if raw_response.startswith("```"):

            raw_response = (
                raw_response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        try:
            data = json.loads(raw_response)

        except json.JSONDecodeError as error:

            raise RuntimeError(
                "GigaChat вернул некорректный JSON:\n"
                f"{raw_response}"
            ) from error

        return WineRecognition(
            name=self._clean_value(
                data.get("name")
            ),
            grape_variety=self._clean_value(
                data.get("grape_variety")
            ),
        )

    @staticmethod
    def _needs_upload_conversion(image_path: Path) -> bool:
        """
        GigaChat умеет загружать только JPEG, PNG и BMP.

        Формат определяем по сигнатуре содержимого, а не по
        расширению: WebP часто лежит в файле с именем .png.
        """
        with open(image_path, "rb") as image_file:

            header = image_file.read(16)

        if header.startswith(b"\x89PNG\r\n\x1a\n"):  # PNG
            return False

        if header.startswith(b"\xff\xd8\xff"):  # JPEG
            return False

        if header.startswith(b"BM"):  # BMP
            return False

        # WebP и любые другие форматы перекодируем в PNG.
        return True

    @staticmethod
    def _clean_value(value):

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        # Модель иногда может вернуть:
        # "none", "null", "nan", "unknown"
        invalid_values = {
            "none",
            "null",
            "nan",
            "n/a",
            "na",
            "unknown",
            "неизвестно",
            "не удалось определить",
        }

        if value.lower() in invalid_values:
            return None

        return value