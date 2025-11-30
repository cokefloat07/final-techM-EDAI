import time
from typing import Dict, Any
from sqlalchemy.orm import Session

from .database import CarbonEstimate
from .model_runner import model_runner
from .config import settings

class SimpleCarbonEstimator:
    def __init__(self):
        self.model_config = settings.MODEL_CONFIG
    
    def estimate_carbon(self, prompt: str, model_name: str, 
                       simulate: bool = True, max_tokens: int = None) -> Dict[str, Any]:
        """
        Simple carbon estimation without CodeCarbon dependency
        """
        # Run model inference
        if simulate:
            inference_result = model_runner.simulate_inference(prompt, model_name, max_tokens)
        else:
            inference_result = model_runner.run_real_model(prompt, model_name, max_tokens)
        
        # Estimate energy based on tokens and model efficiency
        energy_kwh, carbon_kgco2 = self.estimate_from_tokens_and_time(
            inference_result["total_tokens"],
            inference_result["inference_time_ms"],
            model_name
        )
        
        # Combine results
        result = {
            **inference_result,
            "energy_consumed_kwh": energy_kwh,
            "carbon_emitted_kgco2": carbon_kgco2,
            "estimation_method": "simple_model_based",
            "grid_intensity": settings.DEFAULT_GRID_INTENSITY,
            "country_iso_code": settings.DEFAULT_COUNTRY_ISO_CODE
        }
        
        return result
    
    def estimate_from_tokens_and_time(self, total_tokens: int, inference_time_ms: int, model_name: str) -> tuple:
        """
        Estimate energy and carbon based on tokens and inference time
        """
        model_config = self.model_config.get(model_name, {})
        
        # Method 1: Token-based estimation
        energy_per_token = model_config.get("energy_per_token", 0.00001)
        energy_from_tokens = total_tokens * energy_per_token
        
        # Method 2: Time-based estimation (assuming average power consumption)
        # Typical GPU power: 150-300W, CPU: 65-125W
        inference_time_hr = inference_time_ms / (1000 * 3600)  # Convert ms to hours
        
        if "flan" in model_name.lower():
            # Smaller model, likely CPU-based
            avg_power_watts = 100  # watts
        else:
            # Larger model, likely GPU-based
            avg_power_watts = 200  # watts
            
        energy_from_time = (avg_power_watts * inference_time_hr) / 1000  # Convert to kWh
        
        # Use the maximum of both methods as a conservative estimate
        energy_kwh = max(energy_from_tokens, energy_from_time)
        carbon_kgco2 = energy_kwh * settings.DEFAULT_GRID_INTENSITY
        
        return energy_kwh, carbon_kgco2
    
    def save_estimate(self, db: Session, estimate_data: Dict[str, Any]) -> CarbonEstimate:
        """
        Save carbon estimate to database
        """
        db_estimate = CarbonEstimate(
            prompt=estimate_data.get("prompt", ""),
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
            grid_intensity=estimate_data.get("grid_intensity", 0.708)
        )
        
        db.add(db_estimate)
        db.commit()
        db.refresh(db_estimate)
        
        return db_estimate

simple_estimator = SimpleCarbonEstimator()