import time
import os
from codecarbon import EmissionsTracker
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
import json

from .database import CarbonEstimate
from .model_api_client import model_api_client
from .config import settings

class CarbonEstimator:
    def __init__(self):
        self.model_config = settings.MODEL_CONFIG
        self.model_api_client = model_api_client
    
    def estimate_with_codecarbon(self, prompt: str, model_name: str, 
                               simulate: bool = True, max_tokens: int = None) -> Dict[str, Any]:
        """
        Estimate carbon emissions using CodeCarbon tracker with actual model API calls
        """
        # Create output directory for CodeCarbon
        os.makedirs("./codecarbon_output", exist_ok=True)
        
        # Start CodeCarbon tracker
        tracker = EmissionsTracker(
            project_name=f"model-inference-{model_name}",
            measure_power_secs=1,
            output_dir="./codecarbon_output",
            log_level="ERROR"  # Reduce verbosity
        )
        
        try:
            tracker.start()
            
            # Call model API
            response_text, metadata, inference_time_ms = self.model_api_client.call_model(
                model_name, 
                prompt
            )
            
            # Stop tracker and get emissions
            emissions_kg = tracker.stop()
            
            # For CodeCarbon v2, we get direct emissions in kgCO2
            carbon_kgco2 = emissions_kg if emissions_kg else 0.0
            
            # Estimate energy from carbon and grid intensity
            energy_kwh = carbon_kgco2 / settings.DEFAULT_GRID_INTENSITY if carbon_kgco2 > 0 else 0.0
            
            # If CodeCarbon doesn't provide reliable data (zero or very small), use token-based estimation
            # Threshold: 0.000000001 kg (1 nanogram) - if CodeCarbon gives less, it's unreliable
            if carbon_kgco2 < 0.000000001:
                energy_kwh, carbon_kgco2 = self.estimate_from_tokens(
                    metadata["total_tokens"], 
                    model_name
                )
                estimation_method = "token_based"
            else:
                estimation_method = "codecarbon"
            
            # Combine results
            result = {
                "prompt": prompt,
                "model_name": model_name,
                "provider": metadata["provider"],
                "tokens_input": metadata["tokens_input"],
                "tokens_output": metadata["tokens_output"],
                "total_tokens": metadata["total_tokens"],
                "inference_time_ms": inference_time_ms,
                "energy_consumed_kwh": energy_kwh,
                "carbon_emitted_kgco2": carbon_kgco2,
                "estimation_method": estimation_method,
                "grid_intensity": settings.DEFAULT_GRID_INTENSITY,
                "country_iso_code": settings.DEFAULT_COUNTRY_ISO_CODE,
                "response_text": response_text
            }
            
            return result
            
        except Exception as e:
            try:
                tracker.stop()
            except:
                pass
            raise e
    
    def estimate_from_tokens(self, total_tokens: int, model_name: str) -> Tuple[float, float]:
        """
        Fallback estimation using token-based approach
        Returns: (energy_kwh, carbon_kgco2)
        """
        model_config = self.model_config.get(model_name, {})
        energy_per_token = model_config.get("energy_per_token", 0.00001)  # kWh per token
        
        energy_kwh = total_tokens * energy_per_token
        carbon_kgco2 = energy_kwh * settings.DEFAULT_GRID_INTENSITY
        
        return energy_kwh, carbon_kgco2
    
    def save_estimate(self, db: Session, estimate_data: Dict[str, Any], 
                     accuracy_scores: Dict[str, Any] = None) -> CarbonEstimate:
        """
        Save carbon estimate to database with optional accuracy scores
        """
        # Convert accuracy_scores dict to JSON string for storage
        accuracy_json = json.dumps(accuracy_scores) if accuracy_scores else None
        
        db_estimate = CarbonEstimate(
            prompt=estimate_data.get("prompt", ""),
            response_text=estimate_data.get("response_text", ""),
            model_name=estimate_data["model_name"],
            provider=estimate_data["provider"],
            tokens_input=estimate_data["tokens_input"],
            tokens_output=estimate_data["tokens_output"],
            total_tokens=estimate_data["total_tokens"],
            inference_time_ms=estimate_data["inference_time_ms"],
            energy_consumed_kwh=estimate_data["energy_consumed_kwh"],
            carbon_emitted_kgco2=estimate_data["carbon_emitted_kgco2"],
            estimation_method=estimate_data["estimation_method"],
            country_iso_code=estimate_data.get("country_iso_code", "IND"),
            grid_intensity=estimate_data.get("grid_intensity", 0.708),
            accuracy_scores=None  # Will be set separately if needed
        )
        
        db.add(db_estimate)
        db.commit()
        db.refresh(db_estimate)
        
        return db_estimate
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get all available models with their configuration and API availability"""
        return self.model_api_client.get_available_models()
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return self.model_api_client.validate_api_keys()

carbon_estimator = CarbonEstimator()