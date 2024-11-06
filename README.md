**Bookstore-Statisrics API app**
```markdown
Bookstore-Statistics - второй микросервис для Bookstore app. (запускать только после первого микросервиса) 
Первый микросервис: https://github.com/myBlurryface/Bookstore.Books-operator/tree/master 

Это REST API подведения статистики онлайн магазина Bookstore с использованием Django, PostgreSQL, Kafka. 
Проект поддерживает аутентификацию с использованием JWT и использует Docker для контейнеризации приложения.

## Основные возможности

1. Информация по клиентами
   • Список клиентов: Просмотр и сортировка клиентов по дате регистрации и сумме покупок.
   • Статистика: Общее количество клиентов, пользователи без покупок, активные покупатели.

2. Информация по покупками
   • Список покупок: Полный список с фильтрацией по статусу и датам.
   • Покупки за текущий месяц: Быстрый доступ к данным о текущих покупках.
   • Фильтрация по датам: Доступ к покупкам за указанный месяц или конкретную дату.
   • Сортировка: По дате и статусу.

3. Аналитика
   • Топ-покупка и сумма продаж: Определение популярных товаров и общей суммы продаж за выбранный период.
   • Средний чек: Расчет за определенный период.
   • Периоды анализа: Текущий месяц, квартал, день, год и конкретные даты.

4. Безопасность
   • Аутентификация: JWT-токены для безопасного доступа.
   • Защита маршрутов: Все запросы требуют аутентификации.

## Стек технологий

- Python 3.12
- Django Rest Framework
- PostgreSQL
- Docker и Docker Compose
- JWT для аутентификации
- Kafka

## Требования

Для запуска проекта вам потребуется:

- Docker и Docker Compose
- Python 3.12 (если не использовать Docker)
- Установленная и настроенная база данных PostgreSQL
- Kafka
```

## Установка

### Шаг 1: Установка и настройка PostgreSQL

#### 1. Установка PostgreSQL

##### macOS (с Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

##### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

##### Linux (Fedora/RHEL):
```bash
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
```

