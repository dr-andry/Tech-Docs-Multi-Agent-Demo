"""Обёртка для визуализации и управления данными в Redis.

Позволяет:
- Просматривать все ключи и их значения.
- Получать значение конкретного ключа.
- Удалять ключ или очищать всю базу.

Использование:
    python redis_manager.py list          # Показать все ключи и значения
    python redis_manager.py get <key>     # Показать значение ключа
    python redis_manager.py delete <key>  # Удалить ключ
    python redis_manager.py clear         # Очистить всю базу
"""

import redis
import sys
import argparse


class RedisManager:
    """Менеджер для работы с Redis."""

    def __init__(self, host='localhost', port=6379, decode_responses=True):
        self.r = redis.Redis(host=host, port=port, decode_responses=decode_responses)

    def list_all(self):
        """Показать все ключи и их значения."""
        keys = self.r.keys('*')
        if not keys:
            print("Redis пуст.")
            return

        print("Ключи и значения в Redis:")
        for key in keys:
            value_type = self.r.type(key)
            if value_type == 'string':
                value = self.r.get(key)
                print(f"  {key} (string): {value}")
            elif value_type == 'list':
                items = self.r.lrange(key, 0, -1)
                print(f"  {key} (list, {len(items)} элементов):")
                for i, item in enumerate(items):
                    print(f"    [{i}]: {item}")
            elif value_type == 'set':
                items = self.r.smembers(key)
                print(f"  {key} (set, {len(items)} элементов): {list(items)}")
            else:
                print(f"  {key} ({value_type}): <не поддерживается для отображения>")

    def get_value(self, key):
        """Показать значение ключа."""
        if not self.r.exists(key):
            print(f"Ключ '{key}' не существует.")
            return

        value_type = self.r.type(key)
        if value_type == 'string':
            value = self.r.get(key)
            print(f"{key}: {value}")
        elif value_type == 'list':
            items = self.r.lrange(key, 0, -1)
            print(f"{key} (list):")
            for i, item in enumerate(items):
                print(f"  [{i}]: {item}")
        elif value_type == 'set':
            items = self.r.smembers(key)
            print(f"{key} (set): {list(items)}")
        else:
            print(f"Тип данных '{value_type}' не поддерживается для отображения.")

    def delete_key(self, key):
        """Удалить ключ."""
        if self.r.delete(key) > 0:
            print(f"Ключ '{key}' удалён.")
        else:
            print(f"Ключ '{key}' не найден.")

    def clear_all(self):
        """Очистить всю базу данных."""
        self.r.flushdb()
        print("Вся база данных Redis очищена.")


def main():
    parser = argparse.ArgumentParser(description="Управление Redis для проекта MCP.")
    parser.add_argument('command', choices=['list', 'get', 'delete', 'clear'],
                        help="Команда: list (показать всё), get <key> (показать ключ), delete <key> (удалить ключ), clear (очистить всё)")
    parser.add_argument('key', nargs='?', help="Ключ для команд get или delete")

    args = parser.parse_args()

    manager = RedisManager()

    try:
        if args.command == 'list':
            manager.list_all()
        elif args.command == 'get':
            if not args.key:
                print("Ошибка: укажите ключ для команды 'get'.")
                sys.exit(1)
            manager.get_value(args.key)
        elif args.command == 'delete':
            if not args.key:
                print("Ошибка: укажите ключ для команды 'delete'.")
                sys.exit(1)
            manager.delete_key(args.key)
        elif args.command == 'clear':
            confirm = input("Вы уверены, что хотите очистить всю базу? (y/N): ")
            if confirm.lower() == 'y':
                manager.clear_all()
            else:
                print("Отменено.")
    except redis.ConnectionError:
        print("Ошибка подключения к Redis. Убедитесь, что сервер запущен на localhost:6379.")
        sys.exit(1)


if __name__ == "__main__":
    main()