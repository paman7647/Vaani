"""
Intent Analyzer - Fast Command Classification
================================================

Features:
- RapidFuzz-based pattern matching (sub-second classification)
- Multiple intent types (music, time, information, conversation, etc.)
- Entity extraction (song names, times, topics)
- Confidence scoring
- AI-powered fallback for complex queries
- Keyword-based classification with fuzzy matching
- Support for natural language variations
- Minimal logging (professional output)

Quickly figures out what you want using fast pattern matching.
Uses AI only when needed for complex or ambiguous requests.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    
# Spacy is incompatible with Python 3.14+ (pydantic v1 issue)
# Disable it and use fallback intent classification
import sys
SPACY_AVAILABLE = False
nlp = None

if sys.version_info < (3, 14):
    try:
        import spacy
        # Try to load small English model
        try:
            nlp = spacy.load("en_core_web_sm")
            SPACY_AVAILABLE = True
        except:
            pass
    except ImportError:
        pass

from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Intent Analyzer")


class IntentType(Enum):
    """Refined intent categories"""
    # Music intent_analyzer
    MUSIC_PLAY = "music_play"
    MUSIC_PAUSE = "music_pause"
    MUSIC_STOP = "music_stop"
    MUSIC_RESUME = "music_resume"
    MUSIC_NEXT = "music_next"
    MUSIC_PREVIOUS = "music_previous"
    MUSIC_VOLUME_UP = "music_volume_up"
    MUSIC_VOLUME_DOWN = "music_volume_down"
    MUSIC_VOLUME_SET = "music_volume_set"
    MUSIC_QUEUE_ADD = "music_queue_add"
    MUSIC_QUEUE_SHOW = "music_queue_show"
    MUSIC_QUEUE_CLEAR = "music_queue_clear"
    MUSIC_CURRENT = "music_current"
    
    # System intent_analyzer
    SYSTEM_TIME = "system_time"
    SYSTEM_DATE = "system_date"
    SYSTEM_WEATHER = "system_weather"
    SYSTEM_EXIT = "system_exit"
    
    # Information intent_analyzer
    INFO_WHAT = "info_what"
    INFO_WHO = "info_who"
    INFO_WHERE = "info_where"
    INFO_WHEN = "info_when"
    INFO_WHY = "info_why"
    INFO_HOW = "info_how"
    
    # Conversation
    CONVERSATION = "conversation"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: IntentType
    confidence: float  # 0.0 to 1.0
    entities: Dict[str, Any]  # Extracted entities (song_name, volume, etc.)
    requires_ai: bool  # Should this go to AI engine?


class IntentMatcher:
    """
    Intent matching using free NLP tools
    
    Features:
    - Fuzzy matching for typos and variations
    - Entity extraction (numbers, names, etc.)
    - Synonym handling
    - Multi-language support (English + Hindi)
    - Pattern-based extraction
    - Context awareness
    """
    
    def __init__(self):
        self.fuzzy_threshold = 80  # Minimum similarity score (0-100)
        
        # Intent patterns with examples for fuzzy matching
        self.intent_patterns = {
            IntentType.MUSIC_PLAY: [
                "play", "play song", "play music", "start playing", "put on",
                "play the song", "can you play", "i want to hear", "start music",
                # Hindi/Romanized patterns
                "bajao", "gana bajao", "music chalao", "gaana sunao",
                "sing me a song", "sing a song", "play karo"
            ],
            IntentType.MUSIC_PAUSE: [
                "pause", "pause music", "pause song", "hold on", "wait",
                "stop for now", "pause it"
            ],
            IntentType.MUSIC_STOP: [
                "stop", "stop music", "stop playing", "stop song", "end music",
                "turn off music", "close music"
            ],
            IntentType.MUSIC_RESUME: [
                "resume", "continue", "keep playing", "unpause", "play again",
                "resume music", "continue music", "carry on"
            ],
            IntentType.MUSIC_NEXT: [
                "next", "skip", "next song", "skip song", "play next",
                "next track", "forward", "skip this"
            ],
            IntentType.MUSIC_PREVIOUS: [
                "previous", "back", "go back", "previous song", "last song",
                "play previous", "rewind", "back track"
            ],
            IntentType.MUSIC_VOLUME_UP: [
                "volume up", "louder", "increase volume", "turn up", "raise volume",
                "make it louder", "boost volume", "up volume"
            ],
            IntentType.MUSIC_VOLUME_DOWN: [
                "volume down", "quieter", "decrease volume", "turn down", "lower volume",
                "make it quieter", "reduce volume", "down volume", "softer"
            ],
            IntentType.MUSIC_VOLUME_SET: [
                "volume", "set volume", "volume to", "set volume to"
            ],
            IntentType.MUSIC_QUEUE_ADD: [
                "add to queue", "queue", "add song", "add this", "queue song",
                "add to playlist"
            ],
            IntentType.MUSIC_QUEUE_SHOW: [
                "show queue", "what's in queue", "queue list", "show playlist",
                "what's queued", "list queue"
            ],
            IntentType.MUSIC_QUEUE_CLEAR: [
                "clear queue", "empty queue", "remove queue", "delete queue"
            ],
            IntentType.MUSIC_CURRENT: [
                "what's playing", "current song", "what song", "what is this",
                "song name", "what's this song", "playing now"
            ],
            IntentType.SYSTEM_TIME: [
                "what time", "tell time", "current time", "time is", "what's the time"
            ],
            IntentType.SYSTEM_DATE: [
                "what date", "today's date", "current date", "what day", "date today"
            ],
            IntentType.SYSTEM_WEATHER: [
                "weather", "temperature", "how's weather", "weather today", "forecast"
            ],
            IntentType.SYSTEM_EXIT: [
                "exit", "quit", "goodbye", "bye", "shut down", "close", "stop assistant"
            ],
            # Information/Question intent_analyzer
            IntentType.INFO_WHAT: [
                "what is", "what are", "what's", "whats", "tell me about", 
                "explain what", "define", "meaning of", "definition of", "what was"
            ],
            IntentType.INFO_WHO: [
                "who is", "who are", "who's", "whos", "tell me who", 
                "who was", "who were"
            ],
            IntentType.INFO_WHERE: [
                "where is", "where are", "where's", "wheres", "tell me where",
                "where can i find", "location of"
            ],
            IntentType.INFO_WHEN: [
                "when is", "when was", "when did", "when will", "whens",
                "what time", "tell me when"
            ],
            IntentType.INFO_WHY: [
                "why is", "why are", "why did", "why does", "whys",
                "reason for", "tell me why"
            ],
            IntentType.INFO_HOW: [
                "how is", "how are", "how do", "how does", "how to",
                "hows", "tell me how", "explain how"
            ],
            IntentType.CONVERSATION: [
                "hello", "hi", "hey", "how are you", "thanks", "thank you",
                "good morning", "good evening", "nice to meet you"
            ]
        }
        
        # Regex patterns for entity extraction
        self.entity_patterns = {
            'volume_number': re.compile(r'(\d+)\s*(?:percent|%)?'),
            'song_name_after_play': re.compile(r'play\s+(?:the\s+)?(?:song\s+)?(.+)', re.IGNORECASE),
            'song_name_general': re.compile(r'(?:song|music|track)\s+(.+)', re.IGNORECASE),
            'number': re.compile(r'\d+'),
        }
        
        # Synonyms for common words
        self.synonyms = {
            'increase': ['raise', 'boost', 'up', 'higher', 'more'],
            'decrease': ['lower', 'reduce', 'down', 'less', 'softer'],
            'play': ['start', 'begin', 'put on'],
            'pause': ['hold', 'wait', 'stop temporarily'],
            'stop': ['end', 'quit', 'close', 'terminate'],
        }
        
    @error_handler(default_return=IntentResult(IntentType.UNKNOWN, 0.0, {}, True))
    def classify(self, command: str, context: Optional[Dict] = None) -> IntentResult:
        """
        Classify user command into intent + extract entities
        
        Args:
            command: User command text
            context: Optional context (music_playing, last_intent, etc.)
        
        Returns:
            IntentResult with intent, confidence, and entities
        """
        command = command.strip().lower()
        
        # 1. Try exact/fuzzy pattern matching first (fast)
        intent, confidence, entities = self._fuzzy_match_intent(command)
        
        # 2. If low confidence, try regex patterns
        if confidence < 0.6:
            regex_intent, regex_entities = self._regex_extract(command)
            if regex_intent:
                intent = regex_intent
                confidence = 0.8
                entities.update(regex_entities)
        
        # 3. If still low confidence, check question patterns
        if confidence < 0.6:
            question_intent = self._detect_question_type(command)
            if question_intent:
                intent = question_intent
                confidence = 0.7
        
        # 4. Use spaCy for advanced entity extraction (if available)
        if SPACY_AVAILABLE and entities.get('needs_extraction', False):
            spacy_entities = self._extract_with_spacy(command)
            entities.update(spacy_entities)
        
        # 5. Determine if AI is needed
        requires_ai = self._requires_ai(intent, confidence, command)
        
        return IntentResult(
            intent=intent,
            confidence=confidence,
            entities=entities,
            requires_ai=requires_ai
        )
    
    def _fuzzy_match_intent(self, command: str) -> Tuple[IntentType, float, Dict]:
        """Use fuzzy matching to find best intent"""
        if not RAPIDFUZZ_AVAILABLE:
            # Fallback to simple substring matching
            return self._simple_match(command)
        
        best_intent = IntentType.UNKNOWN
        best_score = 0.0
        entities = {}
        
        # Try fuzzy match against all patterns
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                score = fuzz.ratio(command, pattern)
                
                # Also check if command contains pattern (partial match)
                if pattern in command:
                    score = max(score, 85)  # Boost for substring match
                
                # Check token similarity
                token_score = fuzz.token_set_ratio(command, pattern)
                score = max(score, token_score)
                
                if score > best_score:
                    best_score = score
                    best_intent = intent_type
        
        # Normalize score to 0-1 range
        confidence = best_score / 100.0
        
        # Extract entities based on intent
        if confidence >= 0.5:
            entities = self._extract_entities_for_intent(command, best_intent)
        
        return best_intent, confidence, entities
    
    def _simple_match(self, command: str) -> Tuple[IntentType, float, Dict]:
        """Simple substring matching (fallback when rapidfuzz unavailable)"""
        best_intent = IntentType.UNKNOWN
        best_score = 0.0
        entities = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in command:
                    # Calculate rough similarity
                    score = len(pattern) / len(command) if len(command) > 0 else 0
                    score = min(score, 1.0)
                    
                    if score > best_score:
                        best_score = score
                        best_intent = intent_type
        
        if best_score >= 0.3:
            entities = self._extract_entities_for_intent(command, best_intent)
        
        return best_intent, max(best_score, 0.5), entities
    
    def _regex_extract(self, command: str) -> Tuple[Optional[IntentType], Dict]:
        """Extract intent and entities using regex patterns"""
        entities = {}
        
        # Volume number
        if 'volume' in command:
            match = self.entity_patterns['volume_number'].search(command)
            if match:
                entities['volume'] = int(match.group(1))
                return IntentType.MUSIC_VOLUME_SET, entities
        
        # Play song command
        if command.startswith('play'):
            match = self.entity_patterns['song_name_after_play'].search(command)
            if match:
                song_name = match.group(1).strip()
                if song_name and song_name not in ['music', 'song', 'it']:
                    entities['song_name'] = song_name
                    return IntentType.MUSIC_PLAY, entities
        
        return None, entities
    
    def _detect_question_type(self, command: str) -> Optional[IntentType]:
        """Detect question type for information queries"""
        if command.startswith('what'):
            if any(word in command for word in ['time', 'clock']):
                return IntentType.SYSTEM_TIME
            elif any(word in command for word in ['date', 'day', 'today']):
                return IntentType.SYSTEM_DATE
            elif any(word in command for word in ['playing', 'song', 'music', 'this']):
                return IntentType.MUSIC_CURRENT
            else:
                return IntentType.INFO_WHAT
        
        elif command.startswith('who'):
            return IntentType.INFO_WHO
        elif command.startswith('where'):
            return IntentType.INFO_WHERE
        elif command.startswith('when'):
            return IntentType.INFO_WHEN
        elif command.startswith('why'):
            return IntentType.INFO_WHY
        elif command.startswith('how'):
            if 'weather' in command:
                return IntentType.SYSTEM_WEATHER
            return IntentType.INFO_HOW
        
        return None
    
    def _extract_entities_for_intent(self, command: str, intent: IntentType) -> Dict:
        """Extract relevant entities based on detected intent"""
        entities = {}
        
        # Extract song name for play commands
        if intent == IntentType.MUSIC_PLAY:
            song_name = self._extract_song_name(command)
            if song_name:
                entities['song_name'] = song_name
        
        # Extract volume for volume commands
        elif intent in [IntentType.MUSIC_VOLUME_SET, IntentType.MUSIC_VOLUME_UP, IntentType.MUSIC_VOLUME_DOWN]:
            match = self.entity_patterns['volume_number'].search(command)
            if match:
                entities['volume'] = int(match.group(1))
        
        return entities
    
    def _extract_song_name(self, command: str) -> Optional[str]:
        """Extract song name from play command"""
        # Try direct extraction after 'play'
        match = self.entity_patterns['song_name_after_play'].search(command)
        if match:
            song_name = match.group(1).strip()
            # Remove common filler words
            for filler in ['the song', 'song', 'music', 'please', 'for me']:
                song_name = song_name.replace(filler, '').strip()
            
            if song_name and len(song_name) > 1:
                return song_name
        
        return None
    
    def _extract_with_spacy(self, command: str) -> Dict:
        """Use spaCy for advanced entity extraction"""
        if not SPACY_AVAILABLE:
            return {}
        
        entities = {}
        doc = nlp(command)
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'WORK_OF_ART']:
                entities['potential_song'] = ent.text
            elif ent.label_ == 'CARDINAL':
                entities['number'] = int(ent.text) if ent.text.isdigit() else ent.text
        
        return entities
    
    def _requires_ai(self, intent: IntentType, confidence: float, command: str) -> bool:
        """Determine if command needs AI processing"""
        # Low confidence = needs AI
        if confidence < 0.6:
            return True
        
        # Information queries need AI
        if intent in [IntentType.INFO_WHAT, IntentType.INFO_WHO, IntentType.INFO_WHERE,
                      IntentType.INFO_WHEN, IntentType.INFO_WHY, IntentType.INFO_HOW]:
            return True
        
        # Conversation intent needs AI
        if intent == IntentType.CONVERSATION:
            return True
        
        # Unknown intent needs AI
        if intent == IntentType.UNKNOWN:
            return True
        
        # Everything else can be handled directly
        return False


# Global instance
_intent_matcher: Optional[IntentMatcher] = None

def get_intent_matcher() -> IntentMatcher:
    """Get or create global intent matcher instance"""
    global _intent_matcher
    if _intent_matcher is None:
        _intent_matcher = IntentMatcher()
    return _intent_matcher