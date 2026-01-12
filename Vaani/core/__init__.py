"""
Core Module - Central System Components
======================================

Core orchestration components for Vaani.

Components:
- Assistant: Main coordinator and event loop manager
- Processor: Command routing and intent handling
- Lifecycle: System startup and shutdown management

This module contains the central components that coordinate
all other parts of the system into a unified assistant.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""


from ..voice.speech_synthesis import get_voice_synth, speak
from ..voice.speech_recognition import get_system
from ..voice.audio_engine import get_audio_engine
from ..intelligence.conversation import get_conversation_manager
from .assistant import get_assistant

__all__ = [
    'get_voice_synth',
    'speak',
    'get_system',
    'get_audio_engine',
    'get_conversation_manager',
    'get_assistant'
]
