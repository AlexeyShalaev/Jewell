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

1. [MongoDB](https://www.mongodb.com/docs/v4.4/tutorial/install-mongodb-on-ubuntu/)
2. [Git](https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu-20-04-ru)

### Установка пакетов

1. `sudo apt-get install build-essential cmake pkg-config`
2. `sudo apt-get install libx11-dev libatlas-base-dev`
3. `sudo apt-get install libgtk-3-dev libboost-python-dev`
4. `sudo apt-get install python-dev python-pip python3-dev python3-pip`
5. `pip install python-dev-tools`

### Настройка [сервисов](https://dzen.ru/media/cyber/sozdaem-systemd-iunit-unit-na-primere-telegram-bota-62383c5d55ea3027de06d7ed?utm_referer=away.vk.com)

0. Подготовка
* Сервер с установленной операционной системой Ubuntu 18.04 и пользователь без привилегий root и с привилегиями sudo. Следуйте указаниям нашего [руководства по начальной настройке сервера.](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04)
```
adduser jewell
usermod -aG sudo jewell
ufw allow OpenSSH
ufw enable
```

* Веб-сервер Nginx, установленный в соответствии с шагами 1 и 2 модуля [Установка Nginx в Ubuntu 18.04.](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04)
```
// выполняем под пользователем jewell
sudo apt update
sudo apt install nginx
sudo ufw allow 'Nginx HTTP'
```

* Доменное имя, настроенное так, чтобы указывать на ваш сервер. Обязательно создайте следующие записи DNS: 
  * Запись A, где your_domain указывает на публичный IP-адрес вашего сервера.
  * Запись A, где www.your_domain указывает на публичный IP-адрес вашего сервера.


1. jms_assistant
```
[Unit]
Description=Assistant
After=syslog.target
After=network.target

[Service]
Type=simple
User=jewell
WorkingDirectory=/jewell/Jewell/Assistant
ExecStart=/usr/bin/python3 /jewell/Jewell/Assistant/main.py
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
WorkingDirectory=/jewell/Jewell/TelegramBot
ExecStart=/usr/bin/python3 /jewell/Jewell/TelegramBot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. jms_site [Инструкция](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04-ru)
- Шаг 1 — Установка компонентов из хранилищ Ubuntu
```
sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
```
- Шаг 2 — Создание виртуальной среды Python
```
sudo apt install python3-venv
python3.8 -m venv webenv
source webenv/bin/activate
```
- Шаг 3 — Настройка приложения Flask
```
pip install wheel
pip install uwsgi
pip install -r requirements.txt
```
