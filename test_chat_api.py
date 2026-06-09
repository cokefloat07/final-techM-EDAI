#!/usr/bin/env python3
"""
Test script to verify chat API endpoints are working
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    response = requests.post(
        f"{API_BASE_URL}/api/auth/register",
        json={
            "email": f"test_user_{datetime.now().timestamp()}@example.com",
            "full_name": "Test User",
            "password": "testpass123"
        }
    )
    print(f"Status: {response.status_code}")
    user = response.json()
    print(f"Response: {json.dumps(user, indent=2, default=str)}")
    return user

def test_login(email, password):
    """Test user login"""
    print("\n=== Testing User Login ===")
    response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    print(f"Status: {response.status_code}")
    user = response.json()
    print(f"Response: {json.dumps(user, indent=2, default=str)}")
    return user

def test_create_chat(user_id):
    """Test creating a chat"""
    print("\n=== Testing Create Chat ===")
    response = requests.post(
        f"{API_BASE_URL}/api/chats?user_id={user_id}",
        json={
            "title": "Test Chat",
            "messages": [
                {
                    "id": "msg-1",
                    "type": "estimate",
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "model": "test-model",
                    "carbon": 0.001,
                    "energy": 0.05,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    )
    print(f"Status: {response.status_code}")
    chat = response.json()
    print(f"Response: {json.dumps(chat, indent=2, default=str)}")
    return chat

def test_get_chats(user_id):
    """Test getting user chats"""
    print("\n=== Testing Get User Chats ===")
    response = requests.get(f"{API_BASE_URL}/api/chats/{user_id}")
    print(f"Status: {response.status_code}")
    chats = response.json()
    print(f"Response: {json.dumps(chats, indent=2, default=str)}")
    return chats

def test_update_chat(user_id, chat_id):
    """Test updating a chat"""
    print("\n=== Testing Update Chat ===")
    response = requests.put(
        f"{API_BASE_URL}/api/chats/{user_id}/{chat_id}",
        json={
            "title": "Updated Chat Title",
            "messages": [
                {
                    "id": "msg-1",
                    "type": "estimate",
                    "prompt": "Updated prompt",
                    "response": "Updated response",
                    "model": "updated-model",
                    "carbon": 0.002,
                    "energy": 0.1,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": "msg-2",
                    "type": "message",
                    "prompt": "Second message",
                    "response": "Second response",
                    "model": "test-model",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    )
    print(f"Status: {response.status_code}")
    chat = response.json()
    print(f"Response: {json.dumps(chat, indent=2, default=str)}")
    return chat

if __name__ == "__main__":
    try:
        # Register new user
        user = test_register()
        user_id = user["id"]
        email = user["email"]
        
        # Login
        logged_in_user = test_login(email, "testpass123")
        
        # Create chat
        chat = test_create_chat(user_id)
        chat_id = chat["id"]
        
        # Get chats
        chats = test_get_chats(user_id)
        
        # Update chat
        updated_chat = test_update_chat(user_id, chat_id)
        
        # Get chats again to verify updates
        final_chats = test_get_chats(user_id)
        
        print("\n=== All Tests Completed Successfully ===")
        
    except Exception as e:
        print(f"\n!!! Error: {e}")
        import traceback
        traceback.print_exc()
