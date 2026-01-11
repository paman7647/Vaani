Architecture
============

Vaani is built on a modular, event-driven architecture where each component has a clear responsibility. This design makes the system easier to understand, test, and extend.

System Overview
---------------

The interaction flow:

::

   User (Voice/Text)
        ↓
   [Input Processing]
   - Speech Recognition
   - Wake Word Detection
        ↓
   [Intent Understanding]
   - Smart Intent Classifier
   - Command Routing
        ↓
   [Response Generation]
   - AI Engine (with Gemini)
   - Web Search Integration
   - Conversation Memory
        ↓
   [Output Processing]
   - Text-to-Speech
   - Audio Playback
   - Music Control
        ↓
   User (Audio Response)

Each box represents one or more modules working together.

Core Principles
---------------

**Single Responsibility**
   Each module does one thing well. The speech recognizer recognizes speech, nothing more. The AI engine handles language understanding, not audio playback.

**Loose Coupling**
   Components communicate through well-defined interfaces. You can swap the TTS engine without touching the AI logic.

**Configurable**
   System behavior is driven by configuration, not hardcoded values. Languages, voices, API keys all come from config or environment.

**Testable**
   Modules can be tested independently. You can test speech recognition without running the full system.

**Documented**
   Each module has clear docstrings. Future developers should understand what it does without reading dozens of lines of code.

Module Organization
--------------------

Vaani's code is organized into distinct packages:

**vaani_assistant.config**
   System-wide configuration, voice mappings, constants

**vaani_assistant.core**
   Core orchestration: assistant manager, command processor

**vaani_assistant.voice**
   Voice I/O: speech recognition, text-to-speech, audio player

**vaani_assistant.intelligence**
   AI & understanding: conversation engine, intent classifier, memory, personality

**vaani_assistant.integrations**
   External services: web search, music manager

**vaani_assistant.utils**
   Shared utilities: logging, helpers

The Main Loop
-------------

The Assistant Manager coordinates everything:

.. code-block:: python

   AssistantManager:
       ├── Speech Recognizer       (listens for voice)
       ├── Conversation Engine     (generates responses)
       ├── Text-to-Speech          (converts text to speech)
       ├── Audio Player            (plays music and responses)
       ├── Conversation Memory     (maintains conversation history)
       ├── Command Processor       (handles specific tasks)
       └── Watchdog                (monitors system health)

The flow in pseudocode:

::

   while running:
       1. Listen for wake word
       2. Capture user input (voice)
       3. Convert to text
       4. Classify intent
       5. Route to appropriate handler
       6. Generate response
       7. Synthesize speech
       8. Play audio
       9. Store in memory
       10. Loop

All of this happens in real-time with minimal latency.

Key Components
--------------

Speech Recognition
^^^^^^^^^^^^^^^^^^^

Captures and processes audio input. Handles background noise, multiple languages, and can work offline.

**Related modules:**

- ``speech_recognition.py`` - Basic voice input
- ``enhanced_speech_recognition.py`` - Advanced noise handling
- ``wake_word_detector.py`` - Always-listening wake word detection

**Behavior:**

Listens continuously in background. When the wake word is detected ("Hey Aria", "Hi Aria"), captures the following speech for command processing.

Artificial Intelligence Engine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generates natural, contextual responses. Can access web search, remember conversation history, and adapt based on user preferences.

**Related modules:**

- ``ai_engine.py`` - Main AI orchestrator
- ``web_search.py`` - Real-time search integration
- ``memory.py`` - Conversation history and context
- ``smart_intent_classifier.py`` - Determines what user wants
- ``personality.py`` - Customizable response style

**Behavior:**

Takes user input, checks conversation memory, searches web if needed, generates response using Gemini API or fallback logic.

Text-to-Speech
^^^^^^^^^^^^^^^

Converts text responses into natural-sounding audio. Supports multiple languages and voice variants.

**Related modules:**

- ``tts_engine.py`` - Core TTS orchestrator
- ``advanced_tts.py`` - Higher quality synthesis
- ``voice_synthesis.py`` - Production TTS with fallback

**Behavior:**

Receives text, selects appropriate voice based on configuration, generates audio, plays it immediately.

