import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "qwen2.5:3b"
    )
    # Browser

    HEADLESS = True

    SLOW_MO = 300

    # Timeouts

    PAGE_TIMEOUT = 60000

    OTP_TIMEOUT = 300000

    # Session

    SESSION_EXPIRE_MINUTES = 30