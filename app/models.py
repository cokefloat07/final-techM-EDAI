from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================
# ✅ USER & AUTH MODELS (moved here from database.py)
# ============================================================

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


# ============================================================
# ✅ CHAT MESSAGE MODEL
# ============================================================

class ChatMessage(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    role: Optional[str] = "assistant"
    content: Optional[str] = ""
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
        extra = "allow"


# ============================================================
# ✅ CHAT REQUEST / RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = []

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
                        "model": "gemini-2.5-flash"
                    }
                ],
                "total_requests": 1,
                "user_prompts": ["User prompt"],
                "models_used": ["gemini-2.5-flash"],
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
    messages: List[Dict[str, Any]]

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


# ============================================================
# ✅ ESTIMATE MODELS
# ============================================================

class EstimateRequest(BaseModel):
    prompt: str = Field(..., description="The input prompt for the model")
    model_name: str = Field(
        ...,
        description="Model name: gemini-2.5-flash, mistral-7b, nvidia-qwen-coder, or 'auto'"
    )
    provider: Optional[str] = Field(None, description="Provider name")
    simulate: bool = Field(True, description="Whether to simulate or use real model")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for output")
    evaluate_accuracy: bool = Field(True, description="Whether to evaluate accuracy")
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID for context ('auto' to auto-create)"
    )
    auto_select_model: bool = Field(False, description="Whether to automatically select best model")

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
        protected_namespaces = ()


# ============================================================
# ✅ ACCURACY MODELS
# ============================================================

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


# ============================================================
# ✅ CARBON ESTIMATE RESPONSE
# ============================================================

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
    accuracy_scores: Optional[AccuracyScores] = None
    overall_accuracy: Optional[float] = None
    accuracy_level: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None
    detected_issues: Optional[List[str]] = None
    estimation_method: str
    created_at: datetime

    class Config:
        from_attributes = True
        protected_namespaces = ()


# ============================================================
# ✅ MODEL INFO
# ============================================================

class ModelInfo(BaseModel):
    name: str
    provider: str
    energy_per_token: float
    cost_per_token: float
    max_tokens: int

    class Config:
        protected_namespaces = ()


# ============================================================
# ✅ BATCH MODELS
# ============================================================

class BatchEstimateRequest(BaseModel):
    requests: List[EstimateRequest]

    class Config:
        protected_namespaces = ()


class BatchEstimateResponse(BaseModel):
    estimates: List[CarbonEstimateResponse]
    total_energy_kwh: float
    total_carbon_kgco2: float

    class Config:
        protected_namespaces = ()


# ============================================================
# ✅ ACCURACY ANALYSIS
# ============================================================

class AccuracyAnalysisRequest(BaseModel):
    prompt: str
    response: str
    model_name: str

    class Config:
        protected_namespaces = ()


class AccuracyAnalysisResponse(BaseModel):
    accuracy_scores: AccuracyScores
    validation_results: Dict[str, Any]
    recommendations: List[str]

    class Config:
        protected_namespaces = ()


# ============================================================
# ✅ PERFORMANCE METRICS
# ============================================================

class ModelPerformanceMetrics(BaseModel):
    model_name: str
    total_requests: int
    avg_accuracy: float
    avg_carbon_kgco2: float
    avg_response_time_ms: float
    accuracy_std_dev: float
    carbon_efficiency: float

    class Config:
        protected_namespaces = ()


# ============================================================
# ✅ CONVERSATION MODELS
# ============================================================

class ConversationCreateRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="User identifier")
    title: Optional[str] = Field(None, description="Conversation title")

    class Config:
        protected_namespaces = ()


class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: Optional[str]
    title: Optional[str]
    summary: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    stats: Dict[str, Any]

    class Config:
        protected_namespaces = ()


# ============================================================
# ✅ MODEL RECOMMENDATION
# ============================================================

class ModelRecommendationRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    top_k: int = 3

    class Config:
        protected_namespaces = ()


class ModelRecommendation(BaseModel):
    rank: int
    model_name: str
    score: float
    confidence: str
    rationale: str

    class Config:
        protected_namespaces = ()


class ModelRecommendationResponse(BaseModel):
    recommendations: List[ModelRecommendation]
    prompt_analysis: Dict[str, Any]
    conversation_context: Optional[Dict[str, Any]]

    class Config:
        protected_namespaces = ()


# ============================================================
# ✅ MODEL COMPARISON
# ============================================================

class ModelComparisonRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to send to all models")
    models: List[str] = Field(..., description="List of model names to compare")
    evaluate_accuracy: bool = Field(True, description="Whether to evaluate accuracy")

    class Config:
        protected_namespaces = ()


class ModelComparisonResult(BaseModel):
    model_name: str
    response_text: str
    tokens_input: int
    tokens_output: int
    total_tokens: int
    inference_time_ms: float
    energy_consumed_kwh: float
    carbon_emitted_kgco2: float
    accuracy_scores: Optional[AccuracyScores] = None

    class Config:
        protected_namespaces = ()


class ModelComparisonResponse(BaseModel):
    prompt: str
    results: List[ModelComparisonResult]
    best_model: str
    best_accuracy: float
    lowest_carbon: str
    carbon_diff_percentage: float

    class Config:
        protected_namespaces = ()


# ============================================================
# ✅ OTHER MODELS
# ============================================================

class AvailableModelsResponse(BaseModel):
    total_models: int
    models: Dict[str, Dict[str, Any]]
    api_status: Dict[str, bool]

    class Config:
        protected_namespaces = ()


class CarbonImpactRequest(BaseModel):
    model_name: str = Field(..., description="Model name")
    num_requests: int = Field(default=1, description="Number of requests")
    avg_tokens_per_request: int = Field(default=200, description="Average tokens per request")

    class Config:
        protected_namespaces = ()


class CarbonImpactResponse(BaseModel):
    model_name: str
    provider: str
    single_request_carbon_kgco2: float
    annual_carbon_estimate_kgco2: float
    energy_kwh: float
    trees_needed_to_offset: float
    carbon_equivalent: str

    class Config:
        protected_namespaces = ()


class BestModelForTaskRequest(BaseModel):
    task_description: str = Field(..., description="Description of the task")
    constraints: Optional[Dict[str, Any]] = Field(
        None,
        description="Constraints like max_carbon, max_tokens, etc."
    )
    priority: str = Field(
        "balanced",
        description="'accuracy', 'speed', 'carbon', or 'balanced'"
    )


class BestModelForTaskResponse(BaseModel):
    recommended_model: str
    score: float
    reasoning: str
    alternative_models: List[str]
    estimated_metrics: Dict[str, float]