Audio Playback and Music
^^^^^^^^^^^^^^^^^^^^^^^^

Plays audio responses and manages music playback from various sources.

**Related modules:**

- ``audio_player.py`` - Audio output and playback control
- ``music_manager.py`` - Music source discovery and playback

**Behavior:**

Handles playback controls (play, pause, stop, skip), supports local files and YouTube sources, manages volume and audio mixing.

Command Processing
^^^^^^^^^^^^^^^^^^^

Routes specific user requests to specialized handlers. Examples: "Play music", "Set a timer", "Search Wikipedia".

**Related modules:**

- ``command_processor.py`` - Command detection and execution
- ``command_router.py`` - Routing logic

**Behavior:**

Analyzes user intent, finds the right handler, executes the command, returns results to response generator.

Memory and Context
^^^^^^^^^^^^^^^^^^^

Maintains conversation history and context to make responses more natural and relevant.

**Related modules:**

- ``memory.py`` - Conversation storage and retrieval

**Behavior:**

Stores conversation exchanges (user input + Vaani response). When generating new responses, includes relevant previous exchanges for context.

Configuration System
^^^^^^^^^^^^^^^^^^^^

Centralized configuration for languages, voices, API keys, system parameters.

**Related modules:**

- ``global_config.py`` - Constants and voice mappings (32 languages)
- ``settings.py`` - Runtime configuration from environment

**Behavior:**

Loads from ``.env`` file at startup. Provides default values for all parameters. Can be overridden via environment variables.

Data Flow Examples
------------------

Simple Query
^^^^^^^^^^^^

User: "What's the capital of France?"

::

   Wake Word Detected
        ↓
   Capture: "What's the capital of France"
        ↓
   Intent: QUERY
        ↓
   Check Memory (no relevant context)
        ↓
   Web Search: "capital of France"
        ↓
   AI Engine generates: "The capital of France is Paris"
        ↓
   Text-to-Speech synthesizes response
        ↓
   Audio Player plays: "The capital of France is Paris"
        ↓
   Memory stores: [input, response]

Contextual Conversation
^^^^^^^^^^^^^^^^^^^^^^^

User: "Tell me about France"
(Vaani responds with information)

User: "What's the capital?"

::

   Wake Word Detected
        ↓
   Capture: "What's the capital"
        ↓
   Intent: QUERY
        ↓
   Check Memory (finds "France" from previous exchange)
        ↓
   AI Engine with context: "...capital of France is Paris"
        ↓
   (Shorter, more natural response because context is known)

Music Playback
^^^^^^^^^^^^^^

User: "Play some jazz"

::

   Wake Word Detected
        ↓
   Capture: "Play some jazz"
        ↓
   Intent: PLAY_MUSIC
        ↓
   Command Processor routes to Music Manager
        ↓
   Music Manager searches: "jazz music"
        ↓
   Finds YouTube source (or local library)
        ↓
   Audio Player starts playback
        ↓
   Vaani says: "Now playing jazz"

Threading and Async
-------------------

Most components run in separate threads to prevent blocking:

- **Main thread** - User interaction loop
- **Speech recognition thread** - Always listening
- **Audio playback thread** - Handles long audio without blocking
- **Web search thread** - Searches happen without freezing response

This ensures Vaani remains responsive even when doing heavy work like downloading music or processing complex searches.

Error Handling
--------------

Each module is designed to fail gracefully:

- **Speech not recognized?** - Prompts user to repeat
- **Web search fails?** - Falls back to AI-only response
- **TTS fails?** - Uses FallbackSpeech engine (simpler fallback)
- **Network unavailable?** - Operates in offline mode

The system never crashes due to a single component failure.

Extensibility
-------------

Adding new capabilities is straightforward:

1. **New command type** - Add handler to ``command_processor.py``
2. **New language** - Add voice mapping to ``global_config.py``
3. **New AI provider** - Implement provider interface in ``ai_engine.py``
4. **New audio source** - Add source to ``music_manager.py``

Each extension is isolated from others.

Next Steps
----------

- See :doc:`voice_system` for audio details
- Read :doc:`intelligence` for AI engine specifics
- Check :doc:`memory_context` for conversation handling
- Review :doc:`development/project_structure` for code organization
