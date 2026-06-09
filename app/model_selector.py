
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from .config import settings
from .accuracy_detector import accuracy_detector
from .evaluation.metrics import accuracy_metrics

class ModelSelector:
    def __init__(self):
        self.model_config = settings.MODEL_CONFIG
        self.selection_history = []
        
    def select_best_model(self, prompt: str, context: Dict = None, 
                         user_preferences: Dict = None) -> Dict[str, Any]:
        """
        Select the best model based on prompt analysis, context, and historical performance
        """
        # Analyze prompt characteristics
        prompt_analysis = self._analyze_prompt(prompt)
        
        # Get candidate models
        candidate_models = self._get_candidate_models(prompt_analysis, context, user_preferences)
        
        # Score each model
        model_scores = {}
        for model_name in candidate_models:
            score = self._calculate_model_score(model_name, prompt_analysis, context, user_preferences)
            model_scores[model_name] = score
        
        # Select best model
        best_model = max(model_scores.items(), key=lambda x: x[1])
        
        # Prepare selection rationale
        rationale = self._generate_selection_rationale(
            best_model[0], best_model[1], prompt_analysis, model_scores
        )
        
        selection_result = {
            "selected_model": best_model[0],
            "confidence_score": best_model[1],
            "model_scores": model_scores,
            "prompt_analysis": prompt_analysis,
            "rationale": rationale,
            "candidate_models": candidate_models,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store selection history
        self.selection_history.append(selection_result)
        
        return selection_result
    
    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt characteristics to determine model requirements"""
        prompt_lower = prompt.lower()
        words = prompt_lower.split()
        word_count = len(words)
        char_count = len(prompt)
        
        analysis = {
            "length_category": self._categorize_length(word_count),
            "complexity": self._assess_complexity(prompt),
            "domain": self._detect_domain(prompt_lower),
            "task_type": self._detect_task_type(prompt_lower),
            "technical_level": self._assess_technical_level(prompt_lower),
            "requires_creativity": self._requires_creativity(prompt_lower),
            "requires_precision": self._requires_precision(prompt_lower),
            "word_count": word_count,
            "char_count": char_count
        }
        
        return analysis
    
    def _categorize_length(self, word_count: int) -> str:
        """Categorize prompt length"""
        if word_count <= 10:
            return "very_short"
        elif word_count <= 50:
            return "short"
        elif word_count <= 200:
            return "medium"
        elif word_count <= 500:
            return "long"
        else:
            return "very_long"
    
    def _assess_complexity(self, prompt: str) -> float:
        """Assess prompt complexity (0-1 scale)"""
        complexity_score = 0.0
        
        # Sentence complexity
        sentences = prompt.split('.')
        avg_sentence_length = len(prompt) / max(1, len(sentences))
        if avg_sentence_length > 100:
            complexity_score += 0.3
        
        # Vocabulary complexity
        complex_words = ['analyze', 'synthesize', 'evaluate', 'compare', 'contrast', 
                        'demonstrate', 'illustrate', 'interpret', 'summarize']
        complex_word_count = sum(1 for word in complex_words if word in prompt.lower())
        complexity_score += complex_word_count * 0.1
        
        # Question complexity
        if '?' in prompt:
            question_words = ['how', 'why', 'what if', 'explain', 'describe']
            question_complexity = sum(1 for word in question_words if word in prompt.lower())
            complexity_score += question_complexity * 0.1
        
        return min(1.0, complexity_score)
    
    def _detect_domain(self, prompt: str) -> List[str]:
        """Detect domain of the prompt"""
        domains = []
        
        domain_keywords = {
            "technical": ["code", "program", "algorithm", "function", "database", "api", "debug", "python", "bubble sort", "sort"],
            "scientific": ["research", "study", "experiment", "data", "analysis", "hypothesis"],
            "creative": ["story", "poem", "creative", "imagine", "narrative", "fiction"],
            "business": ["strategy", "marketing", "sales", "profit", "business", "enterprise"],
            "academic": ["essay", "thesis", "research", "study", "academic", "scholarly"],
            "medical": ["health", "medical", "treatment", "symptoms", "diagnosis", "medicine"],
            "legal": ["legal", "law", "contract", "agreement", "compliance", "regulation"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ["general"]
    
    def _detect_task_type(self, prompt: str) -> str:
        """Detect the type of task"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["summarize", "summary", "brief"]):
            return "summarization"
        elif any(word in prompt_lower for word in ["translate", "language"]):
            return "translation"
        elif any(word in prompt_lower for word in ["code", "program", "function"]):
            return "coding"
        elif any(word in prompt_lower for word in ["explain", "what is", "define"]):
            return "explanation"
        elif any(word in prompt_lower for word in ["write", "create", "generate"]):
            return "generation"
        elif any(word in prompt_lower for word in ["compare", "contrast", "difference"]):
            return "comparison"
        elif any(word in prompt_lower for word in ["analyze", "analysis"]):
            return "analysis"
        else:
            return "general"
    
    def _assess_technical_level(self, prompt: str) -> str:
        """Assess technical level of prompt"""
        technical_terms = [
            "algorithm", "function", "variable", "database", "api", "framework",
            "neural network", "machine learning", "data structure", "compiler"
        ]
        
        technical_count = sum(1 for term in technical_terms if term in prompt)
        
        if technical_count >= 3:
            return "high"
        elif technical_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _requires_creativity(self, prompt: str) -> bool:
        """Check if prompt requires creative response"""
        creative_indicators = [
            "creative", "imagine", "story", "poem", "narrative", "fiction",
            "innovative", "original", "brainstorm", "idea"
        ]
        return any(indicator in prompt for indicator in creative_indicators)
    
    def _requires_precision(self, prompt: str) -> bool:
        """Check if prompt requires precise response"""
        precision_indicators = [
            "exact", "precise", "accurate", "specific", "detailed",
            "step by step", "instructions", "guide", "tutorial"
        ]
        return any(indicator in prompt for indicator in precision_indicators)
    
    def _get_candidate_models(self, prompt_analysis: Dict, context: Dict = None, 
                            user_preferences: Dict = None) -> List[str]:
        """Get candidate models based on prompt analysis"""
        all_models = list(self.model_config.keys())
        candidates = []
        
        for model_name in all_models:
            if self._is_model_suitable(model_name, prompt_analysis, context, user_preferences):
                candidates.append(model_name)
        
        # Return candidates, or all_models if no suitable models found
        # Filter out deprecated models from fallback
        deprecated_models = ['gemini-pro']  # Models no longer supported
        if candidates:
            return candidates
        else:
            # Fallback to all available models except deprecated ones
            return [m for m in all_models if m not in deprecated_models]
    
    def _is_model_suitable(self, model_name: str, prompt_analysis: Dict, 
                          context: Dict = None, user_preferences: Dict = None) -> bool:
        """Check if model is suitable for the prompt"""
        model_config = self.model_config[model_name]
        
        # Check domain suitability
        domains = prompt_analysis.get("domain", ["general"])
        if "technical" in domains and "flan-t5-base" in model_name:
            return False  # Flan-T5 might not be best for complex technical tasks
        
        # Check length requirements
        length_category = prompt_analysis["length_category"]
        if length_category in ["long", "very_long"] and model_name == "flan-t5-base":
            return False  # Flan-T5 has shorter context window
        
        # Check technical level
        technical_level = prompt_analysis["technical_level"]
        if technical_level == "high" and "flan" in model_name:
            return False
        
        # Check creativity requirements
        if prompt_analysis["requires_creativity"] and "claude" in model_name:
            return True  # Claude is good for creative tasks
        
        return True
    
    def _calculate_model_score(self, model_name: str, prompt_analysis: Dict, 
                             context: Dict = None, user_preferences: Dict = None) -> float:
        """Calculate score for a model (0-1 scale)"""
        base_score = 0.5
        model_config = self.model_config[model_name]
        
        # Domain matching (30% weight)
        domain_score = self._calculate_domain_score(model_name, prompt_analysis["domain"])
        base_score += domain_score * 0.3
        
        # Task type matching (25% weight)
        task_score = self._calculate_task_score(model_name, prompt_analysis["task_type"])
        base_score += task_score * 0.25
        
        # Technical level matching (20% weight)
        technical_score = self._calculate_technical_score(model_name, prompt_analysis["technical_level"])
        base_score += technical_score * 0.2
        
        # Creativity/precision requirements (15% weight)
        requirement_score = self._calculate_requirement_score(model_name, prompt_analysis)
        base_score += requirement_score * 0.15
        
        # User preferences (10% weight)
        preference_score = self._calculate_preference_score(model_name, user_preferences)
        base_score += preference_score * 0.1
        
        # Context consideration
        if context:
            context_score = self._calculate_context_score(model_name, context)
            base_score += context_score * 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _calculate_domain_score(self, model_name: str, domains: List[str]) -> float:
        """Calculate domain matching score"""
        domain_performance = {
            "gemini-2.0-flash": {"technical": 0.8, "scientific": 0.7, "creative": 0.6, "business": 0.9},
            "gemini-1.5-flash": {"technical": 0.8, "scientific": 0.7, "creative": 0.6, "business": 0.9},
            "gemini-1.5-pro": {"technical": 0.9, "scientific": 0.8, "creative": 0.7, "business": 0.8},
            "claude-3": {"technical": 0.7, "scientific": 0.8, "creative": 0.9, "business": 0.7},
            "flan-t5": {"technical": 0.6, "scientific": 0.5, "creative": 0.4, "business": 0.5},
            "mistral": {"technical": 0.8, "scientific": 0.7, "creative": 0.6, "business": 0.7}
        }
        
        # Try exact match first, then partial match
        if model_name in domain_performance:
            scores = [domain_performance[model_name].get(domain, 0.5) for domain in domains]
        else:
            # Fallback: try to match by model type
            score = 0.5
            if "gemini-2.0-flash" in model_name or "gemini" in model_name and "flash" in model_name:
                score = 0.75
            elif "gemini-1.5-pro" in model_name or "pro" in model_name:
                score = 0.8
            elif "claude" in model_name:
                score = 0.75
            elif "mistral" in model_name:
                score = 0.7
            elif "flan" in model_name:
                score = 0.5
            return score
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_task_score(self, model_name: str, task_type: str) -> float:
        """Calculate task type matching score"""
        task_performance = {
            "gemini-2.0-flash": {"summarization": 0.9, "translation": 0.8, "coding": 0.8, 
                          "explanation": 0.8, "generation": 0.7, "comparison": 0.8, "analysis": 0.8},
            "gemini-1.5-flash": {"summarization": 0.9, "translation": 0.8, "coding": 0.7, 
                          "explanation": 0.7, "generation": 0.6, "comparison": 0.7, "analysis": 0.7},
            "gemini-1.5-pro": {"summarization": 0.8, "translation": 0.7, "coding": 0.9, 
                          "explanation": 0.8, "generation": 0.7, "comparison": 0.8, "analysis": 0.8},
            "claude-3-opus": {"summarization": 0.7, "translation": 0.6, "coding": 0.6, 
                      "explanation": 0.9, "generation": 0.8, "comparison": 0.8, "analysis": 0.9},
            "claude-3-sonnet": {"summarization": 0.7, "translation": 0.6, "coding": 0.6, 
                      "explanation": 0.9, "generation": 0.8, "comparison": 0.8, "analysis": 0.9},
            "flan-t5-base": {"summarization": 0.6, "translation": 0.5, "coding": 0.4, 
                           "explanation": 0.5, "generation": 0.4, "comparison": 0.5, "analysis": 0.5},
            "mistral-7b": {"summarization": 0.7, "translation": 0.6, "coding": 0.8, 
                           "explanation": 0.7, "generation": 0.7, "comparison": 0.7, "analysis": 0.7}
        }
        
        return task_performance.get(model_name, {}).get(task_type, 0.5)
    
    def _calculate_technical_score(self, model_name: str, technical_level: str) -> float:
        """Calculate technical level matching score"""
        technical_capability = {
            "gemini-2.0-flash": {"low": 0.8, "medium": 0.8, "high": 0.7},
            "gemini-1.5-flash": {"low": 0.8, "medium": 0.7, "high": 0.6},
            "gemini-1.5-pro": {"low": 0.7, "medium": 0.8, "high": 0.9},
            "claude-3-opus": {"low": 0.6, "medium": 0.7, "high": 0.8},
            "claude-3-sonnet": {"low": 0.6, "medium": 0.7, "high": 0.8},
            "claude-3-haiku": {"low": 0.7, "medium": 0.6, "high": 0.5},
            "flan-t5-base": {"low": 0.5, "medium": 0.4, "high": 0.3},
            "mistral-7b": {"low": 0.6, "medium": 0.7, "high": 0.7}
        }
        
        return technical_capability.get(model_name, {}).get(technical_level, 0.5)
    
    def _calculate_requirement_score(self, model_name: str, prompt_analysis: Dict) -> float:
        """Calculate score based on creativity/precision requirements"""
        score = 0.5
        
        creativity_ability = {
            "gemini-2.0-flash": 0.65,
            "gemini-1.5-flash": 0.6,
            "gemini-1.5-pro": 0.7,
            "claude-3-opus": 0.9,
            "claude-3-sonnet": 0.8,
            "claude-3-haiku": 0.7,
            "flan-t5-base": 0.4,
            "mistral-7b": 0.7
        }
        
        precision_ability = {
            "gemini-2.0-flash": 0.9,
            "gemini-1.5-flash": 0.9,
            "gemini-1.5-pro": 0.8,
            "claude-3-opus": 0.7,
            "claude-3-sonnet": 0.7,
            "claude-3-haiku": 0.6,
            "flan-t5-base": 0.5,
            "mistral-7b": 0.7
        }
        
        if prompt_analysis["requires_creativity"]:
            score = creativity_ability.get(model_name, 0.5)
        elif prompt_analysis["requires_precision"]:
            score = precision_ability.get(model_name, 0.5)
        
        return score
    
    def _calculate_preference_score(self, model_name: str, user_preferences: Dict) -> float:
        """Calculate score based on user preferences"""
        if not user_preferences:
            return 0.5
        
        preferred_models = user_preferences.get("preferred_models", [])
        avoided_models = user_preferences.get("avoided_models", [])
        
        if model_name in preferred_models:
            return 1.0
        elif model_name in avoided_models:
            return 0.0
        else:
            return 0.5
    
    def _calculate_context_score(self, model_name: str, context: Dict) -> float:
        """Calculate score based on conversation context"""
        if not context.get("previous_responses"):
            return 0.5
        
        # Check if model was used successfully in similar context
        previous_success = context.get("model_performance", {}).get(model_name, 0.5)
        return previous_success
    
    def _generate_selection_rationale(self, selected_model: str, score: float, 
                                    prompt_analysis: Dict, model_scores: Dict) -> str:
        """Generate human-readable rationale for model selection"""
        rationale_parts = []
        
        # Add domain rationale
        domains = prompt_analysis["domain"]
        if domains != ["general"]:
            rationale_parts.append(f"Prompt belongs to {', '.join(domains)} domain")
        
        # Add task type rationale
        task_type = prompt_analysis["task_type"]
        rationale_parts.append(f"Task type: {task_type}")
        
        # Add technical level rationale
        tech_level = prompt_analysis["technical_level"]
        if tech_level != "low":
            rationale_parts.append(f"Technical level: {tech_level}")
        
        # Add model comparison
        other_models = {k: v for k, v in model_scores.items() if k != selected_model}
        if other_models:
            best_other = max(other_models.items(), key=lambda x: x[1])
            rationale_parts.append(f"Selected {selected_model} (score: {score:.2f}) over {best_other[0]} (score: {best_other[1]:.2f})")
        
        return ". ".join(rationale_parts)
    
    def get_model_recommendations(self, prompt: str, top_k: int = 3) -> List[Dict]:
        """Get top K model recommendations for a prompt"""
        selection_result = self.select_best_model(prompt)
        model_scores = selection_result["model_scores"]
        
        # Sort models by score
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for i, (model_name, score) in enumerate(sorted_models[:top_k]):
            recommendations.append({
                "rank": i + 1,
                "model_name": model_name,
                "score": score,
                "confidence": "high" if score > 0.7 else "medium" if score > 0.5 else "low",
                "rationale": f"Recommended for {selection_result['prompt_analysis']['task_type']} tasks"
            })
        
        return recommendations

# Global instance
model_selector = ModelSelector()
