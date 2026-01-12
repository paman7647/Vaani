Getting Started
===============

Let's get Vaani running on your system. This should take about 10 minutes.

What You'll Need
----------------

**The Basics**

- Python 3.10 or newer (check with ``python3 --version``)
- A microphone (built-in laptop mic works fine)
- Internet connection (for installation and Google API)
- About 500 MB of free space

**Works On**

- macOS (both Intel and Apple Silicon Macs)
- Linux (Ubuntu, Debian, Fedora, Arch - pretty much any modern distro)
- Windows (through WSL - Windows Subsystem for Linux)

Pick your OS and the installer will handle the rest.

Installation
------------

The easiest way to get started is the automated installer:

.. code-block:: bash

   cd vaani
   ./install_vaani.sh

This script handles:

1. Checking system requirements
2. Installing Python dependencies
3. Setting up the default voice (Hindi)
4. Installing VLC for audio playback
5. Creating a launch script

If you prefer manual installation, see :doc:`installation`.

Fire It Up
----------

Once installation finishes:

.. code-block:: bash

   python3 main.py

You'll see something like::

   VANI Voice Assistant Ready

That's it. It's listening.

No wake word needed when you first start - just talk to it. Say something like "Hello" or "What's the weather?"

Try These First
---------------

Here are some things you can do right away:

**Just ask something:**
   "What's the weather in Tokyo?"
   
   "Who won the World Cup in 2022?"
   
   "Tell me about quantum computing"

**Play some music:**
   "Play some lo-fi music"
   
   "Play Bohemian Rhapsody"

