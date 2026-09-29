"""Rebuild: python scripts/import_catalog.py wines.xlsx (requires openpyxl).

Vintage is extracted only when the title contains exactly one four-digit year.
"""
import json
import re
import sys
from pathlib import Path
import openpyxl

def text(value):
    return str(value).strip() if value is not None else ''

def split(value):
    return [part.strip() for part in text(value).split(',') if part.strip()]

def strength(value):
    if isinstance(value, (int, float)):
        return f'{value * 100 if value < 1 else value:g}'.replace('.', ',') + '%'
    return text(value).replace('.', ',')

workbook = openpyxl.load_workbook(Path(sys.argv[1]), read_only=True, data_only=True)
rows = workbook.active.iter_rows(values_only=True)
headers = next(rows)
wines = []
for row in rows:
    item = dict(zip(headers, row))
    if not item.get('slug'):
        continue
    title = text(item['title'])
    years = re.findall(r'\b(?:19|20)\d{2}\b', title)
    wines.append({
        'slug': text(item['slug']), 'name': title,
        'winery': text(item['manufacturer']), 'region': text(item['region']),
        'category': text(item['category']), 'color': text(item['color']),
        'vintage': int(years[0]) if len(years) == 1 else None,
        'rating': item['rating'], 'image': text(item['bottle_image_url']),
        'sourceImage': text(item['image_url']), 'url': text(item['page_url']),
        'temperature': text(item['temperature']), 'strength': strength(item['strength']),
        'grapes': split(item['grapes']), 'foodPairing': split(item['dishes']),
        'description': text(item['description']),
        'similarSlugs': split(item['similar_wines_slugs']),
        'similarTitles': text(item['similar_wines_titles']),
        'similarUrls': split(item['similar_wines_urls']),
    })
assert len({wine['slug'] for wine in wines}) == len(wines), 'Duplicate wine slug'
for wine in wines:
    assert wine['url'].startswith('https://vino-svoe.ru/wines/')
    assert wine['image'].startswith('https://api.vino-svoe.ru/')
target = Path(__file__).resolve().parents[1] / 'public/catalog/wines.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(wines, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'Imported {len(wines)} wines; {target.stat().st_size:,} bytes')
