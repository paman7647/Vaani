Project Structure and Code Organization
========================================

A detailed walkthrough of Vaani's codebase and how different components fit together.

Entry Point
-----------

**main.py**

The starting point for Vaani. When you run ``python3 main.py``, this file:

1. Imports the assistant manager
2. Sets up signal handling for clean shutdown
3. Starts the main loop
4. Handles keyboard interrupt gracefully

Very minimal - most of the work is delegated to the assistant manager.

Configuration Package
---------------------

``vaani_assistant/config/``

**global_config.py**

System-wide constants that rarely change:

- Assistant name and wake words
- Voice mappings for all 32 supported languages
- System instructions for the AI engine
- Default values for timeouts and limits

**settings.py**

Runtime configuration loaded from ``.env`` or environment variables:

- Gets environment variables with defaults
- Makes settings available throughout the application
- Ensures configuration is centralized

Usage pattern:

.. code-block:: python

   from vaani_assistant.config import settings
   language = settings.config.get("VOICE_LANGUAGE", "en")

Core Package
------------

``vaani_assistant/core/``

Core orchestration and coordination:

**Assistant Manager** (``assistant_manager.py``)

The orchestrator. Coordinates all other components:

.. code-block:: python

   AssistantManager:
       - Owns speech recognizer instance
       - Owns text-to-speech instance
       - Owns conversation engine instance
       - Owns audio player instance
       - Owns command processor instance
       - Manages the main event loop

Think of it like the conductor of an orchestra - it doesn't play instruments itself, but tells each instrument when to come in.

**Command Processor** (``command_processor.py``)

Routes user commands to appropriate handlers.

Voice Package
-------------

``vaani_assistant/voice/``

Handles all voice input and output:

**Speech Recognition** (``speech_recognition.py``)

Converts audio to text with multilingual support.

**Text-to-Speech** (``text_to_speech.py``)

Converts text to natural speech.

**Voice Synthesis** (``voice_synthesis.py``)

Production-grade TTS with guaranteed delivery and multilingual voices.

**Audio Player** (``audio_player.py``)

Manages music playback and audio streaming.

Intelligence Package
--------------------

``vaani_assistant/intelligence/``

AI understanding and context:

**Conversation Engine** (``conversation_engine.py``)

Generates responses using Google Gemini API:

- Takes user input and conversation context
- Optionally searches the web for current information
- Generates natural, contextual responses
- Falls back gracefully if API is unavailable

**Intent Classifier** (``intent_classifier.py``)

Classifies user intent using fuzzy matching.

**Conversation Memory** (``conversation_memory.py``)

Maintains conversation history and context.

**Personality** (``personality.py``)

Defines assistant personality and response tone.

Integrations Package
--------------------

``vaani_assistant/integrations/``

External service integrations:

**Web Search** (``web_search.py``)

Searches the web for current information.

**Music Manager** (``music_manager.py``)

Manages music playback and queue.

**Audio Player** (``audio_player.py``)

Handles audio output and playback control:

- Plays system responses
- Handles playback commands (pause, resume, stop, skip)
- Manages volume and audio mixing

**Music Manager** (``music_manager.py``)

Discovers and plays music:

- Searches for music by name/artist
- Handles YouTube audio extraction
- Supports local music files
- Works with Audio Player for playback control

**Memory System** (``memory.py``)

Maintains conversation history:

- Stores user inputs and responses
- Provides context for future responses
- Limit to prevent unbounded growth
- Can be cleared or persisted

Key insight: Vaani only keeps recent conversation, not all history. This limits memory usage and keeps responses relevant.

**Command Router** (``command_router.py``)

Routes requests to appropriate handlers:

- Detects intent from user input
- Finds the right handler
- Executes the handler
- Returns results to response generator

**Intent Classifier** (``smart_intent_classifier.py``)

Determines what the user wants:

- Music control: "Play jazz"
- Search: "What is...?"
- Conversation: "How are you?"
- Commands: "Set a reminder"

Uses NLP (Spacy) for analysis.

**Personality System** (``personality.py``)

Customizable response style:

- Defines how Vaani responds to greetings
- Customizable tone and vocabulary
- Can be adapted per user or context

**Web Search** (``web_search.py``)

Real-time information retrieval:

- Searches web without API keys (DuckDuckGo)
- Formats results for natural speech
- Provides source citations

**Wake Word Detection** (``wake_word_detector.py``)

Continuously listening for activation:

- Monitors audio for wake words
- Low-power processing
- Activates full recognition when detected

**System Watchdog** (``watchdog.py``)

Monitors system health:

- Detects and handles errors in components
- Restarts failed components
- Prevents system crashes from single failures

**Responses** (``responses.py``)

Static response templates:

- Common phrases
- Error messages
- Fallback responses when AI is unavailable

