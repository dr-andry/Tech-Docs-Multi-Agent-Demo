"""Агент, который занимается валидацией и верификацией документов.

Он получает идентификатор продукта, извлекает все тексты из Redis и прогоняет
каждый через LLM-функции проверки. Невалидные документы автоматически
удаляются из Redis (это реализует ``mcp_server_valid``), результаты
верификации просто логируются.

Такой агент можно запускать периодически или по событию, для каждого
product_id по очереди.
"""

import asyncio
import json
# import redis
import redis
from typing import List

from mcp_servers.mcp_server_valid import validate_document
from mcp_servers.mcp_server_verify import verify_document

# коннектор к Redis, используется в нескольких функциях
_r = redis.Redis(host="localhost", port=6379, decode_responses=True)


async def handle_product(product_id: str) -> None:
    """Проверить и верифицировать все документы по product_id."""
    key = f"unprocessed_docs"
    docs: List[str] = _r.lrange(key, 0, -1)
    _r.delete(key)

    if not docs:
        print(f"[validator] для {product_id} документов не найдено")
        return

    print(f"[validator] обрабатываем {len(docs)} документов для {product_id}")

    # последовательно проверяем каждый документ
    for doc in docs:
        doc = json.loads(doc)
        
        doc_type = doc['doc_type']
        doc_id = doc['doc_id']
        doc_text = doc['text']

        valid = await validate_document(doc_text, product_id)
        if not valid:
            print(f"[validator] документ удалён как невалидный")
            # при удалении список в Redis сокращается, но мы
            # продолжаем работать со старой копией ``docs``
            continue

        verified = await verify_document(doc_text, doc_type)
        print(f"[validator] документ {'пройден' if verified else 'НЕ пройден'} верификацию")
        _r.rpush(f'doc:{product_id}', doc_text)



# async def handle_product(product_id: str) -> None:
#     # print(f"[validator] Начинаем обработку для product_id={product_id}")
#     # while True:
#     #     result = await _r.blpop("unprocessed_docs", timeout=1)
#     #     if not result:
#     #         print("Not result")
#     #         break

#     print(f"[validator] Начинаем обработку для product_id={product_id}")

#     while True:
#         # Ожидаем документ из очереди с таймаутом 1 секунда
#         result = await _r.blpop("unprocessed_docs", timeout=1)

#         # _, doc_json = result

#         # print(result)
        
#         _, doc_json = result
#         try:
#             doc_data = json.loads(doc_json)
#         except json.JSONDecodeError:
#             continue
        
#         doc_id = doc_data.get("doc_id")
#         if doc_id != product_id:
#             # Не наш продукт — возвращаем в очередь
#             await _r.lpush("unprocessed_docs", doc_json)
#             continue
        
#         # Проверки
#         valid = await validate_document(doc_data["text"], doc_id)
#         if not valid:
#             continue
        
#         verified = await verify_document(doc_data["text"])
#         if not verified:
#             continue
        
#         # Сохраняем
#         doc_data["processed"] = True
#         await _r.set(f"doc:{doc_id}", json.dumps(doc_data))
#         print(f"[validator] Документ {doc_id} сохранён")


async def main():
    # для примера обрабатываем один фиксированный ID;
    # в реальности можно читать очередь, аргументы, CLI и т.п.
    product_id = "PROD-123"
    await handle_product()


if __name__ == "__main__":
    asyncio.run(main())
