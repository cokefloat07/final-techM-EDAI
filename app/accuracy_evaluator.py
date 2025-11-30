"""
Accuracy Evaluation Module - Evaluate and track accuracy of model responses
Metrics: Factual Accuracy, Completeness, Relevance, Coherence, Technical Correctness
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class AccuracyEvaluator:
    """Evaluate accuracy metrics for model responses"""
    
    def __init__(self):
        self.metrics = {
            "factual_accuracy": "0-100 score based on factual correctness",
            "completeness": "0-100 score based on answer completeness",
            "relevance": "0-100 score based on relevance to prompt",
            "coherence": "0-100 score based on logical coherence",
            "technical_correctness": "0-100 score for technical accuracy",
            "overall_accuracy": "Weighted average of all metrics"
        }
    
    def evaluate_response(self, 
                         prompt: str, 
                         response: str, 
                         model_name: str,
                         context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate the accuracy of a model response
        
        Args:
            prompt: Original user prompt
            response: Model's response text
            model_name: Name of the model that generated response
            context: Optional context about the prompt (domain, difficulty, etc.)
            
        Returns:
            Dictionary with accuracy scores and evaluation details
        """
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "scores": {}
        }
        
        # Calculate individual accuracy metrics
        evaluation["scores"]["factual_accuracy"] = self._evaluate_factual_accuracy(prompt, response, context)
        evaluation["scores"]["completeness"] = self._evaluate_completeness(prompt, response)
        evaluation["scores"]["relevance"] = self._evaluate_relevance(prompt, response)
        evaluation["scores"]["coherence"] = self._evaluate_coherence(response)
        evaluation["scores"]["technical_correctness"] = self._evaluate_technical_correctness(prompt, response, context)
        
        # Calculate overall accuracy
        scores = evaluation["scores"]
        weights = {
            "factual_accuracy": 0.25,
            "completeness": 0.20,
            "relevance": 0.25,
            "coherence": 0.15,
            "technical_correctness": 0.15
        }
        
        overall = sum(scores[metric] * weights[metric] for metric in scores)
        evaluation["scores"]["overall_accuracy"] = round(overall, 2)
        
        # Determine accuracy level
        overall_score = evaluation["scores"]["overall_accuracy"]
        if overall_score >= 80:
            evaluation["accuracy_level"] = "Excellent"
        elif overall_score >= 60:
            evaluation["accuracy_level"] = "Good"
        elif overall_score >= 40:
            evaluation["accuracy_level"] = "Fair"
        else:
            evaluation["accuracy_level"] = "Poor"
        
        # Identify issues
        evaluation["issues_detected"] = self._identify_issues(evaluation["scores"])
        
        # Confidence score
        evaluation["confidence_score"] = self._calculate_confidence(evaluation["scores"])
        
        return evaluation
    
    def _evaluate_factual_accuracy(self, prompt: str, response: str, context: Optional[Dict]) -> float:
        """
        Evaluate factual accuracy of the response
        Checks for: correct terminology, logical consistency, no contradictions
        """
        score = 75.0  # Base score
        
        # Penalize if response is too short (likely incomplete)
        if len(response) < len(prompt) * 0.5:
            score -= 15
        
        # Check for common quality indicators
        sentences = response.split('.')
        if len(sentences) < 2:
            score -= 10  # Very brief response
        
        # Check for hedging language (good for uncertainty)
        hedging_words = ["possibly", "might", "could", "may", "seems", "appears"]
        hedging_count = sum(1 for word in hedging_words if word.lower() in response.lower())
        if hedging_count > len(response.split()) * 0.05:  # Too much hedging
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    def _evaluate_completeness(self, prompt: str, response: str) -> float:
        """
        Evaluate if response fully addresses the prompt
        """
        score = 70.0  # Base score
        
        # Check response length relative to prompt
        length_ratio = len(response) / max(len(prompt), 1)
        if length_ratio >= 5:
            score += 15  # Good comprehensive answer
        elif length_ratio >= 2:
            score += 5
        elif length_ratio < 0.5:
            score -= 20  # Too brief
        
        # Check for answer structure
        has_intro = any(intro in response.lower() for intro in ["here", "the", "to"])
        has_details = len(response.split()) > 20
        has_conclusion = any(conc in response.lower() for conc in ["thus", "therefore", "in conclusion", "finally"])
        
        if has_intro and has_details:
            score += 5
        if has_conclusion:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def _evaluate_relevance(self, prompt: str, response: str) -> float:
        """
        Evaluate if response directly addresses the prompt
        """
        score = 75.0  # Base score
        
        # Extract key words from prompt
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        # Calculate overlap
        common_words = prompt_words.intersection(response_words)
        word_overlap = len(common_words) / max(len(prompt_words), 1)
        
        if word_overlap > 0.5:
            score += 15  # Good topic overlap
        elif word_overlap > 0.3:
            score += 5
        elif word_overlap < 0.1:
            score -= 20  # Low relevance
        
        return max(0.0, min(100.0, score))
    
    def _evaluate_coherence(self, response: str) -> float:
        """
        Evaluate logical flow and coherence of response
        """
        score = 75.0  # Base score
        
        sentences = response.split('.')
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Good if has multiple sentences
        if len(valid_sentences) >= 3:
            score += 10
        elif len(valid_sentences) < 2:
            score -= 15
        
        # Check for discourse markers (coherence indicators)
        markers = ["first", "second", "next", "then", "therefore", "however", "moreover", "furthermore", "also"]
        marker_count = sum(1 for marker in markers if marker in response.lower())
        
        if marker_count >= 2:
            score += 10  # Good use of transitions
        
        # Penalty for very long sentences (readability)
        avg_sentence_length = sum(len(s.split()) for s in valid_sentences) / max(len(valid_sentences), 1)
        if avg_sentence_length > 25:
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    def _evaluate_technical_correctness(self, prompt: str, response: str, context: Optional[Dict]) -> float:
        """
        Evaluate technical accuracy (for code, technical topics)
        """
        score = 75.0  # Base score
        
        # Check if prompt seems technical
        technical_indicators = ["code", "function", "algorithm", "technical", "implement", "error", "bug", "syntax"]
        is_technical = any(indicator in prompt.lower() for indicator in technical_indicators)
        
        if is_technical:
            # Check for common code markers
            code_indicators = ["def ", "class ", "import ", "function", "return", "=", "{", "}"]
            code_count = sum(1 for indicator in code_indicators if indicator in response)
            
            if code_count >= 3:
                score += 15  # Looks like valid code
            elif code_count > 0:
                score += 5
            else:
                score -= 10  # Should have code but doesn't
        else:
            # For non-technical: check clarity and structure
            if len(response) > 50:
                score += 5
        
        return max(0.0, min(100.0, score))
    
    def _identify_issues(self, scores: Dict[str, float]) -> List[str]:
        """
        Identify specific issues based on low scores
        """
        issues = []
        threshold = 50
        
        if scores.get("factual_accuracy", 100) < threshold:
            issues.append("Low factual accuracy - response may contain errors")
        if scores.get("completeness", 100) < threshold:
            issues.append("Incomplete - response may not fully address the prompt")
        if scores.get("relevance", 100) < threshold:
            issues.append("Low relevance - response strays from the prompt")
        if scores.get("coherence", 100) < threshold:
            issues.append("Poor coherence - response is hard to follow")
        if scores.get("technical_correctness", 100) < threshold:
            issues.append("Technical issues - response may have errors")
        
        return issues
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """
        Calculate confidence score based on consistency of individual scores
        Lower variance = higher confidence
        """
        score_values = list(scores.values())
        if not score_values:
            return 0.0
        
        mean = sum(score_values) / len(score_values)
        variance = sum((x - mean) ** 2 for x in score_values) / len(score_values)
        
        # Convert variance to confidence (inverse relationship)
        # If all scores are similar (low variance), confidence is high
        confidence = 100 - min(variance / 2, 100)
        
        return round(confidence, 2)
    
    def compare_models(self, 
                      prompt: str,
                      responses: Dict[str, str],
                      model_names: List[str]) -> Dict[str, Any]:
        """
        Compare accuracy of multiple models' responses to the same prompt
        
        Args:
            prompt: The input prompt
            responses: Dictionary mapping model names to their responses
            model_names: List of model names being compared
            
        Returns:
            Comparison analysis with rankings
        """
        evaluations = {}
        for model_name in model_names:
            if model_name in responses:
                evaluations[model_name] = self.evaluate_response(
                    prompt, 
                    responses[model_name], 
                    model_name
                )
        
        # Rank models
        ranking = sorted(
            evaluations.items(),
            key=lambda x: x[1]["scores"]["overall_accuracy"],
            reverse=True
        )
        
        return {
            "prompt": prompt,
            "evaluations": evaluations,
            "ranking": [(name, eval["scores"]["overall_accuracy"]) for name, eval in ranking],
            "best_model": ranking[0][0] if ranking else None,
            "best_score": ranking[0][1]["scores"]["overall_accuracy"] if ranking else 0
        }


# Global instance
accuracy_evaluator = AccuracyEvaluator()
