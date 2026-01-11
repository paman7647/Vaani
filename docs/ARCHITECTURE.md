# Vaani Architecture

## What's This About

This document explains how Vaani is built and why I made certain choices. If you're trying to understand the code or add features, start here.

Vaani uses a **modular, event-driven setup** where each piece (speech recognition, TTS, music, AI) can work independently. If something breaks, it doesn't take down the whole system.

**Main Design Choices:**
- Multiple recognition engines (cloud + offline) so it always works
- Context awareness (knows when you need wake word vs when you don't)  
- Minimal logging (only errors - no console spam)
- Global language support (not locked to one region)
- Graceful fallbacks (if primary fails, backup takes over)

Version: 1.0  
Branch: dev

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                 (Voice Input/Output - Indian)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Assistant Manager                          │
│         (Core Orchestrator & Context-Aware Lifecycle)        │
└─┬────────────┬────────────┬────────────┬───────────────────┘
  │            │            │            │
  │            │            │            │
┌─▼──────────┐ ┌──▼────────┐ ┌──▼──────┐ ┌──▼──────┐
│  Speech    │ │    TTS    │ │  Audio  │ │   AI    │
│Recognition │ │ (Indian)  │ │ Player  │ │ Engine  │
│  V2 Multi  │ │  Veena    │ │         │ │ Gemini  │
└────────────┘ └───────────┘ └─────────┘ └─────────┘
     │                                         │
     │ Google API (en-IN) → Vosk → Sphinx     │
     │                                         │
┌────▼────────────────────────────────────────▼──────┐
│           Command Processor                         │
│    (Intent Classification & Business Logic)         │
└─────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Assistant Manager (`core/assistant.py`)

**Role:** Main orchestrator and context-aware lifecycle manager

**Responsibilities:**
- Initialize all components with minimal logging
- Manage background threads (voice listener, music monitor)
- Coordinate component interactions
- Context-aware listening (wake word state management)
- Handle shutdown and cleanup

**Key Features:**
- Professional startup (no verbose logs)
- Thread lifecycle control with error recovery
- Context-aware wake word requirement
- Graceful error handling
- Status monitoring

**Thread Management:**
- Main thread: Keeps process alive
- Voice listener thread: Continuous listening with context awareness
- Music monitor thread: Playback state management
- TTS worker thread: Speech queue processing (non-blocking)

**Context-Aware Listening:**
```python
Idle State:
  - No wake word required
  - Direct command processing
  - Fast response time

Music/TTS Active State:
  - Wake word required ("Hey Vaani")
  - Prevents false triggers
  - Maintains user experience
```

---

### 2. Speech Recognition (`voice/speech_recognition.py`)

**Role:** Multi-engine speech recognition optimized for Indian accents

**Responsibilities:**
- Detect wake words with fuzzy matching
- Recognize user commands via multiple engines
- Provide confidence scores
- Handle inline commands
- Graceful fallback between engines

**Recognition Strategy:**
1. **Google Speech API (Primary)**: Cloud-based, en-IN optimized, ~95% accuracy
2. **Vosk (Offline Backup)**: Indian English model (en-in-0.4), ~85% accuracy, <100ms
3. **Sphinx (Emergency Fallback)**: Basic recognition when others fail

**Key Features:**
- **Hybrid Recognition:** Cloud accuracy + offline availability
- **Indian-Optimized:** en-IN language code, Indian English Vosk model
- **Fast:** Optimized timing parameters (0.8s pause, 0.3s phrase, 0.6s non-speaking)
- **Calibrated:** Balanced energy threshold (300) for diverse voice types
- **Fuzzy Matching:** 85% threshold for wake word variations

**Recognition Flow:**
```
Audio Input → Microphone Capture → 
Try Google API (en-IN) → Success? Return text
↓ Fail/Offline
Try Vosk (Indian English) → Success? Return text
↓ Fail
Try Sphinx → Return text or error
```

**Wake Word Detection:**
1. Continuous listening in background thread
2. Fuzzy match against wake words (RapidFuzz, 85% threshold)
3. Extract any inline command after wake word
4. Return (wake_detected: bool, inline_command: str)

**Timing Configuration:**
```python
Energy threshold: 300        # Balanced for Indian accents
Pause threshold: 0.8s       # Prevents early cutoff
Phrase threshold: 0.3s      # Quick capture start
Non-speaking: 0.6s          # Balanced end detection
Wake timeout: 8s            # Wake word window
Command timeout: 10s        # Max command length
```

---

### 3. Text-to-Speech (`voice/speech_synthesis.py`)

**Role:** Native TTS with Indian voice priority

**Responsibilities:**
- Convert text to speech using macOS native voices
- Prioritize Indian voices (Veena, Rishi)
- Manage speech queue (non-blocking)
- Handle voice selection and fallback

**Key Features:**
- **Thread-safe:** Uses locks for state management
- **Non-blocking:** Queue-based speech processing
- **Indian Voices:** Veena (primary), Rishi, Lekha, Samantha (fallback)
- **Fallback:** Automatic voice selection if preferred unavailable

**Voice Priority (for Indian users):**
1. **Veena** - Indian English Female (Primary)
2. **Rishi** - Indian English Male
3. **Samantha** - US English Female
4. **Lekha** - Hindi Female

**Architecture Pattern:** Producer-Consumer
- Producer: `speak()` function adds to queue
- Consumer: Background worker thread processes queue
- Benefits: Non-blocking, ordered, thread-safe

**State Management:**
```python
self.is_speaking: bool          # Current speaking status
self.speech_lock: threading.Lock # Prevents concurrent access
self.speech_queue: queue.Queue   # FIFO speech tasks
```

---

### 4. Audio Player (`voice/audio_engine.py`)

**Role:** Music streaming with automatic volume ducking

**Responsibilities:**
- Stream music from YouTube
- Manage playback (play/pause/stop)
- Handle playback queue
- Control volume and ducking

**Key Features:**
- **Multi-backend:** VLC (primary), pygame (fallback)
- **Thread-safe:** Locked player state
- **Queue management:** FIFO song queue
- **Auto-ducking:** Lower volume during voice interaction
- **Robust:** Error handling and recovery

**Playback Backends:**

**VLC (Primary):**
- Better streaming performance
- Lower latency for online content
- More reliable for YouTube streaming
- Richer state information

**Pygame (Fallback):**
- Simpler implementation
- Works when VLC unavailable
- Local file playback

**State Management:**
```python
self.is_playing: bool           # Playback status
self.is_paused: bool            # Pause status
self.player_lock: threading.Lock # Thread safety
self.queue: deque               # Song queue
```

---

### 5. AI Engine (`intelligence/conversation.py`)

**Role:** Natural language understanding and response generation

**Responsibilities:**
- Generate contextual responses via Google Gemini
- Maintain conversation history
- Personalize interactions
- Provide fallback responses
- Ground responses with real-time search

**Key Features:**
- **Context-aware:** Uses conversation window
- **Memory:** Maintains history (configurable limit)
- **Personalized:** Remembers user name and preferences
- **Grounded:** Google Search integration for current information
- **Fallback:** Rule-based responses when AI unavailable

**Conversation Context:**
```python
conversation_history: deque  # Full conversation (max 20)
context_window: deque        # Recent context (max 5)
```

**Response Generation Flow:**
```
User Input → Build Prompt (Personality + Context + Query) →
Gemini API (with Search Grounding) → Extract Response → 
Update History → Return Text
```

**Personality:**
- Professional yet conversational
- Concise and clear
- Culturally aware (Indian context)
- Helpful and proactive

---

### 6. Command Processor (`core/processor.py`)

**Role:** Command routing and execution

**Responsibilities:**
- Classify command type via intent analyzer
- Route to appropriate handler
- Execute business logic
- Coordinate component actions
- Minimal logging (errors only)

**Key Features:**
- **Intelligent routing:** RapidFuzz + AI-based classification
- **Fast matching:** Sub-second intent detection
- **Extensible:** Easy to add new handlers
- **Safe:** Validates commands before execution
- **Responsive:** Provides immediate feedback
- **Silent processing:** No verbose logs

**Command Classification:**
```python
Command Types:
- music: Play, pause, stop, volume, skip
- control: Device control, system commands
- time: Time, date, calendar queries
- information: Questions needing AI (web search)
- conversation: General chat, context-aware
- translation: Language translation requests
```

**Intent Analyzer (`intelligence/intent_analyzer.py`):**
- Uses RapidFuzz for fast keyword matching
- Falls back to AI classification for complex queries
- Returns intent type + confidence score + extracted entities
- Professional logging (no verbose intent/entity logs)

**Handler Registration:**
```python
handlers = {
    'music': _handle_music_command,
    'control': _handle_control_command,
    'time': _handle_time_command,
    'information': _handle_information_query,
    'conversation': _handle_conversation,
    'translation': _handle_translation
}
```

---

## Data Flow

### Wake Word to Response Flow (Context-Aware)

**Idle State (No Music/TTS):**
```
1. User speaks → "Tell me about Indian festivals"
   ↓
2. Speech Recognition V2 captures (Google API en-IN)
   ↓
3. NO wake word needed (idle state)
   ↓
4. Command Processor → Intent Analyzer → 'information'
   ↓
5. AI Engine queries Gemini with search grounding
   ↓
6. TTS speaks response (Veena voice)
```

**Music Playing State:**
```
1. User speaks → "Hey Vaani, pause music"
   ↓
2. Wake word detector matches "Hey Vaani" (fuzzy 85%)
   ↓
3. Command extracted: "pause music"
   ↓
4. Command Processor → Intent Analyzer → 'music'
   ↓
5. Music handler pauses playback
   ↓
6. TTS confirms: "Paused" (Veena voice)
```

### Multi-Engine Recognition Flow

```
1. Audio Input captured
   ↓
2. Try Google Speech API (en-IN)
   ├─ Success → Return text (95% accuracy)
   └─ Fail/Offline
       ↓
       3. Try Vosk (Indian English model)
       ├─ Success → Return text (85% accuracy)
       └─ Fail
           ↓
           4. Try Sphinx (emergency)
           └─ Return text or error
```

### AI Conversation Flow (Grounded Search)

```
1. User speaks → "Who is the current Prime Minister of India?"
   ↓
2. Wake word detected (if needed) + command captured
   ↓
3. Command Processor classifies as 'information'
   ↓
4. AI Engine builds prompt with context + personality
   ↓
5. Gemini API with Google Search grounding
   ↓
6. Real-time search results integrated
   ↓
7. Response added to conversation history
   ↓
8. TTS speaks response (Veena voice)
```

---

## Thread Architecture

### Thread Hierarchy

```
Main Thread (Process Control)
├── Voice Listener (Daemon)
│   └── Context-aware listening
│   └── Wake word detection when needed
│   └── Triggers command processing
├── Music Monitor (Daemon)
│   └── Monitors playback status
│   └── Handles queue advancement
│   └── Updates context state
└── TTS Worker (Daemon)
    └── Processes speech queue
    └── Non-blocking synthesis
    └── Updates speaking state
```

### Thread Synchronization

**Locks:**
```python
TTS_LOCK: threading.Lock          # TTS state
LISTENING_LOCK: threading.Lock    # Speech recognition state
PLAYER_LOCK: threading.Lock       # Audio player state
CONTEXT_LOCK: threading.Lock      # Context state (wake word requirement)
```

**Atomic Operations:**
- Get/set listening state
- Check TTS speaking status
- Update player state
- Add/remove from queues
- Update context state (wake word required flag)

---

## Thread Safety

### Race Condition Prevention

**Problem:** Multiple threads accessing shared state
**Solution:** Thread locks and atomic operations

**Example:**
```python
# BAD: Race condition
if not self.is_speaking:
    self.is_speaking = True  # Another thread could interleave here
    self.speak_text()

# GOOD: Thread-safe
with self.speech_lock:
    if not self.is_speaking:
        self.is_speaking = True
        self.speak_text()
```

### Deadlock Prevention

**Strategy:**
- Acquire locks in consistent order
- Use timeout on lock acquisition
- Release locks in finally blocks
- Minimize lock hold time
- Professional error logging only

---

## Dependency Management

### Core Dependencies

```
google-generativeai ─► AI responses (Gemini Pro)
SpeechRecognition ───► Voice input framework
vosk ────────────────► Offline speech recognition (Indian English)
rapidfuzz ───────────► Fast intent matching
pygame ──────────────► Audio playback (fallback)
python-vlc ──────────► Audio playback (primary)
yt-dlp ──────────────► YouTube streaming
```

### Speech Recognition Stack

```
Google Speech API ───► Primary (cloud, en-IN)
Vosk (en-in-0.4) ────► Offline backup (Indian English)
PocketSphinx ────────► Emergency fallback
```

### Optional Dependencies

```
sounddevice ─────► Enhanced audio processing
librosa ─────────► Audio analysis
numpy ───────────► Array operations
```

---

## Design Patterns

### 1. Singleton Pattern
- **Used in:** All core components
- **Why:** Single global instance per component
- **Implementation:** Module-level component instances

### 2. Producer-Consumer Pattern
- **Used in:** TTS Engine, Speech Queue
- **Why:** Non-blocking speech synthesis
- **Implementation:** Queue + worker thread

### 3. Observer Pattern
- **Used in:** Music Monitor, Context Manager
- **Why:** React to playback/state events
- **Implementation:** Polling + state checking

### 4. Strategy Pattern
- **Used in:** Speech Recognition (multi-engine), Audio Player
- **Why:** Multiple recognition/playback backends
- **Implementation:** Google API → Vosk → Sphinx fallback chain

### 5. Command Pattern
- **Used in:** Command Processor
- **Why:** Encapsulate command execution
- **Implementation:** Handler registration + routing

---

## Indian Language Optimization

### Speech Recognition

**Indian English Model:**
- Vosk model: `vosk-model-small-en-in-0.4` (36MB)
- Trained on Indian accents
- Recognizes Indian English pronunciation patterns
- Handles code-mixing (English + Hindi)

**Google Speech API:**
- Language code: `en-IN` (Indian English)
- Server-side accent optimization
- Real-time processing
- Best accuracy for diverse Indian accents

**Timing Optimization:**
```python
ENERGY_THRESHOLD: 300        # Balanced for diverse voice types
PAUSE_THRESHOLD: 0.8         # Indian speech patterns (pauses)
PHRASE_THRESHOLD: 0.3        # Quick capture for conversational style
NON_SPEAKING_DURATION: 0.6   # Natural speech rhythm
```

### Voice Synthesis

**Indian Voice Priority:**
1. **Veena** (Indian English Female) - Clear, natural
2. **Rishi** (Indian English Male) - Professional tone
3. **Lekha** (Hindi Female) - For Hindi responses
4. **Samantha** (US English) - Fallback

**Configuration:**
```json
{
  "PREFERRED_VOICES": ["Veena", "Rishi", "Samantha", "Lekha"],
  "LANGUAGE_VOICE_MAP": {
    "hi": "Veena",
    "en": "Veena",
    "ta": "Veena",
    "te": "Veena"
  }
}
```

---

## Logging Philosophy

### Professional Logging (Production-Ready)

**Principles:**
1. **Minimal logging** - Only errors and critical warnings
2. **No emoji characters** - Professional output
3. **No verbose info/debug** - Clean console
4. **Error-focused** - Track failures for debugging
5. **Performance-aware** - No logging overhead

**Log Levels:**
```python
ERROR: Critical failures only
WARNING: Important state changes only
INFO: Disabled by default
DEBUG: Disabled in production
```

**Examples:**
```python
# BAD: Verbose, emoji-filled logs
logger.info("🎤 Listening for wake word...")
logger.info("✨ Processing: {command}")
logger.info("🗣️ Speaking: {text}")

# GOOD: Minimal, professional logs
# (No logs during normal operation)
logger.error(f"Failed to recognize speech: {error}")
logger.warning("Vosk model not found, using Sphinx fallback")
```

---

## Error Handling Strategy

### Defensive Programming

**Principles:**
1. Validate all inputs
2. Handle all exceptions silently (log errors only)
3. Provide fallbacks (multi-engine recognition)
4. Log comprehensively (errors only)
5. Fail gracefully (user-friendly messages)

**Example:**
```python
def recognize_speech(audio_data: AudioData) -> Optional[str]:
    try:
        # Primary: Google Speech API (en-IN)
        text = recognizer.recognize_google(audio_data, language="en-IN")
        return text
    except Exception:
        # Fallback: Vosk (Indian English)
        try:
            text = recognizer.recognize_vosk(audio_data)
            return text
        except Exception:
            # Final fallback: Sphinx
            try:
                return recognizer.recognize_sphinx(audio_data)
            except Exception as e:
                logger.error(f"All recognition engines failed: {e}")
                return None
```

---

## Performance Considerations

### Response Time Optimization

**Target Response Times:**
- Wake word detection: <500ms
- Google API recognition: 1-2 seconds
- Vosk recognition: <100ms
- AI response: 2-4 seconds
- Music playback: 3-6 seconds

**Optimization Strategies:**
1. **Multi-engine fallback** - Fast offline backup
2. **Non-blocking operations** - TTS, audio in separate threads
3. **Fast intent matching** - RapidFuzz (sub-second)
4. **Minimal logging** - No performance overhead
5. **Efficient API calls** - Optimized prompts
6. **Balanced timing** - Prevents early cutoff vs speed

### Resource Management

**Memory:**
- Limited conversation history (20 items)
- Bounded queues (50 items)
- Log rotation (1MB per file, 3 backups)
- Vosk models loaded once (cached)

**CPU:**
- Optimized timing (no busy loops)
- Daemon threads (don't block exit)
- Efficient string operations (RapidFuzz)
- Minimal logging overhead

---

## Configuration Management

### Centralized Settings

All configuration in `config.json` and `vaani/config/settings.py`:

**Benefits:**
- Single source of truth
- Easy to modify
- Environment-aware (.env for API keys)
- Type-safe defaults

**Categories:**
- API keys (.env)
- Speech recognition settings (timing, thresholds)
- Voice preferences (Indian voices)
- Audio playback options (volume, ducking)
- AI model configuration (Gemini Pro)
- System behavior (context-aware listening)
- Logging configuration (minimal, professional)

---

## Extensibility

### Adding New Features

**1. New Command Type:**
```python
# In intelligence/intent_analyzer.py
INTENT_PATTERNS['new_type'] = ['keyword1', 'keyword2', ...]

# In core/processor.py
def _handle_new_command(self, command, command_lower):
    # Implementation
    pass

# Register
self.handlers['new_type'] = self._handle_new_command
```

**2. New Speech Recognition Engine:**
```python
# In voice/speech_recognition.py
def recognize_new_engine(self, audio_data):
    # Implementation
    return text

# Add to fallback chain
try:
    return self.recognize_google(audio_data, language="en-IN")
except:
    try:
        return self.recognize_vosk(audio_data)
    except:
        try:
            return self.recognize_new_engine(audio_data)
        except:
            return self.recognize_sphinx(audio_data)
```

**3. New Voice (TTS):**
```python
# In config.json
{
  "PREFERRED_VOICES": ["NewVoice", "Veena", "Rishi", ...],
  "LANGUAGE_VOICE_MAP": {
    "new_lang": "NewVoice"
  }
}
```

---

## Security Considerations

### API Key Management

- **Never commit** API keys to version control
- Store in `.env` file (gitignored)
- Use environment variables in production
- Rotate keys periodically

### Input Validation

- Sanitize all user inputs
- Validate command parameters
- Prevent command injection
- Rate limit API calls

### Privacy

- No audio recording stored permanently
- Conversation history kept in memory only
- Optional logging can be disabled
- Vosk models run entirely offline

---

## Deployment

### Production Checklist

- [ ] API keys configured in `.env`
- [ ] Vosk models downloaded (`./install_indian_models.sh`)
- [ ] System dependencies installed (`./install_vaani.sh`)
- [ ] Virtual environment activated
- [ ] Logging level set to ERROR
- [ ] Microphone permissions granted
- [ ] Internet connection verified
- [ ] Voice synthesis tested (`say -v Veena "Test"`)

### System Requirements

**Minimum:**
- Python 3.10+
- 2GB RAM
- 500MB disk (plus 100MB for models)
- Microphone input
- Internet connection

**Recommended:**
- Python 3.11+
- 4GB RAM
- 1GB disk
- Quality USB microphone
- 10+ Mbps internet

---

## Future Enhancements

### Planned Features

1. **Multi-language Input**: Support Hindi, Tamil, Telugu voice input
2. **Offline Mode**: Fully offline operation with local LLM
3. **Custom Wake Words**: User-defined wake phrases
4. **Smart Home Integration**: Control IoT devices
5. **Calendar Integration**: Schedule management
6. **Reminders**: Voice-activated reminders
7. **News Briefings**: Daily news summaries
8. **Weather Integration**: Local weather updates

### Performance Improvements

1. **Faster Recognition**: <100ms wake word detection
2. **Streaming AI**: Real-time response generation
3. **Voice Cloning**: Personalized TTS voices
4. **Background Noise Filtering**: Better recognition in noisy environments

---

## Troubleshooting

### Common Issues

**Issue: Recognition not working**
- Check microphone permissions
- Verify internet connection (Google API)
- Test Vosk model extraction
- Check energy threshold (adjust in config.json)

**Issue: Voice synthesis not working**
- Verify voice availability (`say -v ?`)
- Check audio output settings
- Test with fallback voices

**Issue: Music playback fails**
- Verify VLC installation
- Check internet connection
- Test with YouTube URL directly

**Issue: Slow response times**
- Check internet speed (Google API)
- Reduce conversation history limit
- Lower energy threshold
- Use Vosk-only mode (offline)

---

## References

### Documentation

- [Google Gemini API](https://ai.google.dev/)
- [Vosk Speech Recognition](https://alphacephei.com/vosk/)
- [SpeechRecognition Library](https://github.com/Uberi/speech_recognition)
- [RapidFuzz Documentation](https://rapidfuzz.github.io/RapidFuzz/)

### Models

- [Vosk Indian English Model](https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip)
- [Vosk Hindi Model](https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip)

---

**Last Updated:** January 2025  
**Version:** 2.0 (Indian-Optimized, Multi-Engine Recognition)  
**Built with professional engineering practices for production deployment**
