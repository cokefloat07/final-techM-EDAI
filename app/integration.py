"""
Integration Configuration for Frontend and Backend Pipeline
This file sets up the complete pipeline for the Green Model Advisor application
"""

import os
from pathlib import Path

# ============================================
# PROJECT STRUCTURE
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent

# Backend
BACKEND_DIR = PROJECT_ROOT / "app"
BACKEND_PORT = 8000
BACKEND_URL = "http://localhost:8000"

# Frontend
FRONTEND_DIR = PROJECT_ROOT / "client"
FRONTEND_PORT = 5173
FRONTEND_URL = "http://localhost:5173"

# Database
DATABASE_DIR = PROJECT_ROOT / "carbon_estimates.db"

# ============================================
# ENVIRONMENT SETUP
# ============================================

# API Endpoints
API_ENDPOINTS = {
    "estimate": f"{BACKEND_URL}/estimate",
    "compare_models": f"{BACKEND_URL}/compare-models",
    "models": f"{BACKEND_URL}/models",
    "carbon_impact": f"{BACKEND_URL}/carbon-impact",
    "estimate_carbon": f"{BACKEND_URL}/estimate-carbon",
    "accuracy_analyze": f"{BACKEND_URL}/accuracy/analyze",
    "conversations": f"{BACKEND_URL}/conversations",
    "recommendations": f"{BACKEND_URL}/recommendations/models",
}

# ============================================
# CORS CONFIGURATION
# ============================================

CORS_CONFIG = {
    "allow_origins": [
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# ============================================
# FRONTEND CONFIGURATION
# ============================================

FRONTEND_CONFIG = {
    "title": "Green Model Advisor",
    "description": "Smart Model Selection with Carbon Tracking",
    "apiBaseUrl": BACKEND_URL,
    "models": [
        {
            "name": "gemini-pro",
            "provider": "Google",
            "category": "Fast",
            "emoji": "⚡"
        },
        {
            "name": "gemini-1.5-pro",
            "provider": "Google",
            "category": "Advanced",
            "emoji": "🚀"
        },
        {
            "name": "claude-3-opus",
            "provider": "Anthropic",
            "category": "Premium",
            "emoji": "👑"
        },
        {
            "name": "claude-3-sonnet",
            "provider": "Anthropic",
            "category": "Balanced",
            "emoji": "⚖️"
        },
        {
            "name": "mistral-7b",
            "provider": "HuggingFace",
            "category": "Open Source",
            "emoji": "🔓"
        },
    ]
}

print("""
╔════════════════════════════════════════════════════════════╗
║     Green Model Advisor - Integration Configuration       ║
╚════════════════════════════════════════════════════════════╝

📁 Project Structure:
   Backend:  {BACKEND_DIR}
   Frontend: {FRONTEND_DIR}
   Database: {DATABASE_DIR}

🔌 Network Configuration:
   Backend:  {BACKEND_URL}
   Frontend: {FRONTEND_URL}

🛠️  API Endpoints:
   - /estimate (POST) - Single model estimation
   - /compare-models (POST) - Compare multiple models
   - /models (GET) - List available models
   - /carbon-impact (POST) - Calculate carbon impact
   - /accuracy/analyze (POST) - Analyze accuracy

✅ CORS enabled for frontend integration
✅ Database configured
✅ All endpoints documented
""".format(
    BACKEND_DIR=BACKEND_DIR,
    FRONTEND_DIR=FRONTEND_DIR,
    DATABASE_DIR=DATABASE_DIR,
    BACKEND_URL=BACKEND_URL,
    FRONTEND_URL=FRONTEND_URL,
))
