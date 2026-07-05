# Leads Service

FastAPI-сервис для обработки заявок с использованием паттерна Transactional Outbox и брокера сообщений Kafka (Redpanda).

## Технологии
- **Python** 3.12+
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy** (async / asyncpg)
- **Alembic** (миграции)
- **Kafka** (через Redpanda в Docker и библиотеку `aiokafka`)

---

## Как запустить проект локально

### 1. Подготовка окружения
1. Сделайте копию шаблона переменных окружения:
   Создайте файл `src/.env` (если его нет) и укажите настройки подключения:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASS=Suharik15022006
   DB_NAME=practice_crm
   ```
2. Установите зависимости проекта (в виртуальном окружении):
   ```bash
   pip install -r requirements.txt
   # Или установите основные библиотеки вручную:
   # pip install fastapi uvicorn sqlalchemy asyncpg alembic aiokafka pydantic-settings
   ```

### 2. Запуск инфраструктуры (БД и Kafka/Redpanda)
Запустите контейнеры базы данных, брокера сообщений и веб-консоли одной командой:
```bash
docker compose up -d
```
После запуска вы можете открыть веб-панель управления Redpanda Console в браузере:
`http://localhost:19082` — здесь можно наглядно просматривать топики и сообщения.

### 3. Применение миграций базы данных
Примените миграции Alembic для создания таблиц в PostgreSQL:
```bash
alembic upgrade head
```

### 4. Запуск веб-сервера (API)
Запустите FastAPI сервер:
```bash
uvicorn src.main:app --reload --port 8080
```
Документация Swagger будет доступна по адресу: `http://localhost:8080/docs`

### 5. Запуск воркеров (в отдельных терминалах)
1. **Запуск Outbox Publisher** (отправляет события о новых заявках в Kafka):
   ```bash
   python -m src.publisher
   ```
2. **Запуск Kafka Consumer** (слушает решения модерации и обновляет заявки):
   ```bash
   python -m src.consumer
   ```

---

## Тестирование и ручная отправка событий

### Способ 1: С помощью встроенного Python-скрипта (рекомендуется)
Для удобной отправки событий модерации подготовлен интерактивный скрипт. Запустите его в свободном терминале:
```bash
python -m src.send_test_moderation
```
Скрипт предложит ввести UUID заявки (его можно скопировать из ответа `POST /leads` или базы данных) и выбрать решение (одобрить/отклонить), после чего сам отправит нужное событие в Kafka.

