"""
Global Configuration - System-Wide Settings
===============================================

Features:
- External config.json loading and validation
- Environment variable integration
- API key management (Gemini, Groq, etc.)
- Feature toggles (enable/disable components)
- System paths (logs, temp, models)
- Debug mode settings
- Performance tuning parameters
- Default value fallbacks
- Voice mappings for 32 languages

Loads configuration from external config.json and environment variables.
Provides centralized access to all system settings with validation.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ASSISTANT IDENTITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PRIMARY CONFIGURATION - Change here to rename assistant
ASSISTANT_NAME = "Vaani"
ASSISTANT_NAME_LOWER = ASSISTANT_NAME.lower()

# Wake words (automatically includes name)
WAKE_WORDS = [
    f"hey {ASSISTANT_NAME_LOWER}",
    f"hi {ASSISTANT_NAME_LOWER}",
    f"hello {ASSISTANT_NAME_LOWER}",
    ASSISTANT_NAME_LOWER
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MULTILINGUAL SUPPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# All 22 Scheduled Indian Languages + Major Global Languages
SUPPORTED_LANGUAGES = {
    # Indian Languages (Constitutional)
    'as': {'name': 'Assamese', 'native': 'অসমীয়া', 'region': 'India'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'region': 'India'},
    'brx': {'name': 'Bodo', 'native': 'बड़ो', 'region': 'India'},
    'doi': {'name': 'Dogri', 'native': 'डोगरी', 'region': 'India'},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'region': 'India'},
    'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'region': 'India'},
    'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'region': 'India'},
    'ks': {'name': 'Kashmiri', 'native': 'कॉशुर', 'region': 'India'},
    'kok': {'name': 'Konkani', 'native': 'कोंकणी', 'region': 'India'},
    'mai': {'name': 'Maithili', 'native': 'मैथिली', 'region': 'India'},
    'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'region': 'India'},
    'mni': {'name': 'Manipuri', 'native': 'মৈতৈলোন্', 'region': 'India'},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'region': 'India'},
    'ne': {'name': 'Nepali', 'native': 'नेपाली', 'region': 'India'},
    'or': {'name': 'Odia', 'native': 'ଓଡ଼ିଆ', 'region': 'India'},
    'pa': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ', 'region': 'India'},
    'sa': {'name': 'Sanskrit', 'native': 'संस्कृतम्', 'region': 'India'},
    'sat': {'name': 'Santali', 'native': 'ᱥᱟᱱᱛᱟᱲᱤ', 'region': 'India'},
    'sd': {'name': 'Sindhi', 'native': 'سنڌي', 'region': 'India'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'region': 'India'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'region': 'India'},
    'ur': {'name': 'Urdu', 'native': 'اردو', 'region': 'India'},
    
    # English (Indian & International)
    'en': {'name': 'English', 'native': 'English', 'region': 'Global'},
    'en-IN': {'name': 'English (India)', 'native': 'English (India)', 'region': 'India'},
    'en-US': {'name': 'English (US)', 'native': 'English (US)', 'region': 'USA'},
    'en-GB': {'name': 'English (UK)', 'native': 'English (UK)', 'region': 'UK'},
    
    # Major Global Languages
    'es': {'name': 'Spanish', 'native': 'Español', 'region': 'Spain/Latin America'},
    'fr': {'name': 'French', 'native': 'Français', 'region': 'France'},
    'de': {'name': 'German', 'native': 'Deutsch', 'region': 'Germany'},
    'it': {'name': 'Italian', 'native': 'Italiano', 'region': 'Italy'},
    'pt': {'name': 'Portuguese', 'native': 'Português', 'region': 'Portugal/Brazil'},
    'ru': {'name': 'Russian', 'native': 'Русский', 'region': 'Russia'},
    'ar': {'name': 'Arabic', 'native': 'العربية', 'region': 'Middle East'},
    'zh': {'name': 'Chinese (Simplified)', 'native': '简体中文', 'region': 'China'},
    'zh-TW': {'name': 'Chinese (Traditional)', 'native': '繁體中文', 'region': 'Taiwan'},
    'ja': {'name': 'Japanese', 'native': '日本語', 'region': 'Japan'},
    'ko': {'name': 'Korean', 'native': '한국어', 'region': 'Korea'},
    'id': {'name': 'Indonesian', 'native': 'Bahasa Indonesia', 'region': 'Indonesia'},
    'th': {'name': 'Thai', 'native': 'ไทย', 'region': 'Thailand'},
    'vi': {'name': 'Vietnamese', 'native': 'Tiếng Việt', 'region': 'Vietnam'},
    'tr': {'name': 'Turkish', 'native': 'Türkçe', 'region': 'Turkey'},
    'fa': {'name': 'Persian', 'native': 'فارسی', 'region': 'Iran'},
    'he': {'name': 'Hebrew', 'native': 'עברית', 'region': 'Israel'},
    'sw': {'name': 'Swahili', 'native': 'Kiswahili', 'region': 'East Africa'},
}

# Default language (supports both Hindi and English for Indian users)
DEFAULT_LANGUAGE = 'en-IN'  # English (India) - gives Romanized output for mixed Hindi-English

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VOICE MAPPING (edge-speech_synthesis Neural Voices)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDGE_TTS_VOICES = {
    # Indian Languages (PREMIUM HD Dragon Neural Voices - Best Available)
    'hi': ['hi-IN-SwaraNeural', 'hi-IN-MadhurNeural'],  # Hindi - Warm, clear (best available)
    'en-IN': ['en-IN-Meera:DragonHDLatestNeural', 'en-IN-Aarti:DragonHDLatestNeural', 'en-IN-Arjun:DragonHDLatestNeural', 'en-IN-NeerjaExpressiveNeural'],  # English (India) - PREMIUM HD voices
    'ta': ['ta-IN-PallaviNeural', 'ta-IN-ValluvarNeural'],  # Tamil - Smooth
    'te': ['te-IN-ShrutiNeural', 'te-IN-MohanNeural'],  # Telugu - Melodic
    'bn': ['bn-IN-TanishaaNeural', 'bn-IN-BashkarNeural'],  # Bengali - Expressive
    'mr': ['mr-IN-AarohiNeural', 'mr-IN-ManoharNeural'],  # Marathi - Rich tone
    'gu': ['gu-IN-DhwaniNeural', 'gu-IN-NiranjanNeural'],  # Gujarati - Pleasant
    'kn': ['kn-IN-SapnaNeural', 'kn-IN-GaganNeural'],  # Kannada - Articulate
    'ml': ['ml-IN-SobhanaNeural', 'ml-IN-MidhunNeural'],  # Malayalam - Smooth
    'pa': ['pa-IN-SuhitaNeural', 'pa-IN-GagandeepNeural'],  # Punjabi - Energetic
    'ur': ['ur-IN-GulNeural', 'ur-IN-SalmanNeural'],  # Urdu - Refined
    
    # Global Languages (Premium Expressive Neural Voices)
    'en': ['en-US-VaaniNeural', 'en-US-JennyMultilingualNeural', 'en-US-AndrewNeural'],  # English (US) - Very natural, conversational
    'en-US': ['en-US-VaaniNeural', 'en-US-JennyMultilingualNeural', 'en-US-AndrewNeural'],
    'en-GB': ['en-GB-SoniaNeural', 'en-GB-RyanNeural'],
    'es': ['es-ES-ElviraNeural', 'es-MX-DaliaNeural', 'es-ES-AlvaroNeural'],  # Spanish - Warm & clear
    'fr': ['fr-FR-DeniseNeural', 'fr-FR-HenriNeural'],  # French - Sophisticated
    'de': ['de-DE-KatjaNeural', 'de-DE-ConradNeural'],  # German - Clear & precise
    'it': ['it-IT-ElsaNeural', 'it-IT-IsabellaNeural', 'it-IT-DiegoNeural'],  # Italian - Melodic
    'pt': ['pt-BR-FranciscaNeural', 'pt-BR-ThalitaNeural', 'pt-BR-AntonioNeural'],  # Portuguese - Warm
    'ru': ['ru-RU-SvetlanaNeural', 'ru-RU-DariyaNeural', 'ru-RU-DmitryNeural'],  # Russian - Rich
    'ar': ['ar-SA-ZariyahNeural', 'ar-EG-SalmaNeural', 'ar-SA-HamedNeural'],  # Arabic - Expressive
    'zh': ['zh-CN-XiaoxiaoNeural', 'zh-CN-XiaoyiNeural', 'zh-CN-YunxiNeural'],  # Chinese - Natural
    'zh-TW': ['zh-TW-HsiaoChenNeural', 'zh-TW-HsiaoYuNeural', 'zh-TW-YunJheNeural'],  # Chinese (Traditional)
    'ja': ['ja-JP-NanamiNeural', 'ja-JP-AoiNeural', 'ja-JP-KeitaNeural'],  # Japanese - Polite & clear
    'ko': ['ko-KR-SunHiNeural', 'ko-KR-InJoonNeural'],  # Korean - Natural
    'id': ['id-ID-GadisNeural', 'id-ID-ArdiNeural'],  # Indonesian - Friendly
    'th': ['th-TH-PremwadeeNeural', 'th-TH-AcharaNeural', 'th-TH-NiwatNeural'],  # Thai - Pleasant
    'vi': ['vi-VN-HoaiMyNeural', 'vi-VN-NamMinhNeural'],  # Vietnamese - Melodic
    'tr': ['tr-TR-EmelNeural', 'tr-TR-AhmetNeural'],  # Turkish - Dynamic
    'fa': ['fa-IR-DilaraNeural', 'fa-IR-FaridNeural'],  # Persian - Elegant
    'he': ['he-IL-HilaNeural', 'he-IL-AvriNeural'],  # Hebrew - Clear
    'sw': ['sw-KE-ZuriNeural', 'sw-KE-RafikiNeural'],  # Swahili - Warm
}

# Voice gender preference
PREFERRED_VOICE_GENDER = 'female'  # 'female', 'male', or 'any'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TTS ENGINE CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# TTS fallback priority
TTS_ENGINE_PRIORITY = ['edge-speech_synthesis', 'pyspeech_synthesisx3', 'os-native']

# TTS reliability settings
TTS_RETRY_ATTEMPTS = 2  # Retry speech this many times on failure
TTS_TIMEOUT = 120  # Maximum seconds for single speech operation (increased for long multilingual responses)
TTS_AUDIO_BUFFER_DELAY = 0.3  # Seconds to wait for audio buffer readiness

# pyspeech_synthesisx3 settings (when used as fallback)
PYTTSX3_RATE = 175  # Speaking rate (words per minute)
PYTTSX3_VOLUME = 0.9  # Volume (0.0 to 1.0)
PYTTSX3_FRESH_ENGINE_PER_SPEECH = True  # Fix reuse bug: create new engine each time

# edge-speech_synthesis settings (optimized for natural conversation)
EDGE_TTS_RATE = "+5%"  # Slightly faster for more dynamic feel
EDGE_TTS_VOLUME = "+10%"  # Slightly louder for clarity
EDGE_TTS_PITCH = "+2Hz"  # Warmer, more pleasant tone

# OS Native TTS (final fallback)
OS_NATIVE_VOICES = {
    'darwin': {  # macOS
        'hi': 'Lekha',
        'en-IN': 'Rishi',
        'default': 'Samantha'
    },
    'linux': {
        'default': 'english'
    },
    'win32': {
        'default': 'Microsoft David Desktop'
    }
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI ENGINE CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Gemini multilingual instructions
GEMINI_SYSTEM_INSTRUCTIONS = f"""You are {ASSISTANT_NAME}, a warm, intelligent multilingual voice assistant.

