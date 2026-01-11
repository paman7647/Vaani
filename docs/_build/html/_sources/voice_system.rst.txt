Voice and Audio System
======================

How Vaani captures, generates, and plays voice with multi-engine reliability.

Overview
--------

Vaani's audio system has three main components:

1. **Multi-Engine Speech Recognition** - Converting your voice to text using multiple engines
2. **Native Text-to-Speech** - Converting responses to audio using Indian voices
3. **Audio Playback** - Playing music and voice through your speakers

Each component uses a fallback architecture for maximum reliability.

**Recognition Architecture (V2):**

- **Primary:** Google Speech API (en-IN) - Cloud-based, 95% accuracy for Indian accents
- **Backup:** Vosk (Indian English model) - Offline, 85% accuracy, <100ms processing
- **Fallback:** Sphinx - Emergency recognition when others fail

**Version:** 2.0 (the multi-engine rewrite)

**Branch:** dev (where active development happens)

Speech Recognition (Multi-Engine V2)
-------------------------------------

**How Multi-Engine Recognition Works**

1. **Audio Capture**
   - Records audio from your microphone
   - Captures 16-bit PCM audio at 16kHz sample rate
   - Balanced energy threshold: 300 (optimized for Indian accents)
   - Optimized timing:
     - Pause threshold: 0.8s (prevents early cutoff)
     - Phrase threshold: 0.3s (quick capture start)
     - Non-speaking duration: 0.6s (balanced end detection)

2. **Processing**
   - No ambient calibration (removed for speed)
   - Wake word detection with fuzzy matching (85% threshold)
   - Context-aware wake word requirement (idle vs active)

3. **Multi-Engine Recognition Chain**
   - **Step 1:** Try Google Speech API (language: en-IN)
     - Best accuracy (~95% for Indian English)
     - Requires internet connection
     - Typical latency: 1-2 seconds
   - **Step 2:** If Google fails, try Vosk (Indian English model: en-in-0.4)
     - Good accuracy (~85%)
     - Fully offline
     - Ultra-fast: <100ms processing
   - **Step 3:** If Vosk fails, try Sphinx
     - Basic accuracy
     - Emergency fallback
     - Always available

4. **Wake Word Detection**
   - Fuzzy matching using RapidFuzz (85% threshold)
   - Handles accent variations
   - Context-aware requirement:
     - Idle: No wake word needed
     - Music/TTS: "Hey Vaani" required

**Microphone Requirements**

- Standard USB or built-in laptop microphone
- The system checks your config for ``MICROPHONE_TYPE``:
    - ``internal``: Prioritizes "MacBook", "Built-in" microphones.
    - ``external``: Prioritizes "USB", "Bluetooth", "AirPods".
- If your preferred type isn't found, it falls back to the best available option.

**Testing Your Microphone**

.. code-block:: bash

   # Quick test
   python3 test_audio_direct.py
   
   # Detailed test
   python3 << 'EOF'
   from vaani_assistant.voice.speech_recognition import recognize_speech
   print("Speak something (5 seconds)...")
   text = recognize_speech(timeout=5)
   print(f"You said: {text}")
   EOF

**Microphone Setup by OS**

**macOS**

.. code-block:: bash

   # Check microphone
   system_profiler SPAudioDataType | grep "Microphone"
   
   # In System Preferences → Sound → Input:
   # Select your microphone
   # Ensure input volume is above 50%

**Linux**

.. code-block:: bash

   # Check microphone
   arecord -l
   
   # Test recording
   arecord -D hw:0,0 -d 5 test.wav
   aplay test.wav

**Windows (WSL)**

Audio capture in WSL has limitations. For best experience:

1. Configure WSL to use Windows audio
2. Set microphone as default in Windows Sound settings
3. Grant WSL microphone permission

See :doc:`../troubleshooting` for WSL audio issues.

**Microphone Settings in Vaani**

.. code-block:: bash

   # View current settings
   python3 << 'EOF'
   from vaani_assistant.config import settings
   config = settings.config
   print(f"Sample rate: {config.get('SPEECH_RECOGNITION_SAMPLE_RATE', 16000)}")
   print(f"Language: {config.get('VOICE_LANGUAGE', 'en')}")
   EOF

Text-to-Speech (Native Indian Voices)
--------------------------------------

**How TTS Works**

1. **Text Input**
   - Receives response text to speak
   - Non-blocking queue-based processing
   - Thread-safe state management

