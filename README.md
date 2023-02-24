# Фильтр желтушных новостей

Сервер принимает запрос на анализ статей с сайта [inosmi.ru](https://inosmi.ru/). Адреса стетей для анализа передаются списком в параметре urls.

Пример запроса:
```
http://localhost:8888/?urls=https://inosmi.ru/20230204/neft-260327000.html,https://inosmi.ru/20230204/ssha-260319321.html,https://inosmi.ru/20230204/yuzhnaya-koreya-260307651.html,https://inosmi.ru/not/exist.html,https://lenta.ru/brief/2021/08/26/afg_terror/,asdgftaegdhjtehrs
```

В ответ сервер выдает json с результатами анализа статей. Пример ответа:
```json
[
    {
        "url": "asdgftaegdhjtehrs",
        "status": "FETCH_ERROR",
        "words_count": null,
        "rate": null
    },
    {
        "url": "https://inosmi.ru/not/exist.html",
        "status": "FETCH_ERROR",
        "words_count": null,
        "rate": null
    },
    {
        "url": "https://lenta.ru/brief/2021/08/26/afg_terror/",
        "status": "PARSING_ERROR",
        "words_count": null,
        "rate": null
    },
    {
        "url": "https://inosmi.ru/20230204/ssha-260319321.html",
        "status": "OK",
        "words_count": 490,
        "rate": 1.22
    },
    {
        "url": "https://inosmi.ru/20230204/neft-260327000.html",
        "status": "OK",
        "words_count": 774,
        "rate": 1.94
    },
    {
        "url": "https://inosmi.ru/20230204/yuzhnaya-koreya-260307651.html",
        "status": "OK",
        "words_count": 1153,
        "rate": 0.61
    }
]
```

# Как установить

Вам понадобится Python версии 3.7 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```python3
pip install -r requirements.txt
```

# Как запустить

```python3
python server.py
```

# Как запустить тесты

Для тестирования используется [pytest](https://docs.pytest.org/en/latest/). Команда для запуска тестов:

```
python -m pytest tests
```


# Цели проекта

Код написан в учебных целях. Это урок из курса по веб-разработке — [Девман](https://dvmn.org).
