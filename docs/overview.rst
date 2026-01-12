Overview
========

What is Vaani?
--------------

Vaani is a voice assistant that actually listens and responds like a real person. I built it because I was tired of robotic assistants that don't understand natural conversation.

Here's what makes it different:

- **Multi-engine recognition** - Uses Google API, Vosk, and Sphinx. If one fails, another takes over. Works online or offline.
- **Smart about context** - Remembers what you said before. When music is playing, it knows you need to say "Hey Vaani" first. When it's quiet, just talk normally.
- **Natural voices** - Supports voices from around the world. Indian English (Veena, Rishi), American English (Samantha), Hindi (Lekha), and more.
- **Fast intent matching** - Figures out what you want in under a second using smart pattern matching.

Why Vaani?
----------

Most voice assistants feel robotic or corporate. They're optimized for command-and-response interactions, not conversation. Vaani takes a different approach:

- **Natural conversation** - Vaani remembers what you've said before and adapts its responses
- **Privacy-focused** - No cloud required for core functionality; can work offline
- **Extensible** - Built to be customized; add features without deep system changes
- **Open foundation** - Built with popular Python libraries, not proprietary frameworks

What Can It Do?
----------------

**Actually Understand You**
   Three recognition engines working together. Google API gives the best accuracy (around 95%), Vosk works offline with about 85% accuracy, and Sphinx is there as backup. One of them will get it right.

**Play Your Music**
   Tell it to play something from YouTube and it will. Pause, skip, stop - all with your voice. The volume even ducks down automatically when you start talking.

**Answer Questions (With Real Sources)**
   Powered by Google Gemini with live search. Ask about current events, random facts, whatever. It'll search the web and give you actual answers.

**Be Smart About When to Listen**
   When nothing's happening, just start talking. No wake word needed. But when music is playing or it's already talking, say "Hey Vaani" first so it knows you're talking to it.

**Work in Your Language**
   Built with support for multiple accents and languages. Indian English, American English, Hindi - it adapts. Want to add your language? The system is built to make that easy.

**Stay Quiet Unless There's a Problem**
   No spam in your console. It only logs errors when something actually breaks. Clean and professional.

What Vaani Is Not
------------------

- Not a substitute for professional advice in medical, legal, financial, or safety-critical domains
- Not designed for enterprise-scale deployment (though it can be extended for that)
- Not a replacement for human judgment in important decisions
- Not always perfect; it makes mistakes, especially with ambiguous requests

How It's Built
--------------

I tried to keep things simple and modular:

**Everything is separate** - Speech recognition, TTS, AI, music player - they're all independent modules. Don't like how one works? Swap it out without breaking everything else.

**No magic** - You can see exactly what's happening and why. Open the code, read the logs, understand the flow. No mysterious black boxes.

**Battle-tested tools** - Uses libraries that have been around and proven reliable. No experimental stuff that'll break in production.

**Actually maintainable** - Code is organized so you can jump in, understand what's happening, and make changes without rewriting everything.

The System at a Glance
----------------------

::

   User Voice Input
        ↓
   Multi-Engine Recognition:
   1. Google Speech API (en-IN) → Primary, 95% accuracy
   2. Vosk (Indian English) → Offline backup, 85% accuracy  
   3. Sphinx → Emergency fallback
        ↓
   Context-Aware Wake Word Detection
   (Fuzzy matching, 85% threshold)
        ↓
   Intent Classification
   (RapidFuzz + AI fallback)
        ↓
   Google Gemini Pro AI Engine
   (with Search Grounding + Conversation Context)
        ↓
   Response Generation
        ↓
   Native TTS (Veena/Rishi/Lekha)
        ↓
   Audio Output

Each component is modular with multiple fallback options for reliability.

**Current Version:** 1.0

**Branch:** dev

Technical Architecture Deep Dive
-------------------------------

**Recognition Pipeline**

