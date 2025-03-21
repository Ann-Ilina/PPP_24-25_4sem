# Лабораторная работа: Разработка клиент-серверного файлового менеджера

## Описание работы

Данная лабораторная работа посвящена разработке низкоуровневого клиент-серверного приложения для управления процессами и получения информации о них. В рамках работы необходимо реализовать сервер, который может:

1. Получать информацию о процессах, запущенных на сервере.
2. Сохранять эту информацию в файлы формата JSON.
3. Отправлять сигналы процессам на сервере.
4. Логировать все действия клиента и сервера.

---

##  Структура проекта
```
1lab/
│── main.py              # Главный файл для запуска сервера
│── server.py            # Логика работы сервера (сбор информации, работа с сокетами)
│── client.py            # Клиент для взаимодействия с сервером
│── server.log       # Логи работы сервера
│── client.log       # Логи работы клиента
├── DESCRIPTION.md       # Основной документ с теорией, объяснениями и примерами запуска
```

---

## **Теория по теме:**

1. **Сокеты (sockets):**
   - Сокеты — это механизм для обмена данными между процессами, которые могут находиться на одном компьютере или на разных машинах в сети.
   - В Python для работы с сокетами используется модуль `socket`, который позволяет создавать как TCP, так и UDP соединения.

2. **Модуль `psutil`:**
   - Библиотека `psutil` предоставляет интерфейс для получения информации о запущенных процессах и системных ресурсах (CPU, память, диски и т.д.).
   - Она кроссплатформенна и работает на Windows, Linux и macOS.

3. **Форматы данных:**
   - JSON (JavaScript Object Notation) — это текстовый формат для хранения и передачи структурированных данных. Он легко читается как человеком, так и машиной.

4. **Логирование:**
   - Логирование — это процесс записи информации о работе программы для последующего анализа. В Python для этого используется модуль `logging`.

---

## Описание кода и теоретическая часть

### **Как работает код:**

1. **Сервер:**
   - Сервер запускается на указанном IP-адресе и порту (по умолчанию `127.0.0.1:65432`).
   - Он ожидает подключения клиента и обрабатывает его запросы:
     - Команда `update`: сервер собирает информацию о процессах, сохраняет её в файл `processes.json` и отправляет клиенту.
     - Команда `signal <pid> <sig>`: сервер отправляет сигнал указанному процессу (например, SIGSTOP, SIGCONT, SIGKILL).
   - Все действия сервера логируются в файл `server.log`.

2. **Клиент:**
   - Клиент подключается к серверу и предоставляет интерфейс для ввода команд:
     - Команда `update`: запрашивает у сервера информацию о процессах и сохраняет её в файл с именем в формате `hh-mm-ss_update.json`.
     - Команда `signal <pid> <sig>`: отправляет серверу запрос на отправку сигнала процессу и сохраняет ответ в файл с именем в формате `hh-mm-ss_signal_<pid>_<sig>.json`.
   - Все действия клиента логируются в файл `client.log`.

3. **Сохранение файлов:**
   - Файлы сохраняются в директорию с именем, соответствующим текущей дате (например, `./14-03-2025/`).
   - Имена файлов содержат временную метку и команду, например: `02-28-44_update.json`.

---

#### **Как запустить код:**

1. **Установка зависимостей:**
   - Установите библиотеку `psutil`, если она не установлена:
     ```bash
     pip install psutil
     ```

2. **Запуск сервера:**
   - Откройте терминал и выполните:
     ```bash
     python server.py
     ```
   - Сервер начнет работать на `127.0.0.1:65432`.

3. **Запуск клиента:**
   - Откройте другой терминал и выполните:
     ```bash
     python client.py
     ```
   - Клиент подключится к серверу и предложит ввести команду.

4. **Использование клиента:**
   - Введите одну из доступных команд:
     - `update`: получить информацию о процессах.
     - `signal <pid> <sig>`: отправить сигнал процессу.
     - `exit`: завершить работу клиента.

---

#### **Примеры работы:**

1. **Получение информации о процессах:**
   - Введите команду `update`:
     ```
     Введите команду: update
     Отправка команды серверу: update
     Ожидание данных от сервера...
     Данные получены.
     Создана директория для сохранения: ./14-03-2025
     Файл успешно сохранен: ./14-03-2025/02-28-44_update.json
     ```
   - В папке `./14-03-2025/` появится файл `02-28-44_update.json` с информацией о процессах.

2. **Отправка сигнала процессу:**
   - Введите команду `signal <pid> <sig>` (например, `signal 1234 1`):
     ```
     Введите команду: signal 1234 1
     Отправка команды серверу: signal 1234 1
     Данные получены.
     Создана директория для сохранения: ./14-03-2025
     Файл успешно сохранен: ./14-03-2025/02-29-14_signal_1234_1.json
     ```
   - В папке `./14-03-2025/` появится файл `02-29-14_signal_1234_1.json` с ответом сервера.

3. **Завершение работы клиента:**
   - Введите команду `exit`:
     ```
     Введите команду: exit
     Завершение работы клиента...
     ```

---

#### **Логирование:**
- Все действия сервера записываются в файл `server.log`.
- Все действия клиента записываются в файл `client.log`.

---

## **Заключение:**
Данная лабораторная работа демонстрирует основы работы с сокетами, файлами и процессами в Python. Код реализован с учетом кроссплатформенности и логирования, что делает его удобным для анализа и отладки.