2. **Voice Selection**
   - Prioritizes Indian voices:
     - **Veena** (Indian English Female) - Primary
     - **Rishi** (Indian English Male)
     - **Lekha** (Hindi Female)
     - **Samantha** (US English) - Fallback
   - Automatic selection based on language
   - Graceful fallback if preferred voice unavailable

3. **Audio Generation**
   - Uses macOS native TTS (nsss engine)
   - Natural pronunciation for Indian English
   - Handles Hindi and other Indian languages
   - Queue-based processing (producer-consumer pattern)

4. **Audio Output**
   - Plays through system audio device
   - Automatic volume ducking during music playback
   - Thread-safe speaking state management
   - Updates context for wake word requirement

**Voice Configuration**

Default configuration (config.json):

.. code-block:: json

   {
     "PREFERRED_VOICES": ["Veena", "Rishi", "Samantha", "Lekha"],
     "LANGUAGE_VOICE_MAP": {
       "hi": "Veena",
       "en": "Veena",
       "ta": "Veena",
       "te": "Veena"
     }
   }

**Testing Voices**

.. code-block:: bash

   # List available Indian voices
   say -v ? | grep -E "(hi_IN|en_IN)"
   
   # Test Veena voice
   say -v Veena "Testing Indian English voice"
   
   # Test Lekha voice (Hindi)
   say -v Lekha "नमस्ते, मैं वाणी हूँ"

**Voice Configuration**

Choose different voices by language:

.. code-block:: bash

   # View available voices
   python3 << 'EOF'
   from vaani_assistant.config import settings
   config = settings.config
   language = config.get('VOICE_LANGUAGE', 'en')
   print(f"Current language: {language}")
   print(f"Available voices: {config.get('VOICE_OPTIONS', {}).get(language, [])}")
   EOF

**Configure Voice**

.. code-block:: bash

   # Edit .env file
   echo "VOICE_LANGUAGE=en" >> .env
   echo "TTS_ENGINE_VOICE_ID=female" >> .env
   
   # Then restart Vaani
   python3 main.py

Available voice identifiers by language are in :doc:`../configuration`.

**TTS Testing**

.. code-block:: bash

   # Test TTS
   python3 << 'EOF'
   from vaani_assistant.core.tts_engine import text_to_speech
   
   text = "Hello, this is Vaani. Testing text to speech."
   audio_file = text_to_speech(text, language="en")
   print(f"Generated audio: {audio_file}")
   EOF

Audio Playback
---------------

**Playback Pipeline**

1. **Audio File**
   - Generated TTS audio (WAV, MP3)
   - Or music from YouTube

2. **Audio Device Selection**
   - Detects available audio output devices
   - Selects default or configured device
   - Falls back to next available

3. **Playback**
   - Initiates playback through system audio
   - Handles volume control
   - May reduce music volume if configured

4. **Completion**
   - Waits for audio to finish
   - Cleans up resources

**Audio Devices**

Check available audio devices:

.. code-block:: bash

   # List audio devices
   python3 << 'EOF'
   import sounddevice as sd
   devices = sd.query_devices()
   for i, device in enumerate(devices):
       print(f"{i}: {device['name']}")
   EOF

**Configuring Audio Output**

.. code-block:: bash

   # Edit .env to specify device
   echo "AUDIO_OUTPUT_DEVICE_INDEX=0" >> .env
   
   # Or let Vaani auto-detect
   echo "AUDIO_OUTPUT_DEVICE_INDEX=-1" >> .env

**Music Playback**

Music playback is a special type of audio:

1. **Music Search** - Query YouTube for song/artist
2. **Download** - Get audio stream from YouTube
3. **Playback** - Play through audio output device

See :doc:`../customization` for music-specific settings.

**Testing Playback**

.. code-block:: bash

   # Test speaker/headphones
   python3 test_audio_verification.py
   
   # Test music playback
   python3 test_music.py

Audio Quality
-------------

**Sample Rate**

- **16kHz** (Standard) - Default for Vaani, good for voice
- **44.1kHz** (CD Quality) - Better for music, uses more bandwidth
- **48kHz** (Professional) - Highest quality, rarely needed

Default: 16kHz for speech recognition (sufficient for voice quality)

**Bit Depth**

- **16-bit** (Standard) - Default, good enough for voice
- **24-bit** (High) - Better dynamic range, rarely needed

