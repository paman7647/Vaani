Project Structure
=================

This document provides a comprehensive overview of the Vaani Assistant codebase structure, explaining the purpose and contents of each component.

Repository Layout
-----------------

::

   vaani/
   ├── main.py                    # Application entry point
   ├── config.json                # User configuration file
   ├── .env                       # Environment variables (API keys)
   ├── requirements.txt           # Python dependencies
   ├── setup.sh                   # Linux/macOS setup script
   ├── setup.ps1                  # Windows setup script
   ├── README.md                  # Project overview
   ├── LICENSE                    # MIT License
   │
   ├── Vaani/                     # Main package directory
   │   ├── __init__.py
   │   ├── config/                # Configuration management
   │   ├── core/                  # Core assistant logic
   │   ├── voice/                 # Voice I/O (speech & audio)
   │   ├── intelligence/          # AI & NLP components
   │   ├── integrations/          # External service integrations
   │   ├── modules/               # Feature modules
   │   └── utils/                 # Utility functions
   │
   ├── models/                    # Speech recognition models
   │   ├── vosk-model-small-en-in-0.4/
   │   ├── vosk-model-small-en-us-0.15/
   │   └── vosk-model-small-hi-0.22/
   │
   ├── docs/                      # Sphinx documentation
   │   ├── index.rst
   │   ├── conf.py
   │   ├── *.rst                  # Doc pages
   │   └── _build/                # Built documentation
   │
   └── tests/                     # Test suite
       ├── test_*.py
       └── fixtures/

Entry Point
-----------

**main.py**

The application entry point that initializes and runs Vaani:

.. code-block:: python

   """Main entry point for Vaani Assistant.
   
   Workflow:
   1. Load configuration from config.json and .env
   2. Initialize logging system
   3. Verify required dependencies (audio, models)
   4. Create Assistant instance
   5. Start listening loop
   6. Handle graceful shutdown on Ctrl+C
   """

Key responsibilities:

- Parse command-line arguments
- Set up logging
- Load configuration
- Initialize assistant
- Handle shutdown signals

Main Package (Vaani/)
---------------------

**__init__.py**

Package initialization:

.. code-block:: python

   """Vaani Assistant - Multilingual AI Voice Assistant.
   
   Version: 1.0.0
   """
   
   __version__ = "1.0.0"
   __author__ = "Paman7647"

Configuration (config/)
-----------------------

**Directory Structure**

::

   config/
   ├── __init__.py
   ├── global_config.py           # Global settings and constants
   └── settings.py                # Runtime configuration manager

**global_config.py**

Centralizes all application constants:

.. code-block:: python

   """Global configuration constants.
   
   Contains:
   - Language configurations (32 languages)
   - Voice mappings for each language
   - Wake word definitions
   - Default settings
   - Audio parameters
   - API endpoints
   """
   
   # Language Support
   SUPPORTED_LANGUAGES = {
       'en': 'English',
       'hi': 'Hindi',
       'es': 'Spanish',
       # ... 29 more languages
   }
   
   # Voice Configurations
   LANGUAGE_VOICE_MAP = {
       'en': {
           'voices': ['en-US-GuyNeural', 'en-GB-LibbyNeural'],
           'default': 'en-US-GuyNeural'
       },
       # ... voice configs for all languages
   }
   
   # Wake Words
   DEFAULT_WAKE_WORDS = [
       "hey vaani",
       "vaani",
       "ok vaani"
   ]
   
   # Audio Settings
   AUDIO_SAMPLE_RATE = 16000
   AUDIO_CHUNK_SIZE = 1024
   AUDIO_FORMAT = pyaudio.paInt16

**settings.py**

Runtime configuration management:

.. code-block:: python

   """Runtime settings manager.
   
   Responsibilities:
   - Load config.json
   - Read environment variables from .env
   - Provide type-safe config access
   - Validate configuration values
   - Merge defaults with user settings
   """
   
   class Settings:
       def __init__(self):
           self.load_from_file()
           self.load_from_env()
           self.validate()
       
       def get(self, key: str, default=None):
           """Get configuration value with fallback."""
       
       def set(self, key: str, value):
           """Update configuration at runtime."""

