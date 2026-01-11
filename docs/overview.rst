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

Getting Help
------------

- **Installation issues?** See :doc:`installation`
- **Can't get audio to work?** Check :doc:`troubleshooting`
- **Want to customize Vaani?** Start with :doc:`customization`
- **Curious about the code?** Explore :doc:`development/project_structure`
