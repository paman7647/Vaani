"""
Settings Manager - Configuration System
==========================================

Features:
- Centralized configuration management
- Three-tier priority: Environment → config.json → Defaults
- API key management
- Speech recognition parameters (thresholds, timeouts)
- Voice preferences and language mapping
- Wake word configuration with variations
- Dynamic energy threshold adjustment
- TTS interruption settings
- Music ducking configuration
- System paths (data, logs, temp, models)

Loads and manages all configuration from environment variables,
config.json, and built-in defaults. Single source of truth for
all system settings.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

import os
from pathlib import Path
from typing import Dict, Any

import json

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
TEMP_DIR = BASE_DIR / "temp"

# Load external config if exists
CONFIG_FILE = BASE_DIR / "config.json"
EXTERNAL_CONFIG = {}
if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, 'r') as f:
            EXTERNAL_CONFIG = json.load(f)
        print(f"✅ Loaded external config from {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠️ Could not load config.json: {e}")

# Helper to get setting with priority: Env > External Config > Default
def get_setting(key, default):
    return os.getenv(key, EXTERNAL_CONFIG.get(key, default))

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# =============================================================================
# API KEYS - CONFIGURE THESE
# =============================================================================

# REQUIRED: Google Gemini API key(s)
# Support multiple API keys separated by comma for rotation on quota exhaustion
# Example: "key1,key2,key3" - will rotate through keys when quota exceeded
# REQUIRED: Google Gemini API key(s)
# Support multiple API keys separated by comma for rotation on quota exhaustion
# Example: "key1,key2,key3" - will rotate through keys when quota exceeded
GOOGLE_API_KEY = get_setting("GOOGLE_API_KEY", "your-api-key-here")
GOOGLE_API_KEYS = [key.strip() for key in GOOGLE_API_KEY.split(',') if key.strip()]  # Parse multiple keys

# Optional API keys
WEATHER_API_KEY = get_setting("WEATHER_API_KEY", "your-weather-api-key-here ")

# =============================================================================
# SPEECH RECOGNITION SETTINGS
# =============================================================================

# Wake words and variations - Vani (वाणी) means 'voice/speech' in Sanskrit
# Added 'Shivani' as common Indian name variant
WAKE_WORDS = EXTERNAL_CONFIG.get('WAKE_WORDS', ['hey vani', 'vani', 'okay vani', 'hi vani', 'hello vani', 'hai vani', 'shivani', 'hey shivani'])
WAKE_WORD_VARIATIONS = {
    'vani': ['vanni', 'wani', 'vaani', 'vany', 'bani', 'वाणी', 'वानी'],
    'shivani': ['shivanni', 'shibani', 'shivni', 'शिवानी'],  # Common variations
    'hey vani': ['hey vanni', 'hey wani', 'hay vani', 'hey vaani', 'hey bani', 'हे वाणी'],
    'hey shivani': ['hey shivanni', 'hey shibani', 'hay shivani'],
    'hai vani': ['hai vanni', 'hai bani', 'high vani'],
    'hai shivani': ['hai shivanni', 'high shivani'],
    'okay vani': ['ok vani', 'okay vanni', 'ok vanni'],
    'hi vani': ['hi vanni', 'hi wani', 'high vani', 'hi bani'],
    'hi shivani': ['hi shivanni', 'hi shibani'],
    'hello vani': ['hello vanni', 'hello wani', 'hello bani'],
    'hello shivani': ['hello shivanni']
}

# Recognition settings
RECOGNITION_TIMEOUT = 10
PHRASE_TIME_LIMIT = 15
ENERGY_THRESHOLD = int(get_setting('ENERGY_THRESHOLD', 300))  # Base threshold
DYNAMIC_ENERGY_THRESHOLD = True

# Adaptive thresholds for different scenarios
# Note: Good values range from 50 to 4000 according to SpeechRecognition docs
# Lower values = more sensitive = detects farther/quieter voices
# Music is temporarily ducked to 60% during wake word listening for better detection
ENERGY_THRESHOLD_MUSIC = 60    # Absolute minimum (whisper detection during music)
ENERGY_THRESHOLD_TTS = 600     # Medium threshold during TTS
ENERGY_THRESHOLD_QUIET = 50    # Absolute minimum for maximum sensitivity

# Interruption settings
ALLOW_TTS_INTERRUPTION = True  # Allow wake word during TTS
TTS_INTERRUPTION_DELAY = 2.0   # Wait 2s after TTS starts before allowing interrupt
PAUSE_THRESHOLD = 0.8

# =============================================================================
# TEXT-TO-SPEECH SETTINGS
# =============================================================================

# Voice preferences
# Voice preferences
# Voice preferences
# Voice preferences
PREFERRED_VOICES = EXTERNAL_CONFIG.get('PREFERRED_VOICES', ['Samantha', 'Lekha', 'Damayanti', 'Piya', 'Soumya', 'Alex'])

# Language specific voice mapping
LANGUAGE_VOICE_MAP = EXTERNAL_CONFIG.get('LANGUAGE_VOICE_MAP', {
    'hi': 'Lekha',    # Hindi
    'ta': 'Vani',     # Tamil
    'bn': 'Piya',     # Bengali
    'en': 'Lekha'     # Indian English
})
SPEECH_RATE = 160
SPEECH_VOLUME = 1.0

# Microphone preference: 'internal', 'external', 'system' (default: 'internal')
MICROPHONE_TYPE = get_setting('MICROPHONE_TYPE', 'internal')

# =============================================================================
# AUDIO PLAYBACK SETTINGS
# =============================================================================

# Music settings
DEFAULT_VOLUME = float(get_setting('DEFAULT_VOLUME', 1.0))
MUSIC_DUCK_VOLUME = float(get_setting('MUSIC_DUCK_VOLUME', 0.15))
MAX_QUEUE_SIZE = 50
BUFFER_SIZE = 512
DOWNLOAD_AUDIO = True  # Download audio files before playing (more reliable)
AUDIO_SAMPLE_RATE = 16000

# VLC settings
VLC_NETWORK_CACHING = 3000  # milliseconds
VLC_QUIET_MODE = True

# =============================================================================
# AI SETTINGS
# =============================================================================

# Gemini model configuration
AI_MODEL = get_setting('AI_MODEL', "gemini-2.5-flash-lite")
AI_TEMPERATURE = float(get_setting('AI_TEMPERATURE', 0.9))
AI_MAX_TOKENS = int(get_setting('AI_MAX_TOKENS', 1000))

# Google Search grounding for real-time information
USE_GOOGLE_SEARCH_GROUNDING = str(get_setting('USE_GOOGLE_SEARCH_GROUNDING', "True")).lower() in ("true", "1", "yes")

# Response length control
# Options: 'short' (1-2 sentences), 'medium' (2-4 sentences), 'long' (detailed)
RESPONSE_LENGTH = get_setting('RESPONSE_LENGTH', 'medium')

# Conversation context
MAX_CONVERSATION_HISTORY = 30  # Increased for better context
CONTEXT_WINDOW_SIZE = 5

# =============================================================================
# SYSTEM BEHAVIOR
# =============================================================================

# Debug and logging
# Debug and logging
# Check for DEV or DEBUG in environment
# Debug and logging
# Check for DEV or DEBUG in environment or config
DEBUG_MODE = str(get_setting("DEV", get_setting("DEBUG_MODE", "False"))).lower() in ("true", "1", "yes")
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "WARNING"
LOG_MAX_BYTES = 1024 * 1024  # 1MB
LOG_BACKUP_COUNT = 3

# Threading
MAX_WORKER_THREADS = 4
WAKE_WORD_CHECK_INTERVAL = 0.3
MUSIC_MONITOR_INTERVAL = 1.0

# Timeout and retry settings
# Timeout and retry settings
COMMAND_TIMEOUT = int(get_setting('COMMAND_TIMEOUT', 10))  # Listen for 10 seconds after wake word detected
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.0

# =============================================================================
# DATABASE PATHS
# =============================================================================

DB_PATH = str(DATA_DIR / "vaani_database.db")
NOTES_DB_PATH = str(DATA_DIR / "vaani_notes.db")
MEMORY_DB_PATH = str(DATA_DIR / "vaani_context.db")

# =============================================================================
# FEATURE FLAGS
# =============================================================================

FEATURES = {
    'music_streaming': True,
    'spotify_integration': False,
    'smart_home': False,
    'voice_notes': False,
    'weather': True,
    'news': True,
    'translation': False,
    'camera': False,
    'location': False
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        'api_keys': {
            'google': GOOGLE_API_KEY,
            'weather': WEATHER_API_KEY, #Later used for weather feature
        },
        'paths': {
            'base': str(BASE_DIR),
            'data': str(DATA_DIR),
            'logs': str(LOGS_DIR),
            'temp': str(TEMP_DIR)
        },
        'features': FEATURES,
        'debug': DEBUG_MODE
    }

def validate_config() -> bool:
    """Validate required configuration"""
    errors = []
    
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-api-key-here":
        errors.append("Google API key is not configured")
    
    if errors:
        for error in errors:
            print(f"❌ Config Error: {error}")
        return False
    
    return True