##### Windows:
Загрузите и установите PostgreSQL: [PostgreSQL для Windows](https://www.postgresql.org/download/windows/)

#### 2. Настройка PostgreSQL

1. Войдите в PostgreSQL как суперпользователь:
   ```bash
   sudo -u postgres psql
   ```

2. Создайте пользователя и базу данных:
   ```sql
   CREATE USER admin WITH PASSWORD 'admin';
   CREATE DATABASE db_statisitics;
   GRANT ALL PRIVILEGES ON DATABASE db_statisitics TO admin;
   \q
   ```

#### 3. Установите KAFKA
1. Используйте порт 9092 .
2. Создайте топики: customer_topic, order_topic.

### Шаг 2: Клонирование репозитория

Склонируйте репозиторий на вашу локальную машину:

```bash
git clone https://github.com/myBlurryface/Bookstore.Bookstore-Statistics
cd Bookstore.Bookstore-Statistics
```

### Шаг 3: Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта. Пример содержимого:

```bash
POSTGRES_DB=db_statisitics # Название ДБ
POSTGRES_USER=admin # Пользователь ДБ
POSTGRES_PASSWORD=admin # Пароль DB 
DB_PORT=5432 # Порт ДБ

# !! Обязательный параметр призапуске из контейнера 
DB_HOST=bookstore-statistics-db-1

# При запуске локально   
DB_HOST="localhost" 

KAFKA_BROKER=kafka:9092
```

### Шаг 4: Запуск с использованием Docker

1. Перейдите в корневую директорию проекта. Затем постройте и запустите контейнеры:

    ```bash
    docker-compose up --build
    ```

2. Выполните миграции базы данных:

    ```bash
    docker exec web python manage.py migrate
    ```

3. Создайте суперпользователя для доступа к Django admin:

    ```bash
    docker exec web python manage.py createsuperuser
    ```

4. Создайте нужные топики, если еще этого не сделали
    ```bash
    docker exec -it kafka /bin/kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic customer_topic
    docker exec -it kafka /bin/kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic order_topic  
    docker exec -it kafka /bin/kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic order_items_topic 
    ```

Теперь приложение доступно по адресу `http://localhost:8001`.


### Шаг 5: Локальный запуск (без Docker)

Если вы хотите запустить проект без Docker:

1. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

2. Выполните миграции базы данных:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

3. Запустите сервер разработки:

    ```bash
    python manage.py runserver 8001
    # (при локальном запуске используйте порт 8001, чтобы не было конфликтов с Books-operator)
    ```

4. Создайте суперпользователя:

    ```bash
    python manage.py createsuperuser
    ```
### **Models Overview**

# Модель: Customer (Клиент)

Описание: Модель, представляющая клиентов магазина.

• Поля:
   • customer_id: Уникальный идентификатор клиента (автоматическое целое число, первичный ключ).
   • username: Имя пользователя (строка, обязательное, уникальное).
   • phone_number: Номер телефона (строка, обязательное).
   • total_spent: Общая сумма, потраченная клиентом (десятичное число, по умолчанию 0.00).
   • date_joined: Дата регистрации клиента (дата и время).
   • Модель: OrderItem (Элемент заказа)
   • Описание: Модель, представляющая отдельные книги в заказе.

• Методы:
   __str__(): Возвращает имя пользователя.

# Модель: Purchase (Покупка)

Описание: Модель, представляющая покупку клиента.

• Поля:
   • purchase_id: Уникальный идентификатор покупки (автоматическое целое число, первичный ключ).
   • customer: Ссылка на клиента (внешний ключ на модель Customer, обязательное).
   • status: Статус покупки (строка, выбор из возможных значений).
   • purchase_date: Дата совершения покупки (дата и время).
   • purchase_price: Общая стоимость покупки (десятичное число).

• Метаданные:
   Порядок: Покупки сортируются по дате в порядке убывания.

### API Документация
## API Маршруты

1. CustomerViewSet

• Base URL: /customers/
   Описание: Информация по клиентами, включая получение списка клиентов и статистики.

• Методы:
      • GET /customers/: Возвращает список всех клиентов. 
   Параметры запроса:
      • ordering: (необязательно) 
      Указывает порядок сортировки. Поддерживаемые значения: date_joined, -date_joined, total_spent, -total_spent.
   Пример:
      GET /customers/total_users/: Возвращает статистику по количеству клиентов.

2. PurchaseViewSet

• Base URL: /purchases/

   Описание: Управление покупками с возможностью фильтрации и сортировки.

• Методы:
      • GET /purchases/: Возвращает список всех покупок. Поддерживает фильтрацию по status, start_date, и end_date.
      • GET /purchases/current_month/: Возвращает список покупок за текущий месяц.
      • GET /purchases/by_month/: Возвращает список покупок за указанный месяц и год.
      • GET /purchases/by_date/: Возвращает покупки за определенную дату.
   Пример: 
      # Возвращает покупки за выбранный диапазон
      GET /purchases/?status=delivered&start_date=2024-01-01&end_date=2024-01-31 # Возвращает покупки за выбранный диапазон

3. PurchaseSummaryView

• Base URL: /summary/

   Описание: Сводная информация о продажах и популярных товарах.

Методы:
      • GET /summary/get_summary/: Возвращает сводные данные о продажах, включая топ-покупку, общую сумму продаж и средний чек.
    Параметры:
      • period: Определяет временной интервал (например, this_month, last_quarter, today).
      • date: Используется при period=specific_date.
    Пример: 
      # Самая продаваемая книга/средний чек/тотал покупок за этот месяц 
      GET /summary/get_summary/?period=this_month

# Дополнительно с API маршрутами можно ознакомиться с помощью команды 
    ```bash
    python manage.py show_urls
    ```

### Аутентификация

- Получение JWT токенов:
  - URL: `/api/token/`
  - Метод: `POST`
  - Параметры:
    ```json
    {
      "username": "ваш_username",
      "password": "ваш_пароль"
    }
    ```

- Обновление JWT токена:
  - URL: `/api/token/refresh/`
  - Метод: `POST`
  - Параметры:
    ```json
    {
      "refresh": "ваш_refresh_token"
    }
    ```

## Автоматическое тестирование

Запуск тестов:

```bash
# Используя Docker
docker compose exec web python manage.py test
# Не используя Docker
python manage.py test
```

## Автор

- Лозицкий Константин — ralf_201@hotmail.com
- GitHub: [ваш GitHub профиль](https://github.com/myBlurryface)

