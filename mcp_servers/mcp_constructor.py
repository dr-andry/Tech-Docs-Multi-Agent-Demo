# mcp_servers/mcp_constructor.py

import redis

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def construct_report(product_id: str) -> str:
    """
    Заглушка для формирования отчета по документации.
    Берет все документы из Redis по product_id и составляет отчет.
    """
    # Предполагаем, что документы хранятся под ключами product_id или product_id_1, etc.
    # Для простоты: взять по product_id
    # теперь храним в списке; извлекаем все документы
    key = f"doc:{product_id}"
    documents = r.lrange(key, 0, -1)
    if not documents:
        return "Документы не найдены."
    
    # Заглушка: составить отчет, объединяя все тексты
    combined = "\n\n".join(documents)
    report = f"Отчет по изделию {product_id}:\n{combined}\n\nКонец отчета."
    return report