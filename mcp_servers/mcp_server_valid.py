# mcp_server_valid.py

import redis
from app.llm.client import GemmaClient  # Или как в llm_node


# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

gemma = GemmaClient()

async def validate_document(document_text: str, product_id: str) -> bool:
    """
    Заглушка для валидации документа с помощью LLM.
    Проверяет, все ли заполнено (таблицы, подписи и т.д.).
    Если не валидно, удаляет из Redis.
    """
    # Заглушка: использовать LLM для проверки

    prompt = (
        "<|system|>"
        "Ты эксперт в аудите документов технического содержания."
        "Ты должен проверить, является ли этот документ законченным" #: все таблицы заполнены, есть все подписи у рисунков, мысли текста изложены имеют смысловое завершение."
        f"Документ: {document_text}"
        "Ты должен строго ответить 'да' или 'нет'"
        "</s>\n<|agent|>: "
        )
    
    messages = [{"role": "user", "content": prompt}]
    # Обращение к LLM для получения ответа о валидности документа
    response = await gemma.chat(messages)
    
    answer = response["content"].strip().lower()
    print(f"VALIDATE: {answer}")
    if "да" in answer:
        return True
    else:
        # Удалить этот конкретный документ из списка
        key = f"docs:{product_id}"
        r.lrem(key, 0, document_text)
        print(f"Removed one document for {product_id} from Redis due to validation failure.")
        return False