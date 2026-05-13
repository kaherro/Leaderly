# Leaderly 🚀

**Leaderly** - это бесплатная open-source библиотека на Python для создания системы рейтинга (лидерборда) в реальном времени с использованием Redis и PostgreSQL.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-teal.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org/)



## 📋 Содержание

- [Leaderly 🚀](#leaderly-)
  - [📋 Содержание](#-содержание)
  - [✨ Особенности](#-особенности)
  - [🚀 Быстрый старт и запуск](#-быстрый-старт-и-запуск)
    - [Базовое использование](#базовое-использование)
    - [Запуск базы данных через Docker и WebSocketAPI](#запуск-базы-данных-через-docker-и-websocketapi)
    - [Запуск веб-интерфейса](#запуск-веб-интерфейса)
  - [📚 Методы LeaderboardClient](#-методы-leaderboardclient)
    - [Конструктор класса](#конструктор-класса)
    - [`update_score(key, score)`](#update_scorekey-score)
    - [`get_score(key)`](#get_scorekey)
    - [`update_tags(key, tags)`](#update_tagskey-tags)
    - [`get_tags(key)`](#get_tagskey)
    - [`get_leaderboard(n=0)`](#get_leaderboardn0)
    - [`delete_object(key)`](#delete_objectkey)
    - [💨 Краткая таблица всех методов](#-краткая-таблица-всех-методов)
  - [📚 API-документация](#-api-документация)
  - [🌐 Веб-интерфейс](#-веб-интерфейс)
    - [Технологии](#технологии)
    - [тут будет еще про функционал](#тут-будет-еще-про-функционал)
  - [📁 Структура проекта](#-структура-проекта)
  - [💡 Пример использования](#-пример-использования)

## ✨ Особенности

- ⚡ **Высокая производительность** - Redis для кэширования и быстрых операций
- 🗄️ **Постоянное хранение** - PostgreSQL для надежного сохранения данных
- 🔄 **Синхронизация в реальном времени** - WebSocket для мгновенных обновлений
- 🎯 **Гибкая настройка** - Поддержка пользовательских тегов и формул подсчета очков
- 🌐 **Веб-интерфейс** - Готовый dashboard на Vue.js
- 🐳 **Docker поддержка** - Легкий запуск нужного окружения (Redis, PostgreSQL) с Docker Compose

## 🚀 Быстрый старт и запуск

### Базовое использование
Скопируйте папку ```src``` в ту директорию, где вы планируете использовать модуль

### Запуск базы данных через Docker и WebSocketAPI

```bash
# Запуск Redis, PostgreSQL и WebSocketAPI
docker compose up -d

# Проверка статуса
docker compose ps
```

сервер запустится на ws://localhost:8000

### Запуск веб-интерфейса
```
# Переход в папку с веб-интерфейсом
cd src/web

# Установка зависимостей (первый раз)
npm install

# Запуск development сервера
npm run dev

# Веб-интерфейс будет доступен по адресу: http://localhost:5173
```


## 📚 Методы LeaderboardClient

Класс `LeaderboardClient` находится в файле ```src/leaderboard.py``` и полностью наследует все методы ```DBManager``` из ```src/bases/db_manager.py```. Ниже представлено полное описание всех доступных методов.

---
### Конструктор класса
`__init__(redis_host, redis_port, pg_host, pg_port, pg_user, pg_password, pg_dbname)`

Инициализирует подключение к Redis и PostgreSQL.

**Параметры:**
| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `redis_host` | str | 'localhost' | Хост Redis сервера |
| `redis_port` | int | 6379 | Порт Redis сервера |
| `pg_host` | str | 'localhost' | Хост PostgreSQL сервера |
| `pg_port` | int | 5432 | Порт PostgreSQL сервера |
| `pg_user` | str | 'postgres' | Имя пользователя PostgreSQL |
| `pg_password` | str | '2991' | Пароль PostgreSQL |
| `pg_dbname` | str | 'leaderly' | Название базы данных |


---

### `update_score(key, score)`

Обновляет счет игрока в лидерборде. Если игрок с таким ключом не существует, он будет создан.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `key` | str | Уникальный идентификатор игрока |
| `score` | float | Новое значение счета |

**Возвращает:** `None`

**Пример:**
```python
# Создание нового игрока
lb.update_score("player1", 1000)

# Обновление счета существующего игрока
lb.update_score("player1", 1500)

# Отрицательные счета
lb.update_score("player2", -500)
```

---

### `get_score(key)`

Получает текущий счет игрока.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `key` | str | Уникальный идентификатор игрока |

**Возвращает:** 
- `float` - счет игрока, если найден
- `None` - если игрок не найден

**Пример:**
```python
score = lb.get_score("player1")
if score is not None:
    print(f"Счет: {score}")
else:
    print("Игрок не найден")
```

---

### `update_tags(key, tags)`

Обновляет теги игрока. Теги могут использоваться для хранения дополнительной информации.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `key` | str | Уникальный идентификатор игрока |
| `tags` | List[float] | Список числовых тегов |

**Возвращает:** `None`

**Пример:**
```python
# Добавление тегов
lb.update_tags("player1", [1.5, 2.5, 3.5])

# Обновление тегов
lb.update_tags("player1", [10, 20, 30, 40])

# Очистка всех тегов
lb.update_tags("player1", [])
```

---

### `get_tags(key)`

Получает список тегов игрока.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `key` | str | Уникальный идентификатор игрока |

**Возвращает:**
- `List[float]` - список тегов (может быть пустым)
- `None` - если игрок не найден

**Пример:**
```python
tags = lb.get_tags("player1")
if tags:
    print(f"Теги: {tags}")
else:
    print("Теги отсутствуют")
```

---

### `get_leaderboard(n=0)`

Возвращает топ-N игроков из лидерборда, отсортированных по убыванию счета.

**Параметры:**
| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `n` | int | 0 | Количество игроков (0 - вернуть всех) |

**Возвращает:** `List[tuple(key, score, tags)]`

**Пример:**
```python
# Топ-10 игроков
top10 = lb.get_leaderboard(10)
for rank, (key, score, tags) in enumerate(top10, 1):
    print(f"{rank}. {key}: {score} очков, теги: {tags}")

# Все игроки
all_players = lb.get_leaderboard(0)
print(f"Всего игроков: {len(all_players)}")
```

---

### `delete_object(key)`

Удаляет игрока из лидерборда вместе со всеми его тегами.

**Параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `key` | str | Уникальный идентификатор игрока |

**Возвращает:** `None`

**Пример:**
```python
# Удаление игрока
lb.delete_object("player1")

# Проверка, что игрок удален
score = lb.get_score("player1")  # Вернет None
```

---

### 💨 Краткая таблица всех методов

| Метод | Параметры | Возвращает | Описание |
|-------|-----------|------------|----------|
| `__init__()` | redis_host, redis_port, pg_host, pg_port, pg_user, pg_password, pg_dbname | `None` | Инициализация подключения к БД |
| `update_score()` | key, score | `None` | Обновление счета игрока |
| `get_score()` | key | `float` или `None` | Получение счета игрока |
| `update_tags()` | key, tags | `None` | Обновление тегов игрока |
| `get_tags()` | key | `List[float]` или `None` | Получение тегов игрока |
| `get_leaderboard()` | n | `List[tuple]` | Получение топ-N игроков |
| `delete_object()` | key | `None` | Удаление игрока |


## 📚 API-документация

В проекте используется WebSocket api, документация к реализации которой находится [здесь](https://torkomyanvv-1373059.postman.co/workspace/Vladimir-Torkomyan's-Workspace~16393eea-7580-4f1c-835a-0bc0f1c3ebb1/collection/69d133b8d8c4bec8e63369f2?action=share&creator=53754976&active-environment=53754976-910d929b-69d6-439e-84d9-74a577c32ded)

## 🌐 Веб-интерфейс

Leaderly включает в себя современный веб-интерфейс на Vue.js 3 для визуализации и управления лидербордом в реальном времени.

### Технологии

- **Vue.js 3** - прогрессивный JavaScript фреймворк
- **Vite** - быстрый сборщик проектов
- **Vue Router** - маршрутизация для SPA
- **Chart.js** - графики и визуализация данных
- **WebSocket** - real-time обновления

О запуске веб-интерфейса - [здесь](#-быстрый-старт-и-запуск)

### тут будет еще про функционал

## 📁 Структура проекта
```
Leaderly/
│
├── src/ # Исходный код проекта
│ ├── api/ # WebSocket API сервер
│ │ └── ws-api.py # FastAPI WebSocket сервер (основной endpoint)
│ │
│ ├── bases/ # Классы для работы с БД
│ │ └── db_manager.py # DBManager - работа с Redis и PostgreSQL
│ │
│ ├── web/ # Веб-интерфейс на Vue.js
│ │ ├── components/ # Vue компоненты
│ │ │ └── Header.vue # Шапка с навигацией
│ │ ├── views/ # Страницы приложения
│ │ │ ├── Home.vue # Главная страница
│ │ │ └── Leaderboard.vue # Страница с таблицей лидеров
│ │ ├── assets/ # Статические файлы
│ │ │ └── logo/ # Логотипы
│ │ │ └── logo.png # Логотип Leaderly
│ │ ├── App.vue # Корневой компонент Vue
│ │ ├── main.js # Точка входа Vue приложения
│ │ ├── router.js # Маршрутизация Vue Router
│ │ ├── index.html # HTML шаблон
│ │ ├── package.json # NPM зависимости и скрипты
│ │ ├── package-lock.json # Фиксация версий зависимостей
│ │ └── vite.config.js # Конфигурация Vite сборщика
│ │
│ └── leaderboard.py # Клиентская обертка (экспортируемый интерфейс)
│
├── tests/ # Модульные тесты
│ └── test_db_manager.py # Тесты для DBManager
│
├── docker-compose.yml # Docker Compose конфигурация
├── requirements.txt # Python зависимости
├── example.py # Пример использования библиотеки
└── README.md # Документация проекта
```

## 💡 Пример использования

```python
from src.leaderboard import LeaderboardClient

# Создание клиента с параметрами по умолчанию
lb = LeaderboardClient()

# Добавление игроков
lb.update_score("alice", 1500)
lb.update_score("bob", 2300)
lb.update_score("charlie", 1800)
lb.update_score("diana", 3200)

# Получение счета конкретного игрока
score = lb.get_score("alice")
print(f"Счет Alice: {score}")  # Счет Alice: 1500

# Получение топ-3 игроков
top3 = lb.get_leaderboard(3)
for rank, (key, score, tags) in enumerate(top3, 1):
    print(f"{rank}. {key}: {score} очков")
# 1. diana: 3200 очков
# 2. bob: 2300 очков
# 3. charlie: 1800 очков

# Обновление счета
lb.update_score("alice", 3500)  # Alice теперь лидер

# Удаление игрока
lb.delete_object("charlie")
```

