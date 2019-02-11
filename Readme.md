# Сервис Scoring API

Данная утилита представляет собой сервис скоринга.

## Установка и запуск
Для работы данной утилиты необходимо установить в систему пакет "redis-server"
Или использовать сторонний redis server.
Непосредственной установки данных скриптов не требуется.
Утилита поддерживает следущие параметры запуска:
`-p` или `--port` для указания HTTP порта для работы
`-l` или `--log` для указания имени лог файла.
`--redis-host` для указания адреса redis сервера
`--redis-port`для указания порта redis сервера
`--redis-db`для указания названия базы данных redis сервера

### Примеры запуска утилиты
Без параметров утилита будет запущена на порту 8080 с выводом логов на консоль.
Подкючение к серверу redis будет осуществлено по адресу `127.0.0.1:6379`
```bash
python scoring_api/api.py
```
С запуском на порту *1234* и выводов логов в *my.log*
```bash
python scoring_api/api.py -p 1234 -l my.log
```

### Примеры запросов для проверки работы утилиты
Запрос для *online_score* метода
```bash
curl -X POST -H "Content-Type: application/json" -d '{"account": "ivan", "login": "ivan91","method": "online_score", "token": "36592bae85a52296530b416e9236c503543d9c0fd835614474ec0344b1c33c5b2de933b041bab4c8f04e9c2994a9dc22806b60b08fc3965486fa400f1dc6fbfe", "arguments": {"phone": "78529870534", "email": "ivan@mail.ru", "first_name": "Иван", "last_name": "Иванов", "birthday": "12.12.1991", "gender": 1}}' http://127.0.0.1:8080/method/
```

Запрос для *clients_interests* метода
```bash
curl -X POST -H "Content-Type: application/json" -d '{"account": "ivan", "login": "ivan91","method": "clients_interests", "token": "36592bae85a52296530b416e9236c503543d9c0fd835614474ec0344b1c33c5b2de933b041bab4c8f04e9c2994a9dc22806b60b08fc3965486fa400f1dc6fbfe", "arguments":  {"client_ids": [0]}}' http://127.0.0.1:8080/method/
```


## Запуск тестов
Перед запуском тестов необходим установить в своём окружении систему `pytest`.
Сделать это можно командой
```bash
pip install pytest
```
Для запуска тестов достаточно ввести команду
```bash
pytest -v tests/
```
