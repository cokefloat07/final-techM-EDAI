from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from .config import settings

# Database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False, default="New Chat")
    messages = Column(JSON, default=[])
    
    # Chat metadata and statistics
    total_requests = Column(Integer, default=0)  # Total number of estimates/requests in this chat
    user_prompts = Column(JSON, default=[])  # All user prompts in this chat
    models_used = Column(JSON, default=[])  # List of models used in this chat
    
    # Aggregated statistics
    total_carbon_emitted_kgco2 = Column(Float, default=0.0)  # Total carbon across all requests
    total_energy_consumed_kwh = Column(Float, default=0.0)  # Total energy across all requests
    average_accuracy = Column(Float, default=0.0)  # Average accuracy across all requests
    total_tokens = Column(Integer, default=0)  # Total tokens used
    
    # Comparison data (if comparing models)
    is_comparison = Column(Integer, default=0)  # 1 if this is a comparison, 0 if single estimate
    comparison_models = Column(JSON, default=[])  # Models compared in this chat
    comparison_results = Column(JSON, default={})  # Full comparison results with all 3 models
    
    # Additional metadata
    code_generated = Column(Text, nullable=True)  # Store any generated code
    execution_time_ms = Column(Integer, default=0)  # Time taken to generate response
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CarbonEstimate(Base):
    __tablename__ = "carbon_estimates"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    model_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=True)

    # Token information
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Timing information
    inference_time_ms = Column(Integer, default=0)

    # Carbon estimates
    energy_consumed_kwh = Column(Float, default=0.0)
    carbon_emitted_kgco2 = Column(Float, default=0.0)

    # Accuracy information
    accuracy_scores = Column(JSON, default={})
    overall_accuracy = Column(Float, default=0.0)
    accuracy_level = Column(String(50), default="unknown")
    validation_results = Column(JSON, default={})
    detected_issues = Column(JSON, default=[])

    # Context and selection
    conversation_id = Column(String(100), nullable=True)
    is_best_model_selected = Column(String(5), default="false")
    selection_confidence = Column(Float, default=0.0)
    model_selection_rationale = Column(Text, nullable=True)
    candidate_models = Column(JSON, default=[])

    # Additional metadata
    estimation_method = Column(String(50), default="codecarbon")
    country_iso_code = Column(String(10), default="IND")
    grid_intensity = Column(Float, default=0.708)

    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    metadata_json = Column('metadata', JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ModelSelectionHistory(Base):
    __tablename__ = "model_selection_history"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), nullable=True)
    prompt = Column(Text, nullable=True)
    selected_model = Column(String(100), nullable=False)
    confidence_score = Column(Float, default=0.0)
    candidate_models = Column(JSON, default=[])
    model_scores = Column(JSON, default={})
    selection_rationale = Column(Text, nullable=True)
    prompt_analysis = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class UserRegisterRequest(BaseModel):
    email: str
    full_name: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "securepassword123"
            }
        }

class UserLoginRequest(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None  # "estimate", "comparison", "message"
    role: Optional[str] = "assistant"  # "user" or "assistant" - default to assistant
    content: Optional[str] = ""  # Default to empty string
    prompt: Optional[str] = None
    response: Optional[str] = None
    timestamp: Optional[str] = None
    model: Optional[str] = None
    carbon: Optional[float] = None
    energy: Optional[float] = None
    tokens: Optional[int] = None
    accuracy: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    carbon_estimate: Optional[float] = None
    response_text: Optional[str] = None
    models_compared: Optional[List[str]] = None
    
    class Config:
        extra = "allow"  # Allow additional fields not defined in the schema

class ChatRequest(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = []  # Accept any message format
    
    # Chat metadata
    total_requests: Optional[int] = 0
    user_prompts: Optional[List[str]] = []
    models_used: Optional[List[str]] = []
    
    # Aggregated statistics
    total_carbon_emitted_kgco2: Optional[float] = 0.0
    total_energy_consumed_kwh: Optional[float] = 0.0
    average_accuracy: Optional[float] = 0.0
    total_tokens: Optional[int] = 0
    
    # Comparison data
    is_comparison: Optional[int] = 0
    comparison_models: Optional[List[str]] = []
    comparison_results: Optional[Dict[str, Any]] = {}
    
    # Additional metadata
    code_generated: Optional[str] = None
    execution_time_ms: Optional[int] = 0
    
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "title": "Example Chat",
                "messages": [
                    {
                        "id": "msg-1",
                        "type": "estimate",
                        "role": "assistant",
                        "content": "Response text",
                        "prompt": "User prompt",
                        "model": "gpt-4"
                    }
                ],
                "total_requests": 1,
                "user_prompts": ["User prompt"],
                "models_used": ["gpt-4"],
                "total_carbon_emitted_kgco2": 0.00012,
                "total_energy_consumed_kwh": 0.00005,
                "average_accuracy": 85.5,
                "total_tokens": 450
            }
        }

