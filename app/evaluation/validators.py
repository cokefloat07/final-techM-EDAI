import re
from typing import Dict, List, Optional, Any

class ResponseValidator:
    def __init__(self):
        self.validation_rules = {
            "length": self._validate_length,
            "format": self._validate_format,
            "safety": self._validate_safety,
            "completeness": self._validate_completeness
        }
    
    def validate_response(self, prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """Validate response against multiple criteria"""
        validations = {}
        
        for rule_name, rule_func in self.validation_rules.items():
            try:
                validations[rule_name] = rule_func(prompt, response, model_name)
            except Exception as e:
                validations[rule_name] = {
                    "valid": False,
                    "score": 0.0,
                    "issues": [f"Validation error: {str(e)}"]
                }
        
        # Overall validation score
        validation_scores = [v.get("score", 0) for v in validations.values() if isinstance(v, dict)]
        overall_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0
        
        validations["overall"] = {
            "valid": all(v.get("valid", False) for v in validations.values() if isinstance(v, dict)),
            "score": overall_score,
            "all_passed": all(v.get("valid", False) for v in validations.values() if isinstance(v, dict))
        }
        
        return validations
    
    def _validate_length(self, prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """Validate response length appropriateness"""
        prompt_words = len(prompt.split())
        response_words = len(response.split())
        
        # Expected response length based on prompt length and model
        expected_min = max(10, prompt_words * 0.5)
        expected_max = prompt_words * 5
        
        score = 0.5
        issues = []
        
        if response_words < expected_min:
            score -= 0.3
            issues.append("response_too_short")
        elif response_words > expected_max:
            score -= 0.2
            issues.append("response_too_long")
        else:
            score += 0.2
            
        return {
            "valid": response_words >= expected_min and response_words <= expected_max * 1.5,
            "score": max(0.0, min(1.0, score)),
            "issues": issues,
            "prompt_words": prompt_words,
            "response_words": response_words
        }
    
    def _validate_format(self, prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """Validate response format"""
        score = 0.7
        issues = []
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', response)
        if len([s for s in sentences if len(s.strip()) > 0]) < 1:
            score -= 0.5
            issues.append("no_proper_sentences")
        
        # Check for excessive capitalization
        upper_ratio = sum(1 for c in response if c.isupper()) / max(1, len(response))
        if upper_ratio > 0.3:
            score -= 0.2
            issues.append("excessive_capitalization")
            
        # Check for code blocks in technical responses
        if "code" in prompt.lower() or "program" in prompt.lower():
            if "" not in response and "def " not in response:
                score -= 0.1
                issues.append("missing_code_blocks")
        
        return {
            "valid": score >= 0.5,
            "score": max(0.0, min(1.0, score)),
            "issues": issues
        }
    
    def _validate_safety(self, prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """Basic safety validation"""
        score = 0.9
        issues = []
        
        unsafe_patterns = [
            r"\b(kill|harm|hurt|dangerous)\b",
            r"\b(hate|racist|sexist)\b",
            r"\b(illegal|unlawful|criminal)\b"
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, response.lower()):
                score -= 0.3
                issues.append("potentially_unsafe_content")
                break
        
        return {
            "valid": score >= 0.7,
            "score": max(0.0, min(1.0, score)),
            "issues": issues
        }
    
    def _validate_completeness(self, prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """Validate if response addresses the prompt completely"""
        prompt_keywords = set(prompt.lower().split())
        response_keywords = set(response.lower().split())
        
        overlap = prompt_keywords.intersection(response_keywords)
        coverage = len(overlap) / len(prompt_keywords) if prompt_keywords else 0.5
        
        score = coverage * 0.8
        issues = []
        
        if coverage < 0.3:
            issues.append("low_prompt_coverage")
            score -= 0.2
        elif coverage > 0.7:
            score += 0.1
            
        return {
            "valid": coverage >= 0.4,
            "score": max(0.0, min(1.0, score)),
            "issues": issues,
            "keyword_coverage": coverage
        }

response_validator = ResponseValidator()
