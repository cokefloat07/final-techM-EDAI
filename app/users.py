"""
User and Chat management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import hashlib
import json

from .database import (
    get_db, User, Chat, 
    UserRegisterRequest, UserLoginRequest, UserResponse,
    ChatRequest, ChatResponse, ChatMessage
)

router = APIRouter(prefix="/api", tags=["users", "chats"])


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash


@router.post("/auth/register", response_model=UserResponse)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    password_hash = hash_password(request.password)
    user = User(
        email=request.email,
        full_name=request.full_name,
        password_hash=password_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=UserResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/chats", response_model=ChatResponse)
async def create_chat(request: ChatRequest, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Create a new chat for user"""
    
    print(f"Creating chat for user {user_id}, title: {request.title}")
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    chat_id = str(uuid.uuid4())
    
    # Handle messages - they can be ChatMessage objects or dicts
    messages_data = request.messages or []
    try:
        if messages_data:
            if isinstance(messages_data[0], dict):
                messages_json = json.dumps(messages_data)
            else:
                messages_json = json.dumps([msg.dict() if hasattr(msg, 'dict') else msg for msg in messages_data])
        else:
            messages_json = "[]"
    except Exception as e:
        print(f"Error processing messages: {e}")
        messages_json = "[]"
    
    chat = Chat(
        id=chat_id,
        user_id=user_id,
        title=request.title or "New Chat",
        messages=messages_json,
        # Populate metadata fields
        total_requests=request.total_requests or 0,
        user_prompts=request.user_prompts or [],
        models_used=request.models_used or [],
        total_carbon_emitted_kgco2=request.total_carbon_emitted_kgco2 or 0.0,
        total_energy_consumed_kwh=request.total_energy_consumed_kwh or 0.0,
        average_accuracy=request.average_accuracy or 0.0,
        total_tokens=request.total_tokens or 0,
        is_comparison=request.is_comparison or 0,
        comparison_models=request.comparison_models or [],
        comparison_results=request.comparison_results or {},
        code_generated=request.code_generated,
        execution_time_ms=request.execution_time_ms or 0
    )
    
    try:
        db.add(chat)
        db.commit()
        db.refresh(chat)
        print(f"Chat {chat_id} created successfully")
    except Exception as e:
        print(f"Error creating chat: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat: {str(e)}"
        )
    
    # Parse messages back for response
    if isinstance(chat.messages, str):
        try:
            chat.messages = json.loads(chat.messages)
        except:
            chat.messages = []
    return chat


@router.get("/chats/{user_id}", response_model=list[ChatResponse])
async def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    """Get all chats for a user"""
    print(f"Fetching chats for user {user_id}")
    
    chats = db.query(Chat).filter(Chat.user_id == user_id).all()
    print(f"Found {len(chats)} chats for user {user_id}")
    
    # Parse messages for each chat
    for chat in chats:
        if isinstance(chat.messages, str):
            try:
                chat.messages = json.loads(chat.messages)
            except:
                chat.messages = []
    
    print(f"Returning chats: {[(c.id, c.title) for c in chats]}")
    return chats


@router.get("/chats/{user_id}/{chat_id}", response_model=ChatResponse)
async def get_chat(user_id: int, chat_id: str, db: Session = Depends(get_db)):
    """Get a specific chat"""
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if isinstance(chat.messages, str):
        chat.messages = json.loads(chat.messages)
    
    return chat


@router.put("/chats/{user_id}/{chat_id}", response_model=ChatResponse)
async def update_chat(
    user_id: int,
    chat_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Update a chat (add messages, update title)"""
    print(f"Updating chat {chat_id} for user {user_id}, title: {request.title}, messages: {len(request.messages or [])}")
    
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        print(f"Chat {chat_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Update title if provided
    if request.title:
        chat.title = request.title
    
    # Update messages - normalize and save as-is
    if request.messages:
        try:
            messages_data = request.messages
            # Ensure each message has required fields
            normalized_messages = []
            for msg in messages_data:
                if isinstance(msg, dict):
                    normalized_msg = {
                        **msg,
                        "role": msg.get("role", "assistant"),
                        "content": msg.get("content", msg.get("response", msg.get("response_text", "")))
                    }
                    normalized_messages.append(normalized_msg)
                else:
                    normalized_messages.append(msg)
            
            chat.messages = json.dumps(normalized_messages)
        except Exception as e:
            print(f"Error normalizing messages: {e}")
            chat.messages = json.dumps([])
    else:
        # If messages is empty, try to preserve existing messages
        if not chat.messages:
            chat.messages = json.dumps([])
    
    # Update metadata fields
    if request.total_requests is not None:
        chat.total_requests = request.total_requests
    if request.user_prompts:
        chat.user_prompts = request.user_prompts
    if request.models_used:
        chat.models_used = request.models_used
    if request.total_carbon_emitted_kgco2 is not None:
        chat.total_carbon_emitted_kgco2 = request.total_carbon_emitted_kgco2
    if request.total_energy_consumed_kwh is not None:
        chat.total_energy_consumed_kwh = request.total_energy_consumed_kwh
    if request.average_accuracy is not None:
        chat.average_accuracy = request.average_accuracy
    if request.total_tokens is not None:
        chat.total_tokens = request.total_tokens
    if request.is_comparison is not None:
        chat.is_comparison = request.is_comparison
    if request.comparison_models:
        chat.comparison_models = request.comparison_models
    if request.comparison_results:
        chat.comparison_results = request.comparison_results
    if request.code_generated:
        chat.code_generated = request.code_generated
    if request.execution_time_ms is not None:
        chat.execution_time_ms = request.execution_time_ms
    
    chat.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(chat)
        print(f"Chat {chat_id} updated successfully")
    except Exception as e:
        print(f"Error updating chat: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chat: {str(e)}"
        )
    
    if isinstance(chat.messages, str):
        try:
            chat.messages = json.loads(chat.messages)
        except:
            chat.messages = []
    
    return chat


@router.delete("/chats/{user_id}/{chat_id}")
async def delete_chat(user_id: int, chat_id: str, db: Session = Depends(get_db)):
    """Delete a chat"""
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    db.delete(chat)
    db.commit()
    
    return {"message": "Chat deleted successfully"}


@router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get chat count and message count
    chats = db.query(Chat).filter(Chat.user_id == user_id).all()
    total_chats = len(chats)
    total_messages = 0
    
    for chat in chats:
        messages = json.loads(chat.messages) if isinstance(chat.messages, str) else chat.messages
        total_messages += len(messages)
    
    return {
        "user_id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "total_chats": total_chats,
        "total_messages": total_messages,
        "member_since": user.created_at,
        "last_active": max([chat.updated_at for chat in chats]) if chats else user.created_at
    }