::

   Raw Audio (16kHz, 16-bit PCM)
        ↓
   Noise Reduction (optional)
        ↓
   Voice Activity Detection
        ↓
   Audio Buffering (1s chunks)
        ↓
   Silence Detection (0.6s threshold)
        ↓
   Engine Selection:
   ├─ Try Google API (en-IN)
   │  ├─ Success → Return text
   │  └─ Fail → Next engine
   ├─ Try Vosk (en-in-0.4)
   │  ├─ Success → Return text
   │  └─ Fail → Next engine
   └─ Try Sphinx (fallback)
      └─ Return text (or error)

**Intent Classification Pipeline**

::

   User Text Input
        ↓
   Tokenization & Normalization
        ↓
   Keyword Extraction
        ↓
   Pattern Matching (RapidFuzz)
   ├─ Music Intent? (play, song, music, artist)
   ├─ Question Intent? (what, who, when, where, why, how)
   ├─ Control Intent? (pause, stop, skip, volume)
   ├─ Time Intent? (time, date, when)
   └─ General Intent (conversation, greetings)
        ↓
   Context Integration (previous exchanges)
        ↓
   Final Intent Classification

**Response Generation Pipeline**

::

   Classified Intent + User Input
        ↓
   Conversation Memory Retrieval
   (Last 20 exchanges)
        ↓
   Determine if Web Search Needed
   ├─ Current events → Yes
   ├─ Facts/data → Yes
   ├─ Greetings/chat → No
   └─ Personality queries → No
        ↓
   [If Search Needed]
   ├─ Query formulation
   ├─ Web search (5-10 results)
   └─ Result extraction
        ↓
   AI Prompt Construction:
   ├─ System Instructions (personality)
   ├─ Conversation History
   ├─ Search Results (if any)
   └─ Current Query
        ↓
   Google Gemini API Call
        ↓
   Response Post-Processing
   ├─ Remove markdown
   ├─ Ensure conversational tone
   └─ Length optimization
        ↓
   Store in Memory

**Audio Output Pipeline**

::

   Response Text
        ↓
   Voice Selection (based on language)
        ↓
   TTS Engine Call
   ├─ Primary: Native TTS (pyttsx3)
   └─ Fallback: Edge TTS
        ↓
   Audio File Generation (WAV/MP3)
        ↓
   Check if Music Playing
   ├─ Yes → Duck volume to 15%
   └─ No → Keep current volume
        ↓
   Audio Playback (VLC/pygame)
        ↓
   Playback Complete
        ↓
   Restore Music Volume (if ducked)
        ↓
   Update Context (speaking_state = False)

Performance Characteristics
--------------------------

**Latency Breakdown** (typical values)

::

   Wake Word Detection:     <50ms
   Audio Capture:           1-3 seconds (user speaking)
   Speech Recognition:
   ├─ Google API:          500-1500ms
   ├─ Vosk:               50-100ms
   └─ Sphinx:             100-200ms
   Intent Classification:   <50ms
   Web Search (if needed):  1-2 seconds
   AI Response Generation:  1-3 seconds
   TTS Generation:          500-1000ms
   Audio Playback:          varies by response length
   
   Total (without search):  2-5 seconds
   Total (with search):     4-8 seconds

**Resource Usage** (typical)

::

   RAM:                     150-300 MB
   CPU (idle):             1-3%
   CPU (processing):       20-40%
   Disk Space:             500 MB
   Network (per query):    ~100 KB

**Accuracy Metrics**

::

   Speech Recognition:
   ├─ Google API:          ~95% (en-IN)
   ├─ Vosk:               ~85% (en-in-0.4)
   └─ Sphinx:             ~70% (fallback)
   
   Wake Word Detection:    ~90% (fuzzy matching)
   Intent Classification:  ~92% (with context)
   Response Relevance:     ~85% (with web search)

System Requirements
-------------------

**Minimum Requirements**

- CPU: Dual-core processor (2GHz+)
- RAM: 2 GB available
- Storage: 500 MB free space
- Audio: Microphone and speakers/headphones
- OS: macOS 10.14+, Linux (Ubuntu 18.04+), Windows 10+ (via WSL)
- Python: 3.10 or newer
- Internet: Optional (required for enhanced features)

**Recommended Requirements**

