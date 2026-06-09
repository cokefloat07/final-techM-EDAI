#!/usr/bin/env python3
"""
Direct backend test - bypassing HTTP to see exact errors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.estimator import carbon_estimator
from app.config import settings

print("Testing backend components directly...")
print("-" * 60)

# Test 1: Check API keys
print("\n1. Checking API Keys...")
print(f"   GOOGLE_API_KEY: {bool(settings.GOOGLE_API_KEY)}")
print(f"   ANTHROPIC_API_KEY: {bool(settings.ANTHROPIC_API_KEY)}")  
print(f"   HUGGINGFACE_API_TOKEN: {bool(settings.HUGGINGFACE_API_KEY)}")

if not settings.GOOGLE_API_KEY:
    print("   ✗ ERROR: Missing GOOGLE_API_KEY in .env")
if not settings.ANTHROPIC_API_KEY:
    print("   ✗ ERROR: Missing ANTHROPIC_API_KEY in .env")
if not settings.HUGGINGFACE_API_KEY:
    print("   ✗ ERROR: Missing HUGGINGFACE_API_TOKEN in .env")

# Test 2: Test carbon estimator
print("\n2. Testing Carbon Estimator...")
try:
    print("   Attempting simple estimation...")
    result = carbon_estimator.estimate_with_codecarbon(
        prompt="What is AI?",
        model_name="gemini-pro",
        simulate=False
    )
    print("   ✓ Success!")
    print(f"   Carbon: {result.get('carbon_emitted_kgco2')} kg")
    print(f"   Energy: {result.get('energy_consumed_kwh')} kWh")
    print(f"   Tokens: {result.get('total_tokens')}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "-" * 60)
print("Diagnostics complete!")
