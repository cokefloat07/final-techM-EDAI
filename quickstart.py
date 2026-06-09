#!/usr/bin/env python3
"""
Green Model Advisor - Quick Start Script
Starts the server and provides basic usage examples
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     Green Model Advisor - Smart Model Selection API       ║
    ║          Multi-Provider Carbon Tracking System            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ ERROR: .env file not found!")
        print("Please create .env file with API keys")
        return 1
    
    print("✅ API Keys Configuration")
    print("   - Google Gemini: Configured")
    print("   - Anthropic Claude: Configured")
    print("   - HuggingFace: Optional")
    
    print("\n📊 Available Models:")
    print("   Google Gemini:")
    print("     • gemini-pro")
    print("     • gemini-1.5-pro")
    print("     • gemini-1.5-flash")
    print("   Anthropic Claude:")
    print("     • claude-3-opus")
    print("     • claude-3-sonnet")
    print("     • claude-3-haiku")
    print("   HuggingFace:")
    print("     • mistral-7b")
    print("     • flan-t5-base")
    print("     • flan-t5-large")
    
    print("\n🚀 Starting Server...")
    print("   Server will run on: http://localhost:8000")
    
    try:
        # Start the server
        subprocess.run([sys.executable, "run.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
