Extended Frequently Asked Questions
===================================

This document provides an exhaustive list of questions and answers regarding the Vaani Voice Assistant, covering every aspect of its lifecycle.

.. contents:: Table of Contents
   :depth: 2
   :local:

General & Capabilities
----------------------

1. **What is Vaani?**
   Vaani is a hybrid, context-aware voice assistant designed for natural conversations, prioritizing privacy and speed.

2. **Why was Vaani created?**
   To bridge the gap between rigid command-based assistants (like Siri/Alexa) and conversational AI, offering a more "human" interaction model.

3. **Does Vaani work offline?**
   Yes, partially. Wake word detection, speech synthesis (TTS), and system commands work offline.

4. **Does Vaani work online?**
   Yes. Complex queries, general knowledge questions, and web searches require an active internet connection to access Google Gemini and search APIs.

5. **Is Vaani open source?**
   No, it is proprietary software. You can view the source for personal use, but redistribution is restricted.

6. **Can I use Vaani commercialy?**
   No. The license strictly prohibits commercial use or redistribution.

7. **What OS does Vaani run on?**
   It natively supports macOS, Linux (Ubuntu, Debian, Fedora, Arch), and Windows 10/11.

8. **Is there a mobile app?**
   Not currently. Vaani is designed as a desktop/embedded voice assistant.

9. **Can Vaani control my smart home?**
   Home automation integration (MQTT/HomeAssistant) is on the roadmap but not yet implemented.

10. **Does Vaani record everything I say?**
    No. It only records audio *after* the wake word ("Hey Vaani") is detected locally.

11. **Where is my data stored?**
    Conversation history is stored in memory (RAM) and lost when the application closes. No voice data is uploaded to cloud servers for training.

12. **Can Vaani speak other languages?**
    It currently speaks English (Indian/US accents) and has experimental support for Hindi, Tamil, and Bengali mapping.

13. **Can Vaani understand mixed languages (Hinglish)?**
    It is optimized for Indian English, which handles some common mixed phrasing, but full code-switching support is experimental.

14. **How fast is the response time?**
    Offline commands: <200ms. Cloud AI queries: 1-3 seconds depending on internet speed.

15. **Does it support multiple users?**
    Not yet. It doesn't distinguish between different voice prints.

16. **Can I change the assistant's name?**
    Yes, by changing the wake word configuration.

17. **Is there a GUI?**
    No, it is currently a headless (voice-only) or terminal-based application. A GUI is planned.

Installation & Setup
--------------------

18. **How do I install Vaani?**
    Use the automated ``setup.sh`` script for macOS/Linux or ``setup.ps1`` for Windows.

19. **What are the prerequisites?**
    Python 3.10+, ``git``, and a working microphone/speaker setup.

20. **I get "Permission denied" on setup.sh.**
    Run ``chmod +x setup.sh`` to make it executable.

21. **Do I need sudo for setup?**
    The script may ask for your password to install system dependencies (like ``ffmpeg`` via apt/brew).

22. **Setup fails on "pip install".**
    Ensure you have a stable internet connection. Try running ``pip install --upgrade pip`` manually.

23. **"PortAudio not found" error.**
    You are missing C-level audio headers. Install ``portaudio19-dev`` (Linux) or ``portaudio`` (Homebrew).

24. **"vlc module not found" error.**
    Install VLC media player on your OS (e.g., `apt install vlc` or download from videolan.org). The python module relies on the system binary.

25. **Can I install it on a Raspberry Pi?**
    Yes! It runs well on Pi 4. Recommended OS: Raspberry Pi OS (Bullseye/Bookworm).

26. **Does it work on Apple Silicon (M1/M2/M3)?**
    Yes, it runs natively on ARM64 architecture.

27. **Do I need a GPU?**
    No. Vosk runs on CPU. Generating AI responses happens in the cloud.

28. **Setup is stuck on "Downloading models".**
    These models are large (~50MB). Check your internet speed. You can manually download them to ``models/`` if the script hangs.

29. **Can I use Conda instead of venv?**
    Yes, just create a conda env and install ``requirements.txt`` manually.

30. **What version of Python is best directly?**
    Python 3.10 or 3.11. Python 3.12 compatibility is still being verified for some audio libraries.

31. **Can I install it inside Docker?**
    Yes, but passing audio devices (mic/speaker) to Docker containers can be tricky.

32. **How much disk space does it need?**
    Approx 500MB (including models and venv).

