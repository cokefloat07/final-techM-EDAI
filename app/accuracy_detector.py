import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class AccuracyDetector:
    def __init__(self):
        self.quality_metrics = {
            "factual_accuracy": 0.0,
            "completeness": 0.0,
            "relevance": 0.0,
            "coherence": 0.0,
            "technical_correctness": 0.0
        }
        
    def detect_accuracy(self, prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """
        Main method to detect accuracy across multiple dimensions
        """
        accuracy_scores = {}
        
        # Factual Accuracy Check
        accuracy_scores["factual_accuracy"] = self._check_factual_accuracy(prompt, response)
        
        # Completeness Check
        accuracy_scores["completeness"] = self._check_completeness(prompt, response)
        
        # Relevance Check
        accuracy_scores["relevance"] = self._check_relevance(prompt, response)
        
        # Coherence Check
        accuracy_scores["coherence"] = self._check_coherence(response)
        
        # Technical Correctness (for technical prompts)
        accuracy_scores["technical_correctness"] = self._check_technical_correctness(prompt, response)
        
        # Overall Score (weighted average)
        weights = {
            "factual_accuracy": 0.3,
            "completeness": 0.2,
            "relevance": 0.2,
            "coherence": 0.15,
            "technical_correctness": 0.15
        }
        
        overall_score = sum(accuracy_scores[metric] * weights[metric] for metric in accuracy_scores)
        accuracy_scores["overall_accuracy"] = overall_score
        
        # Accuracy Level Classification
        accuracy_scores["accuracy_level"] = self._classify_accuracy_level(overall_score)
        
        # Issues detected
        accuracy_scores["issues_detected"] = self._detect_issues(prompt, response)
        
        # Confidence score
        accuracy_scores["confidence_score"] = self._calculate_confidence(prompt, response, accuracy_scores)
        
        return accuracy_scores
    
    def _check_factual_accuracy(self, prompt: str, response: str) -> float:
        """
        Check factual accuracy of the response
        """
        score = 0.7  # Base score
        
        # Check for factual indicators
        factual_indicators = [
            "according to", "research shows", "studies indicate",
            "data suggests", "evidence shows", "statistics show"
        ]
        
        # Check for uncertainty indicators (negative)
        uncertainty_indicators = [
            "might be", "could be", "possibly", "perhaps", "maybe",
            "I think", "I believe", "in my opinion"
        ]
        
        factual_count = sum(1 for indicator in factual_indicators if indicator.lower() in response.lower())
        uncertainty_count = sum(1 for indicator in uncertainty_indicators if indicator.lower() in response.lower())
        
        # Adjust score based on indicators
        score += factual_count * 0.05
        score -= uncertainty_count * 0.03
        
        # Check for numerical data consistency
        numbers = re.findall(r'\b\d+\.?\d*\b', response)
        if len(numbers) > 2:
            score += 0.1
        
        # Check response length (longer responses often contain more facts)
        word_count = len(response.split())
        if word_count > 100:
            score += 0.1
        elif word_count < 30:
            score -= 0.1
            
        return max(0.1, min(1.0, score))
    
    def _check_completeness(self, prompt: str, response: str) -> float:
        """
        Check if the response completely addresses the prompt
        """
        prompt_lower = prompt.lower()
        response_lower = response.lower()
        
        score = 0.5  # Base score
        
        # Check for question words in prompt
        question_words = ["what", "how", "why", "when", "where", "who", "explain", "describe"]
        question_present = any(word in prompt_lower for word in question_words)
        
        if question_present:
            # Check if response contains answer indicators
            answer_indicators = [
                "answer is", "solution is", "therefore", "thus", "as a result",
                "in conclusion", "the main", "key points", "important to note"
            ]
            answer_count = sum(1 for indicator in answer_indicators if indicator in response_lower)
            score += answer_count * 0.1
        
        # Check if response addresses multiple aspects
        aspect_indicators = ["first", "second", "third", "additionally", "moreover", "furthermore"]
        aspect_count = sum(1 for indicator in aspect_indicators if indicator in response_lower)
        score += aspect_count * 0.05
        
        # Length-based completeness
        response_ratio = len(response) / max(1, len(prompt))
        if response_ratio > 2:
            score += 0.2
        elif response_ratio < 0.5:
            score -= 0.2
            
        return max(0.1, min(1.0, score))
    
    def _check_relevance(self, prompt: str, response: str) -> float:
        """
        Check if the response is relevant to the prompt
        """
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        # Simple word overlap
        common_words = prompt_words.intersection(response_words)
        if len(prompt_words) > 0:
            relevance_ratio = len(common_words) / len(prompt_words)
        else:
            relevance_ratio = 0.5
            
        score = relevance_ratio * 0.8  # Base on word overlap
        
        # Check for topic consistency
        topic_shift_indicators = [
            "by the way", "changing the subject", "unrelated but",
            "on a different note", "speaking of something else"
        ]
        
        topic_shifts = sum(1 for indicator in topic_shift_indicators if indicator in response.lower())
        score -= topic_shifts * 0.2
        
        return max(0.1, min(1.0, score))
    
    def _check_coherence(self, response: str) -> float:
        """
        Check the coherence and readability of the response
        """
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.3
            
        score = 0.6  # Base score
        
        # Check for transition words
        transition_words = [
            "however", "therefore", "moreover", "furthermore", 
            "consequently", "as a result", "in addition"
        ]
        
        transitions = sum(1 for word in transition_words if word in response.lower())
        score += transitions * 0.05
        
        # Check sentence length variation (indicates better writing)
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = max(sentence_lengths) - min(sentence_lengths) if sentence_lengths else 0
        if 5 <= length_variance <= 15:
            score += 0.1
            
        # Check for paragraph structure
        if '\n\n' in response:
            score += 0.1
            
        return max(0.1, min(1.0, score))
    
    def _check_technical_correctness(self, prompt: str, response: str) -> float:
        """
        Check technical correctness for technical prompts
        """
        technical_terms = [
            # Programming
            "function", "variable", "algorithm", "database", "api", "framework",
            # Science
            "hypothesis", "experiment", "data analysis", "results", "methodology",
            # Medical
            "symptoms", "treatment", "diagnosis", "medication", "therapy"
        ]
        
        prompt_technical = any(term in prompt.lower() for term in technical_terms)
        
        if not prompt_technical:
            return 0.7  # Default score for non-technical prompts
            
        score = 0.5
        
        # Check for code blocks in technical responses
        if "" in response:
            score += 0.2
            
        # Check for structured explanations
        structure_indicators = ["steps:", "process:", "method:", "approach:"]
        if any(indicator in response.lower() for indicator in structure_indicators):
            score += 0.1
            
        # Check for definitions in technical responses
        definition_indicators = ["defined as", "means that", "refers to", "is a"]
        definition_count = sum(1 for indicator in definition_indicators if indicator in response.lower())
        score += definition_count * 0.05
        
        return max(0.1, min(1.0, score))
    
    def _classify_accuracy_level(self, score: float) -> str:
        """Classify accuracy level based on score"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "very_good"
        elif score >= 0.7:
            return "good"
        elif score >= 0.6:
            return "fair"
        elif score >= 0.5:
            return "adequate"
        else:
            return "poor"
    
    def _detect_issues(self, prompt: str, response: str) -> List[str]:
        """Detect specific issues in the response"""
        issues = []
        
        # Check for hallucinations
        if self._detect_hallucinations(response):
            issues.append("potential_hallucination")
            
        # Check for contradictions
        if self._detect_contradictions(response):
            issues.append("internal_contradiction")
            
        # Check for vagueness
        if self._detect_vagueness(response):
            issues.append("vague_response")
            
        # Check for incompleteness
        if len(response.split()) < 20:
            issues.append("very_short_response")
            
        # Check for repetition
        if self._detect_repetition(response):
            issues.append("repetitive_content")
            
        return issues
    
    def _detect_hallucinations(self, response: str) -> bool:
        """Simple hallucination detection"""
        hallucination_indicators = [
            "I cannot find", "there is no information", "unknown",
            "I don't have data on", "not available in my knowledge"
        ]
        
        # If model admits lack of knowledge, it's not hallucinating
        if any(indicator in response.lower() for indicator in hallucination_indicators):
            return False
            
        # Check for overly specific unsupported claims
        specific_claims = re.findall(r'\b(\d{4}|\d+%|study (show|found)|research (indicate|demonstrate))\b', response)
        return len(specific_claims) > 2 and len(response) < 100
    
    def _detect_contradictions(self, response: str) -> bool:
        """Detect internal contradictions"""
        contradiction_pairs = [
            ("always", "never"),
            ("all", "none"),
            ("proven", "unproven"),
            ("increase", "decrease")
        ]
        
        response_lower = response.lower()
        for word1, word2 in contradiction_pairs:
            if word1 in response_lower and word2 in response_lower:
                return True
        return False
    
    def _detect_vagueness(self, response: str) -> bool:
        """Detect vague language"""
        vague_indicators = [
            "might be", "could be", "possibly", "perhaps", "maybe",
            "some people say", "it is believed", "generally"
        ]
        
        vague_count = sum(1 for indicator in vague_indicators if indicator in response.lower())
        return vague_count > 3
    
    def _detect_repetition(self, response: str) -> bool:
        """Detect repetitive content"""
        words = response.lower().split()
        if len(words) < 10:
            return False
            
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
                
        max_freq = max(word_freq.values()) if word_freq else 0
        return max_freq > len(words) * 0.1  # Word appears more than 10% of total words
    
    def _calculate_confidence(self, prompt: str, response: str, accuracy_scores: Dict) -> float:
        """Calculate confidence score for the accuracy assessment"""
        base_confidence = accuracy_scores["overall_accuracy"]
        
        # Adjust confidence based on response characteristics
        adjustments = 0.0
        
        # Longer responses allow more accurate assessment
        word_count = len(response.split())
        if word_count > 200:
            adjustments += 0.1
        elif word_count < 50:
            adjustments -= 0.1
            
        # Technical prompts are harder to assess automatically
        technical_terms = ["function", "algorithm", "hypothesis", "experiment"]
        if any(term in prompt.lower() for term in technical_terms):
            adjustments -= 0.05
            
        return max(0.1, min(1.0, base_confidence + adjustments))

# Global instance
accuracy_detector = AccuracyDetector()