Think of it as a phrase book for common scenarios.

Modules Package
---------------

``vaani_assistant/modules/``

Specialized functionality beyond core:

**Command Processor** (``command_processor.py``)

Executes specific commands:

- Detects music control commands
- Detects search requests
- Detects special operations
- Routes to appropriate handler

Extensible - you can add new command types easily.

Utils Package
-------------

``vaani_assistant/utils/``

Shared utilities:

**Logger** (``logger.py``)

Centralized logging:

.. code-block:: python

   from vaani_assistant.utils.logger import logger
   
   logger.info("Starting Vaani")
   logger.debug("Debug info")
   logger.error("Error occurred")

Uses the ``LOG_LEVEL`` environment variable for verbosity.

Data Flow Through the System
-----------------------------

**Complete workflow: "Play jazz music"**

::

   User speaks: "Play jazz music"
        ↓
   [Assistant Manager] starts listening cycle
        ↓
   [Wake Word Detector] hears "Hey Aria"
        ↓
   [Speech Recognition] converts to text: "Play jazz music"
        ↓
   [Intent Classifier] detects: PLAY_MUSIC
        ↓
   [Command Router] routes to Music Handler
        ↓
   [Music Manager] searches for "jazz music"
        ↓
   [Audio Player] starts playback
        ↓
   [TTS Engine] synthesizes: "Now playing jazz"
        ↓
   [Audio Player] plays response
        ↓
   [Memory] stores in conversation history
        ↓
   [Assistant Manager] returns to listening

Each component does exactly one job. The flow is clear and easy to follow.

Initialization Sequence
-----------------------

When Vaani starts:

1. **main.py** imports and creates AssistantManager
2. **AssistantManager.__init__()** creates instances of:
   - Speech Recognizer
   - TTS Engine
   - AI Engine
   - Audio Player
   - Music Manager
   - Memory
   - Command Processor
3. **Settings** loads from ``.env`` and environment
4. **Main loop** starts listening for wake words
5. **Watchdog** monitors all components

Most of this happens automatically in constructors.

Extension Points
----------------

Where you can add new functionality:

**Add a new command type:**

1. Update ``smart_intent_classifier.py`` to recognize the intent
2. Add handler to ``command_processor.py``
3. Hook into command router

**Add a new language:**

1. Add voice mapping to ``global_config.py``
2. Restart Vaani and set the language

**Add a new AI provider:**

1. Implement provider interface in ``ai_engine.py``
2. Switch provider via configuration

**Add a new audio source:**

1. Add source to ``music_manager.py``
2. Implement search and playback

**Add custom responses:**

1. Edit ``personality.py`` for tone
2. Add phrases to ``responses.py``
3. Or override via configuration

Dependency Graph
----------------

At a high level:

::

   main.py
      ↓
   AssistantManager
      ├── Speech Recognition
      ├── AI Engine → Web Search
      ├── Memory
      ├── TTS Engine
      ├── Audio Player
      ├── Music Manager
      ├── Command Processor
      └── Watchdog
   
   Configuration ← (used by all)
   Logger ← (used by all)

Most components are independent; they communicate through AssistantManager or through the message/event system.

Key Design Patterns
-------------------

**Singleton Pattern**

Most modules use a factory function to provide a single instance:

.. code-block:: python

   def get_tts_engine():
       if not _instance:
           _instance = TTSEngine()
       return _instance

**Dependency Injection**

Components receive dependencies in ``__init__``:

.. code-block:: python

   class AssistantManager:
       def __init__(self):
           self.tts = get_tts_engine()
           self.ai = get_ai_engine()

**Strategy Pattern**

Different implementations of same interface:

- Multiple TTS options (advanced, hardened)
- Multiple Speech Recognition options
- Can switch at runtime

**Observer Pattern**

Components notify each other of state changes through callbacks or event system.

Testing Modules
---------------

Each module can be tested independently:

.. code-block:: bash

   # Test speech recognition
   python3 << 'EOF'
   from vaani_assistant.core.speech_recognition import recognize_speech
   text = recognize_speech(timeout=5)
   print(f"You said: {text}")
   EOF
   
   # Test TTS
   python3 << 'EOF'
   from vaani_assistant.core.tts_engine import speak
   speak("Hello world")
   EOF
   
   # Test memory
   python3 << 'EOF'
   from vaani_assistant.core.memory import get_conversation_memory
   memory = get_conversation_memory()
   memory.add("user said hello", "vaani said hi")
   context = memory.get_context()
   print(context)
   EOF

This modular design makes it easy to debug individual components.

Next Steps
----------

- See :doc:`../architecture` for high-level overview
- Check :doc:`../development/coding_style` for conventions
- Read specific module docs under :doc:`../modules/core`
