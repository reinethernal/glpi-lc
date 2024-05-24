Этот бот разработан для взаимодействия с пользователями через Telegram и предоставляет следующие основные функции:
1. Поиск в базе данных FAQ:
Бот принимает ключевые слова от пользователя и выполняет поиск по базе данных FAQ, используя API системы GLPI.
Если найдены релевантные результаты, бот возвращает ссылки на найденные статьи.
Если результаты не найдены, бот предлагает пользователю начать новый поиск или связаться с оператором.
2. Livechat с оператором:
Пользователь может выбрать опцию для связи с оператором, чтобы задать вопросы или получить дополнительную помощь.
Сообщения пользователей пересылаются оператору, который может ответить на них прямо через бот.
Оператор может завершить разговор, заблокировать или разблокировать пользователя.

Установка:
### Пошаговая инструкция для установки и запуска Telegram бота

#### Шаг 1: Установка необходимых программ

1. **Установите Python 3.7 или выше**:
   - Загрузите установщик Python с официального сайта: [python.org](https://www.python.org/downloads/)
   - Следуйте инструкциям по установке для вашей операционной системы.
   - Убедитесь, что Python добавлен в системный PATH.

2. **Установите MongoDB**:
   - Загрузите и установите MongoDB с официального сайта: [mongodb.com](https://www.mongodb.com/try/download/community)
   - Следуйте инструкциям по установке для вашей операционной системы.
   - Запустите MongoDB сервер, используя команду:
     ```sh
     mongod
     ```

#### Шаг 2: Настройка и активация виртуального окружения

1. **Создайте и активируйте виртуальное окружение**:
   - Создайте виртуальное окружение:
     ```sh
     python3 -m venv venv
     ```
   - Активируйте виртуальное окружение:
       ```sh
       source venv/bin/activate
       ```

#### Шаг 3: Установка зависимостей

1. **Установите зависимости**:
   ```sh
   pip3 install -r requirements.txt
   ```

#### Шаг 4: Настройка переменных окружения

1. **Заполните файл `.env`** в корневой директории вашего проекта следующими переменными:
   ```env
   TELEGRAM_API_TOKEN=your_telegram_api_token
   MONGO_CONNECTION_STRING=mongodb://localhost:27017/
   MONGO_DB_NAME=bot_database
   MONGO_COLLECTION_NAME=fsm
   GLPI_API_URL=https://your-glpi-api-url
   GLPI_APPTOKEN=your_glpi_apptoken
   GLPI_USERTOKEN=your_glpi_usertoken
   GLPI_FAQ_URL=https://your-glpi-faq-url
   OPERATOR_CHAT_ID=your_operator_chat_id
   ```

   Замените `your_telegram_api_token`, `your_glpi_api_url`, `your_glpi_apptoken`, `your_glpi_usertoken`, `your_glpi_faq_url`, `your_operator_chat_id` на реальные значения.

#### Шаг 5: Создание базы данных и коллекций

1. **Подключитесь к MongoDB**:
   - Откройте новый терминал и подключитесь к MongoDB:
     ```sh
     mongosh  # или mongo
     ```

2. **Создайте базу данных и коллекции**:
   ```js
   use bot_database

   db.createCollection("users")
   db.createCollection("fsm")
   db.createCollection("message_links")

   db.users.createIndex({"_id": 1})
   db.fsm.createIndex({"user_id": 1})
   db.message_links.createIndex({"reply_message_id": 1})
   ```

#### Шаг 6: Запуск бота

1. **Запустите бот**:
   - Убедитесь, что все переменные окружения корректно настроены и зависимости установлены.
   - В терминале, где активировано виртуальное окружение, выполните команду:
     ```sh
     python main.py
     ```

Если все шаги выполнены правильно, ваш бот должен начать работу и быть готовым к взаимодействию с пользователями через Telegram.