Default: 16-bit (standard)

**Noise and Issues**

Common audio problems:

.. code-block:: text

   Echo (hearing yourself)
   → Check microphone position
   → Reduce speaker volume
   → Use noise cancellation headset
   
   Background noise being amplified
   → Move closer to microphone
   → Check microphone levels
   → Enable noise reduction in settings
   
   Crackling or distortion
   → Lower input/output volume
   → Use higher quality microphone
   → Check audio cable connections
   
   Stuttering playback
   → Close other applications
   → Increase audio buffer size
   → Check CPU usage with: top -l 1

Noise Handling
--------------

**Noise Reduction**

Vaani can reduce background noise before recognition:

.. code-block:: bash

   # Enable noise reduction in .env
   echo "SPEECH_RECOGNITION_NOISE_REDUCTION=true" >> .env
   
   # Restart Vaani
   python3 main.py

**How It Works**

1. Records baseline of room noise (first 0.5 seconds)
2. Subtracts baseline from incoming audio
3. Reduces background noise while preserving voice

**Limitations**

- Works best with consistent background noise
- Degrades performance with varying noise
- May remove part of speech if sound is overlapping

**When to Disable**

Disable noise reduction if:

1. You're in a quiet environment (unnecessary processing)
2. Noise reduction is cutting off parts of speech
3. Performance is a concern

.. code-block:: bash

   echo "SPEECH_RECOGNITION_NOISE_REDUCTION=false" >> .env

Audio Ducking
-------------

**What Is Audio Ducking?**

**Smart Ducking Strategy**

Vaani uses a "Smart Ducking" approach to balance music enjoyment and voice interaction:

1. **Wake Word Listening**: Music plays at **FULL VOLUME**. The music is *not* ducked while Vaani waits for "Hey Vaani".
2. **Command Listening**: Only *after* the wake word is detected, the music volume drops instantly to 15% (configurable).
3. **Response**: Music stays low while Vaani speaks the response.
4. **Resuming**: Music volume gracefully fades back up to original level.

**Why?**
Previous assistants ducked music *constantly* while listening for the wake word, ruining the song. Vaani's approach keeps the music loud until you actually engage the assistant.

**Music Mode Sensitivity**

When music is playing loudly, Vaani automatically switches to **Music Mode**:
- **Heuristic Filter**: It ignores long sentences (likely lyrics) to prevent false wake word triggers.
- **Dynamic Threshold**: It raises the microphone threshold significantly (to >3000) so it only hears you if you speak *over* the music.

**Configure Ducking**

.. code-block:: bash

   # Enable ducking (default)
   echo "AUDIO_DUCKING_ENABLED=true" >> .env
   
   # Set ducking level (0.2 = 20% volume while speaking)
   echo "AUDIO_DUCKING_LEVEL=0.2" >> .env
   
   # Set fade time (milliseconds)
   echo "AUDIO_DUCKING_FADE_TIME=500" >> .env

**Disable Ducking**

.. code-block:: bash

   echo "AUDIO_DUCKING_ENABLED=false" >> .env

**Limitations**

- Only works with audio Vaani controls
- System-level music apps won't be affected
- Timing might be slightly off on slower systems

Multi-Language Audio
--------------------

**Language Support**

Vaani supports 32 languages for audio:

.. code-block:: text

   English (en), Spanish (es), French (fr), German (de),
   Italian (it), Portuguese (pt), Russian (ru), Japanese (ja),
   Chinese (zh), Korean (ko), Arabic (ar), Hindi (hi),
   Turkish (tr), Polish (pl), Dutch (nl), Swedish (sv),
   Norwegian (no), Danish (da), Finnish (fi), Czech (cs),
   Greek (el), Hebrew (he), Thai (th), Vietnamese (vi),
   Indonesian (id), Filipino (fil), Malay (ms), Romanian (ro),
   Bulgarian (bg), Hungarian (hu), Croatian (hr), Serbian (sr)

**Switching Languages**

.. code-block:: bash

   # Interactive setup
   python3 -c "from vaani_assistant.config import global_config; global_config.setup_initial()"
   
   # Or edit .env
   echo "VOICE_LANGUAGE=es" >> .env

**Language-Specific Voices**

Each language has multiple voice options:

.. code-block:: bash

   # Example: English voices
   # female, male, female_uk, male_deep, etc.
   
   echo "VOICE_LANGUAGE=en" >> .env
   echo "TTS_ENGINE_VOICE_ID=female" >> .env

