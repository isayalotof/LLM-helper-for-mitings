from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import os
import json

from app.models.summarizer import LLMSummarizer
from app.utils.file_utils import get_transcript_file_path, get_summary_file_path

router = APIRouter()
summarizer = LLMSummarizer()

@router.post("/{task_id}")
async def summarize_transcript(
    task_id: str,
    background_tasks: BackgroundTasks,
    model_name: Optional[str] = "llama3"
):
    """
    Запуск суммаризации транскрипции.
    
    - **task_id**: ID задачи транскрибации
    - **model_name**: название модели для суммаризации (llama3, mistral, saiga)
    """
    transcript_path = get_transcript_file_path(task_id)
    
    if not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    # Запуск суммаризации в фоновом режиме
    background_tasks.add_task(
        summarize_transcript_task,
        task_id=task_id,
        transcript_path=transcript_path,
        model_name=model_name
    )
    
    return {"task_id": task_id, "status": "processing"}

@router.get("/status/{task_id}")
async def get_summarization_status(task_id: str):
    """
    Проверка статуса суммаризации.
    
    - **task_id**: ID задачи
    """
    summary_path = get_summary_file_path(task_id)
    
    if os.path.exists(summary_path):
        return {"task_id": task_id, "status": "completed"}
    
    transcript_path = get_transcript_file_path(task_id)
    if not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return {"task_id": task_id, "status": "processing"}

@router.get("/result/{task_id}")
async def get_summarization_result(task_id: str):
    """
    Получение результата суммаризации.
    
    - **task_id**: ID задачи
    """
    summary_path = get_summary_file_path(task_id)
    
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=404, detail="Суммаризация не найдена")
    
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
    
    return summary_data

def summarize_transcript_task(task_id: str, transcript_path: str, model_name: str):
    """
    Фоновая задача для суммаризации транскрипции.
    """
    try:
        # Чтение транскрипции
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        
        # Суммаризация
        summary = summarizer.summarize(transcript, model_name)
        
        # Сохранение результата
        summary_path = get_summary_file_path(task_id)
        
        # Структурированный результат
        summary_data = {
            "task_id": task_id,
            "summary": summary["summary"],
            "key_points": summary["key_points"],
            "action_items": summary["action_items"],
            "participants": summary["participants"]
        }
        
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        # В реальном приложении здесь должна быть обработка ошибок и логирование
        print(f"Ошибка при суммаризации: {str(e)}") 