**Control playback:**
   While music is playing, say "Hey Vaani, pause" or "Hey Vaani, next song"
   
   (You need the wake word when music is playing, otherwise it can't hear you)

**Have a conversation:**
   "What's your name?"
   
   "Tell me a joke"
   
   "How are you?"

First Configuration
--------------------

Vaani works out of the box, but you might want to customize it. The configuration file is `.env`:

.. code-block:: bash

   # View the configuration template
   cat .env.example

   # Create your own configuration (optional)
   cp .env.example .env
   nano .env  # or your favorite editor

Key settings:

- ``VOICE_LANGUAGE`` - Language for Vaani to speak (default: hi for Hindi)
- ``VOICE_NAME`` - Specific voice variant (default: hi-IN-SwaraNeural)
- ``GEMINI_API_KEY`` - Optional, for enhanced AI responses
- ``LOG_LEVEL`` - How much detail to log (DEBUG, INFO, WARNING, ERROR)

See :doc:`configuration` for a complete list of options.

Troubleshooting First Launch
-----------------------------

**"ModuleNotFoundError: No module named..."**
   Dependencies weren't installed. Run the installer again or manually install with:
   
   .. code-block:: bash
   
      pip3 install --user -r requirements-basic.txt

**"Microphone not working"**
   Test your microphone:
   
   .. code-block:: bash
   
      python3 -m speech_recognition
   
   If that doesn't work, check system audio settings.

**"No sound output"**
   Install VLC:
   
   - macOS: ``brew install vlc``
   - Linux: ``sudo apt-get install vlc``

**"Vaani doesn't respond to wake word"**
   Try speaking more clearly and without background noise. You can also type instead of speaking.

Understanding How Vaani Works
-----------------------------

**The Listening Loop**

When Vaani starts, it enters a continuous listening loop:

1. **Wake Word Detection** - Passively listens for "Hey Vaani" or your configured wake words
2. **Command Capture** - Once triggered, records your full command until you pause
3. **Speech Processing** - Converts audio to text using multi-engine recognition
4. **Intent Classification** - Determines what you want (music, search, conversation, etc.)
5. **Response Generation** - Uses AI and/or web search to formulate an answer
6. **Speech Synthesis** - Converts response text to natural speech
7. **Audio Playback** - Plays the response through your speakers
8. **Loop** - Returns to listening for the next wake word

This happens continuously, allowing for natural back-and-forth conversation.

**Multi-Engine Recognition**

Vaani uses three speech recognition engines in priority order:

1. **Google Speech API (Primary)** - Best accuracy (~95%), requires internet
2. **Vosk (Backup)** - Good accuracy (~85%), fully offline, fast (<100ms)
3. **Sphinx (Fallback)** - Basic accuracy, always available

If one engine fails, the next automatically takes over. This ensures Vaani works even without internet or if an API is down.

**Context-Aware Wake Word**

Vaani is smart about when you need to say the wake word:

- **Idle state** (nothing playing): Just talk normally, no wake word needed
- **Music playing**: Say "Hey Vaani" first so it knows you're talking to it
- **Already in conversation**: Continue speaking naturally for follow-up questions

This makes interaction feel more natural than traditional assistants.

Advanced First-Time Setup
-------------------------

**Configuring API Keys**

For enhanced AI responses, add your Google Gemini API key:

.. code-block:: bash

   # Get a free API key from https://makersuite.google.com/app/apikey
   echo "GEMINI_API_KEY=your_actual_key_here" >> .env

**Selecting Your Preferred Voice**

List available voices for your language:

.. code-block:: bash

   python3 << 'EOF'
   from vaani_assistant.config import global_config
   import json
   
   # Show Hindi voices
   voices = global_config.LANGUAGE_VOICE_MAP.get('hi', {})
   print(json.dumps(voices, indent=2))
   EOF

Set your preference in ``.env``:

.. code-block:: bash

   echo "VOICE_LANGUAGE=hi" >> .env
   echo "VOICE_NAME=hi-IN-SwaraNeural" >> .env

**Optimizing Microphone Settings**

Test microphone sensitivity:

.. code-block:: bash

   python3 << 'EOF'
   import speech_recognition as sr
   r = sr.Recognizer()
   with sr.Microphone() as source:
       print("Adjusting for ambient noise... Please wait")
       r.adjust_for_ambient_noise(source, duration=2)
       print(f"Energy threshold set to: {r.energy_threshold}")
       print("Say something!")
       audio = r.listen(source, timeout=5)
       print("Processing...")
       try:
           text = r.recognize_google(audio)
           print(f"You said: {text}")
       except:
           print("Could not understand")
   EOF

If Vaani is too sensitive (triggers accidentally) or not sensitive enough, adjust:

.. code-block:: bash

   # Make less sensitive (higher threshold, default is 300)
   echo "ENERGY_THRESHOLD=500" >> .env
   
   # Make more sensitive (lower threshold)
   echo "ENERGY_THRESHOLD=200" >> .env

**Configuring Music Volume Ducking**

When Vaani speaks while music plays, it automatically lowers music volume:

.. code-block:: bash

   # Set how low music goes (0.0 = mute, 1.0 = full volume)
   echo "MUSIC_DUCK_VOLUME=0.15" >> .env  # Default: 15%
   
   # Or disable ducking entirely
   echo "AUDIO_DUCKING_ENABLED=false" >> .env

Daily Usage Workflow
--------------------

**Morning Routine Example**

.. code-block:: text

   You: [Start Vaani] python3 main.py
   Vaani: "Vaani Assistant Ready"
   
   You: "Good morning"
   Vaani: "Good morning! How can I help you today?"
   
   You: "What's the weather like?"
   Vaani: [Searches] "It's currently 72°F and sunny..."
   
   You: "Play some morning jazz"
   Vaani: "Now playing jazz music"
   [Music starts playing]
   
   You: "Hey Vaani, lower the volume"
   Vaani: [Lowers music] "Volume adjusted"
   
   You: "Hey Vaani, pause"
   Vaani: "Music paused"

**Research Session Example**

.. code-block:: text

   You: "Tell me about quantum computing"
   Vaani: [Searches and explains quantum computing]
   
   You: "What companies are working on it?"
   Vaani: [Remembers context, searches] "Several companies including IBM, Google, Microsoft..."
   
   You: "How do quantum computers differ from regular computers?"
   Vaani: [Continues contextual conversation about quantum vs classical computing]

**Entertainment Session Example**

.. code-block:: text

   You: "Play Bohemian Rhapsody"
   Vaani: "Now playing Bohemian Rhapsody by Queen"
   [Song plays]
   
   You: "Hey Vaani, who wrote this song?"
   Vaani: [Music ducks down] "Freddie Mercury wrote Bohemian Rhapsody in 1975"
   [Music comes back up]
   
   You: "Hey Vaani, next song"
   Vaani: "Playing next song"

Power User Tips
---------------

**Quick Command Mode**

For single commands without conversation, set:

.. code-block:: bash

   echo "RESPONSE_LENGTH=concise" >> .env

Responses will be shorter and more to-the-point.

**Offline-First Mode**

If you primarily work offline:

.. code-block:: bash

   # Disable web search (uses only local AI)
   echo "WEB_SEARCH_ENABLED=false" >> .env
   
   # Use offline speech recognition only
   echo "SPEECH_ENGINE_PRIORITY=vosk" >> .env

**Multi-Language Household**

Switch languages easily:

.. code-block:: bash

   # For Hindi
   VOICE_LANGUAGE=hi python3 main.py
   
   # For English
   VOICE_LANGUAGE=en python3 main.py
   
   # For Spanish
   VOICE_LANGUAGE=es python3 main.py

**Debug Mode**

See exactly what Vaani hears and processes:

.. code-block:: bash

   LOG_LEVEL=DEBUG python3 main.py

Useful for troubleshooting or understanding behavior.

**Background Service**

Run Vaani in the background:

.. code-block:: bash

   # Start in background
   nohup python3 main.py > vaani.log 2>&1 &
   
   # Check if running
   ps aux | grep main.py
   
   # View logs
   tail -f vaani.log
   
   # Stop
   pkill -f main.py

For permanent setup, see :doc:`deployment`.

Extended Troubleshooting
------------------------

**Audio Device Selection Issues**

List all audio devices:

.. code-block:: bash

   python3 << 'EOF'
   import sounddevice as sd
   devices = sd.query_devices()
   print("\nAvailable devices:")
   for i, device in enumerate(devices):
       print(f"{i}: {device['name']}")
       print(f"   Max input channels: {device['max_input_channels']}")
       print(f"   Max output channels: {device['max_output_channels']}")
       print()
   EOF

Select specific input device:

.. code-block:: bash

   echo "AUDIO_INPUT_DEVICE_INDEX=2" >> .env  # Use device #2

**Wake Word Not Triggering**

Test wake word detection:

.. code-block:: bash

   python3 << 'EOF'
   from rapidfuzz import fuzz
   
   test_phrases = [
       "hey vaani",
       "hey vani", 
       "hi vaani",
       "hey varni",
       "a vaani"
   ]
   
   for phrase in test_phrases:
       score = fuzz.ratio("hey vaani", phrase.lower())
       match = "✓" if score >= 85 else "✗"
       print(f"{match} '{phrase}' - Score: {score}%")
   EOF

Adjust wake word sensitivity:

.. code-block:: bash

   # More lenient (accepts more variations)
   echo "WAKE_WORD_THRESHOLD=70" >> .env
   
   # More strict (exact match required)
   echo "WAKE_WORD_THRESHOLD=95" >> .env

**Slow Response Times**

Profile performance:

.. code-block:: bash

   python3 -m cProfile -o vaani.prof main.py
   
   # Analyze results
   python3 << 'EOF'
   import pstats
   p = pstats.Stats('vaani.prof')
   p.sort_stats('cumulative').print_stats(20)
   EOF

Optimize for speed:

.. code-block:: bash

   # Use faster speech model
   echo "VOSK_MODEL_SIZE=small" >> .env
   
   # Disable web search (faster responses)
   echo "WEB_SEARCH_TIMEOUT=2" >> .env
   
   # Use simpler TTS
   echo "TTS_ENGINE=pyttsx3" >> .env

**Memory Usage Too High**

Limit conversation memory:

.. code-block:: bash

   echo "MAX_MEMORY_SIZE=20" >> .env  # Keep only last 20 exchanges

**Inconsistent Recognition**

Test all three engines:

.. code-block:: bash

   python3 << 'EOF'
   from vaani_assistant.voice import speech_recognition
   
   print("Testing Google API...")
   try:
       text = speech_recognition.recognize_google(audio)
       print(f"Result: {text}")
   except Exception as e:
       print(f"Failed: {e}")
   
   print("\nTesting Vosk...")
   try:
       text = speech_recognition.recognize_vosk(audio)
       print(f"Result: {text}")
   except Exception as e:
       print(f"Failed: {e}")
   EOF

Next Steps
----------

- **Ready to customize?** See :doc:`customization`
- **Want to understand the architecture?** Read :doc:`architecture`
- **Interested in development?** Check :doc:`development/setup`
- **Looking for more features?** Explore :doc:`usage`
- **Need detailed configuration?** Review :doc:`configuration`
- **Facing specific issues?** Consult :doc:`troubleshooting`

Common Questions
----------------

**Does Vaani work offline?**
   Partially. Core features work offline (local speech recognition with Vosk, responses from memory, TTS). Web search and Google Gemini AI require internet. You can configure Vaani to be fully offline by disabling web search and using local models only.

**Can I change the language?**
   Yes, see :doc:`configuration`. Vaani supports 32 languages including Hindi, English, Spanish, French, German, Japanese, Chinese, Arabic, and many more.

**Is my voice data stored?**
   Not by Vaani itself on your device. Voice data is processed locally or sent to Google's Speech API (if configured). When using Gemini AI, conversation text (not audio) is sent to Google for processing. See :doc:`disclaimer` for privacy details.

**Can I modify Vaani's personality?**
   Yes, extensively. You can change response style, tone, verbosity, wake words, and even system instructions. See :doc:`customization` for full details.

**Does it work on Raspberry Pi?**
   Yes, though performance depends on the Pi model. Pi 4 works well. You may need to use smaller Vosk models and simpler TTS engines on lower-end models.

**Can multiple people use it?**
   Yes, Vaani doesn't require voice training and works with any voice. However, it doesn't have multi-user profiles or personalization yet.

**How much disk space does it need?**
   About 500 MB total:
   - Vosk models: ~50 MB each (150 MB for 3 models)
   - Python dependencies: ~300 MB
   - Code and documentation: ~50 MB

**Can I use it with smart home devices?**
   Not natively yet, but you can extend Vaani to integrate with Home Assistant, MQTT, or other smart home platforms. See development documentation.

For more questions, see :doc:`faq`.
