Coding Style and Standards
==========================

Guidelines for writing code that fits with Vaani's codebase.

Philosophy
----------

Code is read much more often than it's written. Write for the reader, not the machine.

**Principles**

- Clarity over cleverness
- Explicit over implicit
- Simple over complex
- Documented over assumed

Python Style
------------

Vaani follows PEP 8 with some practical considerations.

**Formatting**

Use ``black`` for consistent formatting:

.. code-block:: bash

   pip install black
   black vaani_assistant/

**Line length**

- Maximum 100 characters (not 79)
- Rationale: Modern monitors, balances readability with density

**Imports**

Group in this order with blank lines between:

.. code-block:: python

   # Standard library
   import os
   import sys
   from typing import Optional, List
   
   # Third-party
   import numpy as np
   from google import genai
   
   # Local
   from ..config import settings
   from ..utils.logger import logger

**Naming**

.. code-block:: python

   # Classes - PascalCase
   class AssistantManager:
       pass
   
   # Functions and methods - snake_case
   def get_assistant_manager():
       pass
   
   def process_input(text):
       pass
   
   # Constants - UPPER_SNAKE_CASE
   ASSISTANT_NAME = "Aria"
   MAX_MEMORY_SIZE = 100
   
   # Private - leading underscore
   def _internal_method():
       pass
   
   _private_variable = 42

**Type Hints**

Use type hints for clarity:

.. code-block:: python

   # Good
   def recognize_speech(timeout: int = 10) -> str:
       pass
   
   def process_audio(data: bytes, sample_rate: int) -> Optional[str]:
       pass
   
   def get_voices(language: str) -> List[str]:
       pass
   
   # Avoid - no hints
   def recognize_speech(timeout=10):
       pass

Documentation
--------------

**Module Docstrings**

Every file should start with:

.. code-block:: python

   """
   Brief description of module.
   
   Longer description explaining purpose, usage, and key concepts.
   
   Copyright © Aman Kumar Pandey 2026–2027. All rights reserved.
   """

**Function and Method Docstrings**

Use Google-style docstrings (supported by Sphinx):

.. code-block:: python

   def recognize_speech(timeout: int = 10) -> str:
       """
       Capture and convert speech to text.
       
       Uses the configured speech recognition engine to listen
       for user input and convert it to text.
       
       Args:
           timeout: Maximum seconds to listen. Default is 10.
       
       Returns:
           Recognized text string.
       
       Raises:
           TimeoutError: If no speech detected within timeout.
           AudioError: If audio device fails or is unavailable.
       
       Example:
           >>> text = recognize_speech(timeout=15)
           >>> print(f"You said: {text}")
       """
       pass

**Class Docstrings**

.. code-block:: python

   class AssistantManager:
       """
       Central orchestrator for Vaani.
       
       Coordinates all system components including speech recognition,
       AI response generation, and audio playback.
       
       Attributes:
           speech_recognizer: Module for voice-to-text conversion.
           ai_engine: Module for response generation.
           tts_engine: Module for text-to-speech.
       """
       
       def __init__(self):
           """Initialize all system components."""
           pass

**Inline Comments**

Use sparingly and only to explain *why*, not *what*:

.. code-block:: python

   # Good - explains why
   # We limit memory to prevent unbounded growth during long sessions
   max_size = 100
   
   # Bad - just explains what
   # Set max_size to 100
   max_size = 100
   
   # Good - helps understand non-obvious code
   # Sort by timestamp, most recent first (for relevance in conversation)
   context = sorted(history, key=lambda x: x.timestamp, reverse=True)
   
   # Bad - obvious what it does
   # Loop through items
   for item in items:
       pass

Error Handling
--------------

**Use Specific Exceptions**

.. code-block:: python

   # Good
   try:
       result = process_audio(data)
   except AudioProcessingError as e:
       logger.error(f"Audio processing failed: {e}")
       return None
   
   # Bad - too broad
   try:
       result = process_audio(data)
   except Exception:  # Catches everything, even bugs
       pass
   
   # Bad - bare except
   try:
       result = process_audio(data)
   except:  # Don't do this
       pass

**Always Log Errors**

.. code-block:: python

   try:
       response = api_call()
   except APIError as e:
       logger.error(f"API call failed: {e}")
       # Then either recover or re-raise
       return fallback_response()

**Define Custom Exceptions**

.. code-block:: python

   class AudioProcessingError(Exception):
       """Raised when audio processing fails."""
       pass
   
   class ResponseGenerationError(Exception):
       """Raised when AI response generation fails."""
       pass

