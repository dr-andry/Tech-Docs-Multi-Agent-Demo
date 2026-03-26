# Tech Docs Multi‑Agent Demo

Проект представляет собой мульти‑агентную систему для обработки документов с использованием Redis и LLM (Gemma). Архитектура разделена на три независимых агента, каждый из которых отвечает за свою часть процесса: чтение документов, их валидацию/верификацию и формирование отчётов. Система использует асинхронные вызовы, HTTP‑запросы к локальной модели и общую память Redis для хранения данных.

1. **reader_agent** – читает (в данном примере – жёстко заданный) текст
   документа и сохраняет его в Redis. Один продукт (`product_id`) может
   иметь несколько документов; все они хранятся в списке под ключом
   `doc:<product_id>`.

2. **validator_agent** – периодически (или вручную) обрабатывает указанный
   `product_id`: извлекает все документы из Redis, отправляет каждый текст
   в LLM для валидации и верификации. Невалидные документы удаляются
   из списка. Результаты верификации логируются.

3. **constructor_agent** – собирает документы для `product_id` и генерирует
   итоговый отчёт (пока по фиксированному шаблону, позже шаблоны можно
   подгружать).

Каждый агент является самостоятельным скриптом в `app/agents`.

🧩 Архитектура
* Reader -  Получает/считывает документ и добавляет его в Redis под ключ `unprocessed_docs`. Поддерживается множество документов для одного продукта.	reader_agent.py + mcp_server_read.py
* Validator / Verifier -	Извлекает все считанные тексты из Redis (удаляет из `unprocessed_docs`), проводит каждый через LLM‑валидацию. Если документ `не валидный`, то говорит о том, что документ не валидный. Если проверка прошла успешно, затем запускается проверка «в пределах ли нормы». Так же, если документ не проходит проверку об этом идёт уведомление и остановка работы.	validator_agent.py + mcp_server_valid.py и mcp_server_verify.py
* Constructor -	Формирует итоговый отчёт по всем оставшимся документам продукта. Отчёт пока статический, позже – с шаблонами.	constructor_agent.py + mcp_constructor.py
Планируется, что все три агента могут запускаться изолированно (например, в разных процессах или на разных машинах), но используют один Redis‑сервер в localhost:6379. Сейчас они просто вызываются соответствующими функциями.

```
mcp/
├─ run_system.py                    # Главный скрипт запуска всей системы 
├─ README.md                        # Документация с описанием архитектуры 
├─ requirements.txt                 # Зависимости (redis, langchain, etc.) 
├─ redis_manager.py                 # Менеджер для работы с Redis напрямую
├─ redis_web.py                     # Flask web приложение для взаиможействия с redis_manager
├─ app/
│  ├─ config.py                     # Конфигурация (URL и параметры модели, добавятся и другие характеристики)
│  ├─ llm/
│  │  ├─ client.py                  # HTTP-клиент для запросов к Gemma
│  │  └─ prompt.py                  # Системный промпт для LLM (сейчас не используется)
│  └─ agents/                       # Агенты
│     ├─ reader_agent.py
│     ├─ validator_agent.py
│     └─ constructor_agent.py
├─ mcp_servers/                     # Серверные утилиты для агентов, дорабатываются
│  ├─ mcp_server_read.py
│  ├─ mcp_server_valid.py
│  ├─ mcp_server_verify.py
└─ └─ mcp_constructor.py
```

Запуск системы: run_system.py последовательно вызывает три агента с фиксированными данными (демо‑режим).

Связи между файлами и модулями
* run_system.py → импортирует функции из app.agents.* (reader_agent.run_reader, validator_agent.handle_product, constructor_agent.run_constructor).
* app.agents.reader_agent.py → импортирует mcp_servers.mcp_server_read.read_document.
* app.agents.validator_agent.py → импортирует mcp_servers.mcp_server_valid.validate_document, mcp_servers.mcp_server_verify.verify_document, и использует redis напрямую.
* app.agents.constructor_agent.py → импортирует mcp_servers.mcp_constructor.construct_report.
* config.py → используется в app.llm.client


## Зависимости

Нужен пакет `redis` (pip install redis) и работающий сервер Redis на
`localhost:6379`. В примерах HTTP‑запросов к LLM используется
локальный экземпляр Gemma (см. `app/config.py`).

## Запуск системы

### Предварительная подготовка

1. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Запустите Redis**:
   - Убедитесь, что Redis сервер запущен на `localhost:6379`.
   - Если Redis не установлен, скачайте и установите его (например, через Docker: `docker run -d -p 6379:6379 redis`).

3. **Запустите LLM**:
   - Убедитесь, что локальный экземпляр Gemma доступен по URL из `app/config.py` (по умолчанию `http://localhost:8000/v1`).

### Запуск всей системы (демо)

Для демонстрации всей системы используйте скрипт `run_system.py`. Он последовательно запускает все три агента с фиксированными данными:

```bash
python run_system.py
```

**Ожидаемый вывод**:
```
🚀 Запуск системы...

📖 Шаг 1: Reader Agent
[reader] сохраняем документ для PROD-123
Document for PROD-123 appended to Redis list docs:PROD-123.
✅ Документ добавлен в Redis.

🔍 Шаг 2: Validator Agent
[validator] обрабатываем 1 документов для PROD-123
VALIDATE: да
[validator] документ пройден верификацию
✅ Валидация и верификация завершены.

📋 Шаг 3: Constructor Agent
[constructor] сформирован отчёт:
Отчет по изделию PROD-123:
Идентификационный номер: prod-123
...
✅ Отчёт сформирован.

🎉 Система завершила работу!
```

## Управление Redis

Для визуализации и управления данными в Redis используйте скрипт `redis_manager.py` или веб-интерфейс `redis_web.py`:

### Консольный менеджер
```bash
# Показать все ключи и значения
python redis_manager.py list

# Показать значение конкретного ключа
python redis_manager.py get docs:PROD-123

# Удалить ключ
python redis_manager.py delete docs:PROD-123

# Очистить всю базу (с подтверждением)
python redis_manager.py clear
```

### Веб-интерфейс
```bash
python redis_web.py
```
Затем откройте http://localhost:5000 в браузере. Интерфейс позволяет просматривать ключи, их значения, удалять ключи и очищать базу.

Это полезно для отладки и очистки данных между запусками системы.

# Ниже это еще не тестил но в теории должно работать
### Запуск отдельных агентов

Если нужно запустить агентов по отдельности (например, для тестирования или параллельной работы):

1. **Reader Agent**:
   ```bash
   python -m app.agents.reader_agent
   # Или: python app/agents/reader_agent.py
   ```

2. **Validator Agent**:
   ```bash
   python -m app.agents.validator_agent
   # Или: python app/agents/validator_agent.py
   ```

3. **Constructor Agent**:
   ```bash
   python -m app.agents.constructor_agent
   # Или: python app/agents/constructor_agent.py
   ```

**Примечание**: Все агенты работают с фиксированным `product_id = "PROD-123"` и демонстрационными данными. Для реального использования добавьте параметры командной строки (например, через `argparse`).