CRITICAL RULES:
1. ALWAYS respond in the SAME LANGUAGE as the user's input
2. Detect language automatically - never ask which language to use
3. Support mixed-language input (Hinglish, Tanglish, etc.) - respond in the primary language
4. Use natural, conversational phrasing - avoid robotic/literal translations
5. Match regional tone and cultural context where possible
6. Keep responses concise for voice interaction (2-3 sentences max unless asked for details)
7. Be warm, helpful, and personalityble

LANGUAGE HANDLING:
- If user writes in Hindi, respond in Hindi
- If user writes in Tamil, respond in Tamil
- If user mixes English + Hindi (Hinglish), respond primarily in Hindi
- If unsure, default to English (India) tone
- Preserve the user's choice of script (Devanagari, Latin, etc.)

PERSONALITY:
- Friendly but professional
- Patient and encouraging
- Culturally sensitive
- Conversational, not formal
- Use appropriate greetings for time of day and culture

Remember: You're a VOICE assistant - keep responses naturally speakable."""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUDIO & PLAYBACK SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Audio player settings
DEFAULT_VOLUME = 0.9  # Default playback volume (0.0 to 1.0)
DOWNLOAD_AUDIO = True  # Download music before playing (more reliable)
VLC_NETWORK_CACHING = 3000  # VLC network cache (ms)
BUFFER_SIZE = 2048  # Audio buffer size
MAX_QUEUE_SIZE = 50  # Maximum queued songs

