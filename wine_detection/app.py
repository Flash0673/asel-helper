import json
import sys
from pathlib import Path

from services.gigachat_service import GigaChatService
from services.wine_catalog import WineCatalog


class WineDetectionApp:

    def __init__(self):

        self.gigachat = GigaChatService()
        self.catalog = WineCatalog()

    def process(
        self,
        image_path: str,
    ) -> dict:

        # ====================================================
        # 1. Распознаём бутылку
        # ====================================================

        recognition = self.gigachat.recognize(
            Path(image_path)
        )

        # ====================================================
        # 2. Ищем в каталоге
        # ====================================================

        match_type, recommendations = (
            self.catalog.find(recognition)
        )

        # ====================================================
        # 3. Формируем результат
        # ====================================================

        main = recommendations[0] if recommendations else None

        additional = None

        if len(recommendations) > 1:
            additional = recommendations[1]

        elif main is not None:
            additional = self.catalog.find_additional(main)

        return {
            "recognition": {
                "name": recognition.name,
                "grape_variety": recognition.grape_variety,
            },

            "match_type": match_type,

            "основное": (
                main.to_public_dict()
                if main is not None
                else None
            ),

            "дополнительное": (
                additional.to_public_dict()
                if additional is not None
                else None
            ),
        }


def main():

    if len(sys.argv) != 2:

        print(
            "Использование:\n"
            "py app.py wine1.png",
            file=sys.stderr,
        )

        sys.exit(1)

    image_path = sys.argv[1]

    try:

        app = WineDetectionApp()

        result = app.process(
            image_path
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )

    except Exception as error:

        print(
            f"Ошибка: {error}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()