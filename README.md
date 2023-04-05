# JMS
### :one:: Management system

* Формы
  * Конструктор
  * Анализатор
* Игры
  * 5 БУКВ
* Курсы
  * Расписание
  * Посещаемость
* Net Working
  * Лента
    * Новости
    * Посты
  * Связи
* Карта поездок
* Уведомления
* Вакансии
* Товары
* Навигатор
* Face ID
* Администрирование
  * Управление Telegram BOT
  * Пользователи
    * Администрация
    * Преподаватели
    * Студенты
    * Зарегистрированные
  * Безопасность
    * Пользователи
    * Восстановление паролей
    * Сессии
    * База Данных
  * Конфигурация 
    * Файлы
    * Переменные
    * Бекапы
* API
  * Получение файлов
  * Net working
  * Счетчики
  * Snapshot
    * Создание резервной копии
    * Восстановление данных из резервной копии
    * Получение списка резервных копий
  * Посещаемость
  * Удаление записей

### :two:: Telegram Bot
* Посещаемость 
* Расписание 
* Уведомления
* Аккаунт
  * Вход на сайт
  * Сессии
  * Восстановление пароля
* Администрация
  * Перезапуск сайта
  * Создание резервных копий
  * Восстановление из резервных копий

### :three:: Assistant
* Автоматическое создание резервных копий
* Проверка состояния работы сайта
* Удаление записей пользователей по времени

## Устновка

### Сервер и ОС

Минимальная конфигурация сервера
- *Процессор*: 2 ядра
- *Память*: 4 GB
- *Диск*: 40 GB

### Настройка среды

1. [MongoDB](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)
2. [Git](https://git-scm.com/download/linux)

### Установка пакетов

1. `sudo apt-get install build-essential cmake pkg-config`
2. `sudo apt-get install libx11-dev libatlas-base-dev`
3. `sudo apt-get install libgtk-3-dev libboost-python-dev`
4. `sudo apt-get install python-dev python-pip python3-dev python3-pip`
5. `pip install python-dev-tools`

### Настройка [сервисов](https://dzen.ru/media/cyber/sozdaem-systemd-iunit-unit-na-primere-telegram-bota-62383c5d55ea3027de06d7ed?utm_referer=away.vk.com)

1. jms_assistant
```
[Unit]
Description=Assistant
After=syslog.target
After=network.target

[Service]
Type=simple
User=jewell
WorkingDirectory=/jewell/JMS/Jewell/Assistant
ExecStart=/usr/bin/python3 /jewell/JMS/Jewell/Assistant/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. jms_bot
```
[Unit]
Description=Bot
After=syslog.target
After=network.target

[Service]
Type=simple
User=jewell
WorkingDirectory=/jewell/JMS/Jewell/TelegramBot
ExecStart=/usr/bin/python3 /jewell/JMS/Jewell/TelegramBot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. jms_site
