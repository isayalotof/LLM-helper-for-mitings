from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import json
from typing import List, Optional

from app.models.chat_model import ChatModel
from app.utils.file_utils import get_transcript_file_path, get_summary_file_path

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    task_id: str
    messages: List[Message]
    model_name: Optional[str] = "llama3"

class ChatResponse(BaseModel):
    task_id: str
    response: str

@router.post("/")
async def chat_with_context(request: ChatRequest) -> ChatResponse:
    """
    Отправка сообщения в чат с контекстом встречи.
    
    - **task_id**: ID задачи транскрибации/суммаризации
    - **messages**: список сообщений
    - **model_name**: название модели для чата (llama3, mistral, saiga)
    """
    task_id = request.task_id
    
    # Проверка наличия транскрипции и суммаризации
    transcript_path = get_transcript_file_path(task_id)
    summary_path = get_summary_file_path(task_id)
    
    if not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    # Загрузка контекста
    context = {}
    
    # Загрузка транскрипции
    with open(transcript_path, "r", encoding="utf-8") as f:
        context["transcript"] = f.read()
    
    # Загрузка суммаризации, если есть
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            context["summary"] = json.load(f)
    
    # Создание или получение модели чата
    chat_model = get_chat_model(request.model_name)
    
    # Преобразование сообщений
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Генерация ответа
    response = chat_model.generate_response(messages, context)
    
    return ChatResponse(task_id=task_id, response=response)

# Кэш моделей для повторного использования
_chat_models = {}

def get_chat_model(model_name: str) -> ChatModel:
    """
    Получение экземпляра модели чата.
    """
    if model_name not in _chat_models:
        _chat_models[model_name] = ChatModel(model_name=model_name)
    
    return _chat_models[model_name] 