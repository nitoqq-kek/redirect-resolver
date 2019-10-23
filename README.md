# Redirect Resolver

### Основная логика

1) Запрашиваем URL
2) Если средиректило больше чем 10 раз то возвращаем результат TooManyRedirects
3) Не пытаемся вычитать тело, т.к оно может иметь бесконечный объем

4) Результаты содержащие следующие данные
```python
class Result(pydantic.BaseModel):
    url: str
    real_url: t.Optional[str]
    content_length: t.Optional[int]
    http_status: t.Optional[int]
    error: t.Optional[str]
```
записывем в файл в `jsonl` формате


### Запуск

#### Сборка контейнеров
```bash
docker-compose build redirect-resolver testing-server
docker-compose build redirect-resolver-test
```

#### Запуск unit тестов
```bash
docker-compose run --rm redirect-resolver-test

```

#### Запуск e2e теста
```bash
docker-compose up -d testing-server
docker-compose run --rm redirect-resolver -v resolve /data/input.txt /data/output.jsonl
```

Результат будет записан в `./.data/output.jsonl`

