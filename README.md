# Svoe Vino

Svoe Vino — объединённое приложение для распознавания вина по фотографии этикетки и отображения карточки вина во frontend-интерфейсе.

Проект состоит из исходного frontend, исходного backend и отдельного интеграционного слоя. Интеграция вынесена из основных приложений, поэтому frontend и backend могут развиваться независимо.

## Структура проекта

```text
svoe-vino/
├── README.md
├── ARCHITECTURE.md
├── integration.py
├── run.py
├── svoe-vino-scanner/
└── wine_detection/
```

- `svoe-vino-scanner/` — frontend на Nuxt.
- `wine_detection/` — backend на FastAPI с логикой распознавания и каталогом вин.
- `integration.py` — адаптер между API frontend и API backend.
- `run.py` — единая точка запуска проекта.
- `ARCHITECTURE.md` — описание компонентов, потока данных и API-контрактов.

## Требования

Для запуска потребуются:

- Python 3.10+;
- Node.js и npm;
- зависимости backend из `wine_detection/requirements.txt`;
- настроенные переменные окружения, необходимые backend для работы сервиса распознавания.

## Установка backend

Из корня проекта создайте виртуальное окружение:

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r wine_detection\requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r wine_detection/requirements.txt
```

## Установка frontend

```bash
cd svoe-vino-scanner
npm install
cd ..
```

## Запуск

Рекомендуемый способ — запуск из корня проекта:

### Windows

```powershell
py run.py
```

### macOS / Linux

```bash
python run.py
```

`run.py` отвечает за запуск объединённого приложения и необходимые параметры интеграции.

После запуска откройте адрес, указанный сервером в терминале.

## Как проходит запрос

Пользователь загружает изображение во frontend. Frontend отправляет его как `multipart/form-data` в:

```http
POST /api/scan
```

Поле изображения:

```text
file
```

`integration.py` принимает запрос, передаёт изображение существующей backend-логике и преобразует результат в контракт, понятный frontend.

Успешный ответ интеграционного API имеет вид:

```json
{
  "found": true,
  "wine": {
    "slug": "wine-slug"
  }
}
```

После получения `slug` frontend открывает соответствующую страницу вина.

## Smoke test

Для быстрой проверки интеграционного endpoint:

```bash
curl -i -X POST http://localhost:8000/api/scan -F "file=@wine.jpg"
```

Где `wine.jpg` — тестовая фотография этикетки.

Проверка считается успешной, если:

1. запрос доходит до `/api/scan`;
2. сервер отвечает без `500 Internal Server Error`;
3. backend обрабатывает изображение;
4. integration возвращает ожидаемый JSON-контракт;
5. frontend может использовать полученный `slug` для перехода на карточку вина.

## Где вносить изменения

Бизнес-логика распознавания, модели и работа с каталогом относятся к `wine_detection/`.

UI, страницы, клиентская логика и отображение результата относятся к `svoe-vino-scanner/`.

Код, необходимый исключительно для связи этих двух приложений, должен оставаться в `integration.py` или другом явно выделенном интеграционном модуле.

Такое разделение позволяет обновлять frontend или backend без переноса интеграционной логики внутрь исходных приложений.
