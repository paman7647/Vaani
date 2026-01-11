"""
Context Manager - Conversation Memory & State
================================================

Features:
- Short-term conversation memory (last N exchanges)
- Long-term memory storage (persistent across restarts)
- User preference tracking
- Session state management
- Context-aware query understanding
- Memory pruning (keeps recent, relevant context)
- Topic tracking and continuity
- Entity tracking (people, places, things mentioned)

Tracks conversation history and context to enable natural,
context-aware responses. Remembers what was discussed recently
and maintains topic continuity.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import deque
from ..config import settings
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Context Manager")


class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 30):
        self.max_history = max_history
        self.conversation_history: deque = deque(maxlen=max_history)
        self.session_start = time.time()
        self.user_preferences: Dict[str, Any] = {}
        self.topics_discussed: List[str] = []
        logger.info("Conversation context initialized")
    
    def add_interaction(self, user_input: str, assistant_response: str, 
                       interaction_type: str = "conversation"):
        """
        Add an interaction to context
        
        Args:
            user_input: What user said
            assistant_response: What assistant responded
            interaction_type: Type of interaction (conversation, command, music, etc.)
        """
        interaction = {
            'timestamp': time.time(),
            'user': user_input,
            'assistant': assistant_response,
            'type': interaction_type
        }
        
        self.conversation_history.append(interaction)
        
        # Extract potential topics
        self._extract_topics(user_input)
        
        logger.debug(f"Added interaction to context (type: {interaction_type})")
    
    def _extract_topics(self, text: str):
        """Extract potential topics from text"""
        # Simple keyword extraction
        keywords = ['music', 'weather', 'time', 'date', 'search', 'play', 'stop']
        
        for keyword in keywords:
            if keyword in text.lower() and keyword not in self.topics_discussed:
                self.topics_discussed.append(keyword)
    
    def get_recent_context(self, num_interactions: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return list(self.conversation_history)[-num_interactions:]
    
    def get_context_summary(self) -> str:
        """Get a summary of recent context for AI"""
        if not self.conversation_history:
            return ""
        
        recent = self.get_recent_context(3)
        
        context_lines = []
        for interaction in recent:
            context_lines.append(f"User: {interaction['user']}")
            context_lines.append(f"You: {interaction['assistant']}")
        
        return "\n".join(context_lines)
    
    def remember_preference(self, key: str, value: Any):
        """Remember a user preference"""
        self.user_preferences[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.info(f"Remembered preference: {key} = {value}")
    
    def get_preference(self, key: str) -> Optional[Any]:
        """Get a user preference"""
        pref = self.user_preferences.get(key)
        return pref['value'] if pref else None
    
    def has_discussed_recently(self, topic: str, within_seconds: int = 300) -> bool:
        """Check if topic was discussed recently"""
        cutoff_time = time.time() - within_seconds
        
        for interaction in reversed(self.conversation_history):
            if interaction['timestamp'] < cutoff_time:
                break
            
            if topic.lower() in interaction['user'].lower():
                return True
        
        return False
    
    def get_last_user_input(self) -> Optional[str]:
        """Get the last thing user said"""
        if self.conversation_history:
            return self.conversation_history[-1]['user']
        return None
    
    def get_last_response(self) -> Optional[str]:
        """Get the last assistant response"""
        if self.conversation_history:
            return self.conversation_history[-1]['assistant']
        return None
    
    def clear_session(self):
        """Clear current session context"""
        self.conversation_history.clear()
        self.topics_discussed.clear()
        self.session_start = time.time()
        logger.info("Session context cleared")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about current session"""
        return {
            'duration': time.time() - self.session_start,
            'interactions': len(self.conversation_history),
            'topics': self.topics_discussed,
            'preferences_set': len(self.user_preferences)
        }


class LongTermMemory:
    """Optional long-term context using simple JSON storage"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path.home() / '.vaani' / 'context.json'
        
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.data: Dict[str, Any] = self._load()
        logger.info(f"Long-term context initialized (path: {storage_path})")
    
    @error_handler(default_return={'preferences': {}, 'facts': {}, 'history': []})
    def _load(self) -> Dict[str, Any]:
        """Load context from disk"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading long-term context: {e}")
        
        return {
            'preferences': {},
            'facts': {},
            'history': []
        }
    
    @error_handler(default_return=None)
    def _save(self):
        """Save context to disk"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving long-term context: {e}")
    
    def remember_fact(self, key: str, value: Any):
        """Remember a fact long-term"""
        self.data['facts'][key] = {
            'value': value,
            'timestamp': time.time()
        }
        self._save()
        logger.info(f"Remembered fact: {key}")
    
    def recall_fact(self, key: str) -> Optional[Any]:
        """Recall a fact"""
        fact = self.data['facts'].get(key)
        return fact['value'] if fact else None
    
    def store_preference(self, key: str, value: Any):
        """Store a preference long-term"""
        self.data['preferences'][key] = value
        self._save()
    
    def get_preference(self, key: str) -> Optional[Any]:
        """Get a stored preference"""
        return self.data['preferences'].get(key)


# Global context instances
_conversation_context: Optional[ConversationMemory] = None
_long_term_context: Optional[LongTermMemory] = None

def get_conversation_context() -> ConversationMemory:
    """Get or create global conversation context"""
    global _conversation_context
    if _conversation_context is None:
        _conversation_context = ConversationMemory()
    return _conversation_context

def get_long_term_context() -> LongTermMemory:
    """Get or create global long-term context"""
    global _long_term_context
    if _long_term_context is None:
        _long_term_context = LongTermMemory()
    return _long_term_context
