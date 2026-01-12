Coding Style Guide
==================

This document outlines the coding standards and best practices for contributing to the Vaani Assistant project.

Python Style Guide
------------------

**General Principles**

Follow PEP 8 with these specific conventions:

- **Line Length**: Maximum 100 characters (slightly longer than PEP 8's 79)
- **Indentation**: 4 spaces (never tabs)
- **Encoding**: UTF-8 for all Python files
- **Quotes**: Double quotes for strings, single quotes for dict keys

Naming Conventions
------------------

**Classes**

Use PascalCase for class names:

.. code-block:: python

   class SpeechRecognizer:
       pass
   
   class IntentAnalyzer:
       pass
   
   class AudioEngine:
       pass

**Functions and Methods**

Use snake_case for functions and methods:

.. code-block:: python

   def process_audio_input():
       pass
   
   def classify_intent(text):
       pass
   
   def synthesize_speech(text, language="en"):
       pass

**Variables**

Use snake_case for variables:

.. code-block:: python

   user_input = ""
   audio_buffer = []
   is_listening = True
   max_retries = 3

**Constants**

Use UPPER_SNAKE_CASE for constants:

.. code-block:: python

   DEFAULT_LANGUAGE = "en"
   MAX_MEMORY_SIZE = 100
   WAKE_WORD_THRESHOLD = 85
   AUDIO_SAMPLE_RATE = 16000

**Private Members**

Use leading underscore for private/internal members:

.. code-block:: python

   class AudioEngine:
       def __init__(self):
           self._audio_stream = None
           self._is_recording = False
       
       def _initialize_stream(self):
           # Private method
           pass

Documentation Standards
-----------------------

**Module Docstrings**

Every module should have a docstring at the top:

.. code-block:: python

   """Speech recognition module for Vaani Assistant.
   
   This module provides multi-engine speech recognition with automatic
   fallback between Google API, Vosk, and Sphinx engines.
   
   Example:
       >>> recognizer = SpeechRecognizer()
       >>> text = recognizer.recognize(audio_data)
       >>> print(text)
       'hello world'
   
   Attributes:
       DEFAULT_ENGINE (str): Primary recognition engine to use
       FALLBACK_ENGINES (list): List of fallback engines
   """

**Class Docstrings**

Document the purpose, attributes, and usage:

.. code-block:: python

   class SpeechRecognizer:
       """Multi-engine speech recognizer with automatic fallback.
       
       Attempts recognition with multiple engines in priority order,
       automatically falling back if an engine fails or is unavailable.
       
       Attributes:
           engines (list): List of available recognition engines
           current_engine (str): Currently active engine
           confidence_threshold (float): Minimum confidence for results
       
       Example:
           >>> recognizer = SpeechRecognizer()
           >>> with sr.Microphone() as source:
           ...     audio = recognizer.listen(source)
           ...     text = recognizer.recognize(audio)
           >>> print(text)
       """

**Function Docstrings**

Use Google-style docstrings:

.. code-block:: python

   def recognize_speech(audio_data, language="en-IN"):
       """Recognize speech from audio data.
       
       Attempts recognition with all available engines in priority order.
       Returns the result from the first successful engine.
       
       Args:
           audio_data (AudioData): Audio data to recognize
           language (str, optional): Language code for recognition.
               Defaults to "en-IN".
       
       Returns:
           str: Recognized text from audio
       
       Raises:
           RecognitionError: If all engines fail to recognize
           ValueError: If audio_data is invalid or empty
       
       Example:
           >>> audio = record_audio()
           >>> text = recognize_speech(audio, language="hi-IN")
           >>> print(text)
           'नमस्ते'
       """

Code Organization
-----------------

**Import Order**

Organize imports in three groups, separated by blank lines:

1. Standard library imports
2. Third-party library imports
3. Local application imports

.. code-block:: python

   # Standard library
   import os
   import sys
   from pathlib import Path
   from typing import List, Optional, Dict
   
   # Third-party
   import speech_recognition as sr
   from rapidfuzz import fuzz
   import google.generativeai as genai
   
   # Local
   from vaani_assistant.config import global_config
   from vaani_assistant.utils.logger import get_logger

**File Structure**

Organize each module consistently:

.. code-block:: python

   """Module docstring."""
   
   # Imports
   import os
   import sys
   
   # Constants
   DEFAULT_TIMEOUT = 5
   MAX_RETRIES = 3
   
   # Module-level variables (if needed)
   _logger = get_logger(__name__)
   
   # Classes
   class MyClass:
       pass
   
   # Functions
   def my_function():
       pass
   
   # Main execution (if applicable)
   if __name__ == "__main__":
       main()

Type Hints
----------

Use type hints for function parameters and return values:

.. code-block:: python

   from typing import List, Optional, Dict, Tuple
   
   def process_command(
       command: str,
       context: Optional[Dict[str, any]] = None
   ) -> Tuple[str, bool]:
       """Process user command with optional context.
       
       Args:
           command: User's command text
           context: Optional conversation context
       
       Returns:
           Tuple of (response text, success boolean)
       """
       # Implementation
       return response, True
   
   def get_conversation_history(
       limit: int = 10
   ) -> List[Dict[str, str]]:
       """Get recent conversation history.
       
       Args:
           limit: Maximum number of exchanges to return
       
       Returns:
           List of conversation exchanges
       """
       return history[:limit]

Error Handling
--------------

**Use Specific Exceptions**

Catch specific exceptions rather than bare except:

.. code-block:: python

   # Good
   try:
       result = recognize_speech(audio)
   except sr.UnknownValueError:
       logger.warning("Speech not recognized")
       result = None
   except sr.RequestError as e:
       logger.error(f"API error: {e}")
       result = None
   
   # Bad
   try:
       result = recognize_speech(audio)
   except:  # Too broad
       result = None

**Custom Exceptions**

Create custom exceptions for domain-specific errors:

.. code-block:: python

   class VaaniException(Exception):
       """Base exception for Vaani errors."""
       pass
   
   class RecognitionError(VaaniException):
       """Speech recognition failed."""
       pass
   
   class IntentClassificationError(VaaniException):
       """Failed to classify user intent."""
       pass
   
   # Usage
   if not text:
       raise RecognitionError("No speech detected in audio")

**Logging Errors**

Always log exceptions with context:

.. code-block:: python

   try:
       result = process_command(command)
   except Exception as e:
       logger.error(
           f"Failed to process command: {command}",
           exc_info=True  # Include stack trace
       )
       raise

Logging Standards
-----------------

**Log Levels**

Use appropriate log levels:

.. code-block:: python

   # DEBUG: Detailed diagnostic information
   logger.debug(f"Raw audio data: {len(audio_data)} bytes")
   
   # INFO: General informational messages
   logger.info("Speech recognition completed successfully")
   
   # WARNING: Potentially problematic situations
   logger.warning("Using fallback engine, primary unavailable")
   
   # ERROR: Error events that might still allow app to continue
   logger.error(f"Failed to connect to API: {error}")
   
   # CRITICAL: Serious errors causing application failure
   logger.critical("Audio device not found, cannot continue")

**Structured Logging**

Include context in log messages:

.. code-block:: python

   logger.info(
       "Speech recognized",
       extra={
           "engine": "google",
           "language": "en-IN",
           "confidence": 0.95,
           "duration_ms": 234
       }
   )

Testing Standards
-----------------

**Unit Tests**

Write unit tests for all public functions:

.. code-block:: python

   import unittest
   from unittest.mock import Mock, patch
   
   class TestSpeechRecognizer(unittest.TestCase):
       """Tests for SpeechRecognizer class."""
       
       def setUp(self):
           """Set up test fixtures."""
           self.recognizer = SpeechRecognizer()
       
       def test_recognize_with_google_api(self):
           """Test speech recognition with Google API."""
           audio = Mock()
           result = self.recognizer.recognize(audio, engine="google")
           self.assertIsInstance(result, str)
           self.assertTrue(len(result) > 0)
       
       def test_fallback_to_vosk(self):
           """Test fallback to Vosk when Google fails."""
           with patch.object(
               self.recognizer,
               '_recognize_google',
               side_effect=Exception("API unavailable")
           ):
               audio = Mock()
               result = self.recognizer.recognize(audio)
               self.assertIsInstance(result, str)
       
       def tearDown(self):
           """Clean up after tests."""
           self.recognizer.cleanup()

**Test Coverage**

Aim for at least 80% code coverage:

.. code-block:: bash

   # Run tests with coverage
   pytest --cov=vaani_assistant --cov-report=html tests/
   
   # View coverage report
   open htmlcov/index.html

Code Comments
-------------

**When to Comment**

- **Why, not what**: Explain the reasoning, not obvious code
- **Complex logic**: Clarify non-obvious algorithms
- **Workarounds**: Explain temporary fixes or hacks
- **TODO/FIXME**: Mark areas needing improvement

.. code-block:: python

   # Good: Explains why
   # Use fuzzy matching to handle pronunciation variations
   # and microphone quality issues
   score = fuzz.ratio(wake_word, heard_text)
   
   # Bad: Explains obvious code
   # Increment counter by 1
   counter += 1
   
   # Good: Explains complex logic
   # Calculate exponential backoff with jitter to prevent
   # thundering herd when API comes back online
   delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
   
   # TODO marker
   # TODO: Implement voice profile support for multi-user scenarios
   # FIXME: Memory leak in audio buffer when running >24 hours

**Docstring vs Comments**

- Use **docstrings** for API documentation (public interfaces)
- Use **comments** for implementation details (private code)

Performance Guidelines
----------------------

**Avoid Premature Optimization**

Write clear code first, optimize if needed:

.. code-block:: python

   # Good: Clear and readable
   def is_wake_word(text):
       return any(
           fuzz.ratio(text.lower(), word) >= threshold
           for word in wake_words
       )
   
   # Premature optimization (only if profiling shows it's needed)
   def is_wake_word_optimized(text):
       text_lower = text.lower()
       text_bytes = text_lower.encode()
       # Complex optimized matching logic...

**Profile Before Optimizing**

Use profiling to find bottlenecks:

.. code-block:: python

   import cProfile
   import pstats
   
   profiler = cProfile.Profile()
   profiler.enable()
   
   # Code to profile
   result = process_audio_stream()
   
   profiler.disable()
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative')
   stats.print_stats(20)  # Top 20 functions

**Caching**

Cache expensive operations:

.. code-block:: python

   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_language_config(language_code: str) -> Dict:
       """Get language configuration (cached).
       
       Configurations are cached to avoid repeated file I/O
       and parsing operations.
       """
       config_path = Path(f"config/languages/{language_code}.json")
       return json.loads(config_path.read_text())

Security Considerations
-----------------------

**API Keys**

Never hardcode API keys:

.. code-block:: python

   # Bad
   API_KEY = "AIzaSyB1234567890abcdef"
   
   # Good
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   API_KEY = os.getenv("GEMINI_API_KEY")
   
   if not API_KEY:
       raise ValueError("GEMINI_API_KEY not set in environment")

**User Input Validation**

Always validate and sanitize user input:

.. code-block:: python

   def play_music(query: str):
       """Play music from query.
       
       Args:
           query: User's music request
       """
       # Sanitize input
       query = query.strip()[:200]  # Limit length
       
       # Validate
       if not query:
           raise ValueError("Empty music query")
       
       # Remove potentially dangerous characters for shell
       safe_query = re.sub(r'[;&|`$]', '', query)
       
       # Process with sanitized input
       play_from_youtube(safe_query)

**File Operations**

Use Path objects and validate paths:

.. code-block:: python

   from pathlib import Path
   
   def save_audio_file(filename: str, data: bytes):
       """Save audio file safely.
       
       Args:
           filename: Name of file to save
           data: Audio data bytes
       """
       # Validate filename
       safe_name = Path(filename).name  # Remove directory traversal
       
       # Restrict to specific directory
       base_dir = Path("audio_cache")
       file_path = base_dir / safe_name
       
       # Ensure path is within base directory
       if not file_path.resolve().is_relative_to(base_dir.resolve()):
           raise ValueError("Invalid filename")
       
       # Safe to write
       file_path.write_bytes(data)

Git Commit Guidelines
---------------------

**Commit Message Format**

.. code-block:: text

   <type>(<scope>): <subject>
   
   <body>
   
   <footer>

**Types**

- ``feat``: New feature
- ``fix``: Bug fix
- ``docs``: Documentation changes
- ``style``: Code style changes (formatting, etc.)
- ``refactor``: Code refactoring
- ``test``: Adding or updating tests
- ``chore``: Maintenance tasks

**Examples**

.. code-block:: text

   feat(speech): Add Vosk offline recognition support
   
   Implement Vosk as fallback engine when Google API is unavailable.
   Includes automatic model downloading and caching.
   
   Fixes #42
   
   ---
   
   fix(audio): Resolve memory leak in audio buffer
   
   Audio buffers were not being properly cleared after processing,
   causing memory usage to grow over time.
   
   ---
   
   docs(installation): Add Raspberry Pi setup instructions
   
   Add detailed steps for installing on Raspberry Pi 4, including
   model selection and performance optimization tips.

Code Review Checklist
---------------------

Before submitting a pull request, verify:

**Functionality**

- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error conditions tested

**Code Quality**

- [ ] Follows style guide
- [ ] Well-documented with docstrings
- [ ] Type hints added
- [ ] No unused imports or variables
- [ ] No debugging print statements

**Testing**

- [ ] Unit tests written
- [ ] Tests pass locally
- [ ] Coverage maintained or improved

**Security**

- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities (if applicable)

**Performance**

- [ ] No obvious performance issues
- [ ] Memory leaks checked
- [ ] Large operations optimized

**Documentation**

- [ ] README updated if needed
- [ ] Docstrings complete
- [ ] Comments explain non-obvious code

Tools and Automation
--------------------

**Code Formatting**

Use Black for automatic formatting:

.. code-block:: bash

   # Install
   pip install black
   
   # Format all files
   black vaani_assistant/
   
   # Check without modifying
   black --check vaani_assistant/

**Linting**

Use Flake8 for style checking:

.. code-block:: bash

   # Install
   pip install flake8
   
   # Run linter
   flake8 vaani_assistant/
   
   # With configuration
   flake8 --max-line-length=100 --ignore=E203,W503 vaani_assistant/

**Type Checking**

Use mypy for static type checking:

.. code-block:: bash

   # Install
   pip install mypy
   
   # Check types
   mypy vaani_assistant/
   
   # With strict mode
   mypy --strict vaani_assistant/

**Pre-commit Hooks**

Set up pre-commit hooks to automate checks:

.. code-block:: bash

   # Install pre-commit
   pip install pre-commit
   
   # Install hooks
   pre-commit install
   
   # Run manually
   pre-commit run --all-files

Create ``.pre-commit-config.yaml``:

.. code-block:: yaml

   repos:
     - repo: https://github.com/psf/black
       rev: 23.0.0
       hooks:
         - id: black
           language_version: python3.11
     
     - repo: https://github.com/pycqa/flake8
       rev: 6.0.0
       hooks:
         - id: flake8
           args: ['--max-line-length=100']
     
     - repo: https://github.com/pre-commit/mirrors-mypy
       rev: v1.0.0
       hooks:
         - id: mypy
           additional_dependencies: [types-all]