33. **How do I uninstall Vaani?**
    Simply delete the project folder. There are no registry keys or hidden system files created.

Configuration & Customization
-----------------------------

34. **Where is the configuration file?**
    ``config.json`` in the root directory.

35. **How do I configure API keys?**
    Create a ``.env`` file (copy from ``.env.example`` if available) and add ``GOOGLE_API_KEY``.

36. **Can I add multiple wake words?**
    Yes. Edit ``"WAKE_WORDS": ["hey vani", "computer", "jarvis"]`` in ``config.json``.

37. **How do I change the speech rate?**
    Change ``"SPEECH_RATE": 160`` in ``config.json``. Lower is slower, higher is faster.

38. **How do I make the volume louder?**
    Adjust ``"DEFAULT_VOLUME": 1.0``. Range is 0.0 to 1.0.

39. **What is "ENERGY_THRESHOLD"?**
    It controls microphone sensitivity. 300 is 'whisper sensitive', 1000 is 'shouting only'.

40. **How do I enable debug mode?**
    Set ``"DEBUG_MODE": true`` in ``config.json`` for verbose logs.

41. **Can I change the AI personality?**
    Modify ``Vaani/intellegence/personality.py`` system prompts.

42. **How to disable music ducking?**
    Set ``"MUSIC_DUCK_VOLUME": 1.0`` (no volume reduction).

43. **Can I use OpenAI/ChatGPT instead of Gemini?**
    Not out of the box. You would need to rewrite ``Vaani/intellegence/conversation.py`` to use the OpenAI API.

44. **Can I use a local LLM (Ollama/Llama)?**
    The architecture supports it, but you need to write a custom adapter in ``Vaani/intellegence/``.

45. **How do I change the weather location?**
    Vaani automatically tries to detect it or asks API. You can set a default in the code if needed.

46. **What is "RESPONSE_LENGTH"?**
    Controls how verbose the AI is. Options: "short", "medium", "long".

47. **Can I turn off Google Search grounding?**
    Yes, set ``"USE_GOOGLE_SEARCH_GROUNDING": false``.

48. **How do I map a language to a different TTS voice?**
    Update ``"LANGUAGE_VOICE_MAP"`` in ``config.json``.

Hardware & Peripherals
----------------------

49. **What microphone should I use?**
    Any USB or internal mic works. A generic webcam mic is sufficient.

50. **Does it support Bluetooth headsets?**
    Yes, as long as the OS recognizes it as the default input device.

51. **Can I use a text-only mode (no mic)?**
    You can pipe input to ``main.py`` via stdin if you modify the entry point, but it's designed for voice.

52. **My microphone is very noisy.**
    Vaani has basic noise reduction. Ensure ``ENERGY_THRESHOLD`` is tuned above the noise floor.

53. **Does it support microphone arrays (ReSpeaker)?**
    Yes, via standard ALSA/PulseAudio drivers.

54. **Can I output audio to a specific speaker?**
    Currently, it uses the system default output. Use your OS settings to route audio.

55. **Does the wake word work while music is playing?**
    Yes, but effectiveness depends on your microphone's echo cancellation capabilities.

Voice Recognition (STT)
-----------------------

56. **What engine is used for Wake Word?**
    Vosk (using the small model).

57. **What engine is used for Commands?**
    Vosk (offline) or Google Speech Recognition (online fall-back).

58. **Why didn't it hear me?**
    You might have spoken too softly, or the ``ENERGY_THRESHOLD`` is too high.

59. **Why is it triggering randomly?**
    ``ENERGY_THRESHOLD`` is too low, or the background noise sounds like the wake word.

60. **Can I train my own wake word model?**
    Vosk doesn't support easy custom wake word training. You'd need to use PocketSphinx or Snowboy for custom training, which requires code changes.

61. **Does it support continuous dictation?**
    No, it is designed for turn-by-turn commands, not transcribing long documents.

62. **How accurate is the offline model?**
    The "small" models are ~85-90% accurate. Full-size models are better but use 2GB+ RAM.

63. **Can I use the large Vosk model?**
    Yes. Download it, place it in ``models/``, and update the path in ``Vaani/core/voice.py`` (if hardcoded) or config.

64. **Does it adapt to my voice?**
    No, Vosk is speaker-independent.

65. **Why is the first command slow?**
    The models need to load into RAM. This "cold start" takes 2-5 seconds.

66. **Does it handle accents well?**
    The `en-in` model is specifically chosen for Indian accents.

Speech Synthesis (TTS)
----------------------

