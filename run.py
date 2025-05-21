import os
import sys
import uvicorn
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла (если есть)
try:
    load_dotenv()
except ImportError:
    pass

def main():
    """
    Функция для запуска приложения.
    """
    # Получение настроек из переменных окружения или значений по умолчанию
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    reload = os.getenv("APP_RELOAD", "True").lower() in ("true", "1", "t")
    
    # Установка Vosk в качестве модели по умолчанию
    if not os.getenv("WHISPER_DEFAULT_MODEL"):
        os.environ["WHISPER_DEFAULT_MODEL"] = "medium"  # Средний размер Vosk
    
    print(f"Запуск сервера на {host}:{port} (reload={reload})")
    
    # Запуск приложения
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )

if __name__ == "__main__":
    main() 