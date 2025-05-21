import os
from pathlib import Path
from fastapi import UploadFile
import shutil

# Базовые пути для хранения файлов
VIDEO_DIR = Path("app/data/videos")
TRANSCRIPT_DIR = Path("app/data/transcripts")
SUMMARY_DIR = Path("app/data/summaries")

# Создание директорий, если они не существуют
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """
    Сохранение загруженного файла.
    
    Args:
        upload_file: Загруженный файл
        destination: Путь назначения
        
    Returns:
        Путь к сохраненному файлу
    """
    # Убедимся, что директория существует
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    # Сохранение файла
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return destination

def get_video_file_path(task_id: str) -> str:
    """
    Получение пути к видеофайлу по ID задачи.
    """
    return str(VIDEO_DIR / f"{task_id}.mp4")

def get_transcript_file_path(task_id: str) -> str:
    """
    Получение пути к файлу транскрипции по ID задачи.
    """
    return str(TRANSCRIPT_DIR / f"{task_id}.txt")

def get_summary_file_path(task_id: str) -> str:
    """
    Получение пути к файлу суммаризации по ID задачи.
    """
    return str(SUMMARY_DIR / f"{task_id}.json")

def extract_audio_from_video(video_path: str, audio_path: str) -> str:
    """
    Извлечение аудио из видео.
    
    Args:
        video_path: Путь к видеофайлу
        audio_path: Путь для сохранения аудио
        
    Returns:
        Путь к аудиофайлу
    """
    try:
        # Импортируем moviepy только при необходимости для ускорения загрузки приложения
        from moviepy.editor import VideoFileClip
        
        video = VideoFileClip(video_path)
        
        # Vosk требует моно WAV файл с частотой 16 кГц и 16-битным PCM
        video.audio.write_audiofile(
            audio_path,
            codec='pcm_s16le',  # 16-битный PCM
            fps=16000,          # 16 кГц
            nbytes=2,           # 16 бит
            ffmpeg_params=["-ac", "1"]  # моно (один канал)
        )
        video.close()
        
        return audio_path
    except Exception as e:
        # В реальном приложении здесь должна быть обработка ошибок и логирование
        print(f"Ошибка при извлечении аудио: {str(e)}")
        raise 