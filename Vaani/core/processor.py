"""
Command Processor - Intent Router & Handler
==============================================

Features:
- Fast intent classification using RapidFuzz pattern matching
- Command routing to appropriate handlers (music, time, information, etc.)
- AI-powered fallback for complex queries
- Translation request detection and handling
- Music playback control (play, pause, stop, next, volume)
- System commands (time, date, open apps)
- Web search integration for questions
- Minimal logging (errors only)

Takes user commands and routes them to the right handler, using smart
pattern matching for speed and AI when needed for accuracy.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import re
import time
import subprocess
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Command Processor")
from ..intelligence.responses import responses

# Try to import advanced systems
try:
    from ..voice.speech_synthesis import get_voice_synth as get_advanced_speech_synthesizer, speak as speak_advanced
    from ..integrations.web_search import get_search
    from ..integrations.translator import get_translator
    from ..intelligence.context import get_conversation_context
    from ..intelligence.personality import get_personality_module
    ADVANCED_MODE = True
except ImportError:
    from ..voice.speech_synthesis import speak, get_voice_synth
    ADVANCED_MODE = False
    logger.info("Using basic mode")

# Try to import translator separately (it might be available even in basic mode)
try:
    from ..integrations.translator import get_translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.info("Translation features not available")

from ..voice.audio_engine import get_audio_engine
from ..intelligence.conversation import get_conversation_manager
from ..config import settings

# Try to import smart intent classifier
try:
    from ..intelligence.intent_analyzer import get_intent_matcher, IntentType, IntentResult
    SMART_CLASSIFIER_AVAILABLE = True
except ImportError as e:
    SMART_CLASSIFIER_AVAILABLE = False


class CommandProcessor:
    """Interprets user intent and responds naturally"""
    
    def __init__(self):
        self.audio_engine = get_audio_engine()
        self.ai_engine = get_conversation_manager()
        
        # Translation support
        if TRANSLATOR_AVAILABLE:
            self.translator = get_translator()
        else:
            self.translator = None
        
        # Advanced features
        if ADVANCED_MODE:
            self.speech_synthesis_engine = get_advanced_speech_synthesizer()
            self.web_search = get_search()
            self.context = get_conversation_context()
            self.personality = get_personality_module()
        else:
            self.speech_synthesis_engine = get_voice_synth()
            self.web_search = None
            self.context = None
            self.personality = None
        
        # Smart intent classifier
        if SMART_CLASSIFIER_AVAILABLE:
            self.smart_classifier = get_intent_matcher()
        else:
            self.smart_classifier = None
        
        self.command_handlers: Dict[str, Callable] = self._register_handlers()
        self.last_command_time = time.time()
        
        logger.debug(f"Command processor initialized (advanced mode: {ADVANCED_MODE}, smart classifier: {SMART_CLASSIFIER_AVAILABLE})")
    
    def _register_handlers(self) -> Dict[str, Callable]:
        """Register command handlers"""
        return {
            'music': self._handle_music_command,
            'control': self._handle_control_command,
            'system': self._handle_system_command,
            'conversation': self._handle_conversation,
            'information': self._handle_information_query,
            'web_search': self._handle_web_search,
            'translation': self._handle_translation
        }
    
    def _speak(self, text: str, blocking: bool = False, tone: str = 'neutral', speed: str = 'normal'):
        """Enhanced speak with automatic music ducking and personality"""
        if not text:
            logger.warning("Attempted to speak empty text")
            return
        
        try:
            
            if ADVANCED_MODE:
                # Use advanced TTS with automatic language detection
                speak_advanced(text)
            else:
                # Fallback to basic TTS
                speak(text, blocking=blocking, player=self.audio_engine)
                
        except Exception as e:
            logger.error(f"Speech error: {e}")
            # Final fallback to system TTS
            try:
                subprocess.run(['say', text], timeout=10)
            except:
                logger.error("Complete TTS failure - continuing silently")
    
    @error_handler(default_return="ERROR", error_message="Command processing failed")
    def process_command(self, command: str) -> str:
        """Understand intent and take action naturally"""
        if not command or command in ["TIMEOUT", "ERROR", "UNCLEAR"]:
            self._speak(responses.unclear_speech())
            return "ERROR"
        
        command_lower = command.lower().strip()
        
        # Exit commands
        if self._is_exit_command(command_lower):
            return self._handle_exit()
        
        # Check for translation request (high priority)
        if TRANSLATOR_AVAILABLE and self.translator and self.translator.is_translation_request(command):
            return self._handle_translation(command, command_lower)
        
        # Use smart classifier if available
        if SMART_CLASSIFIER_AVAILABLE and self.smart_classifier:
            return self._process_with_smart_classifier(command, command_lower)
        else:
            # Fallback to basic classification
            return self._process_with_basic_classifier(command, command_lower)
    
    def _process_with_smart_classifier(self, command: str, command_lower: str) -> str:
        """Process command using smart NLP-based intent classifier"""
        try:
            # Get context for classifier
            context = {
                'is_music_playing': self.audio_engine.is_playing,
                'current_volume': self.audio_engine.volume if self.audio_engine else None,
                'last_command_time': self.last_command_time
            }
            
            # Classify intent with fuzzy matching
            result: IntentResult = self.smart_classifier.classify(command_lower, context)
            
            # Route to AI if needed (low confidence or complex query)
            if result.requires_ai:
                return self._handle_conversation(command, command_lower)
            
            # Direct handling based on intent
            return self._handle_smart_intent(result, command, command_lower)
            
        except Exception as e:
            logger.error(f"Smart classifier error: {e} - Falling back to basic mode")
            return self._process_with_basic_classifier(command, command_lower)
    
    def _process_with_basic_classifier(self, command: str, command_lower: str) -> str:
        """Fallback to basic pattern matching classification"""
        command_type = self._classify_command(command_lower)
        handler = self.command_handlers.get(command_type, self._handle_conversation)
        return handler(command, command_lower)
    
    def _handle_smart_intent(self, result: IntentResult, command: str, command_lower: str) -> str:
        """Handle command based on smart classifier result"""
        intent = result.intent
        entities = result.entities
        
        # Music playback intent_analyzer
        if intent == IntentType.MUSIC_PLAY:
            song_name = entities.get('song_name', '')
            if song_name:
                return self._handle_play_specific_song(song_name)
            else:
                # Ask for song name
                self._speak("What song would you like to play?")
                return "NEEDS_INFO"
        
        elif intent == IntentType.MUSIC_PAUSE:
            return self._handle_music_pause()
        
        elif intent == IntentType.MUSIC_RESUME:
            return self._handle_music_resume()
        
        elif intent == IntentType.MUSIC_STOP:
            return self._handle_music_stop()
        
        elif intent == IntentType.MUSIC_NEXT:
            return self._handle_music_next()
        
        elif intent == IntentType.MUSIC_PREVIOUS:
            return self._handle_music_previous()
        
        # Volume intent_analyzer
        elif intent == IntentType.MUSIC_VOLUME_UP:
            return self._handle_volume_up()
        
        elif intent == IntentType.MUSIC_VOLUME_DOWN:
            return self._handle_volume_down()
        
        elif intent == IntentType.MUSIC_VOLUME_SET:
            volume = entities.get('volume')
            if volume is not None:
                return self._handle_volume_set(volume)
            else:
                self._speak("What volume level? Please say a number between 0 and 100.")
                return "NEEDS_INFO"
        
        # Queue intent_analyzer
        elif intent == IntentType.MUSIC_QUEUE_ADD:
            song_name = entities.get('song_name', '')
            if song_name:
                return self._handle_queue_add(song_name)
            else:
                self._speak("What song should I add to the queue?")
                return "NEEDS_INFO"
        
        elif intent == IntentType.MUSIC_QUEUE_SHOW:
            return self._handle_queue_show()
        
        elif intent == IntentType.MUSIC_QUEUE_CLEAR:
            return self._handle_queue_clear()
        
        elif intent == IntentType.MUSIC_CURRENT:
            return self._handle_music_current()
        
        # System intent_analyzer
        elif intent == IntentType.SYSTEM_TIME:
            return self._handle_time_query()
        
        elif intent == IntentType.SYSTEM_DATE:
            return self._handle_date_query()
        
        elif intent == IntentType.SYSTEM_WEATHER:
            return self._handle_weather_query(command_lower)
        
        elif intent == IntentType.SYSTEM_EXIT:
            return self._handle_exit()
        
        # Information queries - route to AI
        elif intent.name.startswith('INFO_'):
            logger.info(f"Information query ({intent.name}) - routing to AI")
            return self._handle_conversation(command, command_lower)
        
        # Conversation or unknown - route to AI
        elif intent in [IntentType.CONVERSATION, IntentType.UNKNOWN]:
            return self._handle_conversation(command, command_lower)
        
        else:
            logger.warning(f"Unhandled intent: {intent}")
            return self._handle_conversation(command, command_lower)
            logger.error(f"Command error: {e}")
            self._speak(responses.error())
            return "ERROR"
            return "UNCLEAR"
        
        command_lower = command.lower().strip()
        self.last_command_time = time.time()
        
        logger.info(f"Processing command: {command}")
        
        # Check for exit commands
        if self._is_exit_command(command_lower):
            return self._handle_exit()
        
        # Route to appropriate handler
        command_type = self._classify_command(command_lower)
        handler = self.command_handlers.get(command_type, self._handle_conversation)
        
        try:
            result = handler(command, command_lower)
            return result or "SUCCESS"
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            self._speak(responses.error())
            return "ERROR"
    
    def _classify_command(self, command: str) -> str:
        """Classify command type (supports English and Hindi)"""
        # Music commands (English and Hindi)
        music_keywords = ['play', 'pause', 'stop', 'resume', 'music', 'song', 'next', 'skip', 'volume',
                         'प्ले', 'गाना', 'संगीत', 'बजाओ', 'बंद', 'रोको', 'अगला']
        if any(word in command for word in music_keywords):
            return 'music'
        
        # Web search (explicit)
        if any(word in command for word in ['search', 'look up', 'find out', 'google']):
            return 'web_search'
        
        # Control commands
        if any(word in command for word in ['turn on', 'turn off', 'set', 'adjust', 'control']):
            return 'control'
        
        # System commands
        if any(word in command for word in ['time', 'date', 'weather', 'news', 'open', 'launch']):
            return 'system'
        
        # Information queries (may trigger auto-search)
        if any(command.startswith(q) for q in ['what', 'who', 'where', 'when', 'why', 'how', 'tell me', 'explain']):
            return 'information'
        
        # Default to conversation
        return 'conversation'
    


    def _is_exit_command(self, command: str) -> bool:
        """Check if command is an exit request"""
        return any(word in command for word in ['goodbye', 'bye', 'quit', 'exit', 'stop listening', 'shut down'])
    
    def _handle_exit(self) -> str:
        """Handle goodbye naturally"""
        if self.audio_engine.is_playing:
            self.audio_engine.stop()
        
        self._speak(responses.goodbye())
        return "EXIT"
    
    def _handle_music_command(self, command: str, command_lower: str) -> str:
        """Handle music-related commands with mood-based playback"""
        # What's playing?
        if any(phrase in command_lower for phrase in ["what's playing", "current song", "now playing", "what song"]):
            playing = self.audio_engine.get_whats_playing()
            if playing:
                self._speak(f"Currently {playing}")
            else:
                self._speak("Nothing is playing right now")
            return "SUCCESS"
        
        # Pause
        if 'pause' in command_lower:
            if self.audio_engine.pause():
                self._speak(responses.get_random(responses.MUSIC_PAUSED))
            else:
                self._speak("No music playing right now.")
            return "SUCCESS"
        
        # Resume
        if any(word in command_lower for word in ['resume', 'continue', 'unpause']):
            if self.audio_engine.resume():
                self._speak(responses.get_random(responses.MUSIC_RESUMED))
            else:
                self._speak("Nothing to resume.")
            return "SUCCESS"
        
        # Stop
        if 'stop' in command_lower:
            if self.audio_engine.stop():
                self._speak(responses.get_random(responses.MUSIC_STOPPED))
            else:
                self._speak("No music playing.")
            return "SUCCESS"
        
        # Next
        if any(word in command_lower for word in ['next', 'skip']):
            if self.audio_engine.play_next():
                self._speak(responses.get_random(responses.MUSIC_PLAYING))
            else:
                self._speak("Nothing else in the queue.")
            return "SUCCESS"
        
        # Volume
        if 'volume' in command_lower:
            return self._handle_volume_command(command_lower)
        
        # Play music
        if 'play' in command_lower:
            # Check for mood-based playback
            mood_keywords = ['relaxing', 'calm', 'energetic', 'happy', 'sad', 'focus', 'workout', 'sleep', 'party']
            for mood in mood_keywords:
                if mood in command_lower:
                    logger.info(f"🎭 Mood-based playback: {mood}")
                    self._speak(responses.music_playing())
                    # Note: Mood-based selection needs implementation
                    break
            
            # Regular song playback
            return self._handle_play_music(command, command_lower)
        
        # Add to queue
        if any(word in command_lower for word in ['queue', 'add to queue']):
            song_name = self._extract_song_name(command_lower)
            if song_name:
                self.audio_engine.add_to_queue(song_name)
                self._speak(responses.get_random(responses.CONFIRMATIONS))
            return "SUCCESS"
        
        # Get status
        if any(word in command_lower for word in ['what\'s playing', 'current song', 'now playing']):
            status = self.audio_engine.get_status()
            if status['is_playing']:
                self._speak(f"Currently: {status['current_song']}")
            else:
                self._speak("Nothing playing right now.")
            return "SUCCESS"
        
        return "SUCCESS"
    
    def _handle_play_music(self, command: str, command_lower: str) -> str:
        """Handle play music command"""
        # Extract song name
        song_name = self._extract_song_name(command_lower)
        
        if not song_name:
            self._speak("What would you like me to play?")
            return "SUCCESS"
        
        logger.info(f"🎵 Searching for song: {song_name}")
        self._speak(responses.music_searching())
        
        # Get YouTube URL
        url, title, duration = self.audio_engine.get_youtube_audio_url(song_name)
        
        if url:
            logger.info(f"✅ Found song: {title}")
            self._speak(responses.music_playing())
            
            logger.info(f"🎬 Starting playback...")
            success = self.audio_engine.play_url(url, title)
            
            if success:
                logger.info(f"✅ Playback started successfully")
            else:
                logger.error(f"❌ Playback failed")
                self._speak(responses.get_random(responses.MUSIC_ERRORS))
                return "ERROR"
        else:
            logger.warning(f"❌ Song not found: {song_name}")
            self._speak(responses.get_random(responses.MUSIC_NOT_FOUND))
            return "ERROR"
        
        return "SUCCESS"
    
    def _extract_song_name(self, command: str) -> Optional[str]:
        """Extract song name from command"""
        # Remove command words
        song_name = command
        
        for word in ['play', 'music', 'song', 'queue', 'add to queue', 'add', 'the song', 'the music']:
            song_name = song_name.replace(word, '')
        
        # Clean up
        song_name = song_name.strip()
        
        # Remove articles at the beginning
        for article in ['the ', 'a ', 'an ']:
            if song_name.startswith(article):
                song_name = song_name[len(article):]
        
        return song_name if song_name else None
    
    def _handle_volume_command(self, command: str) -> str:
        """Handle volume control naturally"""
        if 'up' in command or 'increase' in command or 'louder' in command:
            current_volume = self.audio_engine.volume
            new_volume = min(1.0, current_volume + 0.1)
            self.audio_engine.set_volume(new_volume)
            self._speak(responses.get_random(responses.CONFIRMATIONS))
        
        elif 'down' in command or 'decrease' in command or 'quieter' in command or 'lower' in command:
            current_volume = self.audio_engine.volume
            new_volume = max(0.0, current_volume - 0.1)
            self.audio_engine.set_volume(new_volume)
            self._speak(responses.get_random(responses.CONFIRMATIONS))
        
        elif 'mute' in command:
            self.audio_engine.set_volume(0.0)
            self._speak(responses.get_random(responses.CONFIRMATIONS))
        
        elif 'max' in command or 'maximum' in command or 'full' in command:
            # Set volume to maximum (100%)
            self.audio_engine.set_volume(1.0)
            self._speak(responses.get_random(responses.CONFIRMATIONS))
        
        else:
            # Try to extract percentage
            match = re.search(r'(\d+)', command)
            if match:
                volume_percent = int(match.group(1))
                volume = max(0, min(100, volume_percent)) / 100.0
                self.audio_engine.set_volume(volume)
                self._speak(responses.get_random(responses.CONFIRMATIONS))
            else:
                self._speak(responses.unclear_speech())
        
        return "SUCCESS"
    
    def _handle_control_command(self, command: str, command_lower: str) -> str:
        """Handle device control commands"""
        # This is a placeholder for smart home integration
        self._speak("That's not set up yet, but it's coming soon!")
        return "SUCCESS"
    
    def _handle_system_command(self, command: str, command_lower: str) -> str:
        """Handle system information commands naturally"""
        # Time
        if 'time' in command_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            self._speak(f"It's {current_time}.")
            return "SUCCESS"
        
        # Date
        if 'date' in command_lower:
            current_date = datetime.now().strftime("%B %d, %Y")
            self._speak(f"Today's {current_date}.")
            return "SUCCESS"
        
        # Weather (placeholder)
        if 'weather' in command_lower:
            self._speak("Weather's not hooked up yet, but it's coming.")
            return "SUCCESS"
        
        # Open application
        if 'open' in command_lower or 'launch' in command_lower:
            app_name = self._extract_app_name(command_lower)
            if app_name:
                success = self._open_application(app_name)
                if success:
                    self._speak(responses.get_random(responses.CONFIRMATIONS))
                else:
                    self._speak(f"Couldn't open {app_name}.")
            else:
                self._speak("What should I open?")
            return "SUCCESS"
        
        return "SUCCESS"
    
    def _extract_app_name(self, command: str) -> Optional[str]:
        """Extract application name from command"""
        app_name = command
        for word in ['open', 'launch', 'start', 'run']:
            app_name = app_name.replace(word, '')
        
        return app_name.strip() if app_name.strip() else None
    
    def _open_application(self, app_name: str) -> bool:
        """Open an application"""
        try:
            if 'safari' in app_name.lower():
                subprocess.Popen(['open', '-a', 'Safari'])
                return True
            elif 'chrome' in app_name.lower():
                subprocess.Popen(['open', '-a', 'Google Chrome'])
                return True
            elif 'spotify' in app_name.lower():
                subprocess.Popen(['open', '-a', 'Spotify'])
                return True
            elif 'music' in app_name.lower():
                subprocess.Popen(['open', '-a', 'Music'])
                return True
            else:
                # Try to open generic app
                subprocess.Popen(['open', '-a', app_name])
                return True
        except Exception as e:
            logger.error(f"Error opening application: {e}")
            return False
    
    @error_handler(default_return="ERROR", error_message="Web search failed")
    def _handle_web_search(self, command: str, command_lower: str) -> str:
        """Handle explicit web search requests naturally"""
        if not self.web_search:
            self._speak("Search isn't working right now.")
            return "ERROR"
        
        # Extract search query
        query = command_lower
        for word in ['search', 'look up', 'find out', 'google', 'search for', 'the web for']:
            query = query.replace(word, '')
        query = query.strip()
        
        if not query or (self.web_search and not self.web_search.validate_query(query)):
            self._speak("What should I search for?")
            return "SUCCESS"
        
        logger.info(f"🌐 Web search: {query}")
        self._speak("Let me check...")
        
        # Perform search and get summary
        summary = self.web_search.search_and_summarize(query, max_results=3)
        
        if summary:
            self._speak(summary)
            return "SUCCESS"
        else:
            self._speak("Couldn't find anything on that.")
            return "ERROR"
    
    @error_handler(default_return="ERROR", error_message="Translation failed")
    def _handle_translation(self, command: str, command_lower: str) -> str:
        """
        🌍 Handle translation requests (FREE, no API key!)
        
        Examples:
        - "translate hello to spanish"
        - "how do you say thank you in french"
        - "what is goodbye in german"
        """
        if not TRANSLATOR_AVAILABLE or not self.translator:
            self._speak("Translation isn't available right now.")
            return "ERROR"
        
        logger.info(f"🌍 Translation request: {command}")
        
        # Parse the translation request
        parsed = self.translator.parse_translation_request(command)
        
        if not parsed:
            # Try to let AI handle it if parsing failed
            logger.warning("⚠️ Couldn't parse translation request, routing to AI")
            return self._handle_conversation(command, command_lower)
        
        text_to_translate, target_language, source_language = parsed
        
        logger.info(f"📝 Translate: '{text_to_translate}' → {target_language}")
        
        # Perform translation
        response = self.translator.translate_and_speak(
            text=text_to_translate,
            target_language=target_language,
            source_language=source_language
        )
        
        # Speak the translation result
        if response:
            self._speak(response, tone='informative')
            logger.info(f"✅ Translation successful: {response[:100]}...")
            return "SUCCESS"
        else:
            self._speak("I couldn't translate that. Please try again.")
            return "ERROR"
    
    @error_handler(default_return="ERROR", error_message="Information query failed")
    def _handle_information_query(self, command: str, command_lower: str) -> str:
        """Handle information queries using AI with automatic web search fallback"""
        logger.info(f"📝 Information query: {command}")
        
        try:
            # Generate AI response (AI engine will auto-trigger web search if needed)
            # Intelligent fallback chain:
            # 1. AI with Google Search grounding
            # 2. API key rotation if needed
            # 3. Web search (DuckDuckGo/Google) with natural summarization
            # 4. Pattern-based NLP
            response = self.ai_engine.generate_response(
                command,
                use_context=True,
                context_type='information'
            )
            
            logger.info(f"💡 Generated answer ({len(response)} chars): {response[:100]}...")
            
            # CRITICAL: Ensure response is ALWAYS spoken
            if response and response.strip():
                self._speak(response, tone='confident')
                logger.info("✅ Answer spoken successfully")
                return "SUCCESS"
            else:
                logger.warning("⚠️ Empty response, cannot answer")
                self._speak("I couldn't find a good answer to that question right now.")
                return "ERROR"
                
        except Exception as e:
            logger.error(f"❌ Information query error: {e}")
            # Final fallback - admit we can't answer
            self._speak("I'm unable to answer that question at the moment. Try rephrasing it?")
            return "ERROR"
    
    @error_handler(default_return="ERROR", error_message="Conversation processing failed")
    def _handle_conversation(self, command: str, command_lower: str) -> str:
        """Handle general conversation using AI with intelligent fallback to web search"""
        logger.info(f"💬 Conversation: {command}")
        
        # Detect if this is likely Hindi/Indian language (Romanized or Devanagari)
        language_hint = self._detect_language_hint(command)
        
        # Build prompt with language hint if needed
        if language_hint:
            # Add explicit language instruction for Romanized Hindi
            enhanced_prompt = f"{command}\n\n(Note: Please respond in {language_hint})"
            logger.info(f"🌐 Language hint added: {language_hint}")
        else:
            enhanced_prompt = command
        
        try:
            # Generate AI response with automatic fallback system
            # The AI engine will automatically:
            # 1. Try AI with Google Search grounding
            # 2. Try API key rotation if quota exhausted
            # 3. Fall back to pattern-based NLP
            # 4. Fall back to web search if it's a question
            # 5. Fall back to conversational response
            response = self.ai_engine.generate_response(
                enhanced_prompt,
                use_context=True,
                context_type='conversation'
            )
            
            logger.info(f"🤖 Generated response ({len(response)} chars): {response[:100]}...")
            
            # Speak the response
            if response and response.strip():
                self._speak(response, tone='warm')
                logger.info("✅ Response spoken successfully")
                return "SUCCESS"
            else:
                logger.warning("⚠️ Empty response from AI, using fallback")
                self._speak(responses.unclear_speech())
                return "ERROR"
                
        except Exception as e:
            logger.error(f"❌ Conversation handler error: {e}")
            # Final fallback
            self._speak("I'm having trouble processing that right now. Could you try again?")
            return "ERROR"
    
    def _detect_language_hint(self, text: str) -> Optional[str]:
        """Detect language from text and return hint for AI"""
        # Check for Devanagari script (Hindi)
        if any(0x0900 <= ord(char) <= 0x097F for char in text):
            return "Hindi"
        
        # Check for other Indian scripts
        if any(0x0980 <= ord(char) <= 0x09FF for char in text):
            return "Bengali"
        if any(0x0A80 <= ord(char) <= 0x0AFF for char in text):
            return "Gujarati"
        if any(0x0B80 <= ord(char) <= 0x0BFF for char in text):
            return "Tamil"
        if any(0x0C00 <= ord(char) <= 0x0C7F for char in text):
            return "Telugu"
        
        # Check for common Romanized Hindi/Indian words
        text_lower = text.lower()
        hindi_words = [
            'namaste', 'namaskar', 'dhanyavaad', 'shukriya', 'aap', 'kaise', 
            'kya', 'kaise ho', 'aapka', 'mera', 'hai', 'hain', 'main',
            'tum', 'tumhara', 'kahan', 'kyun', 'kab', 'kaun', 'kaunsa',
            'accha', 'theek', 'matlab', 'zaroor', 'bilkul', 'haan', 'nahi'
        ]
        
        # If multiple Hindi words found, likely Hindi input
        hindi_word_count = sum(1 for word in hindi_words if word in text_lower)
        if hindi_word_count >= 1:
            return "Hindi"
        
        return None


    # ==================== SMART INTENT HANDLERS ====================
    # These methods handle specific intent_analyzer from the smart classifier
    
    def _handle_play_specific_song(self, song_name: str) -> str:
        """Play a specific song by name - auto-queues if multiple songs detected"""
        try:
            # Check for multiple songs (separated by "and", "also", commas, "then")
            separators = [' and ', ' also ', ' then ', ',']
            songs_to_play = [song_name]
            
            for separator in separators:
                if separator in song_name.lower():
                    # Split into multiple songs
                    parts = [part.strip() for part in song_name.split(separator) if part.strip()]
                    if len(parts) > 1:
                        songs_to_play = parts
                        break
            
            # If multiple songs detected, play first and queue others
            if len(songs_to_play) > 1:
                first_song = songs_to_play[0]
                remaining_songs = songs_to_play[1:]
                
                logger.info(f"🎵 Playing {first_song} and queueing {len(remaining_songs)} more songs")
                self._speak(f"Playing {first_song} and queueing {len(remaining_songs)} more songs")
                
                # Play first song
                if self.audio_engine.play_mood_music(first_song):
                    # Queue the rest
                    for song in remaining_songs:
                        self.audio_engine.add_to_queue(song)
                        logger.info(f"➕ Queued: {song}")
                    return "SUCCESS"
                else:
                    self._speak(f"Sorry, I couldn't find {first_song}")
                    return "ERROR"
            else:
                # Single song - play normally
                self._speak(f"Searching for {song_name}")
                
                if self.audio_engine.play_mood_music(song_name):
                    self._speak(f"Playing {song_name}")
                    return "SUCCESS"
                else:
                    self._speak(f"Sorry, I couldn't find {song_name}")
                    return "ERROR"
                    
        except Exception as e:
            logger.error(f"Error playing song: {e}")
            self._speak(f"Sorry, I couldn't play that")
            return "ERROR"
    
    def _handle_music_pause(self) -> str:
        """Pause current music"""
        if self.audio_engine.pause():
            self._speak(responses.get_random(responses.MUSIC_PAUSED))
            return "SUCCESS"
        else:
            self._speak("No music playing right now.")
            return "ERROR"
    
    def _handle_music_resume(self) -> str:
        """Resume paused music"""
        if self.audio_engine.resume():
            self._speak(responses.get_random(responses.MUSIC_RESUMED))
            return "SUCCESS"
        else:
            self._speak("No music to resume.")
            return "ERROR"
    
    def _handle_music_stop(self) -> str:
        """Stop current music"""
        if self.audio_engine.stop():
            self._speak(responses.get_random(responses.MUSIC_STOPPED))
            return "SUCCESS"
        else:
            self._speak("No music playing right now.")
            return "ERROR"
    
    def _handle_music_next(self) -> str:
        """Skip to next song"""
        try:
            self.audio_engine.next()
            self._speak(responses.get_random(responses.MUSIC_NEXT))
            return "SUCCESS"
        except Exception as e:
            logger.error(f"Error skipping song: {e}")
            self._speak("Sorry, couldn't skip to next song.")
            return "ERROR"
    
    def _handle_music_previous(self) -> str:
        """Go to previous song"""
        try:
            self.audio_engine.previous()
            self._speak(responses.get_random(responses.MUSIC_PREVIOUS))
            return "SUCCESS"
        except Exception as e:
            logger.error(f"Error going to previous song: {e}")
            self._speak("Sorry, couldn't go to previous song.")
            return "ERROR"
    
    def _handle_volume_up(self) -> str:
        """Increase volume by 10%"""
        current_volume = self.audio_engine.volume
        new_volume = min(1.0, current_volume + 0.1)
        self.audio_engine.set_volume(new_volume)
        logger.info(f"🔊 Volume increased to {int(new_volume * 100)}%")
        self._speak(responses.get_random(responses.CONFIRMATIONS))
        return "SUCCESS"
    
    def _handle_volume_down(self) -> str:
        """Decrease volume by 10%"""
        current_volume = self.audio_engine.volume
        new_volume = max(0.0, current_volume - 0.1)
        self.audio_engine.set_volume(new_volume)
        logger.info(f"🔉 Volume decreased to {int(new_volume * 100)}%")
        self._speak(responses.get_random(responses.CONFIRMATIONS))
        return "SUCCESS"
    
    def _handle_volume_set(self, volume: int) -> str:
        """Set volume to specific level (0-100)"""
        volume_float = max(0.0, min(1.0, volume / 100.0))
        self.audio_engine.set_volume(volume_float)
        logger.info(f"🔊 Volume set to {volume}%")
        self._speak(f"Volume set to {volume} percent")
        return "SUCCESS"
    
    def _handle_queue_add(self, song_name: str) -> str:
        """Add song to queue"""
        logger.info(f"➕ Adding to queue: {song_name}")
        try:
            # Placeholder - implement actual queue logic
            self._speak(f"Added {song_name} to the queue")
            return "SUCCESS"
        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            self._speak(f"Sorry, couldn't add {song_name} to the queue")
            return "ERROR"
    
    def _handle_queue_show(self) -> str:
        """Show current queue"""
        try:
            # Placeholder - implement actual queue logic
            self._speak("The queue is empty right now")
            return "SUCCESS"
        except Exception as e:
            logger.error(f"Error showing queue: {e}")
            self._speak("Sorry, couldn't show the queue")
            return "ERROR"
    
    def _handle_queue_clear(self) -> str:
        """Clear the queue"""
        try:
            # Placeholder - implement actual queue logic
            self._speak("Queue cleared")
            return "SUCCESS"
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")
            self._speak("Sorry, couldn't clear the queue")
            return "ERROR"
    
    def _handle_music_current(self) -> str:
        """Tell what's currently playing"""
        playing = self.audio_engine.get_whats_playing()
        if playing:
            self._speak(f"Currently {playing}")
        else:
            self._speak("Nothing is playing right now")
        return "SUCCESS"
    
    def _handle_time_query(self) -> str:
        """Tell current time"""
        current_time = datetime.now().strftime("%I:%M %p")
        self._speak(f"It's {current_time}.")
        return "SUCCESS"
    
    def _handle_date_query(self) -> str:
        """Tell current date"""
        current_date = datetime.now().strftime("%B %d, %Y")
        self._speak(f"Today's {current_date}.")
        return "SUCCESS"
    
    def _handle_weather_query(self, command: str) -> str:
        """Handle weather query (placeholder)"""
        self._speak("Weather's not hooked up yet, but it's coming.")
        return "SUCCESS"


# Global command processor instance
_processor: Optional[CommandProcessor] = None

def get_processor() -> CommandProcessor:
    """Get or create global command processor instance"""
    global _processor
    if _processor is None:
        _processor = CommandProcessor()
    return _processor