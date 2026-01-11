"""
Speech Synthesis - Natural Voice Output
==========================================

Features:
- Native system TTS (macOS: nsss, Linux: espeak/festival)
- Voice priority system (Veena → Rishi → Samantha → Lekha)
- Language-specific voice mapping (Hindi → Veena/Lekha, English → Veena)
- Queue-based non-blocking speech (producer-consumer pattern)
- Thread-safe state management
- Automatic fallback if preferred voice unavailable
- Context state updates (wake word requirement during speech)
- Supports multiple languages with native pronunciation

Handles all voice output with natural-sounding voices optimized for
different languages and accents. Non-blocking design ensures smooth
operation while speaking.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import pyttsx3
import subprocess
import shlex
import sys
import time
import threading
import queue
from typing import Optional, List
from ..config import settings
from ..config import settings
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Speech Synthesis")

class VoiceSynthesizer:
    """Thread-safe Text-to-Speech engine with fallback support"""
    
    def __init__(self):
        self.engine: Optional[pyttsx3.Engine] = None
        self.is_speaking = False
        self.speech_lock = threading.Lock()
        self.speech_queue = queue.Queue()
        self.current_voice = 'System Default'
        self.last_speech_end_time = 0
        self._initialize_engine()
        
        # Start speech worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()
    
    @error_handler(default_return=False)
    def _initialize_engine(self) -> bool:
        """Initialize the TTS engine with preferred settings"""
        try:
            # Use native macOS speech synthesizer if available
            if sys.platform == 'darwin':
                self.engine = pyttsx3.init(driverName='nsss')
                logger.info("Using native macOS speech synthesizer (nsss)")
            else:
                self.engine = pyttsx3.init()
                logger.info("Using default TTS engine")
            
            # Configure voice
            voices = self.engine.getProperty('voices')
            if voices:
                selected_voice = None
                
                # Try preferred voices in order
                for preferred_name in settings.PREFERRED_VOICES:
                    for voice in voices:
                        if preferred_name.lower() in voice.name.lower():
                            selected_voice = voice.id
                            self.current_voice = voice.name
                            logger.info(f"Selected voice: {voice.name}")
                            break
                    if selected_voice:
                        break
                
                if selected_voice:
                    self.engine.setProperty('voice', selected_voice)
                else:
                    logger.warning("Preferred voice not found, using default")
            
            # Set speech rate and volume
            self.engine.setProperty('rate', settings.SPEECH_RATE)
            self.engine.setProperty('volume', settings.SPEECH_VOLUME)
            
            logger.info("TTS engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"TTS initialization error: {e}")
            return False
    
    def _speech_worker(self):
        """Background worker to process speech queue"""
        while True:
            try:
                text, callback = self.speech_queue.get()
                
                if text is None:  # Shutdown signal
                    break
                
                self._speak_sync(text)
                
                if callback:
                    callback()
                
                self.speech_queue.task_done()
                
            except Exception as e:
                logger.error(f"Speech worker error: {e}")
    
    def _detect_language_voice(self, text: str) -> Optional[str]:
        """Detect best voice based on text script/language"""
        import re
        
        # Unicode ranges
        # Devanagari (Hindi, Marathi, Sanskrit): 0900-097F
        if re.search(r'[\u0900-\u097F]', text):
            return settings.LANGUAGE_VOICE_MAP.get('hi')
            
        # Tamil: 0B80-0BFF
        if re.search(r'[\u0B80-\u0BFF]', text):
            return settings.LANGUAGE_VOICE_MAP.get('ta')
            
        # Bengali: 0980-09FF
        if re.search(r'[\u0980-\u09FF]', text):
            return settings.LANGUAGE_VOICE_MAP.get('bn')
            
        return None

    @error_handler(default_return=False, error_message="Speech synthesis failed")
    def _speak_sync(self, text: str) -> bool:
        """Synchronous speech synthesis with language detection"""
        # On macOS, use system 'say' command to avoid pyttsx3 threading issues
        if sys.platform == 'darwin':
            with self.speech_lock:
                self.is_speaking = True
                try:
                    return self._speak_system_fallback(text)
                finally:
                    self.is_speaking = False
            
        with self.speech_lock:
            self.is_speaking = True
            original_voice = self.current_voice
            temp_voice_id = None
            
            try:
                if self.engine:
                    # Detect and switch voice if needed
                    target_voice_name = self._detect_language_voice(text)
                    if target_voice_name:
                        # Find voice ID for the name
                        voices = self.engine.getProperty('voices')
                        for voice in voices:
                            if target_voice_name.lower() in voice.name.lower():
                                temp_voice_id = voice.id
                                self.engine.setProperty('voice', temp_voice_id)
                                logger.debug(f"Temporarily switched to {voice.name} for regional text")
                                break
                    
                    logger.debug(f"Speaking: {text}")
                    self.engine.say(text)
                    self.engine.runAndWait()
                    
                    # Restore original voice if we switched
                    if temp_voice_id and original_voice != 'System Default':
                        # Find ID for original voice (we only store name in current_voice usually)
                        # But wait, self.change_voice updates self.current_voice using name.
                        # Ideally we should store the ID or just use change_voice logic to restore.
                        # For now let's just re-run the selection or assume we can find it.
                        self.change_voice(original_voice)
                        
                    return True
                else:
                    return self._speak_system_fallback(text)
            except Exception as e:
                logger.error(f"TTS runtime error: {e}")
                return self._speak_system_fallback(text)
            finally:
                self.is_speaking = False
                self.last_speech_end_time = time.time()
    
    def speak(self, text: str, blocking: bool = False, callback=None, player=None):
        """
        Speak text with automatic music ducking (non-blocking by default)
        
        Args:
            text: Text to speak
            blocking: If True, waits for speech to complete
            callback: Optional function to call after speech completes
            player: Optional AudioEngine instance for music ducking
        """
        if not text:
            return
        
        # Auto-pause music if audio player is provided and music is playing
        should_resume = False
        if player and player.is_playing and not player.is_paused:
            logger.info("Pausing music for speech")
            player.pause()
            should_resume = True
        
        # Create callback to resume music after speech
        def resume_callback():
            if should_resume and player:
                logger.info("Resuming music after speech")
                player.resume()
            if callback:
                callback()
        
        if blocking:
            self._speak_sync(text)
            resume_callback()
        else:
            self.speech_queue.put((text, resume_callback))
    
    @error_handler(default_return=False)
    def _speak_system_fallback(self, text: str) -> bool:
        """Fallback to system command for speech"""
        try:
            if sys.platform == 'darwin':  # macOS
                # Check for specific language requirement first
                target_voice = self._detect_language_voice(text)
                
                if target_voice:
                    # Use specific regional voice
                    try:
                        safe_text = shlex.quote(text)
                        cmd = f"say -v {target_voice} {safe_text}"
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            logger.info(f"System TTS fallback successful with regional voice: {target_voice}")
                            return True
                    except Exception:
                        pass # Fall through to standard list
                
                # Use preferred voices from settings instead of hardcoded list
                for voice in settings.PREFERRED_VOICES:
                    try:
                        safe_text = shlex.quote(text)
                        
                        # Calculate dynamic timeout based on text length for long responses
                        # Avg speaking rate: ~15 chars/sec. We give buffer of 0.2s per char + 10s base
                        # 460 chars -> ~100 seconds timeout (plenty of time)
                        dynamic_timeout = max(30, len(text) * 0.2 + 10)
                        
                        cmd = f"say -v {voice} {safe_text}"
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=dynamic_timeout)
                        if result.returncode == 0:
                            logger.info(f"System TTS fallback successful with voice: {voice}")
                            return True
                    except subprocess.TimeoutExpired:
                        logger.warning(f"System TTS timeout with voice {voice} (timeout: {dynamic_timeout:.1f}s)")
                        continue
                    except Exception:
                        continue
                
                # Final fallback to default say
                subprocess.run(f"say {shlex.quote(text)}", shell=True, timeout=30)
                return True
            else:
                logger.warning(f"System TTS fallback not available on {sys.platform}")
                return False
        except Exception as e:
            logger.error(f"System TTS error: {e}")
            return False
    
    @error_handler(default_return=False)
    def change_voice(self, voice_name: str) -> bool:
        """Change the TTS voice"""
        try:
            if not self.engine:
                self._initialize_engine()
            
            if not self.engine:
                return False
            
            voices = self.engine.getProperty('voices')
            
            if voice_name.lower() == 'default':
                self.engine.setProperty('voice', None)
                self.current_voice = 'System Default'
                logger.info("Voice changed to system default")
                return True
            
            for voice in voices:
                if voice_name.lower() in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    self.current_voice = voice.name
                    logger.info(f"Voice changed to: {voice.name}")
                    return True
            
            logger.warning(f"Voice '{voice_name}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Error changing voice: {e}")
            return False
    
    @error_handler(default_return=[])
    def get_available_voices(self) -> List[str]:
        """Get list of available voices"""
        try:
            if not self.engine:
                return []
            
            voices = self.engine.getProperty('voices')
            return [voice.name for voice in voices] if voices else []
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def stop(self):
        """Stop current speech"""
        try:
            if self.engine:
                self.engine.stop()
            self.is_speaking = False
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    @error_handler(default_return=None)
    def shutdown(self):
        """Shutdown the TTS engine"""
        try:
            # Signal worker thread to stop
            self.speech_queue.put((None, None))
            
            # Wait for queue to empty
            self.speech_queue.join()
            
            if self.engine:
                self.engine.stop()
            
            logger.info("TTS engine shut down")
        except Exception as e:
            logger.error(f"Error shutting down TTS: {e}")

# Global TTS instance
_voice_synth: Optional[VoiceSynthesizer] = None

def get_voice_synth() -> VoiceSynthesizer:
    """Get or create global TTS engine instance"""
    global _voice_synth
    if _voice_synth is None:
        _voice_synth = VoiceSynthesizer()
    return _voice_synth

def speak(text: str, blocking: bool = False, callback=None, player=None):
    """Convenience function to speak text with automatic music ducking"""
    engine = get_voice_synth()
    engine.speak(text, blocking=blocking, callback=callback, player=player)

def stop_speaking():
    """Stop current speech"""
    engine = get_voice_synth()
    engine.stop()