67. **What TTS engine is used?**
    `pyttsx3`, which wraps system engines (NSSpeechSynthesizer on macOS, SAPI5 on Windows, eSpeak on Linux).

68. **The voice sounds robotic.**
    On Linux (`espeak`), this is normal. On macOS/Windows, it should sound natural.

69. **Can I use ElevenLabs/Azure TTS?**
    You can extend `ResponseSynthesizer` class to use API-based TTS, but it adds latency/cost.

70. **How do I verify available voices?**
    Run a python script: `import pyttsx3; [print(v.id) for v in pyttsx3.init().getProperty('voices')]`.

71. **Can I make it speak faster?**
    Increase ``SPEECH_RATE`` in configuration.

Media & Playback
----------------

72. **How does music playback work?**
    It searches YouTube via `yt-dlp`, extracts the audio stream URL, and plays it via VLC.

73. **Do I need a YouTube Premium account?**
    No.

74. **Can I play Spotify?**
    No, Spotify has a closed API for streaming.

75. **Can I play local MP3 files?**
    Not currently implemented, but easy to add.

76. **Why does music stop after a while?**
    YouTube stream URLs expire. Vaani handles this by fetching new URLs for next tracks.

77. **Can I seek forward/backward?**
    Commands like "skip" work. "Fast forward 10 seconds" is not implemented yet.

78. **Does it block ads?**
    Since it streams audio directly, you don't hear video ads.

79. **What happens if I ask for a song that doesn't exist?**
    It will try to play the closest match or say "I couldn't find that."

Intelligence & AI (Gemini)
--------------------------

80. **Which Gemini model is used?**
    Default is `gemini-2.5-flash`.

81. **Does it have a memory limit?**
    It keeps the last N turns of conversation (configurable in code).

82. **Is my API key safe?**
    It's stored locally. It's only sent to Google's servers for authentication.

83. **Can it write code?**
    Yes, Gemini is good at coding, but dictating code via voice is difficult.

84. **Can it summarize web pages?**
    If configured with search grounding, it can summarize search results.

85. **What is "Search Grounding"?**
    It allows the model to look up current info (news, weather) before answering.

86. **Why does it sometimes hallucinate?**
    All LLMs hallucinate. Use search grounding to reduce this.

Privacy & Security
------------------

87. **Is there a "mute" button?**
    There is no software mute button yet. You can mute your system mic.

88. **Does it start listening on boot?**
    Only if you configured it as a system service.

89. **Are logs encrypted?**
    No. Do not share logs if they contain sensitive info.

90. **Can someone hack my Vaani?**
    If your computer is compromised, yes. Vaani itself doesn't open external network ports (it's a client, not a server).

Development & Contributing
--------------------------

91. **What is the coding style?**
    PEP 8.

92. **Do you use type hinting?**
    Yes, extensively.

93. **How do I run tests?**
    `pytest` (if tests are added). Currently manual testing is primary.

94. **Where is the main entry point?**
    `main.py`.

95. **How is the project structured?**
    - `Vaani/core`: Hardware I/O.
    - `Vaani/intellegence`: AI and Logic.
    - `models/`: ML assets.

96. **Can I submit a PR?**
    Yes! Please read `CONTRIBUTING.md` (or the section in docs).

97. **Is there a developer discord?**
    Check the GitHub repository for community links.

Troubleshooting Errors
----------------------

98. **Error: `AttributeError: PyAudio object has no attribute '...'`**
    You likely have a version mismatch. Ensure you installed dependencies from `requirements.txt`.

99. **Error: `[Errno -9996] Invalid input device`**
    No microphone found. Check OS settings.

100. **Error: `ssl.SSLCertVerificationError`**
     Common on corporate networks or old macOS python installs. Run "Install Certificates.command" in your Python folder on Mac.

101. **Error: `429 Too Many Requests` (Google API)**
     You exceeded your free tier quota on Gemini. Wait a minute or upgrade to a paid key.

102. **System crashes when playing music.**
     Usually a `libvlc` version issue. Update VLC player.

103. **It speaks but I hear nothing.**
     Check if volume is 0 or if output is routed to headphones you aren't wearing.

104. **The application exits immediately.**
     Check `config.json` for syntax errors (missing commas/quotes).

105. **How do I clear the cache?**
     Delete the `__pycache__` directories.

106. **Why is the response cut off?**
     Token limit in the API call. Increase `max_output_tokens` in `Vaani/intellegence/response_synthesizer.py`.
