core
====

Core functionality modules for Vaani.

.. autosummary::
   :toctree: core
   :template: autosummary/module.rst

   vaani_assistant.core.assistant_manager
   vaani_assistant.core.command_processor
   vaani_assistant.core.watchdog

Core Modules Overview
---------------------

Assistant Manager
^^^^^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.assistant_manager
   :members:
   :undoc-members:
   :show-inheritance:

The central orchestrator that coordinates all system components.

Command Processor
^^^^^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.command_processor
   :members:
   :undoc-members:
   :show-inheritance:

Routes and processes user commands.

Watchdog
^^^^^^^^

.. automodule:: vaani_assistant.core.watchdog
   :members:
   :undoc-members:
   :show-inheritance:

Discovers and manages music from various sources.

Memory System
^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.memory
   :members:
   :undoc-members:
   :show-inheritance:

Maintains conversation history and context.

Command Router
^^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.command_router
   :members:
   :undoc-members:
   :show-inheritance:

Routes user requests to appropriate handlers.

Intent Classification
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.smart_intent_classifier
   :members:
   :undoc-members:
   :show-inheritance:

Analyzes user input to determine intent.

Personality System
^^^^^^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.personality
   :members:
   :undoc-members:
   :show-inheritance:

Customizable response style and tone.

Web Search
^^^^^^^^^^

.. automodule:: vaani_assistant.core.web_search
   :members:
   :undoc-members:
   :show-inheritance:

Real-time web search integration.

Wake Word Detector
^^^^^^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.wake_word_detector
   :members:
   :undoc-members:
   :show-inheritance:

Detects wake words to activate the assistant.

System Watchdog
^^^^^^^^^^^^^^^

.. automodule:: vaani_assistant.core.watchdog
   :members:
   :undoc-members:
   :show-inheritance:

Monitors system health and handles errors.

See Also
--------

- :doc:`../architecture` - System architecture overview
- :doc:`../voice_system` - Voice and audio details
- :doc:`../intelligence` - AI engine specifics
