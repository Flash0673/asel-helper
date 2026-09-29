import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# GigaChat
# ============================================================

GIGACHAT_CREDENTIALS = os.getenv(
    "GIGACHAT_CREDENTIALS",
    "MDE5ZGY3NjMtN2U5ZS03YmRhLTgyMmYtYzM1ZjJkMDAwZjlkOjUzZGYxZTJiLTZkMzctNDU5MS05NzEyLTMxMzIxNTIxNWU0MA=="
)

GIGACHAT_SCOPE = os.getenv(
    "GIGACHAT_SCOPE",
    "GIGACHAT_API_PERS"
)

# api.giga.chat с этой сети не завершает TLS.
# Рабочий адрес — контур Сбера.
GIGACHAT_BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1"

GIGACHAT_MODEL = os.getenv(
    "GIGACHAT_MODEL",
    "GigaChat-2-Max"
)

# Пока оставляем False из-за твоей проблемы с сертификатом.
# В production лучше настроить нормальный CA и поставить True.
GIGACHAT_VERIFY_SSL = False

EXCEL_PATH = BASE_DIR / "data" / "wines.xlsx"

TITLE_COLUMN = "title"
MANUFACTURER_COLUMN = "manufacturer"
REGION_COLUMN = "region"
CATEGORY_COLUMN = "category"
COLOR_COLUMN = "color"
PAGE_URL_COLUMN = "page_url"
RATING_COLUMN = "rating"
TEMPERATURE_COLUMN = "temperature"
STRENGTH_COLUMN = "strength"
GRAPE_COLUMN = "grapes"
DESCRIPTION_COLUMN = "description"
SIMILAR_TITLES_COLUMN = "similar_wines_titles"

TOP_RECOMMENDATIONS = 5