# Auth service

Cервис авторизации.

<details><summary><h1>Инструкция по установке</h1></summary>

Клонируйте репозиторий и перейдите в него.
```bash
git clone git@hub.mos.ru:shift-python/y2024/homeworks/vstakrotskij/auth_service.git
```
Создайте файл .env, в корневой папке проекта, с переменными окружения.
```
SECRET = (секрет для создания токена)
```
Для установки виртуального окружения с помощью Poetry нужно установить его через pip:
```bash
pip install poetry
```
Для установки зависимостей выполните команду:

```bash
poetry install
```

</details>
<details><summary><h1>Инструкция по запуску линтера</h1></summary>
Для установки виртуального окружения с помощью Poetry нужно установить его через pip:
```bash
pip install poetry
```
Для установки зависимостей выполните команду:

```bash
poetry install
```
Для запуска линтера выполните команду:

```bash
flake8 src/
```
</details>
