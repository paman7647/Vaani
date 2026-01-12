"""
Personality Engine - Voice & Behavior Customization
======================================================

Features:
- Configurable personality traits (helpful, friendly, professional)
- Tone adaptation based on context
- Mood tracking and appropriate responses
- Cultural awareness and sensitivity
- Humor and casual conversation support
- Response style customization
- Personality profiles (formal, casual, witty)

Defines Vaani's personality and interaction style. Makes conversations
feel natural and human-like with consistent character traits.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import re
from typing import Literal, Optional
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Personality Engine")


class PersonalityModule:
    """Applies personality traits to responses - handles tone, style, and speech optimization"""
    
    def __init__(self):
        self.personality_traits = {
            'name': 'Vaani',
            'tone': 'warm and friendly',
            'style': 'conversational and natural',
            'formality': 'casual but respectful'
        }
        
        self.greeting_variations = [
            "Hello!",
            "Hi there!",
            "Hey!",
            "Hello, how can I help?"
        ]
        
        self.acknowledgments = [
            "Got it",
            "Understood",
            "Sure",
            "Okay",
            "Alright"
        ]
        
        logger.info("Personality module loaded")
    
    @error_handler(default_return=None)
    def process_response(self, text: str, 
                        context: Literal['greeting', 'command', 'conversation', 
                                       'error', 'confirmation'] = 'conversation') -> str:
        """
        Post-process AI response for natural speech
        
        Args:
            text: Raw AI response
            context: Response context
        
        Returns:
            Processed, speech-optimized response
        """
        if not text:
            return text
        
        # Apply context-specific processing
        if context == 'error':
            text = self._make_apologetic(text)
        elif context == 'confirmation':
            text = self._make_concise(text)
        elif context == 'greeting':
            text = self._make_warm(text)
        
        # General post-processing
        text = self._remove_jargon(text)
        text = self._optimize_for_speech(text)
        text = self._add_natural_pauses(text)
        text = self._limit_length(text)
        
        return text
    
    def _make_apologetic(self, text: str) -> str:
        """Add apologetic tone for errors"""
        apologies = [
            "I'm sorry, ",
            "My apologies, ",
            "Sorry about that, "
        ]
        
        if not any(text.startswith(a) for a in ["Sorry", "I'm sorry", "Apologies"]):
            text = "Sorry about that. " + text
        
        # Remove technical details
        text = re.sub(r'\b(error|exception|failed|traceback)\b', 'issue', text, flags=re.IGNORECASE)
        
        return text
    
    def _make_concise(self, text: str) -> str:
        """Make confirmations brief and natural"""
        # If it's already short, keep it
        if len(text) < 20:
            return text
        
        # Extract key action
        if 'playing' in text.lower():
            return "Playing it now."
        elif 'stopped' in text.lower():
            return "Stopped."
        elif 'paused' in text.lower():
            return "Paused."
        elif 'volume' in text.lower():
            return "Volume adjusted."
        
        # Otherwise keep first sentence only
        sentences = text.split('. ')
        return sentences[0] + '.' if sentences[0] else text
    
    def _make_warm(self, text: str) -> str:
        """Add warmth to greetings"""
        if not text.endswith('!') and len(text) < 50:
            text = text.rstrip('.') + '!'
        
        return text
    
    def _remove_jargon(self, text: str) -> str:
        """Remove technical jargon"""
        replacements = {
            'API': 'system',
            'database': 'context',
            'execute': 'do',
            'terminate': 'stop',
            'initialize': 'start',
            'parameter': 'setting',
            'configuration': 'setup'
        }
        
        for jargon, replacement in replacements.items():
            text = re.sub(r'\b' + jargon + r'\b', replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _optimize_for_speech(self, text: str) -> str:
        """Optimize text for natural speech"""
        # Remove markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'_(.+?)_', r'\1', text)  # Underscore
        text = re.sub(r'`(.+?)`', r'\1', text)  # Code
        
        # Remove URLs (they don't speak well)
        text = re.sub(r'https?://\S+', 'the website', text)
        
        # Convert lists to spoken format
        text = re.sub(r'^\s*[-•*]\s+', '', text, flags=re.MULTILINE)
        
        # Remove extra newlines
        text = re.sub(r'\n+', '. ', text)
        
        # Fix common speech issues
        text = text.replace('e.g.', 'for example')
        text = text.replace('i.e.', 'that is')
        text = text.replace('etc.', 'and so on')
        
        return text
    
    def _add_natural_pauses(self, text: str) -> str:
        """Add natural pauses for better speech flow"""
        # Add pause after introductory phrases
        text = re.sub(r'\b(Well|So|Now|Actually|Basically),\s', r'\1... ', text)
        
        # Add pause before conjunctions
        text = re.sub(r'\s(however|although|meanwhile|furthermore)', r'... \1', text)
        
        return text
    
    def _limit_length(self, text: str, max_length: int = 500) -> str:
        """Limit response length for speech"""
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence boundary
        sentences = text[:max_length].split('. ')
        
        if len(sentences) > 1:
            # Keep all but last incomplete sentence
            result = '. '.join(sentences[:-1]) + '.'
            logger.debug(f"Truncated long response: {len(text)} → {len(result)} chars")
            return result
        
        # Cut at word boundary
        result = text[:max_length].rsplit(' ', 1)[0] + '...'
        logger.debug(f"Hard-truncated response: {len(text)} → {len(result)} chars")
        return result
    
    def create_system_prompt(self) -> str:
        """Create system prompt that defines personality"""
        return f"""You are {self.personality_traits['name']}, a {self.personality_traits['tone']} AI voice assistant.

Your personality:
- Warm, friendly, and conversational
- Clear and concise in responses
- Never overly technical or robotic
- Naturally helpful without being pushy
- Calm and reassuring when errors occur

Communication style:
- Use natural, spoken language
- Keep responses brief (2-3 sentences typically)
- Avoid long explanations unless asked
- Use simple, everyday words
- Be confident but not arrogant

When speaking:
- You will be heard, not read
- Keep sentences short and clear
- Use conversational phrasing
- Avoid lists, bullet points, or formatting

Remember:
- User is speaking, not reading
- Speak naturally as a human would
- Stay on topic
- Be helpful and pleasant"""
    
    def handle_interruption(self) -> str:
        """Generate response when interrupted"""
        return "Yes, what do you need?"
    
    def handle_confusion(self, user_input: str) -> str:
        """Generate response when command is unclear"""
        if len(user_input) < 5:
            return "I didn't catch that. Could you say it again?"
        else:
            return "I'm not sure I understood. Could you rephrase that?"
    
    def processing_message(self) -> str:
        """Message to say when processing takes time"""
        return "One moment..."
    
    def thinking_message(self) -> str:
        """Message when generating complex response"""
        return "Let me think about that..."


# Global personality engine
_personality_module: Optional[PersonalityModule] = None

def get_personality_module() -> PersonalityModule:
    """Get singleton personality module"""
    global _personality_module
    if _personality_module is None:
        _personality_module = PersonalityModule()
    return _personality_module
