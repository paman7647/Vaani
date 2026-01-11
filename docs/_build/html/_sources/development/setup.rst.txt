Development Setup
=================

This guide covers setting up Vaani for development and contribution.

Prerequisites
-------------

- Python 3.10 or higher
- git (for version control)
- Familiarity with Python and command line basics
- Text editor or IDE (VS Code, PyCharm, vim, etc.)

Development Environment
-----------------------

**Clone the repository**

.. code-block:: bash

   git clone https://github.com/paman7647/Vaani.git
   cd Vaani

**Create a development virtual environment** (recommended)

.. code-block:: bash

   python3 -m venv venv-dev
   source venv-dev/bin/activate  # On Windows: venv-dev\Scripts\activate

**Install development dependencies**

.. code-block:: bash

   # Install core dependencies
   pip install -r requirements-basic.txt
   
   # Install optional development tools
   pip install -r requirements-full.txt
   
   # Install development extras (if available)
   pip install sphinx sphinx-rtd-theme pytest black flake8

**Test the installation**

.. code-block:: bash

   python3 main.py

You should hear startup messages and be ready to interact with Vaani.

Project Structure for Developers
--------------------------------

::

   vaani/
   ├── .gitignore                 # Git configuration
   ├── .env.example               # Config template
   ├── README.md                  # Main readme
   ├── main.py                    # Entry point
   ├── install_vaani.sh           # Installation script
   ├── requirements*.txt          # Dependencies
   ├── docs/                      # Documentation (Sphinx)
   ├── vaani_assistant/           # Main package
   │   ├── __init__.py
   │   ├── config/                # Configuration
   │   │   ├── global_config.py   # Constants
   │   │   └── settings.py        # Runtime settings
   │   ├── core/                  # Core functionality
   │   │   ├── assistant_manager.py
   │   │   ├── ai_engine.py
   │   │   ├── speech_recognition.py
   │   │   ├── tts_engine.py
   │   │   ├── audio_player.py
   │   │   ├── music_manager.py
   │   │   ├── memory.py
   │   │   ├── command_router.py
   │   │   └── ...
   │   ├── modules/               # Specialized features
   │   │   └── command_processor.py
   │   └── utils/                 # Utilities
   │       └── logger.py
   └── venv-dev/                  # Development virtual env

Common Development Tasks
------------------------

**Running Vaani**

Standard:

.. code-block:: bash

   python3 main.py

With verbose logging:

.. code-block:: bash

   LOG_LEVEL=DEBUG python3 main.py

With custom voice:

.. code-block:: bash

   VOICE_LANGUAGE=es python3 main.py

**Testing a specific module**

.. code-block:: bash

   # Test speech recognition
   python3 -m speech_recognition
   
   # Test imports
   python3 -c "from vaani_assistant import get_assistant_manager; print('OK')"

**Examining logs**

.. code-block:: bash

   tail -f vaani.log

**Adding a new dependency**

.. code-block:: bash

   pip install package_name
   pip freeze > requirements-full.txt  # Update requirements

**Building documentation locally**

.. code-block:: bash

   cd docs
   make html
   open _build/html/index.html

Code Organization
------------------

**Module Layout**

Each module in ``vaani_assistant/core/`` follows this pattern:

.. code-block:: python

   """
   Module docstring explaining purpose and usage.
   
   Copyright © Aman Kumar Pandey 2026–2027. All rights reserved.
   """
   
   import dependencies
   from ..config import settings
   from ..utils.logger import logger
   
   class MainClass:
       """Class docstring."""
       
       def __init__(self):
           """Initialize with configuration."""
           pass
       
       def main_method(self):
           """Method docstring."""
           pass
   
   def get_module_instance():
       """Factory function for singleton pattern."""
       return MainClass()

**Naming Conventions**

- Classes: ``PascalCase`` (e.g., ``AssistantManager``)
- Functions: ``snake_case`` (e.g., ``get_audio_player``)
- Constants: ``UPPER_SNAKE_CASE`` (e.g., ``RESPONSE_TIMEOUT``)
- Private methods: ``_leading_underscore`` (e.g., ``_process_audio``)

**Documentation**

All functions and classes should have docstrings:

