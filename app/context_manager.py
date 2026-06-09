
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

class ContextManager:
    def __init__(self):
        self.conversation_contexts = {}
        self.max_context_length = 10  # Maximum messages to keep in context
        
    def create_conversation(self, user_id: str = None) -> str:
        """Create a new conversation context"""
        conversation_id = str(uuid.uuid4())
        
        self.conversation_contexts[conversation_id] = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": [],
            "model_usage": {},
            "topics": [],
            "preferences": {},
            "summary": ""
        }
        
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   model_used: str = None, accuracy_scores: Dict = None) -> bool:
        """Add a message to conversation context"""
        if conversation_id not in self.conversation_contexts:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "model_used": model_used,
            "accuracy_scores": accuracy_scores or {}
        }
        
        context = self.conversation_contexts[conversation_id]
        context["messages"].append(message)
        context["updated_at"] = datetime.utcnow()
        
        # Update model usage statistics
        if model_used:
            if model_used not in context["model_usage"]:
                context["model_usage"][model_used] = {
                    "count": 0,
                    "total_accuracy": 0.0,
                    "last_used": datetime.utcnow()
                }
            context["model_usage"][model_used]["count"] += 1
            if accuracy_scores and "overall_accuracy" in accuracy_scores:
                context["model_usage"][model_used]["total_accuracy"] += accuracy_scores["overall_accuracy"]
        
        # Maintain context length
        if len(context["messages"]) > self.max_context_length:
            context["messages"] = context["messages"][-self.max_context_length:]
        
        # Update topics
        self._update_topics(conversation_id, content)
        
        # Generate summary if needed
        if len(context["messages"]) % 5 == 0:  # Update summary every 5 messages
            self._generate_summary(conversation_id)
        
        return True
    
    def get_conversation_context(self, conversation_id: str) -> Optional[Dict]:
        """Get full conversation context"""
        return self.conversation_contexts.get(conversation_id)
    
    def get_recent_messages(self, conversation_id: str, last_n: int = 5) -> List[Dict]:
        """Get recent messages from conversation"""
        context = self.conversation_contexts.get(conversation_id)
        if not context:
            return []
        
        return context["messages"][-last_n:]
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """Get conversation summary"""
        context = self.conversation_contexts.get(conversation_id)
        if not context:
            return ""
        
        if not context["summary"] and context["messages"]:
            self._generate_summary(conversation_id)
        
        return context.get("summary", "")
    
    def get_model_preferences(self, conversation_id: str) -> Dict[str, Any]:
        """Get model preferences based on conversation history"""
        context = self.conversation_contexts.get(conversation_id)
        if not context:
            return {}
        
        preferences = {
            "preferred_models": [],
            "avoided_models": [],
            "domain_preferences": {},
            "performance_history": {}
        }
        
        # Analyze model performance
        for model_name, usage in context["model_usage"].items():
            avg_accuracy = usage["total_accuracy"] / usage["count"] if usage["count"] > 0 else 0.5
            
            if avg_accuracy > 0.7:
                preferences["preferred_models"].append(model_name)
            elif avg_accuracy < 0.4:
                preferences["avoided_models"].append(model_name)
            
            preferences["performance_history"][model_name] = {
                "usage_count": usage["count"],
                "average_accuracy": avg_accuracy,
                "last_used": usage["last_used"]
            }
        
        return preferences
    
    def _update_topics(self, conversation_id: str, new_content: str):
        """Update conversation topics based on new content"""
        context = self.conversation_contexts.get(conversation_id)
        if not context:
            return
        
        # Simple topic extraction (in real implementation, use NLP)
        topic_keywords = {
            "technology": ["code", "program", "software", "tech", "computer", "algorithm"],
            "science": ["research", "study", "experiment", "data", "analysis", "scientific"],
            "business": ["company", "business", "strategy", "market", "sales", "profit"],
            "education": ["learn", "study", "teach", "education", "school", "university"],
            "health": ["health", "medical", "treatment", "medicine", "symptoms", "doctor"]
        }
        
        content_lower = new_content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if topic not in context["topics"]:
                    context["topics"].append(topic)
        
        # Keep only recent topics
        context["topics"] = context["topics"][-5:]
    
    def _generate_summary(self, conversation_id: str):
        """Generate a summary of the conversation"""
        context = self.conversation_contexts.get(conversation_id)
        if not context or not context["messages"]:
            return
        
        # Simple summary generation (in real implementation, use summarization model)
        user_messages = [msg["content"] for msg in context["messages"] if msg["role"] == "user"]
        assistant_messages = [msg["content"] for msg in context["messages"] if msg["role"] == "assistant"]
        
        if user_messages:
            last_user_message = user_messages[-1]
            summary = f"Conversation about: {last_user_message[:100]}..."
        else:
            summary = "General conversation"
        
        context["summary"] = summary
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations"""
        current_time = datetime.utcnow()
        expired_conversations = []
        
        for conv_id, context in self.conversation_contexts.items():
            if current_time - context["updated_at"] > timedelta(hours=max_age_hours):
                expired_conversations.append(conv_id)
        
        for conv_id in expired_conversations:
            del self.conversation_contexts[conv_id]
    
    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Get statistics for a conversation"""
        context = self.conversation_contexts.get(conversation_id)
        if not context:
            return {}
        
        user_messages = [msg for msg in context["messages"] if msg["role"] == "user"]
        assistant_messages = [msg for msg in context["messages"] if msg["role"] == "assistant"]
        
        return {
            "total_messages": len(context["messages"]),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "models_used": list(context["model_usage"].keys()),
            "topics": context["topics"],
            "duration_minutes": (context["updated_at"] - context["created_at"]).total_seconds() / 60,
            "average_accuracy": self._calculate_average_accuracy(context)
        }
    
    def _calculate_average_accuracy(self, context: Dict) -> float:
        """Calculate average accuracy across all messages"""
        accuracy_scores = []
        for message in context["messages"]:
            if message.get("accuracy_scores") and "overall_accuracy" in message["accuracy_scores"]:
                accuracy_scores.append(message["accuracy_scores"]["overall_accuracy"])
        
        return sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0

# Global instance
context_manager = ContextManager()
