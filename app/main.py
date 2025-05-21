from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from app.api.transcription import router as transcription_router
from app.api.summarization import router as summarization_router
from app.api.chat import router as chat_router

app = FastAPI(title="MeetingSummarizer AI", description="API для транскрибации и анализа видеовстреч")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(transcription_router, prefix="/api/transcribe", tags=["Транскрибация"])
app.include_router(summarization_router, prefix="/api/summarize", tags=["Суммаризация"])
app.include_router(chat_router, prefix="/api/chat", tags=["Чат"])

# Создание директорий для данных, если они не существуют
os.makedirs("app/data/videos", exist_ok=True)
os.makedirs("app/data/transcripts", exist_ok=True)
os.makedirs("app/data/summaries", exist_ok=True)

# Монтирование статических файлов для фронтенда
app.mount("/", StaticFiles(directory="app/frontend/static", html=True), name="static") 