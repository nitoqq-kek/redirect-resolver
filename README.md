# Redirect Resolver

### Основная логика

1) Запрашиваем URL
2) Если редирект циклический или средиректило больше N раз то возвращаем ошибку
3) Не пытаемся вычитать тело, т.к оно может иметь бесконечный объем

### Запуск

#### Сборка контейнеров
```bash
docker-compose build redirect-resolver-test
```

#### Запуск unit тестов
```bash
docker-compose run --rm redirect-resolver-test

```
