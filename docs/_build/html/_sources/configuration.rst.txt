Configuration
=============

How to customize Vaani to work the way you want.

Where Settings Come From
------------------------

Vaani checks for settings in this order:

1. **Environment variables** - Stuff you set in ``.env`` or your shell (wins every time)
2. **config.json** - Your personal config file (this is the easiest place to change things)
3. **Program defaults** - Built-in fallbacks if you haven't set anything

Just edit ``config.json`` for most changes. It's cleaner than environment variables and easier than digging into code.

Global Configuration
---------------------

``vaani_assistant/config/global_config.py`` defines:

**Assistant Identity**

.. code-block:: python

   ASSISTANT_NAME = "Aria"
   ASSISTANT_NAME_LOWER = "aria"
   WAKE_WORDS = ["hey aria", "hi aria", "hello aria", "aria"]

The wake words include the assistant name automatically. To rename the assistant, edit ``ASSISTANT_NAME`` here.

**Supported Languages and Voices**

Vaani supports 32 languages with native speakers for each. For example:

.. code-block:: python

   # Hindi
   "hi": {"default": "hi-IN-SwaraNeural", "alternatives": ["hi-IN-MadhurNeural"]},
   
   # English
   "en": {"default": "en-US-VaaniNeural", "alternatives": ["en-US-GuyNeural"]},
   
   # Spanish
   "es": {"default": "es-ES-ElviraNeural", "alternatives": ["es-ES-AlvaroNeural"]},

**System Prompts**

The AI engine's personality is defined here:

.. code-block:: python

   GEMINI_SYSTEM_INSTRUCTIONS = """
   You are Aria, a helpful voice assistant...
   """

Customize this to change how Vaani responds.

**Default Behaviors**

- Response timeouts
- Memory limits (how much conversation history to keep)
- Audio settings (sample rate, bit depth)
- Search result limits

Runtime Settings
----------------

**config.json File Format**

A ``config.json`` file is automatically created in the project root. You can edit it directly:

.. code-block:: json

   {
     "MICROPHONE_TYPE": "internal",
     "MUSIC_DUCK_VOLUME": 0.15,
     "DEFAULT_VOLUME": 0.5,
     "GOOGLE_API_KEY": "your_key_here",
     "WEATHER_API_KEY": "your_key_here",
     "PREFERRED_VOICES": ["Lekha", "Rishi", "Vani", "Piya"],
     "WAKE_WORDS": ["hey vani", "hey vaani"],
     "AI_MODEL": "gemini-1.5-flash"
   }

**Available Settings**

Voice and Language
^^^^^^^^^^^^^^^^^^^

- ``PREFERRED_VOICES`` - List of preferred voice names (e.g., ["Lekha", "Rishi"]).
- ``LANGUAGE_VOICE_MAP`` - Maps languages to specific voices (e.g., {"hi": "Lekha"}).

Audio & Hardware
^^^^^^^^^^^^^^^^

- ``MICROPHONE_TYPE`` - "internal" (laptop mic) or "external" (USB/Bluetooth).
- ``MUSIC_DUCK_VOLUME`` - Volume level (0.0 - 1.0) when Vaani is speaking (default 0.15).
- ``DEFAULT_VOLUME`` - Initial system volume (0.0 - 1.0).
- ``ENERGY_THRESHOLD`` - Manual sensitivity override (default None).

Behaviors
^^^^^^^^^

- ``WAKE_WORDS`` - List of triggers to wake the assistant.
- ``AI_MODEL`` - Gemini model to use (e.g., "gemini-1.5-flash").
- ``RESPONSE_LENGTH`` - "concise" (default) or "detailed".

Supported Languages
--------------------

Vaani supports the following languages with full text-to-speech and voice recognition:

**Asian Languages**

- Hindi (hi-IN)
- Bengali (bn-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
- Marathi (mr-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Japanese (ja-JP)
- Mandarin Chinese (zh-CN)
- Korean (ko-KR)

**European Languages**

- English (en-US, en-GB)
- French (fr-FR)
- Spanish (es-ES)
- German (de-DE)
- Italian (it-IT)
- Dutch (nl-NL)
- Portuguese (pt-PT, pt-BR)
- Russian (ru-RU)
- Polish (pl-PL)

**Middle Eastern Languages**

- Arabic (ar-SA)
- Hebrew (he-IL)
- Turkish (tr-TR)

**Other Languages**

- Thai (th-TH)
- Vietnamese (vi-VN)
- Indonesian (id-ID)

Customizing Configuration
-------------------------

**Change the default language**

.. code-block:: bash

   export VOICE_LANGUAGE=es
   python3 main.py

This starts Vaani in Spanish.

**Use a different voice**

See the full list of voices in ``global_config.py``. Choose a variant:

.. code-block:: bash

   export VOICE_LANGUAGE=en
   export VOICE_NAME=en-US-GuyNeural
   python3 main.py

**Customize the personality**

Edit ``global_config.py`` and modify ``GEMINI_SYSTEM_INSTRUCTIONS``:

.. code-block:: python

   GEMINI_SYSTEM_INSTRUCTIONS = """
   You are a professional assistant named Aria...
   Keep responses concise and technical...
   """

**Change wake words**

Edit ``WAKE_WORDS`` in ``global_config.py``:

.. code-block:: python

   WAKE_WORDS = ["hey assistant", "hi helper", "activate"]

**Add an API key**

Create or edit ``.env``:

.. code-block:: bash

   GEMINI_API_KEY=your_actual_key_here

Then restart Vaani.

Configuration Best Practices
----------------------------

**Environment Separation**

Use different ``.env`` files for development and production:

.. code-block:: bash

   # Development with verbose logging
   LOG_LEVEL=DEBUG
   
   # Production with minimal logging
   LOG_LEVEL=WARNING

**Secrets Management**

Never commit ``.env`` to version control. Use ``.env.example`` as a template:

.. code-block:: bash

   # .env.example - Safe to commit
   GEMINI_API_KEY=
   
   # .env - Never commit, add to .gitignore
   GEMINI_API_KEY=abc123xyz...

**Performance Tuning**

Adjust timeouts based on your machine:

.. code-block:: bash

   # Slower hardware - allow more time
   RECOGNITION_TIMEOUT=15
   RESPONSE_TIMEOUT=10
   
   # Fast hardware - respond quicker
   RECOGNITION_TIMEOUT=8
   RESPONSE_TIMEOUT=5

Debugging Configuration
-----------------------

**Check current settings**

.. code-block:: python

   from vaani_assistant.config import settings
   
   print(settings.config)  # Shows all loaded settings

**Verify a specific setting**

.. code-block:: python

   voice = settings.config.get("VOICE_NAME", "fallback_value")

**Trace setting resolution**

.. code-block:: bash

   # Set debug logging
   export LOG_LEVEL=DEBUG
   python3 main.py
   
   # Watch configuration loading in logs

Module Reference
----------------

.. toctree::
   
   modules/config

See Also
--------

- :doc:`usage` - How to use Vaani
- :doc:`customization` - Adapting Vaani to your needs
- :doc:`modules/core` - Core module documentation
