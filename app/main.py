
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid

from .database import get_db, create_tables, CarbonEstimate, Conversation, ModelSelectionHistory
from .models import (
    EstimateRequest, 
    CarbonEstimateResponse,
    ModelInfo,
    BatchEstimateRequest,
    BatchEstimateResponse,
    AccuracyAnalysisRequest,
    AccuracyAnalysisResponse,
    ModelPerformanceMetrics,
    ConversationCreateRequest,
    ConversationResponse,
    ModelRecommendationRequest,
    ModelRecommendationResponse,
    ModelComparisonRequest
)
from .estimator import carbon_estimator
from .accuracy_detector import accuracy_detector
from .accuracy_evaluator import accuracy_evaluator
from .code_quality_evaluator import code_quality_evaluator
from .evaluation.validators import response_validator
from .evaluation.metrics import accuracy_metrics
from .model_selector import model_selector
from .context_manager import context_manager
from .config import settings

# Create FastAPI app
app = FastAPI(
    title="Green Model Advisor - Smart Model Selection & Carbon Estimation API",
    description="API for automatically selecting best models based on accuracy and context, with carbon emission tracking",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        print("Creating database tables...")
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error during startup: {e}")
        import traceback
        traceback.print_exc()
@app.get("/")
async def root():
    return {
        "message": "Green Model Advisor Smart Model Selection & Carbon Estimation API",
        "version": "3.0.0",
        "endpoints": {
            "estimate": "/estimate",
            "estimates": "/estimates",
            "models": "/models",
            "stats": "/stats",
            "accuracy": "/accuracy/analyze",
            "performance": "/performance/models",
            "conversations": "/conversations",
            "recommendations": "/recommendations/models"
        }
    }

@app.post("/estimate")
async def create_carbon_estimate(
    request: EstimateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Estimate carbon emissions with automatic model selection based on accuracy and context
    """
    try:
        # Handle conversation context
        conversation_id = request.conversation_id or "auto"
        if conversation_id == "auto" or not conversation_id:
            conversation_id = context_manager.create_conversation()
        
        # Select best model if auto-selection is enabled (only if model_name is "auto")
        selected_model = request.model_name
        
        if request.model_name == "auto":
            try:
                user_preferences = context_manager.get_model_preferences(conversation_id)
                selection_result = model_selector.select_best_model(
                    request.prompt, 
                    context_manager.get_conversation_context(conversation_id),
                    user_preferences
                )
                selected_model = selection_result.get("selected_model", selected_model)
            except Exception as e:
                print(f"Model selection failed, using default: {str(e)}")
        
        # Run carbon estimation with selected model
        try:
            estimate_data = carbon_estimator.estimate_with_codecarbon(
                prompt=request.prompt,
                model_name=selected_model,
                simulate=request.simulate,
                max_tokens=request.max_tokens
            )
        except Exception as e:
            print(f"Carbon estimation error: {str(e)}")
            raise
        
        estimate_data["prompt"] = request.prompt
        
        # Use actual response from the model for accuracy evaluation
        actual_response = estimate_data.get("response_text", "")
        
        # Evaluate accuracy if requested using code quality evaluator
        if request.evaluate_accuracy:
            try:
                # Use code quality evaluator for actual code quality assessment
                eval_result = code_quality_evaluator.evaluate_code(
                    request.prompt, actual_response, selected_model
                )
                # Store both detailed scores and overall accuracy
                overall_acc = eval_result.get("overall_accuracy", 50.0)
                estimate_data["accuracy_scores"] = {"overall_accuracy": overall_acc}
                estimate_data["overall_accuracy"] = overall_acc
                estimate_data["accuracy_level"] = "Good" if overall_acc >= 75 else "Fair" if overall_acc >= 50 else "Poor"
            except Exception as e:
                print(f"Code quality evaluation error: {str(e)}")
                estimate_data["accuracy_scores"] = {"overall_accuracy": 0}
                estimate_data["overall_accuracy"] = 0
        
        # Save to database
        try:
            db_estimate = carbon_estimator.save_estimate(db, estimate_data)
            return {
                "id": db_estimate.id,
                "prompt": db_estimate.prompt,
                "model_name": db_estimate.model_name,
                "provider": db_estimate.provider,
                "tokens_input": db_estimate.tokens_input,
                "tokens_output": db_estimate.tokens_output,
                "total_tokens": db_estimate.total_tokens,
                "inference_time_ms": db_estimate.inference_time_ms,
                "energy_consumed_kwh": db_estimate.energy_consumed_kwh,
                "carbon_emitted_kgco2": db_estimate.carbon_emitted_kgco2,
                "response_text": estimate_data.get("response_text", ""),
                "accuracy_scores": estimate_data.get("accuracy_scores"),
                "overall_accuracy": estimate_data.get("overall_accuracy"),
                "accuracy_level": estimate_data.get("accuracy_level"),
                "estimation_method": db_estimate.estimation_method,
                "created_at": db_estimate.created_at
            }
        except Exception as e:
            print(f"Database save error: {str(e)}")
            raise
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Full error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")

@app.post("/conversations", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreateRequest):
    """Create a new conversation context"""
    try:
        conversation_id = context_manager.create_conversation(request.user_id)
        context = context_manager.get_conversation_context(conversation_id)
        
        if request.title:
            context["title"] = request.title
        
        stats = context_manager.get_conversation_stats(conversation_id)
        
        return ConversationResponse(
            conversation_id=conversation_id,
            user_id=request.user_id,
            title=request.title,
            summary=context["summary"],
            metadata=context,
            created_at=context["created_at"],
            updated_at=context["updated_at"],
            stats=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation creation failed: {str(e)}")

@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Get conversation context and details"""
    try:
        context = context_manager.get_conversation_context(conversation_id)
        if not context:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        stats = context_manager.get_conversation_stats(conversation_id)
        
        return ConversationResponse(
            conversation_id=conversation_id,
            user_id=context["user_id"],
            title=context.get("title"),
            summary=context["summary"],
            metadata=context,
            created_at=context["created_at"],
            updated_at=context["updated_at"],
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@app.post("/recommendations/models", response_model=ModelRecommendationResponse)
async def get_model_recommendations(request: ModelRecommendationRequest):
    """Get model recommendations for a prompt"""
    try:
        # Get conversation context if available
        conversation_context = None
        user_preferences = None
        
        if request.conversation_id:
            conversation_context = context_manager.get_conversation_context(request.conversation_id)
            user_preferences = context_manager.get_model_preferences(request.conversation_id)
        
        # Select best model to get full analysis
        selection_result = model_selector.select_best_model(
            request.prompt,
            conversation_context,
            user_preferences
        )
        
        # Get top K recommendations
        recommendations = model_selector.get_model_recommendations(request.prompt, request.top_k)
        
        return ModelRecommendationResponse(
            recommendations=recommendations,
            prompt_analysis=selection_result["prompt_analysis"],
            conversation_context=conversation_context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

# ... (keep all existing endpoints from previous version)

@app.get("/performance/models", response_model=Dict[str, ModelPerformanceMetrics])
async def get_model_performance(db: Session = Depends(get_db)):
    """Get performance metrics for all models"""
    try:
        estimates = db.query(CarbonEstimate).all()
        estimates_data = []
        
        for estimate in estimates:
            estimate_dict = {
                'model_name': estimate.model_name,
                'accuracy_scores': estimate.accuracy_scores or {},
                'carbon_emitted_kgco2': estimate.carbon_emitted_kgco2,
                'inference_time_ms': estimate.inference_time_ms
            }
            estimates_data.append(estimate_dict)
        
        performance_metrics = accuracy_metrics.calculate_model_performance(estimates_data)
        return performance_metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance calculation failed: {str(e)}")

@app.post("/accuracy/analyze", response_model=AccuracyAnalysisResponse)
async def analyze_accuracy(request: AccuracyAnalysisRequest):
    """Analyze accuracy of a model response"""
    try:
        accuracy_scores = accuracy_detector.detect_accuracy(
            request.prompt, request.response, request.model_name
        )
        
        validation_results = response_validator.validate_response(
            request.prompt, request.response, request.model_name
        )
        
        recommendations = generate_recommendations(accuracy_scores, validation_results)
        
        return AccuracyAnalysisResponse(
            accuracy_scores=accuracy_scores,
            validation_results=validation_results,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accuracy analysis failed: {str(e)}")


@app.get("/models", response_model=Dict[str, Any])
async def get_available_models():
    """Get list of available models with their configurations"""
    try:
        from .estimator import carbon_estimator
        models = carbon_estimator.get_available_models()
        api_status = carbon_estimator.check_api_keys()
        
        return {
            "total_models": len(models),
            "models": models,
            "api_status": api_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {str(e)}")


@app.post("/compare-models", response_model=Dict[str, Any])
async def compare_models(request: Dict[str, Any]):
    """
    Compare multiple models on the same prompt
    Request body should have: prompt, models (list of model names)
    """
    try:
        prompt = request.get("prompt", "")
        models = request.get("models", [])
        
        if not prompt:
            raise ValueError("Prompt is required")
        if not models:
            raise ValueError("At least one model is required")
        
        from .accuracy_evaluator import accuracy_evaluator
        
        # Call each model
        responses = {}
        results = []
        metrics = {}
        
        for model_name in models:
            try:
                estimate_data = carbon_estimator.estimate_with_codecarbon(
                    prompt=prompt,
                    model_name=model_name,
                    simulate=False
                )
                
                response_text = estimate_data.get("response_text", "")
                responses[model_name] = response_text
                
                # Evaluate accuracy if requested using code quality evaluator
                accuracy_scores = None
                if request.get("evaluate_accuracy", True):
                    eval_result = code_quality_evaluator.evaluate_code(
                        prompt, response_text, model_name
                    )
                    accuracy_scores = {"overall_accuracy": eval_result["overall_accuracy"]}
                
                result = {
                    "model_name": model_name,
                    "response_text": response_text[:500],  # Truncate for response
                    "tokens_input": estimate_data["tokens_input"],
                    "tokens_output": estimate_data["tokens_output"],
                    "total_tokens": estimate_data["total_tokens"],
                    "inference_time_ms": estimate_data["inference_time_ms"],
                    "energy_consumed_kwh": estimate_data["energy_consumed_kwh"],
                    "carbon_emitted_kgco2": estimate_data["carbon_emitted_kgco2"],
                    "accuracy_scores": accuracy_scores
                }
                
                results.append(result)
                
                if accuracy_scores:
                    metrics[model_name] = accuracy_scores["overall_accuracy"]
                
            except Exception as e:
                results.append({
                    "model_name": model_name,
                    "error": str(e)
                })
        
        # Find best model by accuracy
        best_model = max(metrics, key=metrics.get) if metrics else results[0]["model_name"]
        best_accuracy = max(metrics.values()) if metrics else 0
        
        # Find lowest carbon
        carbon_results = {r["model_name"]: r["carbon_emitted_kgco2"] for r in results if "carbon_emitted_kgco2" in r}
        lowest_carbon = min(carbon_results, key=carbon_results.get) if carbon_results else None
        
        carbon_diff = ((carbon_results[best_model] - carbon_results[lowest_carbon]) / carbon_results[lowest_carbon] * 100) if lowest_carbon and best_model in carbon_results else 0
        
        return {
            "prompt": prompt,
            "results": results,
            "best_model": best_model,
            "best_accuracy": best_accuracy,
            "lowest_carbon": lowest_carbon,
            "carbon_diff_percentage": carbon_diff
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model comparison failed: {str(e)}")


@app.post("/carbon-impact")
async def calculate_carbon_impact(request: Dict[str, Any]):
    """
    Calculate carbon impact of using a model multiple times
    Request: model_name, num_requests, avg_tokens_per_request
    """
    try:
        model_name = request.get("model_name", "")
        num_requests = request.get("num_requests", 1)
        avg_tokens = request.get("avg_tokens_per_request", 200)
        
        if not model_name:
            raise ValueError("Model name is required")
        
        from .estimator import carbon_estimator
        energy_kwh, carbon_kgco2 = carbon_estimator.estimate_from_tokens(avg_tokens, model_name)
        
        single_carbon = carbon_kgco2
        annual_carbon = single_carbon * 365 * num_requests  # Estimate annual if daily requests
        
        # Tree offset calculation (1 tree absorbs ~20 kg CO2 per year)
        trees_needed = annual_carbon / 20
        
        # Carbon equivalents
        carbon_equivalents = {
            "km_car_driven": annual_carbon / 0.120,  # 0.12 kg CO2 per km
            "trees_planted": trees_needed,
            "kg_coal": annual_carbon / 2.4,  # 2.4 kg CO2 per kg coal
        }
        
        model_config = settings.MODEL_CONFIG.get(model_name, {})
        
        return {
            "model_name": model_name,
            "provider": model_config.get("provider", "unknown"),
            "single_request_carbon_kgco2": round(single_carbon, 6),
            "annual_carbon_estimate_kgco2": round(annual_carbon, 4),
            "energy_kwh": round(energy_kwh, 6),
            "trees_needed_to_offset": round(trees_needed, 2),
            "carbon_equivalent": carbon_equivalents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Carbon impact calculation failed: {str(e)}")


@app.get("/estimate-carbon/{model_name}")
async def get_carbon_estimate(model_name: str):
    """Get carbon estimation for a specific model"""
    try:
        if model_name not in settings.MODEL_CONFIG:
            raise ValueError(f"Unknown model: {model_name}")
        
        from .estimator import carbon_estimator
        config = settings.MODEL_CONFIG[model_name]
        
        # Estimate for 1000 tokens
        energy_kwh, carbon_kgco2 = carbon_estimator.estimate_from_tokens(1000, model_name)
        
        return {
            "model_name": model_name,
            "provider": config["provider"],
            "energy_per_1000_tokens_kwh": round(energy_kwh, 6),
            "carbon_per_1000_tokens_kg": round(carbon_kgco2, 6),
            "max_tokens": config["max_tokens"],
            "cost_per_token": config["cost_per_token"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get carbon estimate: {str(e)}")


def generate_recommendations(accuracy_scores: Dict, validation_results: Dict) -> List[str]:
    """Generate recommendations based on accuracy and validation results"""
    recommendations = []
    
    if accuracy_scores["overall_accuracy"] < 0.7:
        recommendations.append("Consider using a different model or refining your prompt for better accuracy")
    
    if accuracy_scores["factual_accuracy"] < 0.6:
        recommendations.append("Verify factual claims in the response before using them")
    
    if "potential_hallucination" in accuracy_scores["issues_detected"]:
        recommendations.append("Response may contain hallucinations - cross-verify critical information")
    
    if not validation_results.get("overall", {}).get("valid", False):
        recommendations.append("Response validation failed - consider regenerating the response")
    
    if accuracy_scores["completeness"] < 0.5:
        recommendations.append("Response appears incomplete - consider asking follow-up questions")
    
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
