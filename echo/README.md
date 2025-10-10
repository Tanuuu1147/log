Сервер будет доступен по адресу: `http://127.0.0.1:5000`

## Использование

### Обычный GET запрос
```bash
curl http://127.0.0.1:5000/test
```

### GET с кастомным статус-кодом
```bash
curl "http://127.0.0.1:5000/test?status=404"
curl "http://127.0.0.1:5000/test?status=500"
```

### POST запрос с данными
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' \
  http://127.0.0.1:5000/api/endpoint
```

```

## Запуск тестов

```bash
pytest test_echo_server.py -v
```

## Примеры ответов

### Успешный запрос (200 OK)
```
Request Method: GET
Request Source: ('127.0.0.1', 51720)
Response Status: 200 OK
Host: 127.0.0.1:5000
User-Agent: curl/8.6.0
Accept: */*
```

### Запрос с ошибкой (404 Not Found)
```
Request Method: GET
Request Source: ('127.0.0.1', 51862)
Response Status: 404 Not Found
Host: 127.0.0.1:5000
User-Agent: curl/8.6.0
Accept: */*
```

