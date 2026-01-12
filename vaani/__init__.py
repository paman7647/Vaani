"""
Vaani Voice Assistant - Main Package
====================================

An AI-powered voice assistant with offline capabilities.

Features:
- Multi-engine speech recognition (Google, Vosk, PocketSphinx)
- Natural language processing with Gemini AI
- Offline NLP for privacy and reliability
- Music streaming from YouTube
- Web search integration
- Multi-language translation
- Context-aware conversations
- Professional logging and error handling

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.

Main package for the Vaani voice assistant system.

"""

__version__ = "1.0.0"
__author__ = "Aman Kumar Pandey"

from .core.assistant import get_assistant

__all__ = ['get_assistant']
