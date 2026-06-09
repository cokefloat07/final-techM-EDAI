"""
Code Quality Evaluator - Evaluates code responses with actual quality metrics
"""

from typing import Dict, List, Any, Optional
import re

class CodeQualityEvaluator:
    """Evaluate actual code quality metrics"""
    
    def evaluate_code(self, prompt: str, response: str, model_name: str) -> Dict[str, Any]:
        """
        Evaluate code quality based on actual metrics
        Returns score 0-100
        """
        if not response or len(response.strip()) < 10:
            return {"overall_accuracy": 10, "factors": {"length": 10, "structure": 0, "completeness": 0}}
        
        scores = {
            "completeness": self._evaluate_completeness(prompt, response),
            "code_quality": self._evaluate_code_quality(response),
            "functionality": self._evaluate_functionality(response, prompt),
            "efficiency": self._evaluate_efficiency(response),
            "documentation": self._evaluate_documentation(response)
        }
        
        # Weighted average
        weights = {
            "completeness": 0.25,
            "code_quality": 0.25,
            "functionality": 0.30,
            "efficiency": 0.10,
            "documentation": 0.10
        }
        
        overall = sum(scores[key] * weights[key] for key in scores)
        
        return {
            "overall_accuracy": round(overall, 2),
            "factors": scores
        }
    
    def _evaluate_completeness(self, prompt: str, response: str) -> float:
        """
        Check if response addresses all requirements
        """
        score = 50.0
        response_lower = response.lower()
        prompt_lower = prompt.lower()
        
        # Check response length vs prompt
        if len(response) < len(prompt) * 0.3:
            return 20.0  # Too short
        elif len(response) > len(prompt) * 3:
            score += 20  # Good comprehensive answer
        else:
            score += 10
        
        # For HTML tic-tac-toe, check for key elements
        required_elements = {
            "html": r"<html|<!DOCTYPE",
            "head": r"<head",
            "body": r"<body",
            "style": r"<style|css",
            "script": r"<script",
            "input_elements": r"<div|<button|<input|<cell"
        }
        
        found_elements = sum(1 for elem, pattern in required_elements.items() 
                            if re.search(pattern, response_lower))
        
        score += (found_elements / len(required_elements)) * 20
        
        return min(100.0, score)
    
    def _evaluate_code_quality(self, response: str) -> float:
        """
        Evaluate code structure, formatting, and best practices
        """
        score = 50.0
        
        # Check indentation consistency
        lines = response.split('\n')
        indented_lines = [l for l in lines if l and l[0].isspace()]
        if indented_lines:
            # Check for consistent indentation
            indent_levels = [len(l) - len(l.lstrip()) for l in indented_lines]
            if indent_levels and len(set(indent_levels)) <= 4:  # Reasonable indent levels
                score += 15
        
        # Check for proper closing tags
        opening_tags = len(re.findall(r'<[^/][^>]*>', response))
        closing_tags = len(re.findall(r'</[^>]+>', response))
        
        if opening_tags == closing_tags:
            score += 15
        elif closing_tags >= opening_tags * 0.8:
            score += 10
        
        # Check for HTML comments
        has_comments = len(re.findall(r'<!--.*?-->', response, re.DOTALL)) > 0
        if has_comments:
            score += 10
        
        # Check for proper CSS syntax
        css_blocks = len(re.findall(r'\{[^}]+\}', response))
        if css_blocks > 0:
            score += 10
        
        return min(100.0, score)
    
    def _evaluate_functionality(self, response: str, prompt: str) -> float:
        """
        Evaluate if code actually works (functional aspects)
        """
        score = 50.0
        response_lower = response.lower()
        
        # Check for game board grid
        board_patterns = [
            r'grid-template-columns.*3',  # CSS Grid
            r'display.*grid',
            r'<table',  # Table layout
            r'\[0,1,2\]|\[3,4,5\]|\[6,7,8\]'  # Array indices
        ]
        
        has_board_layout = any(re.search(p, response_lower) for p in board_patterns)
        if has_board_layout:
            score += 15
        
        # Check for game logic (JavaScript functions)
        logic_keywords = ['function', 'const', 'let', 'var', 'if', 'for', 'while', 'onclick', 'addEventListener']
        logic_count = sum(response_lower.count(kw) for kw in logic_keywords)
        
        if logic_count > 5:
            score += 20
        elif logic_count > 0:
            score += 10
        
        # Check for event handling
        has_events = bool(re.search(r'onclick|addEventListener|on\w+\s*=', response_lower))
        if has_events:
            score += 10
        
        # Check for game state management
        has_state = bool(re.search(r'gameBoard|board|currentPlayer|player|state', response_lower))
        if has_state:
            score += 10
        
        return min(100.0, score)
    
    def _evaluate_efficiency(self, response: str) -> float:
        """
        Evaluate code efficiency and optimization
        """
        score = 60.0  # Base score for efficiency
        
        # Check for redundancy
        lines = response.split('\n')
        non_empty_lines = [l.strip() for l in lines if l.strip()]
        
        # Check for repeated code patterns
        line_str = '\n'.join(non_empty_lines)
        repeated_patterns = len(re.findall(r'(.+)\n\1', line_str))
        
        if repeated_patterns == 0:
            score += 20  # No obvious repetition
        elif repeated_patterns < 3:
            score += 10
        
        # Check for use of loops instead of repetition
        has_loops = bool(re.search(r'for\s*\(|while\s*\(', response))
        if has_loops:
            score += 10
        
        # Check code size (not too bloated)
        if len(response) < 5000:
            score += 10
        
        return min(100.0, score)
    
    def _evaluate_documentation(self, response: str) -> float:
        """
        Evaluate code documentation and clarity
        """
        score = 40.0
        
        # Check for comments
        comments = len(re.findall(r'<!--.*?-->|//.*?$|/\*.*?\*/', response, re.MULTILINE | re.DOTALL))
        if comments > 3:
            score += 30
        elif comments > 0:
            score += 15
        
        # Check for meaningful variable names (longer than 1-2 chars)
        variables = re.findall(r'\b\w{3,}\b', response)
        meaningful_vars = [v for v in variables if not v.isdigit()]
        if len(meaningful_vars) > 5:
            score += 15
        
        # Check for readable code structure (not minified)
        if '\n' in response and len(response.split('\n')) > 5:
            score += 10
        
        return min(100.0, score)

# Global instance
code_quality_evaluator = CodeQualityEvaluator()
