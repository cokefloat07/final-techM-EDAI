import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    # 🔧 PRODUCTION FIX: Use environment-aware database path
    # On Render, use /tmp directory (writable in free tier)
    IS_PRODUCTION = os.getenv("RENDER", False) or os.getenv("PRODUCTION", False)
    
    if IS_PRODUCTION:
        DEFAULT_DB_PATH = "/tmp/green_model_advisor.db"
    else:
        DEFAULT_DB_PATH = str(BASE_DIR / "green_model_advisor.db")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    
    # 🔧 Frontend URL for CORS (used in main.py)
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER", "") or os.getenv("OPENROUTER_API_KEY", "")
    GROQ_API_KEY = os.getenv("groq", "") or os.getenv("GROQ_API_KEY", "")
    NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY", "")
    NVIDIA_NIM_URL = os.getenv("NVIDIA_NIM_URL", "https://integrate.api.nvidia.com/v1")
    
    # Carbon Estimation - India specific
    DEFAULT_GRID_INTENSITY = float(os.getenv("GRID_INTENSITY", "0.708"))
    DEFAULT_COUNTRY_ISO_CODE = os.getenv("COUNTRY_ISO_CODE", "IND")
    
    # 🔧 CodeCarbon output directory (use /tmp on production)
    CODECARBON_OUTPUT_DIR = "/tmp/codecarbon_output" if IS_PRODUCTION else "./codecarbon_output"
    
    # Model Configuration with API Provider Details
    MODEL_CONFIG = {
        "gemini-2.5-flash": {
            "provider": "google",
            "api_name": "Gemini 2.5 Flash",
            "model_id": "gemini-2.5-flash",
            "energy_per_token": 0.000012,
            "cost_per_token": 0.000015,
            "max_tokens": 1000000,
            "requires_api_key": True,
            "api_key_env": "GOOGLE_API_KEY"
        },
        "mistral-7b": {
            "provider": "huggingface",
            "api_name": "Mistral 7B",
            "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
            "energy_per_token": 0.000008,
            "cost_per_token": 0.000001,
            "max_tokens": 32768,
            "requires_api_key": True,
            "api_key_env": "HUGGINGFACE_API_KEY"
        },
        "flan-t5-base": {
            "provider": "huggingface",
            "api_name": "Flan-T5 Base",
            "model_id": "google/flan-t5-base",
            "energy_per_token": 0.000008,
            "cost_per_token": 0.000001,
            "max_tokens": 512,
            "requires_api_key": True,
            "api_key_env": "HUGGINGFACE_API_KEY"
        },
        "flan-t5-large": {
            "provider": "huggingface",
            "api_name": "Flan-T5 Large",
            "model_id": "google/flan-t5-large",
            "energy_per_token": 0.000012,
            "cost_per_token": 0.0000015,
            "max_tokens": 512,
            "requires_api_key": True,
            "api_key_env": "HUGGINGFACE_API_KEY"
        },
        "mistral-7b-openrouter": {
            "provider": "openrouter",
            "api_name": "Mistral 7B Instruct (OpenRouter)",
            "model_id": "mistralai/mistral-7b-instruct:free",
            "energy_per_token": 0.000008,
            "cost_per_token": 0.0,
            "max_tokens": 32768,
            "requires_api_key": True,
            "api_key_env": "OPENROUTER_API_KEY"
        },
        "nvidia-qwen-coder": {
            "provider": "nvidia-nim",
            "api_name": "Qwen 2.5 Coder 32B (NVIDIA NIM)",
            "model_id": "qwen/qwen2.5-coder-32b-instruct",
            "energy_per_token": 0.000008,
            "cost_per_token": 0.0,
            "max_tokens": 32768,
            "requires_api_key": True,
            "api_key_env": "NVIDIA_NIM_API_KEY"
        }
    }

settings = Settings()