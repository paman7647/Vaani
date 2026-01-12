"""
Assistant Manager - Main Orchestrator
=====================================

Features:
- Context-aware listening (no wake word when idle, wake word during music/TTS)
- Thread management for voice listener and music monitor
- Lifecycle coordination between all components
- Professional startup with minimal logging
- Graceful shutdown and cleanup
- State management for wake word requirements

This is the central coordinator that brings together speech recognition,
TTS, music playback, and AI conversation into a unified assistant experience.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import time
import threading
from typing import Optional
from ..voice.speech_synthesis import get_voice_synth, speak
from ..voice.speech_recognition import get_system
from ..voice.audio_engine import get_audio_engine
from ..intelligence.conversation import get_conversation_manager
from .processor import get_processor
from ..intelligence.responses import responses
from ..config import settings
from ..config import settings
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler

logger = VaaniLogger.get_logger("Assistant Core")


class Assistant:
    """Main orchestrator - manages all components and handles the interaction loop"""
    
    def __init__(self):
        self.running = False
        self.voice = None
        self.mic = None
        self.audio_engine = None
        self.conversation = None
        self.commands = None
        
        # Threading
        self.wake_word_thread: Optional[threading.Thread] = None
        self.lifecycle_thread: Optional[threading.Thread] = None
    
    @error_handler(default_return=False)
    def initialize(self) -> bool:
        """Set up all components - returns True if successful, False otherwise"""
        try:
            if not settings.validate_config():
                logger.error("Configuration validation failed")
                return False
            
            self.voice = get_voice_synth()
            self.mic = get_system()
            self.audio_engine = get_audio_engine()
            self.conversation = get_conversation_manager()
            self.commands = get_processor()
            
            # Professional startup - no wake word needed
            print("\nVANI Voice Assistant Ready")
            print("Listening for commands...")
            print("Press Ctrl+C to exit\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    @error_handler(default_return=None)
    def start(self):
        """Main entry point - initializes and starts the listening loop"""
        if not self.initialize():
            logger.error("Failed to initialize assistant")
            return
        
        self.running = True
        
        # Start background threads
        self.wake_word_thread = threading.Thread(target=self._wake_word_listener, daemon=True)
        self.wake_word_thread.start()
        
        self.lifecycle_thread = threading.Thread(target=self._music_lifecycle, daemon=True)
        self.lifecycle_thread.start()
        
        # Keep main thread alive
        try:
            last_status = time.time()
            while self.running:
                time.sleep(1)
                
                last_status = time.time()
        
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
            self.shutdown()
    
    def _wake_word_listener(self):
        """Background thread listening with context-aware mode"""
        
        listening_count = 0
        last_speech_synthesizer_check = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check if we should allow interruption during TTS/music
                speech_synthesis_speaking = self.voice.is_speaking
                music_playing = self.audio_engine.is_playing if hasattr(self, 'player') else False
                
                # Allow listening even during TTS/music (for interruption)
                # But wait a bit after TTS starts to avoid capturing own voice
                if speech_synthesis_speaking and (current_time - last_speech_synthesizer_check) < 2.0:
                    time.sleep(0.2)
                    last_speech_synthesizer_check = current_time
                    continue
                
                if self.mic.is_listening():
                    time.sleep(0.2)
                    continue
                
                # CONTEXT-AWARE LISTENING MODE:
                # - If music playing OR TTS speaking: require wake word "Hey Vani"
                # - If idle (no music, no TTS): directly respond to any speech
                
                # Get TTS engine reference
                advanced_speech_synthesizer = self.commands.speech_synthesis_engine
                
                # Check if enough time has passed since last speech
                time_since_speech = current_time - advanced_speech_synthesizer.last_speech_end_time
                
                # If TTS just finished speaking, wait 2.5 seconds before direct listening
                # This prevents hearing tail end of TTS or acoustic echo
                if advanced_speech_synthesizer.is_speaking or time_since_speech < 2.5:
                    time.sleep(0.3)
                    continue
                
                music_playing = self.audio_engine.is_playing if self.audio_engine else False
                requires_wake_word = music_playing
                
                if requires_wake_word:
                    # Music playing OR TTS speaking - require wake word
                    wake_detected, inline_command = self.mic.listen_wake(timeout=8.0)
                    
                    if wake_detected:
                        if speech_synthesis_speaking:
                            self.voice.stop_speaking()
                        print("\nWake word detected!")
                        
                        # Quick acknowledgment beep (non-blocking)
                        import os
                        os.system('afplay /System/Library/Sounds/Tink.aiff &> /dev/null &')
                        
                        last_speech_synthesizer_check = current_time
                        
                        if inline_command:
                            result = self.commands.process_command(inline_command)
                            
                            if result == "EXIT":
                                self.running = False
                                break
                        else:
                            # Acknowledge naturally and wait for command
                            speak(responses.wake_acknowledgment(), blocking=True)
                            
                            # Listen for command
                            command = self.mic.listen_command(timeout=8.0)
                            
                            if command:
                                result = self.commands.process_command(command)
                                
                                if result == "EXIT":
                                    self.running = False
                                    break
                            else:
                                speak(responses.unclear_speech())
                else:
                    # No music - direct response mode
                    command = self.mic.listen_general(timeout=30.0)
                    
                    if command:
                        print(f"\nHeard: {command}")
                        
                        # Quick acknowledgment beep
                        import os
                        os.system('afplay /System/Library/Sounds/Tink.aiff &> /dev/null &')
                        
                        # Process command directly
                        result = self.commands.process_command(command)
                        
                        # Update TTS check time AFTER command processing completes
                        last_speech_synthesizer_check = time.time()
                        
                        if result == "EXIT":
                            self.running = False
                            break
                
                # Longer delay before listening again to prevent loop spam
                time.sleep(1.0)
            
            except Exception as e:
                logger.error(f"Wake word listener error: {e}")
                time.sleep(1)
        
        pass
    
    def _music_lifecycle(self):
        """Background thread managing music playback"""
        
        while self.running:
            try:
                status = self.audio_engine.get_status()
                
                # Check if music ended and queue has more songs
                if status['is_playing'] and self.audio_engine.audio_engine_type == 'vlc':
                    if self.audio_engine.audio_engine:
                        import vlc # type: ignore
                        state = self.audio_engine.audio_engine.get_state()
                        
                        if state == vlc.State.Ended:
                            logger.info("Song ended, checking queue...")
                            
                            if status['queue_length'] > 0:
                                logger.info("Playing next song from queue")
                                self.audio_engine.play_next()
                            else:
                                logger.info("Queue empty, stopping playback")
                                self.audio_engine.stop()
                
                time.sleep(settings.MUSIC_MONITOR_INTERVAL)
            
            except Exception as e:
                logger.error(f"Music lifecycle error: {e}")
                time.sleep(2)

    
    @error_handler(default_return=None)
    def shutdown(self):
        """Shutdown the assistant"""
        logger.info("Shutting down Vaani...")
        
        self.running = False
        
        # Stop audio
        if self.audio_engine:
            self.audio_engine.shutdown()
        
        # Shutdown TTS
        if self.voice:
            speak(responses.goodbye(), blocking=True)
            self.voice.shutdown()
        
        logger.info("Vaani has shut down completely")


# Global assistant manager
_assistant: Optional[Assistant] = None

def get_assistant() -> Assistant:
    """Get or create global assistant manager instance"""
    global _assistant
    if _assistant is None:
        _assistant = Assistant()
    return _assistant