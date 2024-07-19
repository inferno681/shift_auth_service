[https://hub.mos.ru/shift-python/y2024/homeworks/vstakrotskij/auth_service/badges/main/coverage.svg](https://hub.mos.ru/shift-python/y2024/homeworks/vstakrotskij/auth_service/badges/main/coverage.svg)
[https://hub.mos.ru/shift-python/y2024/homeworks/vstakrotskij/auth_service/badges/main/coverage.svg](https://hub.mos.ru/shift-python/y2024/homeworks/vstakrotskij/auth_service/badges/main/pipeline.svg)

# Auth service

Cервис авторизации.

## Реализованы следующие возможности

### Регистрация

На основе логина, пароля создает в хранилище запись о новом пользователе. В качестве ответа возвращает JWT-токен.

### Авторизация

На основе логина и пароля проверяет наличие пользователя в хранилище. Затем:
если JWT-токена нет в хранилище, то создает его и сохраняет в хранилище;
если JWT-токен есть в хранилище, обновляет его.
В качестве ответа возвращает JWT-токен.
если входящие данные некорректны возвращает None