Core (core/)
------------

**Directory Structure**

::

   core/
   ├── __init__.py
   ├── assistant.py               # Main Assistant class
   ├── lifecycle.py               # Lifecycle management
   └── processor.py               # Command processing logic

**assistant.py**

Main assistant orchestration:

.. code-block:: python

   """Core Assistant class.
   
   The Assistant class is the central coordinator that:
   1. Manages lifecycle (startup, running, shutdown)
   2. Coordinates voice input/output
   3. Processes user commands
   4. Maintains conversation context
   5. Handles music playback
   
   Architecture:
       Assistant
       ├── SpeechRecognizer (voice input)
       ├── SpeechSynthesizer (voice output)
       ├── IntentAnalyzer (understand intent)
       ├── ResponseSynthesizer (generate response)
       ├── MusicClient (handle music)
       └── ContextManager (maintain memory)
   """
   
   class Assistant:
       def __init__(self, config: Settings):
           self.config = config
           self.initialize_components()
       
       def start(self):
           """Start the assistant listening loop."""
       
       def process_input(self, text: str):
           """Process user input through the pipeline."""
       
       def shutdown(self):
           """Clean shutdown of all components."""

**processor.py**

Command processing pipeline:

.. code-block:: python

   """Command processor.
   
   Pipeline:
   1. Receive user text input
   2. Classify intent (music, question, control, etc.)
   3. Extract entities (song name, artist, etc.)
   4. Route to appropriate handler
   5. Generate response
   6. Return result
   
   Intent Types:
   - music: Play songs, control playback
   - question: Answer questions, web search
   - control: Volume, pause, stop
   - conversation: General chat
   - time: Time and date queries
   """
   
   class CommandProcessor:
       def process(self, text: str, context: Dict) -> ProcessResult:
           intent = self.classify_intent(text)
           entities = self.extract_entities(text, intent)
           response = self.handle_intent(intent, entities, context)
           return response

**lifecycle.py**

Manages component lifecycle:

.. code-block:: python

   """Lifecycle management.
   
   Handles:
   - Component initialization order
   - Dependency injection
   - Resource allocation
   - Graceful shutdown
   - Error recovery
   """
   
   class LifecycleManager:
       def startup(self):
           """Initialize all components in correct order."""
       
       def shutdown(self):
           """Cleanup all resources."""
       
       def restart_component(self, component_name: str):
           """Restart a specific component."""

Voice (voice/)
--------------

**Directory Structure**

::

   voice/
   ├── __init__.py
   ├── speech_recognition.py      # Multi-engine speech-to-text
   ├── speech_synthesis.py        # Text-to-speech
   ├── audio_engine.py            # Low-level audio I/O
   └── wake_word.py               # Wake word detection

**speech_recognition.py**

Multi-engine speech recognition:

.. code-block:: python

   """Speech recognition with fallback engines.
   
   Engines (in priority order):
   1. Google Speech API
      - Highest accuracy (~95%)
      - Requires internet
      - Fast (500-1500ms)
   
   2. Vosk
      - Good accuracy (~85%)
      - Fully offline
      - Very fast (<100ms)
   
   3. Sphinx
      - Basic accuracy (~70%)
      - Offline fallback
      - Slower (200-300ms)
   
   Features:
   - Automatic engine selection
   - Fallback on failure
   - Adjustable timeout
   - Ambient noise adjustment
   - Phrase time limits
   """
   
   class SpeechRecognizer:
       def __init__(self):
           self.engines = ['google', 'vosk', 'sphinx']
       
       def recognize(self, audio_data, language="en-IN"):
           """Try each engine until one succeeds."""
           for engine in self.engines:
               try:
                   return self._recognize_with_engine(engine, audio_data)
               except Exception:
                   continue
           raise RecognitionError("All engines failed")

**speech_synthesis.py**

Text-to-speech generation:

.. code-block:: python

   """Text-to-speech synthesis.
   
   Engines:
   - pyttsx3: Native TTS (offline, fast)
   - Edge TTS: Microsoft Edge voices (online, high quality)
   
   Features:
   - 32 language support
   - Multiple voices per language
   - Gender selection
   - Rate and volume control
   - Audio file caching
   """
   
   class SpeechSynthesizer:
       def synthesize(self, text: str, language: str) -> Path:
           """Generate speech audio file from text."""
       
       def get_available_voices(self, language: str) -> List[str]:
           """List voices for a language."""

**audio_engine.py**

Low-level audio operations:

.. code-block:: python

   """Audio capture and playback engine.
   
   Responsibilities:
   - Microphone input capture
   - Speaker output playback
   - Audio format conversion
   - Volume control
   - Device management
   - Buffer management
   
   Uses:
   - PyAudio for capture
   - VLC/pygame for playback
   - sounddevice for device enumeration
   """
   
   class AudioEngine:
       def capture_audio(self, duration: float) -> AudioData:
           """Capture audio from microphone."""
       
       def play_audio(self, file_path: Path):
           """Play audio file through speakers."""
       
       def set_volume(self, level: float):
           """Set playback volume (0.0 to 1.0)."""
       
       def duck_audio(self, level: float = 0.15):
           """Lower volume temporarily (for music ducking)."""

**wake_word.py**

Wake word detection:

.. code-block:: python

   """Wake word detection using fuzzy matching.
   
   Algorithm:
   1. Continuously listen for speech
   2. Compare heard text to wake words
   3. Use fuzzy matching (RapidFuzz) for tolerance
   4. Trigger if score >= threshold (default 85%)
   
   Features:
   - Multiple wake word support
   - Pronunciation variation tolerance
   - Adjustable sensitivity
   - Context-aware triggering
   """
   
   class WakeWordDetector:
       def is_wake_word(self, text: str) -> bool:
           """Check if text matches any wake word."""
           for word in self.wake_words:
               score = fuzz.ratio(text.lower(), word.lower())
               if score >= self.threshold:
                   return True
           return False

Intelligence (intelligence/)
----------------------------

**Directory Structure**

::

   intelligence/
   ├── __init__.py
   ├── intent_analyzer.py         # Intent classification
   ├── classifier.py              # ML-based classification
   ├── context.py                 # Context management
   ├── conversation.py            # Conversation memory
   ├── offline_nlp.py             # Offline NLP processing
   ├── personality.py             # Personality traits
   ├── response_synthesizer.py   # Response generation
   └── responses.py               # Response templates

**intent_analyzer.py**

Intent classification system:

.. code-block:: python

   """Intent analysis using keyword matching and patterns.
   
   Intent Types:
   - music: play, song, music, artist, album
   - question: what, who, when, where, why, how
   - control: pause, stop, resume, volume, skip
   - time: time, date, clock, when
   - weather: weather, temperature, forecast
   - greeting: hello, hi, good morning
   - farewell: bye, goodbye, see you
   - gratitude: thank you, thanks
   
   Classification Method:
   1. Tokenize input text
   2. Extract keywords
   3. Match against patterns
   4. Calculate confidence scores
   5. Return highest confidence intent
   """
   
   class IntentAnalyzer:
       def analyze(self, text: str) -> Intent:
           """Classify user intent from text."""

**response_synthesizer.py**

AI response generation:

.. code-block:: python

   """Generate contextual responses using AI.
   
   Pipeline:
   1. Receive user input + intent
   2. Retrieve conversation history
   3. Determine if web search needed
   4. Perform search if needed
   5. Construct AI prompt with:
      - System instructions (personality)
      - Conversation history
      - Search results
      - Current query
   6. Call Gemini API
   7. Post-process response
   8. Store in memory
   
   Features:
   - Context-aware responses
   - Web search integration
   - Personality traits
   - Response length control
   - Markdown cleanup
   """
   
   class ResponseSynthesizer:
       def generate(self, query: str, intent: Intent, context: Context) -> str:
           """Generate contextual response."""

**context.py**

Context management:

.. code-block:: python

   """Maintain conversation context and memory.
   
   Tracks:
   - Conversation history (last N exchanges)
   - Current topic/subject
   - User preferences
   - Music playback state
   - Application state
   
   Storage:
   - In-memory during session
   - Optional persistence to file
   - Automatic cleanup of old entries
   """
   
   class ContextManager:
       def add_exchange(self, user_input: str, assistant_response: str):
           """Add conversation turn to memory."""
       
       def get_context(self, limit: int = 10) -> List[Dict]:
           """Retrieve recent context."""
       
       def clear(self):
           """Clear all context."""

**conversation.py**

Conversation management:

.. code-block:: python

   """Manage multi-turn conversations.
   
   Features:
   - Turn tracking
   - Topic continuity
   - Pronoun resolution
   - Context propagation
   - Conversation state
   """
   
   class ConversationManager:
       def __init__(self):
           self.turns = []
           self.current_topic = None
       
       def add_turn(self, role: str, content: str):
           """Add conversation turn."""
       
       def get_relevant_context(self) -> str:
           """Get context relevant to current conversation."""

Integrations (integrations/)
----------------------------

**Directory Structure**

::

   integrations/
   ├── __init__.py
   ├── music_client.py            # YouTube music integration
   ├── web_search.py              # Web search via DuckDuckGo
   └── translator.py              # Language translation

**music_client.py**

YouTube music playback:

.. code-block:: python

   """YouTube music integration.
   
   Features:
   - Search for songs/artists
   - Extract audio stream
   - Playback control (play, pause, stop, skip)
   - Volume control with ducking
   - Queue management
   
   Libraries:
   - yt-dlp: YouTube data extraction
   - VLC: Audio playback
   
   Workflow:
   1. Search YouTube for query
   2. Select best match
   3. Extract audio URL
   4. Stream via VLC
   5. Control playback
   """
   
   class MusicClient:
       def play(self, query: str):
           """Search and play music."""
       
       def pause(self):
           """Pause current track."""
       
       def resume(self):
           """Resume playback."""
       
       def stop(self):
           """Stop playback."""
       
       def set_volume(self, level: float):
           """Set volume level."""

**web_search.py**

Web search integration:

.. code-block:: python

   """Web search via DuckDuckGo.
   
   Features:
   - Privacy-focused (no tracking)
   - No API key required
   - Results with snippets
   - Safe search
   - Result caching
   
   Workflow:
   1. Receive search query
   2. Query DuckDuckGo
   3. Parse results
   4. Extract relevant snippets
   5. Return top N results
   """
   
   class WebSearch:
       def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
           """Perform web search."""

**translator.py**

Language translation:

.. code-block:: python

   """Multi-language translation.
   
   Features:
   - 32 language support
   - Automatic language detection
   - Bidirectional translation
   - Caching for common phrases
   
   Use Cases:
   - Translate user commands
   - Translate responses
   - Multi-language conversations
   """
   
   class Translator:
       def translate(self, text: str, target_lang: str) -> str:
           """Translate text to target language."""

Utilities (utils/)
------------------

**Directory Structure**

::

   utils/
   ├── __init__.py
   ├── logger.py                  # Logging configuration
   └── error_handler.py           # Error handling utilities

**logger.py**

Centralized logging:

.. code-block:: python

   """Logging configuration.
   
   Features:
   - Colored console output
   - File logging with rotation
   - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Component-specific loggers
   - Structured logging support
   
   Configuration:
   - Log file: vaani.log
   - Max size: 10 MB
   - Backup count: 5
   - Format: [timestamp] [level] [component] message
   """
   
   def get_logger(name: str) -> logging.Logger:
       """Get logger for component."""
   
   def configure_logging(level: str = "INFO"):
       """Configure global logging settings."""

**error_handler.py**

Error handling utilities:

.. code-block:: python

   """Error handling and recovery.
   
   Features:
   - Custom exception classes
   - Error recovery strategies
   - Retry logic with backoff
   - User-friendly error messages
   - Error reporting
   """
   
   class ErrorHandler:
       def handle_error(self, error: Exception, context: Dict):
           """Handle error with appropriate recovery strategy."""
       
       def retry_with_backoff(self, func, max_retries: int = 3):
           """Retry function with exponential backoff."""

Models Directory (models/)
--------------------------

Contains Vosk speech recognition models:

::

   models/
   ├── vosk-model-small-en-in-0.4/     # Indian English (50 MB)
   ├── vosk-model-small-en-us-0.15/    # US English (40 MB)
   └── vosk-model-small-hi-0.22/       # Hindi (60 MB)

Each model contains:

- ``am/`` - Acoustic model
- ``conf/`` - Configuration files
- ``graph/`` - Language model graph
- ``ivector/`` - I-vector extractor
- ``README`` - Model information

Documentation (docs/)
---------------------

Sphinx documentation source:

::

   docs/
   ├── conf.py                    # Sphinx configuration
   ├── index.rst                  # Documentation home
   ├── installation.rst           # Installation guide
   ├── getting_started.rst        # Quick start
   ├── usage.rst                  # Detailed usage
   ├── configuration.rst          # Configuration reference
   ├── architecture.rst           # Architecture overview
   ├── performance.rst            # Performance tuning
   ├── troubleshooting.rst        # Common issues
   ├── development/               # Development docs
   │   ├── setup.rst
   │   ├── coding_style.rst
   │   ├── contributing.rst
   │   └── project_structure.rst
   ├── modules/                   # API documentation
   └── _build/                    # Built HTML docs

Tests (tests/)
--------------

Test suite organization:

::

   tests/
   ├── test_speech_recognition.py
   ├── test_intent_analyzer.py
   ├── test_audio_engine.py
   ├── test_music_client.py
   ├── test_context.py
   └── fixtures/
       ├── sample_audio.wav
       ├── test_config.json
       └── test_responses.json

Configuration Files
-------------------

**config.json**

User configuration:

.. code-block:: json

   {
     "language": "en",
     "voice": "en-US-GuyNeural",
     "wake_words": ["hey vaani"],
     "volume": 0.8,
     "music_duck_volume": 0.15,
     "response_length": "normal",
     "web_search_enabled": true
   }

**.env**

Environment variables (not in git):

.. code-block:: bash

   # API Keys
   GEMINI_API_KEY=your_api_key_here
   
   # Optional Settings
   LOG_LEVEL=INFO
   VOSK_MODEL_PATH=./models/vosk-model-small-en-in-0.4

**requirements.txt**

Python dependencies:

.. code-block:: text

   # Core Dependencies
   SpeechRecognition==3.10.0
   vosk==0.3.45
   pyttsx3==2.90
   
   # AI & NLP
   google-generativeai==0.3.1
   rapidfuzz==3.5.2
   
   # Audio
   pyaudio==0.2.13
   python-vlc==3.0.18121
   
   # Integrations
   yt-dlp==2023.12.30
   duckduckgo-search==4.1.0
   
   # Utilities
   python-dotenv==1.0.0

Module Import Paths
-------------------

Standard import patterns:

.. code-block:: python

   # Configuration
   from vaani_assistant.config import global_config, settings
   
   # Core
   from vaani_assistant.core.assistant import Assistant
   from vaani_assistant.core.processor import CommandProcessor
   
   # Voice
   from vaani_assistant.voice.speech_recognition import SpeechRecognizer
   from vaani_assistant.voice.speech_synthesis import SpeechSynthesizer
   from vaani_assistant.voice.audio_engine import AudioEngine
   
   # Intelligence
   from vaani_assistant.intelligence.intent_analyzer import IntentAnalyzer
   from vaani_assistant.intelligence.response_synthesizer import ResponseSynthesizer
   from vaani_assistant.intelligence.context import ContextManager
   
   # Integrations
   from vaani_assistant.integrations.music_client import MusicClient
   from vaani_assistant.integrations.web_search import WebSearch
   
   # Utils
   from vaani_assistant.utils.logger import get_logger
   from vaani_assistant.utils.error_handler import ErrorHandler

Architecture Diagrams
---------------------

See :doc:`../architecture` for detailed component interaction diagrams and data flow explanations.

Contributing
------------

When adding new code, follow the established structure:

1. Place in appropriate directory based on functionality
2. Follow naming conventions
3. Add comprehensive docstrings
4. Include type hints
5. Write tests
6. Update this document if adding new major components

See :doc:`contributing` for detailed contribution guidelines.
