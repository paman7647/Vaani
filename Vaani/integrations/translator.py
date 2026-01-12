"""
Translator - Multi-Language Translation
==========================================

Features:
- Support for 100+ languages via deep-translator
- Automatic language detection
- Translation request parsing ("translate X to Y")
- Bidirectional translation (any language to any language)
- Error handling and fallback
- Language code normalization
- Popular language shortcuts (Hindi, Spanish, French, etc.)
- NO API KEYS REQUIRED (uses free Google Translate)

Translates text between languages using Google Translate backend.
Automatically detects source language when not specified.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

import logging
from typing import Optional, List, Dict, Tuple
from Vaani.utils.error_handler import error_handler

logger = logging.getLogger(__name__)

# Try importing deep-translator
try:
    from deep_translator import GoogleTranslator, MyMemoryTranslator
    from deep_translator.exceptions import LanguageNotSupportedException, TranslationNotFound
    TRANSLATOR_AVAILABLE = True
    logger.info("Translation module enabled (deep-translator)")
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.warning("Translation module not available - install: pip install deep-translator")


class TranslationHelper:
    """
    🌍 FREE Translation Helper (NO API KEYS NEEDED!)
    
    Provides:
    - Text translation between 100+ languages
    - Auto language detection
    - Multiple provider fallback (Google → MyMemory)
    - Natural language query parsing ("translate X to Y")
    """
    
    def __init__(self):
        self.available = TRANSLATOR_AVAILABLE
        
        # Common language mappings for natural queries
        self.language_aliases = {
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'italian': 'it',
            'portuguese': 'pt',
            'russian': 'ru',
            'japanese': 'ja',
            'chinese': 'zh-CN',
            'korean': 'ko',
            'arabic': 'ar',
            'hindi': 'hi',
            'turkish': 'tr',
            'dutch': 'nl',
            'polish': 'pl',
            'swedish': 'sv',
            'norwegian': 'no',
            'danish': 'da',
            'finnish': 'fi',
            'greek': 'el',
            'hebrew': 'he',
            'thai': 'th',
            'vietnamese': 'vi',
            'indonesian': 'id',
            'malay': 'ms',
            'filipino': 'tl',
            'english': 'en',
            'mandarin': 'zh-CN',
            'cantonese': 'zh-TW',
        }
        
        if self.available:
            logger.debug("Translation helper initialized with Google Translate (FREE)")
    
    @error_handler(default_return=None)
    def translate(
        self, 
        text: str, 
        target_language: str, 
        source_language: str = 'auto'
    ) -> Optional[Dict[str, str]]:
        """
        🌍 Translate text to target language (FREE, no API key!)
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'es', 'fr') or name ('spanish')
            source_language: Source language code or 'auto' for auto-detection
        
        Returns:
            Dict with 'translated_text', 'source_lang', 'target_lang', 'provider'
            or None if translation fails
        """
        if not self.available:
            logger.warning("Translation not available - deep-translator not installed")
            return None
        
        if not text or not text.strip():
            return None
        
        # Normalize language codes
        target_lang = self._normalize_language_code(target_language)
        source_lang = self._normalize_language_code(source_language) if source_language != 'auto' else 'auto'
        
        logger.info(f"Translating: '{text[:50]}...' ({source_lang} -> {target_lang})")
        
        try:
            # Try Google Translate first (PRIMARY - FREE)
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text)
            
            if translated:
                logger.info(f"Translated via Google Translate ({len(translated)} chars)")
                return {
                    'translated_text': translated,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'original_text': text,
                    'provider': 'Google Translate (FREE)'
                }
        
        except LanguageNotSupportedException as e:
            logger.warning(f"Language not supported: {e}")
            return None
        
        except TranslationNotFound:
            logger.warning("Translation not found")
            return None
        
        except Exception as e:
            logger.warning(f"Google Translate failed: {e}")
            
            # Fallback to MyMemory (BACKUP - FREE)
            try:
                logger.info("Trying MyMemory Translator (fallback)...")
                translator = MyMemoryTranslator(source=source_lang, target=target_lang)
                translated = translator.translate(text)
                
                if translated:
                    logger.info(f"Translated via MyMemory ({len(translated)} chars)")
                    return {
                        'translated_text': translated,
                        'source_lang': source_lang,
                        'target_lang': target_lang,
                        'original_text': text,
                        'provider': 'MyMemory Translator (FREE)'
                    }
            except Exception as fallback_error:
                logger.error(f"MyMemory fallback also failed: {fallback_error}")
        
        return None
    
    @error_handler(default_return=None)
    def parse_translation_request(self, query: str) -> Optional[Tuple[str, str, str]]:
        """
        🔍 Parse natural language translation request
        
        Examples:
        - "translate hello to spanish"
        - "how do you say thank you in french"
        - "what is goodbye in german"
        - "translate 'good morning' to italian"
        
        Returns:
            Tuple of (text_to_translate, target_language, source_language)
            or None if not a translation request
        """
        import re
        
        query_lower = query.lower().strip()
        
        # Pattern 1: "translate X to Y"
        match = re.search(r"translate\s+['\"]?(.+?)['\"]?\s+(?:to|into)\s+(\w+)", query_lower)
        if match:
            text = match.group(1).strip()
            target_lang = match.group(2).strip()
            return (text, target_lang, 'auto')
        
        # Pattern 2: "how do you say X in Y"
        match = re.search(r"how\s+(?:do\s+you\s+)?say\s+['\"]?(.+?)['\"]?\s+in\s+(\w+)", query_lower)
        if match:
            text = match.group(1).strip()
            target_lang = match.group(2).strip()
            return (text, target_lang, 'auto')
        
        # Pattern 3: "what is X in Y"
        match = re.search(r"what\s+is\s+['\"]?(.+?)['\"]?\s+in\s+(\w+)", query_lower)
        if match:
            text = match.group(1).strip()
            target_lang = match.group(2).strip()
            return (text, target_lang, 'auto')
        
        # Pattern 4: "X in Y" (simple)
        match = re.search(r"^['\"]?(.+?)['\"]?\s+in\s+(\w+)$", query_lower)
        if match:
            text = match.group(1).strip()
            target_lang = match.group(2).strip()
            # Only match if it's clearly a translation request
            if any(keyword in query_lower for keyword in ['translate', 'say', 'mean']):
                return (text, target_lang, 'auto')
        
        return None
    
    @error_handler(default_return=[])
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes
        
        Returns:
            List of language codes (e.g., ['en', 'es', 'fr', ...])
        """
        if not self.available:
            return []
        
        try:
            # Get supported languages from GoogleTranslator
            languages = GoogleTranslator().get_supported_languages(as_dict=False)
            return languages
        except Exception as e:
            logger.warning(f"Failed to get supported languages: {e}")
            return list(self.language_aliases.keys())
    
    def _normalize_language_code(self, language: str) -> str:
        """
        Convert language name or code to standard code
        
        Args:
            language: Language name ('spanish') or code ('es')
        
        Returns:
            Standard language code ('es')
        """
        language = language.lower().strip()
        
        # Check if it's already a language code (2-5 chars)
        if len(language) <= 5 and language.replace('-', '').isalpha():
            return language
        
        # Try to find in aliases
        return self.language_aliases.get(language, language)
    
    @error_handler(default_return="I couldn't translate that.")
    def translate_and_speak(
        self, 
        text: str, 
        target_language: str, 
        source_language: str = 'auto'
    ) -> str:
        """
        🗣️ Translate text and format for natural speech response
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language (default: auto-detect)
        
        Returns:
            Natural speech-friendly response with translation
        """
        result = self.translate(text, target_language, source_language)
        
        if not result:
            # Provide helpful error
            target_name = self._get_language_name(target_language)
            return f"I couldn't translate that to {target_name}. Please check the language and try again."
        
        translated = result['translated_text']
        source_lang = result['source_lang']
        target_lang = result['target_lang']
        provider = result['provider']
        
        # Get language names for speech
        target_name = self._get_language_name(target_lang)
        
        # Format natural response
        if source_lang == 'auto':
            response = f"In {target_name}, that's: {translated}"
        else:
            source_name = self._get_language_name(source_lang)
            response = f"Translating from {source_name} to {target_name}: {translated}"
        
        return response
    
    def _get_language_name(self, code: str) -> str:
        """Get human-readable language name from code"""
        # Reverse lookup in aliases
        for name, lang_code in self.language_aliases.items():
            if lang_code == code or code.startswith(lang_code):
                return name.capitalize()
        
        # Common codes not in aliases
        common_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'zh-CN': 'Chinese',
            'ko': 'Korean',
            'ar': 'Arabic',
        }
        
        return common_names.get(code, code.upper())
    
    @error_handler(default_return=False)
    def is_translation_request(self, query: str) -> bool:
        """
        🔍 Check if query is a translation request
        
        Args:
            query: User query
        
        Returns:
            True if it's a translation request
        """
        if not query:
            return False
        
        query_lower = query.lower()
        
        # Check for translation keywords
        translation_keywords = [
            'translate',
            'how do you say',
            'how to say',
            'what is',
            'say in',
            'in spanish',
            'in french',
            'in german',
            'in italian',
            'in japanese',
            'in chinese',
            'in korean',
        ]
        
        return any(keyword in query_lower for keyword in translation_keywords)


# Global translation helper instance
_translator: Optional[TranslationHelper] = None

def get_translator() -> TranslationHelper:
    """Get or create global translator instance"""
    global _translator
    if _translator is None:
        _translator = TranslationHelper()
    return _translator
