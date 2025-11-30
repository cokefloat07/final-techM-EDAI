from typing import Dict, List, Any
from datetime import datetime, timedelta

class AccuracyMetrics:
    def __init__(self):
        self.metrics_history = []
    
    def calculate_model_performance(self, estimates: List[Dict]) -> Dict[str, Any]:
        """Calculate performance metrics for models"""
        if not estimates:
            return {}
            
        model_data = {}
        
        for estimate in estimates:
            model_name = estimate.get('model_name')
            if model_name not in model_data:
                model_data[model_name] = {
                    'total_requests': 0,
                    'accuracy_scores': [],
                    'carbon_per_request': [],
                    'response_times': []
                }
            
            model_data[model_name]['total_requests'] += 1
            model_data[model_name]['accuracy_scores'].append(
                estimate.get('accuracy_scores', {}).get('overall_accuracy', 0)
            )
            model_data[model_name]['carbon_per_request'].append(
                estimate.get('carbon_emitted_kgco2', 0)
            )
            model_data[model_name]['response_times'].append(
                estimate.get('inference_time_ms', 0)
            )
        
        # Calculate aggregates
        performance_metrics = {}
        for model_name, data in model_data.items():
            accuracy_scores = data['accuracy_scores']
            carbon_values = data['carbon_per_request']
            response_times = data['response_times']
            
            performance_metrics[model_name] = {
                'total_requests': data['total_requests'],
                'avg_accuracy': sum(accuracy_scores) / len(accuracy_scores),
                'avg_carbon_kgco2': sum(carbon_values) / len(carbon_values),
                'avg_response_time_ms': sum(response_times) / len(response_times),
                'accuracy_std_dev': self._calculate_std_dev(accuracy_scores),
                'carbon_efficiency': self._calculate_carbon_efficiency(
                    sum(accuracy_scores) / len(accuracy_scores),
                    sum(carbon_values) / len(carbon_values)
                )
            }
        
        return performance_metrics
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _calculate_carbon_efficiency(self, accuracy: float, carbon: float) -> float:
        """Calculate carbon efficiency score (accuracy per unit carbon)"""
        if carbon <= 0:
            return accuracy * 100  # Arbitrary high efficiency
        return (accuracy / carbon) * 1000  # Scale for readability

accuracy_metrics = AccuracyMetrics()