See :doc:`../configuration` for complete voice list by language.

**Accent Considerations**

- Speech recognition works with various accents
- Specify your language for best accuracy
- Some accents may reduce recognition accuracy

Advanced Configuration
----------------------

**Audio Buffering**

For systems with audio lag or dropouts:

.. code-block:: bash

   # Increase buffer size (higher = more latency but fewer dropouts)
   echo "AUDIO_BUFFER_SIZE=4096" >> .env

**Sample Rate Override**

.. code-block:: bash

   # Match your system's default
   echo "SPEECH_RECOGNITION_SAMPLE_RATE=44100" >> .env

**Device Fallback**

If primary audio device fails:

.. code-block:: bash

   # Try next device automatically
   echo "AUDIO_FALLBACK_ENABLED=true" >> .env

Debugging Audio Issues
----------------------

**Enable Audio Logging**

.. code-block:: bash

   LOG_LEVEL=DEBUG python3 main.py 2>&1 | grep -i audio

**Check Audio System**

.. code-block:: bash

   # macOS
   system_profiler SPAudioDataType
   
   # Linux
   aplay -l
   pactl list short sinks
   
   # Windows (WSL)
   pactl list short sinks

**Test Components Independently**

.. code-block:: bash

   # Test microphone
   python3 test_audio_direct.py
   
   # Test TTS
   python3 << 'EOF'
   from vaani_assistant.core.tts_engine import text_to_speech
   text_to_speech("Testing text to speech")
   EOF
   
   # Test playback
   python3 << 'EOF'
   from vaani_assistant.core.audio_player import play_audio
   play_audio("test_audio.wav")
   EOF

**Capture Audio for Analysis**

.. code-block:: bash

   # Record what Vaani is hearing
   python3 << 'EOF'
   from vaani_assistant.core.speech_recognition import recognize_speech
   import sounddevice as sd
   import soundfile as sf
   
   duration = 5  # seconds
   print(f"Recording for {duration} seconds...")
   recording = sd.rec(int(16000 * duration), samplerate=16000, channels=1)
   sd.wait()
   sf.write("captured_audio.wav", recording, 16000)
   print("Saved to captured_audio.wav")
   EOF

See :doc:`../troubleshooting` for common audio problems and solutions.

Technical Details
-----------------

**Audio Processing Pipeline**

When you speak to Vaani:

1. Microphone captures analog sound
2. Sound card converts to digital (analog-to-digital conversion)
3. Vaani records 16-bit PCM at 16kHz
4. Optional noise reduction is applied
5. Audio is buffered in 1-second chunks
6. When you stop speaking (silence detected), processing starts
7. Audio sent to speech recognition engine
8. Recognized text is returned

**TTS Generation Pipeline**

When Vaani responds:

1. Response text is prepared
2. Selected TTS engine is called
3. Engine generates audio data
4. Audio may be cached
5. Audio output device is selected
6. Audio is decoded (if necessary)
7. Volume levels are set
8. Audio is played through output device

**Music Playback Pipeline**

When music is requested:

1. Song name is sent to YouTube search
2. Top result is selected
3. Audio stream is downloaded
4. Stream is decoded in real-time
5. Audio ducking is applied if enabled
6. Audio is played through output device

Performance Tuning
------------------

**For Slow Systems**

.. code-block:: bash

   # Use faster TTS engine
   echo "TTS_ENGINE_PRIORITY=standard" >> .env
   
   # Disable noise reduction
   echo "SPEECH_RECOGNITION_NOISE_REDUCTION=false" >> .env
   
   # Reduce sample rate
   echo "SPEECH_RECOGNITION_SAMPLE_RATE=8000" >> .env

**For High Quality**

.. code-block:: bash

   # Use advanced TTS
   echo "TTS_ENGINE_PRIORITY=advanced" >> .env
   
   # Enable noise reduction
   echo "SPEECH_RECOGNITION_NOISE_REDUCTION=true" >> .env
   
   # Use higher sample rate
   echo "SPEECH_RECOGNITION_SAMPLE_RATE=44100" >> .env

Next Steps
----------

- See :doc:`../configuration` for all audio settings
- Read :doc:`../troubleshooting` for audio problems
- Check :doc:`../customization` for music options
- Review :doc:`project_structure` for code details