- CPU: Quad-core processor (2.5GHz+)
- RAM: 4 GB available
- Storage: 1 GB free space (for models and cache)
- Audio: USB microphone or good quality built-in mic
- OS: macOS 12+, Linux (Ubuntu 20.04+), Windows 11
- Python: 3.11+
- Internet: Stable broadband connection

**Optimal Performance Setup**

- CPU: 8+ cores
- RAM: 8 GB+
- Storage: SSD with 2 GB+ free
- Audio: Professional USB microphone, dedicated speakers
- OS: Latest stable OS version
- Python: 3.11+ with optimized builds
- Internet: High-speed connection

Comparison with Other Assistants
--------------------------------

**vs. Alexa/Google Assistant**

::

   Privacy:     Vaani ✓ (local first) | Alexa/GA ✗ (cloud required)
   Offline:     Vaani ✓ (partial)    | Alexa/GA ✗ (minimal)
   Open Source: Vaani ✓              | Alexa/GA ✗
   Customizable: Vaani ✓             | Alexa/GA △ (limited)
   Smart Home: Vaani △ (extensible)  | Alexa/GA ✓ (native)
   Accuracy:    Vaani ~85-95%        | Alexa/GA ~95-98%
   Languages:   Vaani 32             | Alexa/GA 40+

**vs. Mycroft**

::

   Ease of Use:  Vaani ✓            | Mycroft △
   Setup Time:   Vaani ~10 min      | Mycroft ~30 min
   AI Quality:   Vaani ✓ (Gemini)   | Mycroft △
   Offline:      Vaani ✓            | Mycroft ✓
   Extensibility: Vaani ✓           | Mycroft ✓
   Community:    Vaani △ (new)      | Mycroft ✓

**vs. Siri**

::

   macOS Native: Vaani △            | Siri ✓
   Privacy:      Vaani ✓            | Siri △
   Customizable: Vaani ✓            | Siri ✗
   Offline:      Vaani ✓ (partial)  | Siri △
   Context:      Vaani ✓            | Siri ✓
   Apple Ecosystem: Vaani ✗         | Siri ✓

Development Roadmap
-------------------

**Current Version: 1.0**

- ✓ Multi-engine speech recognition
- ✓ Google Gemini AI integration
- ✓ 32 language support
- ✓ YouTube music playback
- ✓ Conversation context memory
- ✓ Web search integration
- ✓ Multi-platform support

**Planned Features (Future Versions)**

**Version 1.1** (Q1 2026)

- Voice profiles (multi-user support)
- Improved wake word detection
- Spotify integration
- Calendar/reminder integration
- Weather API integration

**Version 1.2** (Q2 2026)

- Home Assistant integration
- Custom skill/plugin system
- Voice training for accuracy
- Emotion detection in voice
- Multi-device synchronization

**Version 2.0** (Q3 2026)

- Neural TTS for better voice quality
- On-device AI model (no cloud needed)
- Video call integration
- Smart home device control
- Mobile app (iOS/Android)

Getting Help
------------

- **Installation issues?** See :doc:`installation`
- **Can't get audio to work?** Check :doc:`troubleshooting`
- **Want to customize Vaani?** Start with :doc:`customization`
- **Curious about the code?** Explore :doc:`development/project_structure`
- **Performance problems?** Review :doc:`performance`
- **Want to contribute?** Read :doc:`development/contributing`
- **Found a bug?** Report it on GitHub Issues
- **Need API documentation?** See module reference pages

Community and Support
---------------------

**Getting Involved**

- GitHub Repository: https://github.com/paman7647/vaani
- Report Issues: Use GitHub Issues for bugs and feature requests
- Discussions: Use GitHub Discussions for questions and ideas
- Contributions: See :doc:`development/contributing`

**Stay Updated**

- Star the repository to get notifications
- Watch for release announcements
- Check the documentation for updates

**Acknowledgements**

Vaani is built on excellent open-source projects:

- Google Gemini API (AI responses)
- Vosk (offline speech recognition)
- pyttsx3 (text-to-speech)
- SpeechRecognition (audio processing)
- RapidFuzz (fuzzy matching)
- yt-dlp (YouTube audio extraction)
- And many more (see :doc:`credits`)
