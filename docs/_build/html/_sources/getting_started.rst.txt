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

Next Steps
----------

- **Ready to customize?** See :doc:`customization`
- **Want to understand the architecture?** Read :doc:`architecture`
- **Interested in development?** Check :doc:`development/setup`
- **Looking for more features?** Explore :doc:`usage`

Common Questions
----------------

**Does Vaani work offline?**
   Partially. Core features work offline (local speech recognition, responses from memory). Web search and some advanced features require internet.

**Can I change the language?**
   Yes, see :doc:`configuration`. Vaani supports 32 languages.

**Is my voice data stored?**
   Not by Vaani itself. Depending on your configuration, some data may go to Google's Gemini API for processing.

**Can I modify Vaani's personality?**
   Yes, see :doc:`customization`.

For more questions, see :doc:`faq`.
