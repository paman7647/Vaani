utils
=====

Utility modules and shared functions for Vaani.

.. autosummary::
   :toctree: utils
   :template: autosummary/module.rst

   vaani_assistant.utils.logger

Logger
^^^^^^

.. automodule:: vaani_assistant.utils.logger
   :members:
   :undoc-members:
   :show-inheritance:

The logger provides consistent logging across all Vaani modules. It's configured through the ``LOG_LEVEL`` environment variable and writes to both console and log files.

Usage:

.. code-block:: python

   from vaani_assistant.utils.logger import logger
   
   logger.info("Vaani started")
   logger.debug("Debug information")
   logger.warning("Something unusual happened")
   logger.error("An error occurred")

See Also
--------

- :doc:`../development/setup` - Development setup
- :doc:`core` - Core modules
