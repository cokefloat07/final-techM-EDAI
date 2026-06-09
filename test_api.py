#!/usr/bin/env python3
"""
Test the Green Model Advisor API endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("\n=== Testing GET / ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_models():
    """Test available models endpoint"""
    print("\n=== Testing GET /models ===")
    try:
        response = requests.get(f"{BASE_URL}/models")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total models: {data['total_models']}")
        print(f"API Status: {data['api_status']}")
        print("\nAvailable Models:")
        for model_name, model_info in data['models'].items():
            print(f"  {model_name}:")
            print(f"    Provider: {model_info['provider']}")
            print(f"    Energy per token: {model_info['energy_per_token']}")
            print(f"    API Available: {model_info['api_available']}")
    except Exception as e:
        print(f"Error: {e}")

def test_carbon_impact():
    """Test carbon impact calculation"""
    print("\n=== Testing POST /carbon-impact ===")
    try:
        payload = {
            "model_name": "gemini-pro",
            "num_requests": 365,
            "avg_tokens_per_request": 200
        }
        response = requests.post(f"{BASE_URL}/carbon-impact", json=payload)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_carbon_estimate():
    """Test carbon estimate for a model"""
    print("\n=== Testing GET /estimate-carbon/{model_name} ===")
    try:
        response = requests.get(f"{BASE_URL}/estimate-carbon/claude-3-sonnet")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Green Model Advisor API Test Suite")
    print("=" * 50)
    print("Base URL:", BASE_URL)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    sleep(2)
    
    # Run tests
    test_root()
    test_models()
    test_carbon_estimate()
    test_carbon_impact()
    
    print("\n" + "=" * 50)
    print("Tests completed!")
