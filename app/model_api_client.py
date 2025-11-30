"""
Model API Client - Unified interface for calling different LLM providers
Supports: Google Gemini, Anthropic Claude, HuggingFace models
"""

import os
import time
from typing import Dict, List, Tuple, Optional, Any
from .config import settings
import requests
import json

class ModelAPIClient:
    """Unified client for calling different LLM providers"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.huggingface_api_key = settings.HUGGINGFACE_API_KEY
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.groq_api_key = settings.GROQ_API_KEY
        self.nvidia_nim_api_key = settings.NVIDIA_NIM_API_KEY
        self.model_config = settings.MODEL_CONFIG
        
    def call_model(self, model_name: str, prompt: str) -> Tuple[str, Dict[str, Any], float]:
        """
        Call a model and return response with metadata
        
        Args:
            model_name: Model key from MODEL_CONFIG
            prompt: Input prompt for the model
            
        Returns:
            Tuple of (response_text, metadata, inference_time_ms)
            metadata includes: tokens_input, tokens_output, total_tokens, provider
        """
        if model_name not in self.model_config:
            raise ValueError(f"Unknown model: {model_name}")
        
        config = self.model_config[model_name]
        provider = config["provider"]
        
        start_time = time.time()
        
        try:
            if provider == "google":
                response, metadata = self._call_google(model_name, prompt, config)
            elif provider == "anthropic":
                response, metadata = self._call_anthropic(model_name, prompt, config)
            elif provider == "huggingface":
                response, metadata = self._call_huggingface(model_name, prompt, config)
            elif provider == "openrouter":
                response, metadata = self._call_openrouter(model_name, prompt, config)
            elif provider == "groq":
                response, metadata = self._call_groq(model_name, prompt, config)
            elif provider == "nvidia-nim":
                response, metadata = self._call_nvidia_nim(model_name, prompt, config)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            inference_time_ms = (time.time() - start_time) * 1000
            return response, metadata, inference_time_ms
            
        except Exception as e:
            raise Exception(f"Error calling {model_name}: {str(e)}")
    
    def _call_google(self, model_name: str, prompt: str, config: Dict) -> Tuple[str, Dict]:
        """Call Google Gemini API"""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        
        genai.configure(api_key=self.google_api_key)
        
        try:
            model = genai.GenerativeModel(config["model_id"])
            
            # Count input tokens (estimate for now)
            input_tokens = len(prompt.split())
            
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Count output tokens (estimate)
            output_tokens = len(response_text.split())
            
            metadata = {
                "tokens_input": input_tokens,
                "tokens_output": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "provider": "google",
                "model_name": model_name,
                "model_id": config["model_id"]
            }
            
            return response_text, metadata
            
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")
    
    def _call_anthropic(self, model_name: str, prompt: str, config: Dict) -> Tuple[str, Dict]:
        """Call Anthropic Claude API"""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
        
        try:
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            # Count input tokens (estimate for now)
            input_tokens = len(prompt.split())
            
            message = client.messages.create(
                model=config["model_id"],
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Count output tokens (estimate)
            output_tokens = len(response_text.split())
            
            metadata = {
                "tokens_input": input_tokens,
                "tokens_output": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "provider": "anthropic",
                "model_name": model_name,
                "model_id": config["model_id"]
            }
            
            return response_text, metadata
            
        except Exception as e:
            raise Exception(f"Anthropic Claude API error: {str(e)}")
    
    def _call_huggingface(self, model_name: str, prompt: str, config: Dict) -> Tuple[str, Dict]:
        """Call HuggingFace API"""
        if not self.huggingface_api_key:
            raise ValueError("HUGGINGFACE_API_KEY not configured")
        
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError("huggingface-hub not installed. Run: pip install huggingface-hub")
        
        try:
            client = InferenceClient(api_key=self.huggingface_api_key)
            
            # Count input tokens (estimate for now)
            input_tokens = len(prompt.split())
            
            response = client.text_generation(
                prompt,
                model=config["model_id"],
                max_new_tokens=512
            )
            
            response_text = response
            
            # Count output tokens (estimate)
            output_tokens = len(response_text.split())
            
            metadata = {
                "tokens_input": input_tokens,
                "tokens_output": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "provider": "huggingface",
                "model_name": model_name,
                "model_id": config["model_id"]
            }
            
            return response_text, metadata
            
        except Exception as e:
            raise Exception(f"HuggingFace API error: {str(e)}")
    
    def _call_openrouter(self, model_name: str, prompt: str, config: Dict) -> Tuple[str, Dict]:
        """Call OpenRouter API"""
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": config["model_id"],
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2048
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            
            # Estimate tokens (OpenRouter doesn't always provide token counts)
            input_tokens = len(prompt.split())
            output_tokens = len(response_text.split())
            
            metadata = {
                "tokens_input": input_tokens,
                "tokens_output": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "provider": "openrouter",
                "model_name": model_name,
                "model_id": config["model_id"]
            }
            
            return response_text, metadata
            
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    def _call_groq(self, model_name: str, prompt: str, config: Dict) -> Tuple[str, Dict]:
        """Call Groq API"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq not installed. Run: pip install groq")
        
        try:
            client = Groq(api_key=self.groq_api_key)
            
            # Count input tokens (estimate for now)
            input_tokens = len(prompt.split())
            
            message = client.chat.completions.create(
                model=config["model_id"],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048
            )
            
            response_text = message.choices[0].message.content
            
            # Count output tokens (estimate)
            output_tokens = len(response_text.split())
            
            metadata = {
                "tokens_input": input_tokens,
                "tokens_output": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "provider": "groq",
                "model_name": model_name,
                "model_id": config["model_id"]
            }
            
            return response_text, metadata
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def _call_nvidia_nim(self, model_name: str, prompt: str, config: Dict) -> Tuple[str, Dict]:
        """Call NVIDIA NIM API"""
        if not self.nvidia_nim_api_key:
            raise ValueError("NVIDIA_NIM_API_KEY not configured")
        
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")
        
        try:
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.nvidia_nim_api_key
            )
            
            # Count input tokens (estimate for now)
            input_tokens = len(prompt.split())
            
            completion = client.chat.completions.create(
                model=config["model_id"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=2048,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            
            # Count output tokens (estimate)
            output_tokens = len(response_text.split())
            
            metadata = {
                "tokens_input": input_tokens,
                "tokens_output": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "provider": "nvidia-nim",
                "model_name": model_name,
                "model_id": config["model_id"]
            }
            
            return response_text, metadata
            
        except Exception as e:
            raise Exception(f"NVIDIA NIM API error: {str(e)}")
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get all available models with their configuration"""
        models = {}
        for model_key, config in self.model_config.items():
            api_key_env = config.get("api_key_env", "")
            api_key_available = bool(getattr(settings, api_key_env.replace("_ENV", ""), None))
            
            models[model_key] = {
                "api_name": config.get("api_name", model_key),
                "provider": config["provider"],
                "max_tokens": config["max_tokens"],
                "energy_per_token": config["energy_per_token"],
                "cost_per_token": config["cost_per_token"],
                "api_available": api_key_available
            }
        
        return models
    
    def get_models_by_provider(self, provider: str) -> List[str]:
        """Get all models from a specific provider"""
        return [
            model_name for model_name, config in self.model_config.items()
            if config["provider"] == provider
        ]
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return {
            "google": bool(self.google_api_key),
            "anthropic": bool(self.anthropic_api_key),
            "huggingface": bool(self.huggingface_api_key),
            "openrouter": bool(self.openrouter_api_key),
            "groq": bool(self.groq_api_key),
            "nvidia-nim": bool(self.nvidia_nim_api_key)
        }


# Global instance
model_api_client = ModelAPIClient()
