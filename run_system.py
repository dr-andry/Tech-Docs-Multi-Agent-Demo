"""Скрипт для запуска всей мульти‑агентной системы в демо‑режиме.

Последовательно запускает три агента:
1. reader_agent — добавляет документ в Redis.
2. validator_agent — проверяет и верифицирует документы.
3. constructor_agent — формирует отчёт.

Все агенты работают с фиксированным product_id = "PROD-123".
Для реального использования добавьте параметры командной строки.
"""

import asyncio
from app.agents.reader_agent import run_reader
from app.agents.validator_agent import handle_product
from app.agents.constructor_agent import run_constructor


async def run_full_system():
    """Запуск всей системы: чтение → валидация → отчёт."""
    product_id = "PROD-123"  # фиксированный для демо

    print("🚀 Запуск системы...")

    # Шаг 1: Чтение документа
    print("\n📖 Шаг 1: Reader Agent")
    
   
    
    # Можно делать запуск если в системе загрузки появился файл
    await run_reader()
    print("✅ Документ добавлен в Redis.")

    # Шаг 2: Валидация и верификация
    print("\n🔍 Шаг 2: Validator Agent")
    await handle_product(product_id)
    print("✅ Валидация и верификация завершены.")

    # Шаг 3: Формирование отчёта
    print("\n📋 Шаг 3: Constructor Agent")
    await run_constructor(product_id)
    print("✅ Отчёт сформирован.")

    print("\n🎉 Система завершила работу!")


def main():
    """Точка входа."""
    asyncio.run(run_full_system())


if __name__ == "__main__":
    main()