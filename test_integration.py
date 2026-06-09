#!/usr/bin/env python3
"""
Green Model Advisor - Integration Test Script
Tests all backend endpoints and verifies system integration
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_PROMPT = "What is artificial intelligence and its applications?"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def test_connection():
    """Test if backend is running"""
    print_test("Backend Connection")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is running on {API_BASE_URL}")
            return True
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {API_BASE_URL}")
        print_info("Start the backend with: python run.py")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_models_endpoint():
    """Test /models endpoint"""
    print_test("/models Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Models endpoint returned data")
            
            models = data.get("models", {})
            print_info(f"Total model groups: {len(models)}")
            
            total_models = sum(len(v) for v in models.values())
            print_info(f"Total models available: {total_models}")
            
            api_status = data.get("api_status", {})
            for provider, status in api_status.items():
                status_text = f"{Colors.GREEN}✓ Online{Colors.END}" if status else f"{Colors.RED}✗ Offline{Colors.END}"
                print_info(f"{provider}: {status_text}")
            
            return True, models
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False, {}
    except Exception as e:
        print_error(f"Error: {e}")
        return False, {}

def test_single_estimate(models):
    """Test /estimate endpoint"""
    print_test("/estimate Endpoint (Single Model)")
    try:
        # Get first available model
        model_name = None
        for group_models in models.values():
            if group_models:
                model_name = group_models[0]
                break
        
        if not model_name:
            print_error("No models available to test")
            return False
        
        payload = {
            "prompt": TEST_PROMPT,
            "model_name": model_name
        }
        
        print_info(f"Testing with model: {model_name}")
        print_info(f"Prompt: {TEST_PROMPT[:50]}...")
        
        response = requests.post(
            f"{API_BASE_URL}/estimate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Estimation completed")
            
            if "carbon_emitted_grams" in data:
                carbon = data["carbon_emitted_grams"]
                print_info(f"Carbon emissions: {carbon:.6f}g")
            
            if "energy_consumed_kwh" in data:
                energy = data["energy_consumed_kwh"]
                print_info(f"Energy consumed: {energy:.6f} kWh")
            
            if "tokens_used" in data:
                tokens = data["tokens_used"]
                print_info(f"Tokens used: {tokens}")
            
            if "accuracy_scores" in data:
                accuracy = data["accuracy_scores"].get("overall_accuracy", 0)
                print_info(f"Overall accuracy: {accuracy:.1f}%")
            
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print_error("Request timed out (model might be slow)")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_compare_models(models):
    """Test /compare-models endpoint"""
    print_test("/compare-models Endpoint")
    try:
        # Get multiple models
        model_list = []
        for group_models in models.values():
            model_list.extend(group_models[:1])  # One from each group
            if len(model_list) >= 2:
                break
        
        if len(model_list) < 2:
            print_error("Need at least 2 models to compare")
            return False
        
        payload = {
            "prompt": TEST_PROMPT,
            "model_names": model_list[:2]
        }
        
        print_info(f"Comparing models: {', '.join(model_list[:2])}")
        
        response = requests.post(
            f"{API_BASE_URL}/compare-models",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Comparison completed")
            
            results = data.get("results", [])
            print_info(f"Comparison results for {len(results)} models:")
            
            for result in results:
                print_info(f"  - {result.get('model_name', 'Unknown')}:")
                print_info(f"    Carbon: {result.get('carbon_emitted_kgco2', 0):.6f} kg")
                print_info(f"    Energy: {result.get('energy_consumed_kwh', 0):.6f} kWh")
            
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_carbon_impact():
    """Test /carbon-impact endpoint"""
    print_test("/carbon-impact Endpoint")
    try:
        payload = {
            "carbon_grams": 0.001,
            "energy_kwh": 0.0001
        }
        
        response = requests.post(
            f"{API_BASE_URL}/carbon-impact",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Carbon impact calculation completed")
            
            print_info(f"Impact description: {data.get('impact_description', 'N/A')}")
            print_info(f"Mitigation tips: {data.get('mitigation_tips', ['N/A'])}")
            
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_health():
    """Test /health endpoint"""
    print_test("/health Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print_info(f"Status: {data.get('status', 'unknown')}")
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Green Model Advisor - Integration Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    results = {}
    
    # Test 1: Connection
    if not test_connection():
        print(f"\n{Colors.RED}Cannot proceed without backend connection{Colors.END}")
        sys.exit(1)
    results['connection'] = True
    
    # Test 2: Health check
    results['health'] = test_health()
    
    # Test 3: Models endpoint
    success, models = test_models_endpoint()
    results['models'] = success
    
    if not models:
        print(f"\n{Colors.RED}No models available{Colors.END}")
        sys.exit(1)
    
    # Test 4: Single estimate
    results['estimate'] = test_single_estimate(models)
    
    # Test 5: Compare models
    results['compare'] = test_compare_models(models)
    
    # Test 6: Carbon impact
    results['carbon_impact'] = test_carbon_impact()
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All tests passed! System is ready to use.{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠ Some tests failed. Check configuration and try again.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
