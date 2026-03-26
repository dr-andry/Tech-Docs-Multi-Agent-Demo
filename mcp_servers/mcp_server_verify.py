# mcp_server_verify.py

from app.llm.client import GemmaClient

gemma = GemmaClient()

async def verify_document(document_text: str, document_type: str) -> bool:
    """
    Заглушка для верификации данных в документе.
    Проверяет, в пределах ли нормы результаты экспериментов и т.д.
    """
    # Заглушка: использовать LLM для проверки
    prompt = f"Ты эсперт в аудите технических документов прикладного характера. Здесь текст документа: {document_type}. Проверь, являются ли данные в этом документе правильными. Документ: {document_text}... Ответь 'да' или 'нет'."
    
    messages = [{"role": "user", "content": prompt}]
    # Обращение к LLM для получения ответа о верификации документа
    response = await gemma.chat(messages)
    print(f"VERIFY: {response}")
    
    answer = response["content"].strip().lower()
    if "да" in answer:
        return True
    else:
        return False