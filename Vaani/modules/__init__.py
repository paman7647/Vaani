"""
Modules Package - Plugin Architecture
====================================

Extensible module system for custom plugins.

This package allows users to add custom modules and plugins
to extend Vaani's functionality without modifying core code.

Place your custom modules here to integrate with Vaani.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

from ..core.processor import get_processor

__all__ = ['get_processor']