# Audio ducking (lower music volume during speech)
ENABLE_AUDIO_DUCKING = True
MUSIC_DUCKED_VOLUME = 0.3  # Music volume during speech

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING & DEBUGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Logging
DEBUG_MODE = False  # Verbose logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/vaani.log"

# Audio verification
LOG_AUDIO_VERIFICATION = True  # Log when audio actually plays
LOG_LANGUAGE_DETECTION = True  # Log detected languages

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIRECTORIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEMP_AUDIO_DIR = "temp/audio"
LOG_DIR = "logs"
DATA_DIR = "data"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ERROR MESSAGES (Multilingual)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ERROR_MESSAGES = {
    'en': {
        'speech_synthesis_failure': "Sorry, my voice glitched for a moment.",
        'music_not_found': "I couldn't find that song.",
        'music_playback_failed': "Sorry, I had trouble playing that.",
        'no_internet': "I need an internet connection for that.",
    },
    'hi': {
        'speech_synthesis_failure': "माफ़ करें, मेरी आवाज़ में कुछ गड़बड़ी हुई।",
        'music_not_found': "मुझे वह गाना नहीं मिला।",
        'music_playback_failed': "माफ़ करें, मुझे वो बजाने में परेशानी हुई।",
        'no_internet': "इसके लिए मुझे इंटरनेट कनेक्शन चाहिए।",
    },
    'ta': {
        'speech_synthesis_failure': "மன்னிக்கவும், எனது குரல் சிக்கல் உள்ளது.",
        'music_not_found': "அந்த பாடலை என்னால் கண்டுபிடிக்க முடியவில்லை.",
        'music_playback_failed': "மன்னிக்கவும், அதை இயக்குவதில் சிக்கல்.",
        'no_internet': "இதற்கு எனக்கு இணைய இணைப்பு தேவை.",
    },
    'te': {
        'speech_synthesis_failure': "క్షమించండి, నా వాయిస్ లో సమస్య వచ్చింది.",
        'music_not_found': "ఆ పాటను నేను కనుగొనలేకపోయాను.",
        'music_playback_failed': "క్షమించండి, దానిని ప్లే చేయడంలో సమస్య.",
        'no_internet': "దీని కోసం నాకు ఇంటర్నెట్ కనెక్షన్ కావాలి.",
    },
    'bn': {
        'speech_synthesis_failure': "দু��ঃখিত, আমার কণ্ঠে সমস্যা হয়েছে।",
        'music_not_found': "আমি সেই গানটি খুঁজে পাইনি।",
        'music_playback_failed': "দুঃখিত, এটি বাজাতে সমস্যা হয়েছে।",
        'no_internet': "এর জন্য আমার ইন্টারনেট সংযোগ প্রয়োজন।",
    },
}

# Default to English if language not found
def get_error_message(error_key: str, language: str = 'en') -> str:
    """Get localized error message"""
    return ERROR_MESSAGES.get(language, ERROR_MESSAGES['en']).get(
        error_key, 
        ERROR_MESSAGES['en'][error_key]
    )
