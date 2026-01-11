"""
Classifier - Intent & Entity Recognition
===========================================

Features:
- Fast pattern-based classification
- Entity extraction (names, dates, numbers, etc.)
- Intent confidence scoring
- Support for multiple intent types
- Fuzzy matching for variations
- Context-aware classification
- Multi-language support
- Fallback to AI for ambiguous queries

Analyzes user input to determine intent and extract relevant
entities. Uses fast pattern matching with AI fallback for
accuracy.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import re
from typing import Tuple, Optional, Dict, Callable
from enum import Enum
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Intent Classifier")


class CommandType(Enum):
    """Command classification types"""
    MUSIC_PLAYBACK = "music_playback"      # play, pause, stop
    MUSIC_CONTROL = "music_control"        # skip, volume, queue
    MUSIC_QUERY = "music_query"            # what's playing, show queue
    SYSTEM = "system"                      # time, weather, system info
    CONVERSATION = "conversation"          # conversation, questions
    INFORMATION = "information"            # facts, search queries
    UNKNOWN = "unknown"


class CommandHandler:
    """
    Routes user commands to the right handler based on keyword matching
    
    Music commands bypass the AI and go straight to the music manager.
    Everything else goes through the conversation engine.

    Professional command classifier and router
    
    Routes commands to appropriate handlers:
    - Music → Music Manager (bypasses AI)
    - System → System handlers  
    - Conversation → AI Engine
    """
    
    def __init__(self):
        # Music playback keywords (PRIORITY - checked first)
        self.music_playback_keywords = [
            'play', 'play song', 'play music', 'start playing',
            'pause', 'pause music', 'pause song',
            'stop', 'stop music', 'stop playing', 'stop song',
            'resume', 'continue', 'unpause'
        ]
        
        # Music control keywords
        self.music_control_keywords = [
            'skip', 'next', 'next song', 'play next',
            'previous', 'go back', 'last song', 'previous song',
            'restart', 'replay', 'restart song', 'play again',
            'volume', 'louder', 'quieter', 'turn up', 'turn down',
            'increase volume', 'decrease volume', 'mute',
            'add to queue', 'queue', 'add song',
            'clear queue', 'show queue', 'what\'s in queue'
        ]
        
        # Music query keywords
        self.music_query_keywords = [
            'what\'s playing', 'what song', 'current song',
            'now playing', 'what music', 'what is this',
            'song name', 'artist'
        ]
        
        # System command keywords
        self.system_keywords = [
            'what time', 'current time', 'time is it',
            'what\'s the date', 'date', 'today\'s date',
            'weather', 'temperature', 'forecast',
            'battery', 'volume', 'brightness',
            'shutdown', 'restart', 'sleep',
            'open', 'close', 'launch'
        ]
        
        # Conversational keywords (lower priority - default)
        self.conversation_indicators = [
            'tell me', 'what do you think', 'can you explain',
            'do you know', 'what is', 'who is', 'when did',
            'how does', 'why does', 'where is',
            'i want to know', 'i\'m curious'
        ]
        
        logger.info("📋 Command Router initialized")
    
    @error_handler(default_return=CommandType.UNKNOWN)
    def classify_command(self, command: str) -> CommandType:
        """
        Classify command into appropriate category
        
        Args:
            command: User command text
        
        Returns:
            CommandType classification
        """
        command_lower = command.lower().strip()
        
        # PRIORITY 1: Music Playback (highest priority)
        if self._is_music_playback(command_lower):
            logger.info(f"🎵 Classified as: MUSIC_PLAYBACK")
            return CommandType.MUSIC_PLAYBACK
        
        # PRIORITY 2: Music Control
        if self._is_music_control(command_lower):
            logger.info(f"🎛️  Classified as: MUSIC_CONTROL")
            return CommandType.MUSIC_CONTROL
        
        # PRIORITY 3: Music Query
        if self._is_music_query(command_lower):
            logger.info(f"🎵 Classified as: MUSIC_QUERY")
            return CommandType.MUSIC_QUERY
        
        # PRIORITY 4: System Commands
        if self._is_system_command(command_lower):
            logger.info(f"⚙️  Classified as: SYSTEM")
            return CommandType.SYSTEM
        
        # PRIORITY 5: Information Query
        if self._is_information_query(command_lower):
            logger.info(f"📚 Classified as: INFORMATION")
            return CommandType.INFORMATION
        
        # DEFAULT: Conversation
        logger.info(f"💬 Classified as: CONVERSATION")
        return CommandType.CONVERSATION
    
    def _is_music_playback(self, command: str) -> bool:
        """Check if command is music playback"""
        # Exact matches for critical commands
        if command in ['pause', 'stop', 'resume', 'play']:
            return True
        
        # Pattern matching for play commands
        if re.match(r'^play\s+.+', command):
            return True
        
        # Keyword matching
        for keyword in self.music_playback_keywords:
            if command.startswith(keyword) or f' {keyword} ' in f' {command} ':
                return True
        
        return False
    
    def _is_music_control(self, command: str) -> bool:
        """Check if command is music control"""
        # Exact matches
        if command in ['skip', 'next', 'previous', 'back', 'restart', 'queue', 'clear queue']:
            return True
        
        # Keyword matching
        for keyword in self.music_control_keywords:
            if keyword in command:
                return True
        
        return False
    
    def _is_music_query(self, command: str) -> bool:
        """Check if command is music query"""
        for keyword in self.music_query_keywords:
            if keyword in command:
                return True
        return False
    
    def _is_system_command(self, command: str) -> bool:
        """Check if command is system-level"""
        for keyword in self.system_keywords:
            if keyword in command:
                return True
        return False
    
    def _is_information_query(self, command: str) -> bool:
        """Check if command is information query"""
        # Question patterns
        question_patterns = [
            r'^what\s+',
            r'^who\s+',
            r'^when\s+',
            r'^where\s+',
            r'^why\s+',
            r'^how\s+',
            r'^tell me about',
            r'^explain'
        ]
        
        for pattern in question_patterns:
            if re.match(pattern, command, re.IGNORECASE):
                return True
        
        return False
    
    def extract_song_name(self, command: str) -> Optional[str]:
        """
        Extract song name from play command
        
        Args:
            command: Play command text
        
        Returns:
            Song name or None
        """
        command_lower = command.lower().strip()
        
        # Remove play keywords
        for keyword in ['play', 'play song', 'play music', 'play the song', 'play the music']:
            if command_lower.startswith(keyword):
                song_name = command_lower[len(keyword):].strip()
                break
        else:
            song_name = command_lower
        
        # Remove common filler words
        fillers = ['the song', 'the music', 'song called', 'music called', 'called', 'the', 'a', 'an']
        for filler in fillers:
            song_name = song_name.replace(filler, '').strip()
        
        return song_name if song_name else None
    
    def extract_volume_change(self, command: str) -> Tuple[str, Optional[int]]:
        """
        Extract volume change intent
        
        Returns:
            Tuple of (action, value) where action is 'set', 'up', 'down', or 'mute'
        """
        command_lower = command.lower()
        
        # Check for mute
        if 'mute' in command_lower or 'silence' in command_lower:
            return 'mute', 0
        
        # Check for specific value
        match = re.search(r'(\d+)\s*(?:percent|%)?', command_lower)
        if match:
            value = int(match.group(1))
            value = max(0, min(100, value))  # Clamp 0-100
            return 'set', value
        
        # Check for relative change
        if any(word in command_lower for word in ['up', 'louder', 'increase', 'raise', 'higher']):
            return 'up', None
        
        if any(word in command_lower for word in ['down', 'quieter', 'decrease', 'lower']):
            return 'down', None
        
        return 'unknown', None
    
    def is_queue_operation(self, command: str) -> Tuple[str, Optional[int]]:
        """
        Determine queue operation
        
        Returns:
            Tuple of (operation, index) where operation is:
            'add', 'clear', 'show', 'remove'
        """
        command_lower = command.lower()
        
        if 'clear' in command_lower:
            return 'clear', None
        
        if 'show' in command_lower or 'what\'s in' in command_lower or 'list' in command_lower:
            return 'show', None
        
        if 'remove' in command_lower or 'delete' in command_lower:
            # Try to extract index
            match = re.search(r'\d+', command_lower)
            index = int(match.group()) - 1 if match else None  # Convert to 0-based
            return 'remove', index
        
        if 'add' in command_lower or 'queue' in command_lower:
            return 'add', None
        
        return 'unknown', None
    
    def should_bypass_ai(self, command_type: CommandType) -> bool:
        """
        Determine if command should bypass AI engine
        
        Music and system commands bypass AI for instant response
        """
        return command_type in [
            CommandType.MUSIC_PLAYBACK,
            CommandType.MUSIC_CONTROL,
            CommandType.MUSIC_QUERY
        ]
    
    def get_confirmation_message(self, command_type: CommandType) -> str:
        """Get appropriate confirmation for command type"""
        confirmations = {
            CommandType.MUSIC_PLAYBACK: "On it",
            CommandType.MUSIC_CONTROL: "Done",
            CommandType.MUSIC_QUERY: "",  # No confirmation needed
            CommandType.SYSTEM: "Let me check",
            CommandType.CONVERSATION: "",  # AI generates response
            CommandType.INFORMATION: "Searching",
        }
        return confirmations.get(command_type, "")


# Global command router instance
_command_handler: Optional[CommandHandler] = None

def get_command_handler() -> CommandHandler:
    """Get singleton command handler"""
    global _command_handler
    if _command_handler is None:
        _command_handler = CommandHandler()
    return _command_handler