.. code-block:: python

   def recognize_speech(timeout: int = 10) -> str:
       """
       Capture and convert speech to text.
       
       Args:
           timeout: Maximum seconds to listen (default: 10)
       
       Returns:
           Recognized text string
       
       Raises:
           TimeoutError: If no speech detected within timeout
           AudioException: If audio device fails
       
       Example:
           >>> text = recognize_speech(timeout=15)
           >>> print(text)
       """
       pass

**Error Handling**

Use specific exceptions, not bare ``except``:

.. code-block:: python

   # Good
   try:
       result = process_audio(data)
   except AudioProcessingError as e:
       logger.error(f"Audio failed: {e}")
       return None
   
   # Avoid
   try:
       result = process_audio(data)
   except:  # Too broad
       pass

Making Changes
--------------

**Before making changes**

1. Create a branch for your work

.. code-block:: bash

   git checkout -b feature/my-feature

2. Make your changes
3. Test thoroughly
4. Check code quality

**Code style**

Use ``black`` for consistent formatting:

.. code-block:: bash

   black vaani_assistant/

Check for issues with ``flake8``:

.. code-block:: bash

   flake8 vaani_assistant/ --max-line-length=100

**After making changes**

1. Update documentation if needed
2. Update tests if applicable
3. Commit with clear messages

.. code-block:: bash

   git add .
   git commit -m "Add feature: clear description of changes"

4. Push your branch

.. code-block:: bash

   git push origin feature/my-feature

5. Create a pull request on GitHub

Testing Your Code
-----------------

**Manual testing**

.. code-block:: bash

   # Start Vaani and interact with it manually
   python3 main.py

**Check specific functionality**

.. code-block:: bash

   # Test speech recognition
   python3 -c "from vaani_assistant.core.speech_recognition import recognize_speech; print(recognize_speech())"
   
   # Test TTS
   python3 -c "from vaani_assistant.core.tts_engine import speak; speak('Hello world')"

**Check imports**

.. code-block:: bash

   python3 -c "from vaani_assistant import get_assistant_manager; print('Imports OK')"

Debugging Tips
--------------

**Enable debug logging**

.. code-block:: bash

   export LOG_LEVEL=DEBUG
   python3 main.py

Watch the log output for detailed information about what's happening.

**Check configuration**

.. code-block:: bash

   python3 << 'EOF'
   from vaani_assistant.config import settings
   print("Current settings:")
   for key, value in settings.config.items():
       if "key" not in key.lower():
           print(f"  {key}: {value}")
   EOF

**Debug specific module**

.. code-block:: python

   # Add to your code temporarily
   from vaani_assistant.utils.logger import logger
   
   logger.debug(f"Variable state: {variable}")
   logger.debug(f"Function input: {input_data}")

**Performance profiling**

.. code-block:: bash

   python3 -m cProfile -s cumulative main.py

Shows which functions take the most time.

Common Pitfalls
---------------

**Forgetting to activate the virtual environment**

.. code-block:: bash

   # Wrong - uses system Python
   python3 main.py
   
   # Right - uses venv Python
   source venv-dev/bin/activate
   python3 main.py

**Not updating requirements.txt after adding dependencies**

.. code-block:: bash

   pip install new_package
   pip freeze > requirements-full.txt  # Always update!

**Hardcoding paths or configuration**

.. code-block:: python

   # Bad
   api_key = "abc123xyz"
   voice = "en-US-VaaniNeural"
   
   # Good
   from vaani_assistant.config import settings
   api_key = settings.config.get("GEMINI_API_KEY")
   voice = settings.config.get("VOICE_NAME")

**Not checking for exceptions**

.. code-block:: python

   # Bad
   result = process_input(data)  # What if it fails?
   
   # Good
   try:
       result = process_input(data)
   except ProcessingError as e:
       logger.error(f"Processing failed: {e}")
       return None

Getting Help
-------------

- Check existing issues on GitHub
- Review :doc:`../troubleshooting` for common issues
- Look at similar modules for patterns
- Ask in discussions or documentation

Next Steps
----------

- Read :doc:`project_structure` for detailed code walkthrough
- Check :doc:`coding_style` for conventions
- See :doc:`contributing` for contribution guidelines