Testing and Verification
------------------------

**Check Code Quality**

.. code-block:: bash

   # Format with black
   black vaani_assistant/
   
   # Check style with flake8
   flake8 vaani_assistant/ --max-line-length=100
   
   # Check type hints
   mypy vaani_assistant/

**Test Modules Independently**

.. code-block:: bash

   python3 << 'EOF'
   from vaani_assistant.core.speech_recognition import recognize_speech
   
   try:
       text = recognize_speech(timeout=5)
       print(f"Success: {text}")
   except Exception as e:
       print(f"Error: {e}")
   EOF

**Enable Debug Logging**

.. code-block:: bash

   LOG_LEVEL=DEBUG python3 main.py

Common Patterns
---------------

**Singleton with Configuration**

.. code-block:: python

   _instance = None
   
   def get_ai_engine():
       global _instance
       if _instance is None:
           _instance = AIEngine()
       return _instance

**Graceful Degradation**

.. code-block:: python

   def generate_response(prompt):
       try:
           return gemini_response(prompt)
       except APIError:
           logger.warning("Gemini API failed, using fallback")
           return fallback_response(prompt)

**Context Management**

.. code-block:: python

   class AudioContext:
       def __enter__(self):
           self.device = open_audio_device()
           return self.device
       
       def __exit__(self, exc_type, exc_val, exc_tb):
           self.device.close()
   
   # Usage
   with AudioContext() as device:
       data = device.read()

Things to Avoid
---------------

**No Magic Numbers**

.. code-block:: python

   # Bad - what does 2048 mean?
   buffer_size = 2048
   
   # Good
   AUDIO_BUFFER_SIZE = 2048  # Samples for 50ms at 44kHz

**No Deep Nesting**

.. code-block:: python

   # Bad - hard to follow
   if condition1:
       if condition2:
           if condition3:
               do_something()
   
   # Good - early returns
   if not condition1:
       return
   if not condition2:
       return
   if not condition3:
       return
   do_something()

**No Unused Variables**

.. code-block:: python

   # Bad
   for user_input in inputs:
       process(inputs[0])  # Wrong!
   
   # Good
   for user_input in inputs:
       process(user_input)

**No Global State**

.. code-block:: python

   # Bad - global mutable state
   _data = []
   
   def add_data(item):
       _data.append(item)
   
   # Good - encapsulated
   class DataStore:
       def __init__(self):
           self._data = []
       
       def add(self, item):
           self._data.append(item)

**No Hardcoded Paths**

.. code-block:: python

   # Bad
   config = open("/home/user/vaani/config.txt")
   
   # Good
   config_path = os.path.join(os.path.expanduser("~"), ".vaani", "config.txt")
   config = open(config_path)

**No Hardcoded Configuration**

.. code-block:: python

   # Bad
   RESPONSE_TIMEOUT = 30
   
   # Good
   RESPONSE_TIMEOUT = settings.config.get("RESPONSE_TIMEOUT", 30)

Specific Guidelines
-------------------

**Logging**

.. code-block:: python

   from ..utils.logger import logger
   
   # Appropriate logging levels
   logger.debug("Detailed diagnostic info")    # Development
   logger.info("General informational message") # User should see
   logger.warning("Something unexpected")       # User should investigate
   logger.error("An error occurred")            # System failed at something

**Configuration Access**

.. code-block:: python

   from ..config import settings
   
   # Always use config with defaults
   language = settings.config.get("VOICE_LANGUAGE", "en")
   api_key = settings.config.get("GEMINI_API_KEY")

**Response Generation**

.. code-block:: python

   # Always try graceful fallback
   def generate_response(prompt: str) -> str:
       try:
           response = primary_method(prompt)
       except Exception as e:
           logger.warning(f"Primary method failed: {e}")
           response = fallback_method(prompt)
       return response

**Audio Processing**

.. code-block:: python

   # Always specify sample rate and format
   def process_audio(
       data: bytes,
       sample_rate: int = 16000,
       channels: int = 1,
   ) -> Optional[str]:
       """Process audio data."""
       pass

Continuous Improvement
----------------------

Code quality is not static. When you see code that breaks these guidelines:

1. **Comment** - Add a note explaining why the current approach exists
2. **Document** - Update this guide if the situation is common
3. **Improve** - Refactor when you have time and can test thoroughly
4. **Review** - Have someone else review significant changes

The goal is a codebase that's pleasant to work with, not perfection.

Next Steps
----------

- See :doc:`contributing` for contribution process
- Read :doc:`../development/setup` for development environment
- Check :doc:`project_structure` for code organization