class ChatResponse(BaseModel):
    id: str
    user_id: int
    title: str
    messages: List[Dict[str, Any]]  # Return raw message objects
    
    # Chat metadata
    total_requests: Optional[int] = 0
    user_prompts: Optional[List[str]] = []
    models_used: Optional[List[str]] = []
    
    # Aggregated statistics
    total_carbon_emitted_kgco2: Optional[float] = 0.0
    total_energy_consumed_kwh: Optional[float] = 0.0
    average_accuracy: Optional[float] = 0.0
    total_tokens: Optional[int] = 0
    
    # Comparison data
    is_comparison: Optional[int] = 0
    comparison_models: Optional[List[str]] = []
    comparison_results: Optional[Dict[str, Any]] = {}
    
    # Additional metadata
    code_generated: Optional[str] = None
    execution_time_ms: Optional[int] = 0
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EstimateRequest(BaseModel):
    prompt: str = Field(..., description="The input prompt for the model")
    model_name: Optional[str] = Field(None, description="Specific model name or 'auto' for automatic selection")
    provider: Optional[str] = Field(None, description="Provider name")
    simulate: bool = Field(True, description="Whether to simulate or use real model")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for output")
    evaluate_accuracy: bool = Field(True, description="Whether to evaluate accuracy")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    auto_select_model: bool = Field(True, description="Whether to automatically select best model")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Explain the impact of climate change on biodiversity",
                "model_name": "auto",
                "simulate": True,
                "max_tokens": 500,
                "evaluate_accuracy": True,
                "conversation_id": "auto",
                "auto_select_model": True
            }
        }

class AccuracyScores(BaseModel):
    factual_accuracy: float
    completeness: float
    relevance: float
    coherence: float
    technical_correctness: float
    overall_accuracy: float
    accuracy_level: str
    issues_detected: List[str]
    confidence_score: float

class ValidationResult(BaseModel):
    valid: bool
    score: float
    issues: List[str]

class ModelSelectionResult(BaseModel):
    selected_model: str
    confidence_score: float
    model_scores: Dict[str, float]
    prompt_analysis: Dict[str, Any]
    rationale: str
    candidate_models: List[str]
    timestamp: str

class CarbonEstimateResponse(BaseModel):
    id: int
    prompt: str
    model_name: str
    provider: str
    tokens_input: int
    tokens_output: int
    total_tokens: int
    inference_time_ms: int
    energy_consumed_kwh: float
    carbon_emitted_kgco2: float
    # Accuracy fields
    accuracy_scores: AccuracyScores
    overall_accuracy: float
    accuracy_level: str
    validation_results: Dict[str, ValidationResult]
    detected_issues: List[str]
    # Context and selection fields (NEW)
    conversation_id: Optional[str]
    is_best_model_selected: bool
    selection_confidence: float
    model_selection_rationale: Optional[str]
    candidate_models: List[str]
    # Original fields
    estimation_method: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ModelInfo(BaseModel):
    name: str
    provider: str
    energy_per_token: float
    cost_per_token: float
    max_tokens: int
    capabilities: List[str]

class BatchEstimateRequest(BaseModel):
    requests: List[EstimateRequest]

class BatchEstimateResponse(BaseModel):
    estimates: List[CarbonEstimateResponse]
    total_energy_kwh: float
    total_carbon_kgco2: float

class AccuracyAnalysisRequest(BaseModel):
    prompt: str
    response: str
    model_name: str

class AccuracyAnalysisResponse(BaseModel):
    accuracy_scores: AccuracyScores
    validation_results: Dict[str, ValidationResult]
    recommendations: List[str]

class ModelPerformanceMetrics(BaseModel):
    model_name: str
    total_requests: int
    avg_accuracy: float
    avg_carbon_kgco2: float
    avg_response_time_ms: float
    accuracy_std_dev: float
    carbon_efficiency: float

class ConversationCreateRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="User identifier")
    title: Optional[str] = Field(None, description="Conversation title")

class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: Optional[str]
    title: Optional[str]
    summary: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    stats: Dict[str, Any]

class ModelRecommendationRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    top_k: int = 3

class ModelRecommendation(BaseModel):
    rank: int
    model_name: str
    score: float
    confidence: str
    rationale: str

class ModelRecommendationResponse(BaseModel):
    recommendations: List[ModelRecommendation]
    prompt_analysis: Dict[str, Any]
    conversation_context: Optional[Dict[str, Any]]
