import math
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from config import (
    EXCEL_PATH,
    TITLE_COLUMN,
    MANUFACTURER_COLUMN,
    REGION_COLUMN,
    CATEGORY_COLUMN,
    COLOR_COLUMN,
    PAGE_URL_COLUMN,
    RATING_COLUMN,
    TEMPERATURE_COLUMN,
    STRENGTH_COLUMN,
    GRAPE_COLUMN,
    DESCRIPTION_COLUMN,
    SIMILAR_TITLES_COLUMN,
    TOP_RECOMMENDATIONS,
)
from models.wine import WineRecommendation, WineRecognition


class WineCatalog:

    def __init__(
        self,
        excel_path: Path = EXCEL_PATH,
    ):
        self.excel_path = excel_path

        if not self.excel_path.exists():
            raise FileNotFoundError(
                f"Excel-файл не найден: {self.excel_path}"
            )

        # Читаем XLSX
        self.df = pd.read_excel(
            self.excel_path
        )

        self._validate_columns()

        # Нормализованное название
        self.df["_normalized_title"] = (
            self.df[TITLE_COLUMN]
            .fillna("")
            .astype(str)
            .apply(self.normalize)
        )

        # Нормализованный сорт
        self.df["_normalized_grape"] = (
            self.df[GRAPE_COLUMN]
            .fillna("")
            .astype(str)
            .apply(self.normalize)
        )

        # Рейтинг → число
        self.df["_rating"] = pd.to_numeric(
            self.df[RATING_COLUMN],
            errors="coerce",
        ).fillna(0)

    # ========================================================
    # ОСНОВНОЙ ПОИСК
    # ========================================================

    def find(
        self,
        recognition: WineRecognition,
    ) -> tuple[str, list[WineRecommendation]]:

        # ----------------------------------------------------
        # CASE 2:
        # GigaChat не смог определить название
        # ----------------------------------------------------

        if not self.is_valid_value(
            recognition.name
        ):

            return (
                "fallback_all",
                self.top_rated(
                    TOP_RECOMMENDATIONS
                ),
            )

        # ----------------------------------------------------
        # Ищем точное название в Excel
        # ----------------------------------------------------

        wine = self.find_by_title(
            recognition.name
        )

        if wine is not None:

            return (
                "exact_match",
                [wine],
            )

        # ----------------------------------------------------
        # CASE 1:
        # Названия нет в Excel.
        #
        # Пробуем найти вина такого же сорта.
        # ----------------------------------------------------

        if self.is_valid_value(
            recognition.grape_variety
        ):

            wines = self.top_rated_by_grape(
                recognition.grape_variety,
                TOP_RECOMMENDATIONS,
            )

            if wines:

                return (
                    "same_grape",
                    wines,
                )

        # ----------------------------------------------------
        # Если сорта тоже нет
        # → самые рейтинговые вина вообще
        # ----------------------------------------------------

        return (
            "fallback_all",
            self.top_rated(
                TOP_RECOMMENDATIONS
            ),
        )

    # ========================================================
    # ПОИСК ПО TITLE
    # ========================================================

    def find_by_title(
        self,
        title: str,
    ) -> Optional[WineRecommendation]:

        normalized_title = self.normalize(
            title
        )

        if not normalized_title:
            return None

        matches = self.df[
            self.df["_normalized_title"]
            == normalized_title
        ]

        if matches.empty:
            return None

        row = matches.iloc[0]

        return self._row_to_wine(row)

    def find_additional(
        self,
        wine: WineRecommendation,
    ) -> Optional[WineRecommendation]:

        main_title = self.normalize(wine.title)

        for title in wine.similar_titles:

            candidate = self.find_by_title(title)

            if candidate is None:
                candidate = self._find_title_contains(title)

            if (
                candidate is not None
                and self.normalize(candidate.title) != main_title
            ):
                return candidate

        if self.is_valid_value(wine.grape_variety):

            for candidate in self.top_rated_by_grape(
                wine.grape_variety,
                TOP_RECOMMENDATIONS,
            ):

                if self.normalize(candidate.title) != main_title:
                    return candidate

        for candidate in self.top_rated(TOP_RECOMMENDATIONS):

            if self.normalize(candidate.title) != main_title:
                return candidate

        return None

    def _find_title_contains(
        self,
        title: str,
    ) -> Optional[WineRecommendation]:

        normalized_title = self.normalize(title)

        if len(normalized_title) < 8:
            return None

        matches = self.df[
            self.df["_normalized_title"].str.contains(
                re.escape(normalized_title),
                regex=True,
                na=False,
            )
        ].copy()

        if matches.empty:
            return None

        matches = matches.sort_values(
            by="_rating",
            ascending=False,
        )

        return self._row_to_wine(matches.iloc[0])

    # ========================================================
    # ТОП ПО СОРТУ
    # ========================================================

    def top_rated_by_grape(
        self,
        grape_variety: str,
        limit: int = 5,
    ) -> list[WineRecommendation]:

        normalized_grape = self.normalize(
            grape_variety
        )

        if not normalized_grape:
            return []

        matches = self.df[
            self.df["_normalized_grape"]
            == normalized_grape
        ].copy()

        # Если точного совпадения нет,
        # попробуем частичное
        if matches.empty:

            matches = self.df[
                self.df["_normalized_grape"].apply(
                    lambda value:
                    normalized_grape in value
                    or value in normalized_grape
                )
            ].copy()

        if matches.empty:
            return []

        matches = matches.sort_values(
            by="_rating",
            ascending=False,
        )

        matches = matches.head(limit)

        return [
            self._row_to_wine(row)
            for _, row in matches.iterrows()
        ]

    # ========================================================
    # САМЫЕ РЕЙТИНГОВЫЕ
    # ========================================================

    def top_rated(
        self,
        limit: int = 5,
    ) -> list[WineRecommendation]:

        matches = self.df.sort_values(
            by="_rating",
            ascending=False,
        ).head(limit)

        return [
            self._row_to_wine(row)
            for _, row in matches.iterrows()
        ]

    # ========================================================
    # ROW → OBJECT
    # ========================================================

    def _row_to_wine(
        self,
        row,
    ) -> WineRecommendation:

        title = str(row[TITLE_COLUMN])

        return WineRecommendation(
            title=title,

            page_url=str(
                row[PAGE_URL_COLUMN]
            ),

            rating=float(
                row["_rating"]
            ),

            grape_variety=self._clean_value(
                row[GRAPE_COLUMN]
            ),

            manufacturer=self._clean_value(
                row[MANUFACTURER_COLUMN]
            ),

            category=self._clean_value(
                row[CATEGORY_COLUMN]
            ),

            strength=self.format_strength(
                row[STRENGTH_COLUMN]
            ),

            region=self._clean_value(
                row[REGION_COLUMN]
            ),

            year=self.extract_year(title),

            color=self._clean_value(
                row[COLOR_COLUMN]
            ),

            temperature=self._clean_value(
                row[TEMPERATURE_COLUMN]
            ),

            character=self._clean_value(
                row[DESCRIPTION_COLUMN]
            ),

            similar_titles=self._split_titles(
                row[SIMILAR_TITLES_COLUMN]
            ),
        )

    # ========================================================
    # ПРОВЕРКА КОЛОНОК
    # ========================================================

    def _validate_columns(self):

        required = {
            TITLE_COLUMN,
            MANUFACTURER_COLUMN,
            REGION_COLUMN,
            CATEGORY_COLUMN,
            COLOR_COLUMN,
            PAGE_URL_COLUMN,
            RATING_COLUMN,
            TEMPERATURE_COLUMN,
            STRENGTH_COLUMN,
            GRAPE_COLUMN,
            DESCRIPTION_COLUMN,
            SIMILAR_TITLES_COLUMN,
        }

        missing = (
            required
            - set(self.df.columns)
        )

        if missing:

            raise ValueError(
                "В Excel отсутствуют колонки: "
                + ", ".join(
                    sorted(missing)
                )
            )

    # ========================================================
    # NORMALIZE
    # ========================================================

    @staticmethod
    def normalize(
        value: str,
    ) -> str:

        if value is None:
            return ""

        value = str(value).strip().lower()

        if not value:
            return ""

        value = value.replace(
            "ё",
            "е",
        )

        value = re.sub(
            r"[\"'«»„“”]",
            "",
            value,
        )

        value = re.sub(
            r"[–—−]",
            "-",
            value,
        )

        value = re.sub(
            r"[^a-zа-я0-9]+",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # ========================================================
    # VALID VALUE
    # ========================================================

    @staticmethod
    def is_valid_value(
        value,
    ) -> bool:

        if value is None:
            return False

        if (
            isinstance(value, float)
            and math.isnan(value)
        ):
            return False

        value = str(
            value
        ).strip().lower()

        return value not in {
            "",
            "none",
            "null",
            "nan",
            "n/a",
            "na",
            "unknown",
        }

    @staticmethod
    def _clean_value(
        value,
    ):

        if not WineCatalog.is_valid_value(
            value
        ):
            return None

        return str(value).strip()

    @staticmethod
    def format_strength(value) -> Optional[str]:

        cleaned = WineCatalog._clean_value(value)

        if cleaned is None:
            return None

        if "%" in cleaned:
            return cleaned

        normalized = cleaned.replace(",", ".")

        try:
            number = float(normalized)
        except ValueError:
            return cleaned

        if 0 < number <= 1:
            number *= 100

        if number == int(number):
            return f"{int(number)}%"

        return f"{number:g}%"

    @staticmethod
    def extract_year(title: Optional[str]) -> Optional[int]:

        if not title:
            return None

        match = re.search(
            r"(?<!\d)(?:19|20)\d{2}(?!\d)",
            str(title),
        )

        if match is None:
            return None

        return int(match.group(0))

    @staticmethod
    def _split_titles(value) -> list[str]:

        cleaned = WineCatalog._clean_value(value)

        if cleaned is None:
            return []

        return [
            part.strip()
            for part in cleaned.split(",")
            if part.strip()
        ]