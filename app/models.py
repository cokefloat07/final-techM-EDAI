
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class EstimateRequest(BaseModel):
    prompt: str = Field(..., description="The input prompt for the model")
    model_name: str = Field(..., description="Model name: gemini-pro, flash, claude, flan-t5-base, or 'auto' for automatic selection")
    provider: Optional[str] = Field(None, description="Provider name")
    simulate: bool = Field(True, description="Whether to simulate or use real model")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for output")
    evaluate_accuracy: bool = Field(True, description="Whether to evaluate accuracy")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context ('auto' to auto-create)")
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
    # Accuracy fields (optional if not evaluated)
    accuracy_scores: Optional[AccuracyScores] = None
    overall_accuracy: Optional[float] = None
    accuracy_level: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None
    detected_issues: Optional[List[str]] = None
    # Original fields
    estimation_method: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        protected_namespaces = ()

class ModelInfo(BaseModel):
        class Config:
            protected_namespaces = ()
        name: str
        provider: str
        energy_per_token: float
        cost_per_token: float
        max_tokens: int

class BatchEstimateRequest(BaseModel):
        class Config:
            protected_namespaces = ()
        requests: List[EstimateRequest]

class BatchEstimateResponse(BaseModel):
        class Config:
            protected_namespaces = ()
        estimates: List[CarbonEstimateResponse]
        total_energy_kwh: float
        total_carbon_kgco2: float

class AccuracyAnalysisRequest(BaseModel):
        class Config:
            protected_namespaces = ()
        prompt: str
        response: str
        model_name: str

class AccuracyAnalysisResponse(BaseModel):
        class Config:
            protected_namespaces = ()
        accuracy_scores: AccuracyScores
        validation_results: Dict[str, Any]
        recommendations: List[str]

class ModelPerformanceMetrics(BaseModel):
        class Config:
            protected_namespaces = ()
        model_name: str
        total_requests: int
        avg_accuracy: float
        avg_carbon_kgco2: float
        avg_response_time_ms: float
        accuracy_std_dev: float
        carbon_efficiency: float

class ConversationCreateRequest(BaseModel):
        class Config:
            protected_namespaces = ()
        user_id: Optional[str] = Field(None, description="User identifier")
        title: Optional[str] = Field(None, description="Conversation title")


class ConversationResponse(BaseModel):
        class Config:
            protected_namespaces = ()
        conversation_id: str
        user_id: Optional[str]
        title: Optional[str]
        summary: Optional[str]
        metadata: Dict[str, Any]
        created_at: datetime
        updated_at: datetime
        stats: Dict[str, Any]


class ModelRecommendationRequest(BaseModel):
        class Config:
            protected_namespaces = ()
        prompt: str
        conversation_id: Optional[str] = None
        top_k: int = 3


class ModelRecommendation(BaseModel):
        class Config:
            protected_namespaces = ()
        rank: int
        model_name: str
        score: float
        confidence: str
        rationale: str


class ModelRecommendationResponse(BaseModel):
        class Config:
            protected_namespaces = ()
        recommendations: List[ModelRecommendation]
        prompt_analysis: Dict[str, Any]
        conversation_context: Optional[Dict[str, Any]]


# New models for multi-model comparison and detailed analysis
class ModelComparisonRequest(BaseModel):
        class Config:
            protected_namespaces = ()
        prompt: str = Field(..., description="The prompt to send to all models")
        models: List[str] = Field(..., description="List of model names to compare")
        evaluate_accuracy: bool = Field(True, description="Whether to evaluate accuracy")


class ModelComparisonResult(BaseModel):
        class Config:
            protected_namespaces = ()
        model_name: str
        response_text: str
        tokens_input: int
        tokens_output: int
        total_tokens: int
        inference_time_ms: float
        energy_consumed_kwh: float
        carbon_emitted_kgco2: float
        accuracy_scores: Optional[AccuracyScores] = None


class ModelComparisonResponse(BaseModel):
        class Config:
            protected_namespaces = ()
        prompt: str
        results: List[ModelComparisonResult]
        best_model: str
        best_accuracy: float
        lowest_carbon: str
        carbon_diff_percentage: float


class AvailableModelsResponse(BaseModel):
        class Config:
            protected_namespaces = ()
        total_models: int
        models: Dict[str, Dict[str, Any]]
        api_status: Dict[str, bool]


class CarbonImpactRequest(BaseModel):
        class Config:
            protected_namespaces = ()
        model_name: str = Field(..., description="Model name")
        num_requests: int = Field(default=1, description="Number of requests to estimate")
        avg_tokens_per_request: int = Field(default=200, description="Average tokens per request")


class CarbonImpactResponse(BaseModel):
        class Config:
            protected_namespaces = ()
        model_name: str
        provider: str
        single_request_carbon_kgco2: float
        annual_carbon_estimate_kgco2: float
        energy_kwh: float
        trees_needed_to_offset: float
        carbon_equivalent: str


class BestModelForTaskRequest(BaseModel):
    task_description: str = Field(..., description="Description of the task")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Constraints like max_carbon, max_tokens, etc.")
    priority: str = Field("balanced", description="'accuracy', 'speed', 'carbon', or 'balanced'")


class BestModelForTaskResponse(BaseModel):
    recommended_model: str
    score: float
    reasoning: str
    alternative_models: List[str]
    estimated_metrics: Dict[str, float]
