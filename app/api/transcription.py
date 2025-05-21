from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from typing import Optional
import time
from pathlib import Path

from app.models.transcriber import VoskTranscriber
from app.utils.file_utils import save_upload_file, get_video_file_path, get_transcript_file_path

router = APIRouter()
transcriber = VoskTranscriber()

@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_size: str = Form("medium")
):
    """
    Загрузка видео для транскрибации.
    
    - **file**: видеофайл (MP4, MKV, AVI и т.д.)
    - **model_size**: размер модели Vosk (tiny, base, small, medium, large-v3)
    """
    # Проверка типа файла
    if not file.filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm')):
        raise HTTPException(status_code=400, detail="Поддерживаются только видеофайлы")
    
    # Генерация уникального ID для задачи транскрибации
    task_id = str(uuid.uuid4())
    
    # Сохранение файла
    video_path = get_video_file_path(task_id)
    await save_upload_file(file, video_path)
    
    # Запуск транскрибации в фоновом режиме
    background_tasks.add_task(
        transcribe_video_task, 
        task_id=task_id, 
        video_path=video_path,
        model_size=model_size
    )
    
    return {"task_id": task_id, "status": "processing"}

@router.get("/status/{task_id}")
async def get_transcription_status(task_id: str):
    """
    Проверка статуса транскрибации.
    
    - **task_id**: ID задачи транскрибации
    """
    transcript_path = get_transcript_file_path(task_id)
    
    if os.path.exists(transcript_path):
        return {"task_id": task_id, "status": "completed"}
    
    video_path = get_video_file_path(task_id)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return {"task_id": task_id, "status": "processing"}

@router.get("/result/{task_id}")
async def get_transcription_result(task_id: str):
    """
    Получение результата транскрибации.
    
    - **task_id**: ID задачи транскрибации
    """
    transcript_path = get_transcript_file_path(task_id)
    
    if not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    return {"task_id": task_id, "transcript": transcript}

def transcribe_video_task(task_id: str, video_path: str, model_size: str):
    """
    Фоновая задача для транскрибации видео.
    """
    try:
        # Транскрибация видео
        transcript = transcriber.transcribe(video_path, model_size)
        
        # Сохранение результата
        transcript_path = get_transcript_file_path(task_id)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
            
    except Exception as e:
        # В реальном приложении здесь должна быть обработка ошибок и логирование
        print(f"Ошибка при транскрибации: {str(e)}")
        # Можно создать файл с ошибкой для последующей проверки через API 