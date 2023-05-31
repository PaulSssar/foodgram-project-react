# FOODGRAM
_Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд_
Технологии
- Python
- Django
- Django Rest Framework
- PostgreSQL
- Docker
- Docker-Compose
- Nginx
- Gunicorn
## Установка
### Шаблон описания файла .env
 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=postgres
 - POSTGRES_USER=postgres
 - POSTGRES_PASSWORD=postgres
 - DB_HOST=db
 - DB_PORT=5432
 - SECRET_KEY=<секретный ключ проекта django>
### Инструкции для развертывания и запуска приложения
для Linux-систем все команды необходимо выполнять от имени администратора1
- Склонировать репозиторий
```bash
git clone https://github.com/paulsssar/yamdb_final.git
```
- Выполнить вход на удаленный сервер
- Установить docker на сервер:
```bash
apt install docker.io 
```
- Установить docker-compose на сервер:
```bash
apt install docker-compose
```

- Скопировать файлы docker-compose.yml и default.conf на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp default.conf <username>@<host>:/home/<username>/nginx/default.conf
```
- Создать .env файл по предлагаемому выше шаблону.
- Для работы с Workflow добавить в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    SECRET_KEY=<секретный ключ проекта django>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    Workflow состоит из четырёх шагов:
     - Проверка кода на соответствие PEP8.
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления в телеграм-чат.
- собрать и запустить контейнеры на сервере:
```bash
docker-compose up -d --build
```
- После успешной сборки выполнить следующие действия (только при первом деплое):
    * провести миграции внутри контейнеров:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
    * собрать статику проекта:
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```  
    * Создать суперпользователя Django, после запроса от терминала ввести логин и пароль для суперпользователя:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

### Команды для заполнения базы данными
- Заполнить базу данными
- Создать резервную копию данных:
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json
```
- Остановить и удалить неиспользуемые элементы инфраструктуры Docker:
```bash
docker-compose down -v --remove-orphans
```

## Автор
Павел Сарыгин 


## Ссылка на проект
http://51.250.12.162/api
