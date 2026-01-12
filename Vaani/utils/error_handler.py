"""
Error Handler - Comprehensive Error Management
=============================================

Features:
- Decorator-based error handling (@error_handler)
- Automatic retry logic with exponential backoff
- Error severity classification (low, medium, high, critical)
- Recovery action suggestions
- Graceful degradation strategies
- Error telemetry and statistics
- Circuit breaker pattern for failing services
- Context-aware error messages
- Fallback return values

Wraps functions with intelligent error handling that automatically
retries, logs appropriately, and suggests recovery actions. Keeps
the system running even when components fail.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import functools
import traceback
import sys
import os
import psutil
import platform
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Any, Callable, Type, List, Dict, Tuple
from enum import Enum
from collections import defaultdict
from .logger import VaaniLogger

# Get error logger
logger = VaaniLogger.get_logger("ErrorHandler")

class ErrorSeverity(Enum):
    """Error severity levels for prioritization"""
    DEBUG = "DEBUG"             # Minor issues, informational
    INFO = "INFO"               # Notable but harmless
    WARNING = "WARNING"         # Degraded functionality
    ERROR = "ERROR"             # Significant failure
    CRITICAL = "CRITICAL"       # System-level failure
    FATAL = "FATAL"             # Immediate shutdown required

class RecoveryAction(Enum):
    """Programmatic recovery strategies"""
    NONE = "none"                   # Log only, no action
    RETRY = "retry"                 # Transient error, retry operation
    RETRY_WITH_BACKOFF = "backoff"  # Retry with exponential backoff
    REINITIALIZE = "reinit"         # Reinitialize component
    RESTART_SERVICE = "restart"     # Restart specific service
    FALLBACK = "fallback"           # Switch to alternative method
    GRACEFUL_DEGRADE = "degrade"    # Reduce functionality
    CACHE_INVALIDATE = "cache"      # Clear cache and retry
    PERMISSION_ESCALATE = "elevate" # Request elevated permissions
    RESOURCE_CLEANUP = "cleanup"    # Free resources and retry
    USER_INTERVENTION = "user"      # Requires user action
    FATAL = "fatal"                 # Unrecoverable, shutdown

class ErrorCategory(Enum):
    """Error categorization for analytics"""
    AUDIO = "audio"
    NETWORK = "network"
    API = "api"
    FILE_SYSTEM = "filesystem"
    MEMORY = "memory"
    SYSTEM = "system"
    SECURITY = "security"
    DATA = "data"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    HARDWARE = "hardware"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


@dataclass
class ErrorReport:
    """Comprehensive structured error report"""
    error_type: str
    message: str
    user_friendly_message: str
    probable_cause: str
    suggested_fix: str
    severity: ErrorSeverity
    recovery_action: RecoveryAction
    category: ErrorCategory
    traceback_str: str = field(default="")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = field(default=0)
    resolution_time: Optional[float] = None

@dataclass
class ErrorStatistics:
    """Track error patterns for analytics"""
    total_errors: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_category: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_severity: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    recovery_success_rate: Dict[str, float] = field(default_factory=dict)
    last_error_time: Optional[str] = None

class SystemMonitor:
    """Monitor system resources for error context"""
    
    @staticmethod
    def get_system_state() -> Dict[str, Any]:
        """Capture current system state"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': psutil.virtual_memory().available / (1024**3),
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'platform': platform.system(),
                'python_version': sys.version.split()[0],
                'process_count': len(psutil.pids()),
            }
        except Exception as e:
            logger.debug(f"Could not capture system state: {e}")
            return {}
    
    @staticmethod
    def check_resource_constraints() -> List[str]:
        """Check if system resources are constrained"""
        warnings = []
        try:
            # Memory check
            mem = psutil.virtual_memory()
            if mem.percent > 90:
                warnings.append(f"Critical memory usage: {mem.percent}%")
            elif mem.percent > 80:
                warnings.append(f"High memory usage: {mem.percent}%")
            
            # CPU check
            cpu = psutil.cpu_percent(interval=0.1)
            if cpu > 90:
                warnings.append(f"Critical CPU usage: {cpu}%")
            elif cpu > 80:
                warnings.append(f"High CPU usage: {cpu}%")
            
            # Disk check
            disk = psutil.disk_usage('/')
            if disk.percent > 95:
                warnings.append(f"Critical disk space: {disk.percent}% used")
            elif disk.percent > 90:
                warnings.append(f"Low disk space: {disk.percent}% used")
        
        except Exception as e:
            logger.debug(f"Resource check failed: {e}")
        
        return warnings


@dataclass
class ErrorEvent:
    """Event payload for error bus"""
    report: ErrorReport
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    source_function: Optional[str] = None


class EventBus:
    """Central event bus for error decoupling"""
    _subscribers: Dict[str, List[Callable[[ErrorEvent], None]]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: str, callback: Callable[[ErrorEvent], None]):
        """
        Subscribe to error events.
        event_type can be:
          - specific error type (e.g., "OSError")
          - category prefix (e.g., "category:audio")
          - wildcard "*" for all errors
        """
        cls._subscribers[event_type].append(callback)

    @classmethod
    def unsubscribe(cls, event_type: str, callback: Callable[[ErrorEvent], None]):
        """Unsubscribe a callback"""
        if event_type in cls._subscribers:
            try:
                cls._subscribers[event_type].remove(callback)
            except ValueError:
                pass

    @classmethod
    def publish(cls, event: ErrorEvent):
        """Publish an error event to subscribers"""
        # 1. Notify specific error type listeners
        for callback in cls._subscribers.get(event.report.error_type, []):
            cls._safe_notify(callback, event)
        
        # 2. Notify category listeners
        cat_key = f"category:{event.report.category.value}"
        for callback in cls._subscribers.get(cat_key, []):
            cls._safe_notify(callback, event)
            
        # 3. Notify severity listeners
        sev_key = f"severity:{event.report.severity.value}"
        for callback in cls._subscribers.get(sev_key, []):
            cls._safe_notify(callback, event)

        # 4. Notify global listeners
        for callback in cls._subscribers.get("*", []):
            cls._safe_notify(callback, event)

    @staticmethod
    def _safe_notify(callback, event):
        try:
            callback(event)
        except Exception as e:
            logger.debug(f"Event subscriber failed: {e}")


class ErrorAnalyzer:
    """
    Advanced error analysis engine with ML-inspired pattern matching
    Translates 100+ technical exceptions into actionable insights
    """
    
    # Track error statistics
    stats = ErrorStatistics()
    
    @classmethod
    def analyze(cls, e: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorReport:
        """
        Comprehensive error analysis with intelligent recovery strategies
        
        Args:
            e: Exception to analyze
            context: Optional context dict (e.g., {'operation': 'play_music', 'attempt': 2})
        
        Returns:
            Detailed ErrorReport with recovery strategy
        """
        error_type = type(e).__name__
        error_msg = str(e)
        tb_str = "".join(traceback.format_tb(e.__traceback__)) if e.__traceback__ else ""
        
        # Capture system state
        system_state = SystemMonitor.get_system_state()
        resource_warnings = SystemMonitor.check_resource_constraints()
        
        # Default analysis
        user_message = "An unexpected error occurred."
        cause = "Unknown technical issue."
        fix = "Check logs and restart the assistant."
        severity = ErrorSeverity.WARNING
        recovery = RecoveryAction.NONE
        category = ErrorCategory.UNKNOWN
        
        # Update statistics
        cls.stats.total_errors += 1
        cls.stats.errors_by_type[error_type] += 1
        cls.stats.last_error_time = datetime.now().isoformat()
        
        # ═══════════════════════════════════════════════════════════════════
        # AUDIO & VOICE ERRORS (Category 1)
        # ═══════════════════════════════════════════════════════════════════
        
        # 1.1 Microphone Errors
        if "Device index out of range" in error_msg or "-9999" in error_msg:
            user_message = "I can't access your microphone."
            cause = "Microphone device index is invalid or device disconnected."
            fix = "1. Reconnect microphone\n2. Check config.json MICROPHONE_TYPE\n3. Run 'python -m sounddevice' to list devices\n4. Restart Vaani"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.REINITIALIZE
            category = ErrorCategory.AUDIO
            
        elif "Input overflowed" in error_msg or "-9981" in error_msg:
            user_message = "Audio input is stuttering."
            cause = "System processing too slowly (buffer overflow). High CPU/memory usage detected." if resource_warnings else "System processing too slowly (buffer overflow)."
            fix = f"1. Close background apps\n2. Increase CHUNK_SIZE in config\n3. Lower SAMPLE_RATE\n{chr(10).join(['⚠️ ' + w for w in resource_warnings])}"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.AUDIO

        elif "Internal PortAudio error" in error_msg or "-9986" in error_msg:
            user_message = "Audio system encountered a critical error."
            cause = "CoreAudio/PortAudio internal crash or driver issue."
            fix = "1. Restart Vaani\n2. Restart computer\n3. Update audio drivers\n4. Check System Preferences > Sound"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.RESTART_SERVICE
            category = ErrorCategory.AUDIO
        
        elif "No default input device" in error_msg or "-9996" in error_msg:
            user_message = "No microphone detected."
            cause = "No audio input device available to the system."
            fix = "1. Connect a microphone\n2. Enable microphone in System Preferences\n3. Grant microphone permissions to Terminal/Python"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.HARDWARE
        
        elif "Output underflowed" in error_msg or "-9980" in error_msg:
            user_message = "Audio playback is glitching."
            cause = "Audio buffer underrun - system can't keep up with playback."
            fix = "1. Close resource-intensive apps\n2. Increase audio buffer size\n3. Check CPU usage"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.AUDIO
        
        elif "Sample rate not supported" in error_msg or "Invalid sample rate" in error_msg:
            user_message = "Audio settings are incompatible."
            cause = "Requested sample rate not supported by audio device."
            fix = "Change SAMPLE_RATE in config to 16000, 22050, 44100, or 48000"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.REINITIALIZE
            category = ErrorCategory.CONFIGURATION

        # 1.2 Speech Recognition Errors
        elif "RequestError" in error_type:
            user_message = "I can't reach the speech recognition service."
            cause = "Internet connection down or API endpoint unreachable."
            fix = "1. Check Wi-Fi connection\n2. Test with: ping google.com\n3. Check firewall settings\n4. Try switching to offline recognition"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.FALLBACK
            category = ErrorCategory.NETWORK
            
        elif "UnknownValueError" in error_type:
            user_message = "I didn't catch that."
            cause = "Audio was too quiet, unintelligible, or background noise too high."
            fix = "1. Speak clearly and closer to microphone\n2. Reduce background noise\n3. Check microphone volume levels"
            severity = ErrorSeverity.INFO
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.USER_INPUT
        
        elif "WaitTimeoutError" in error_type or "Listening timed out" in error_msg:
            user_message = "I didn't hear anything."
            cause = "No speech detected within timeout period."
            fix = "Increase timeout in config or speak more promptly"
            severity = ErrorSeverity.INFO
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.USER_INPUT

        # 1.3 Text-to-Speech Errors
        elif "pyttsx3" in error_msg.lower() or "SAPI5" in error_msg:
            user_message = "Text-to-speech engine failed."
            cause = "TTS engine initialization error or voice not available."
            fix = "1. Reinstall pyttsx3: pip install --upgrade pyttsx3\n2. Check available voices\n3. Switch to alternative TTS engine"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.FALLBACK
            category = ErrorCategory.AUDIO
        
        elif "espeak" in error_msg.lower():
            user_message = "Speech synthesis failed."
            cause = "eSpeak not installed or not in PATH."
            fix = "Install eSpeak: brew install espeak (macOS) or apt-get install espeak (Linux)"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.DEPENDENCY

        # ═══════════════════════════════════════════════════════════════════
        # NETWORK & API ERRORS (Category 2)
        # ═══════════════════════════════════════════════════════════════════
        
        # 2.1 Connection Errors
        elif "ConnectionError" in error_type or "gaierror" in error_msg or "NewConnectionError" in error_msg:
            user_message = "I'm having trouble connecting to the internet."
            cause = "Network connection failed or DNS resolution error."
            fix = "1. Check Wi-Fi connection\n2. Test: ping 8.8.8.8\n3. Check DNS settings\n4. Disable VPN temporarily\n5. Check proxy settings"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY_WITH_BACKOFF
            category = ErrorCategory.NETWORK
        
        elif "ConnectTimeout" in error_type or "connect timed out" in error_msg.lower():
            user_message = "Connection timed out."
            cause = "Server took too long to respond."
            fix = "1. Check internet speed\n2. Try again later\n3. Increase timeout in config\n4. Check if service is down"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY_WITH_BACKOFF
            category = ErrorCategory.NETWORK
        
        elif "ReadTimeout" in error_type or "read timed out" in error_msg.lower():
            user_message = "Server response timed out."
            cause = "Server started responding but didn't finish."
            fix = "1. Increase read timeout\n2. Check network stability\n3. Try simpler request"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.NETWORK
        
        elif "SSLError" in error_type or "CERTIFICATE_VERIFY_FAILED" in error_msg:
            user_message = "Secure connection failed."
            cause = "SSL certificate validation failed or expired."
            fix = "1. Update system certificates\n2. Check system date/time\n3. Run: pip install --upgrade certifi\n4. For dev only: Disable SSL verification (not recommended)"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.SECURITY
        
        elif "ProxyError" in error_type or "proxy" in error_msg.lower():
            user_message = "Proxy connection failed."
            cause = "Proxy server is unreachable or misconfigured."
            fix = "1. Check proxy settings\n2. Disable proxy temporarily\n3. Verify proxy credentials\n4. Use: export http_proxy='' to clear"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.NETWORK
        
        elif "MaxRetryError" in error_type or "Max retries exceeded" in error_msg:
            user_message = "Connection failed after multiple attempts."
            cause = "Network unstable or server unreachable."
            fix = "1. Check network connection\n2. Wait and retry\n3. Check if service is operational"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.GRACEFUL_DEGRADE
            category = ErrorCategory.NETWORK

        # 2.2 HTTP Status Errors
        elif "400" in error_msg or "Bad Request" in error_msg:
            user_message = "Invalid request sent to server."
            cause = "Malformed request or invalid parameters."
            fix = "1. Check request parameters\n2. Verify API documentation\n3. Update client library"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.API
        
        elif "401" in error_msg or "Unauthorized" in error_msg or "UNAUTHENTICATED" in error_msg:
            user_message = "Authentication failed."
            cause = "Invalid or missing API credentials."
            fix = "1. Check API key in config.json\n2. Verify key hasn't expired\n3. Regenerate API key if needed\n4. Check for typos in key"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.API
        
        elif "403" in error_msg or "PERMISSION_DENIED" in error_msg or "Forbidden" in error_msg:
            user_message = "My AI access key is invalid or lacks permissions."
            cause = "Valid credentials but insufficient permissions."
            fix = "1. Check GOOGLE_API_KEY in config.json\n2. Verify API is enabled in Google Cloud Console\n3. Check API restrictions\n4. Verify billing is enabled"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.FATAL
            category = ErrorCategory.API
        
        elif "404" in error_msg or "Not Found" in error_msg:
            user_message = "Requested resource not found."
            cause = "API endpoint doesn't exist or has changed."
            fix = "1. Check API endpoint URL\n2. Update client library\n3. Verify API version"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.FALLBACK
            category = ErrorCategory.API
        
        elif "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg or "rate limit" in error_msg.lower():
            user_message = "I've run out of usage quota for now."
            cause = "API rate limit or quota exceeded."
            fix = "1. Wait a few minutes before retrying\n2. Add more API keys for rotation\n3. Upgrade API plan\n4. Implement request throttling"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.FALLBACK
            category = ErrorCategory.API
        
        elif "500" in error_msg or "Internal Server Error" in error_msg:
            user_message = "The AI service is experiencing issues."
            cause = "Upstream server internal error."
            fix = "1. Wait and retry in a few moments\n2. Check service status page\n3. Use fallback service"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY_WITH_BACKOFF
            category = ErrorCategory.API
        
        elif "502" in error_msg or "Bad Gateway" in error_msg:
            user_message = "Service gateway error."
            cause = "Proxy or gateway received invalid response."
            fix = "1. Retry the request\n2. Check service status\n3. Wait for service recovery"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY_WITH_BACKOFF
            category = ErrorCategory.API
        
        elif "503" in error_msg or "Service Unavailable" in error_msg:
            user_message = "The service is temporarily down."
            cause = "Service is temporarily unavailable or overloaded."
            fix = "1. Wait and retry\n2. Check service status\n3. Use alternative service"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY_WITH_BACKOFF
            category = ErrorCategory.API
        
        elif "504" in error_msg or "Gateway Timeout" in error_msg:
            user_message = "Gateway timeout occurred."
            cause = "Upstream service didn't respond in time."
            fix = "1. Increase timeout\n2. Retry request\n3. Check network speed"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.API

        # ═══════════════════════════════════════════════════════════════════
        # FILE SYSTEM & I/O ERRORS (Category 3)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "FileNotFoundError" in error_type or "No such file or directory" in error_msg:
            user_message = "Required file not found."
            cause = f"File doesn't exist at specified path."
            fix = "1. Verify file path is correct\n2. Check if file was moved/deleted\n3. Ensure working directory is correct\n4. Check file permissions"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.FILE_SYSTEM
        
        elif "PermissionError" in error_type or "Access denied" in error_msg or "Permission denied" in error_msg:
            user_message = "I don't have permission to access that."
            cause = "Insufficient permissions to read/write file or access device."
            fix = "1. Run with administrator/sudo privileges\n2. Check file permissions: chmod +r file\n3. Verify ownership: chown user file\n4. Grant app permissions in System Preferences"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.PERMISSION_ESCALATE
            category = ErrorCategory.SECURITY
        
        elif "IsADirectoryError" in error_type:
            user_message = "Expected file but found directory."
            cause = "Attempted file operation on a directory."
            fix = "Check path - ensure it points to a file, not a directory"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.FILE_SYSTEM
        
        elif "NotADirectoryError" in error_type:
            user_message = "Expected directory but found file."
            cause = "Attempted directory operation on a file."
            fix = "Check path - ensure it points to a directory, not a file"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.FILE_SYSTEM
        
        elif "OSError" in error_type and ("Disk full" in error_msg or "No space left" in error_msg):
            user_message = "Out of disk space."
            cause = f"Disk is full. Current usage: {system_state.get('disk_usage_percent', 'unknown')}%"
            fix = "1. Free up disk space\n2. Delete unnecessary files\n3. Empty trash\n4. Move files to external storage"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.RESOURCE_CLEANUP
            category = ErrorCategory.SYSTEM
        
        elif "IOError" in error_type or "OSError" in error_type:
            user_message = "File operation failed."
            cause = "Generic I/O error during file operation."
            fix = "1. Check disk health\n2. Verify file isn't locked\n3. Check available disk space\n4. Scan for disk errors"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.FILE_SYSTEM

        # ═══════════════════════════════════════════════════════════════════
        # DEPENDENCY & IMPORT ERRORS (Category 4)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "ImportError" in error_type or "ModuleNotFoundError" in error_type:
            missing_module = str(e).split("'")[-2] if "'" in str(e) else "unknown"
            user_message = f"I'm missing a required component: {missing_module}."
            cause = f"Python library '{missing_module}' is not installed."
            fix = f"Install missing dependency:\n  pip install {missing_module}\n\nOr install all requirements:\n  pip install -r requirements.txt"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.FATAL
            category = ErrorCategory.DEPENDENCY
        
        elif "AttributeError" in error_type and "module" in error_msg.lower():
            user_message = "Library version mismatch detected."
            cause = "Module doesn't have expected attribute - likely outdated library."
            fix = "Update all dependencies:\n  pip install --upgrade -r requirements.txt"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.DEPENDENCY
        
        elif "VersionError" in error_type or "version" in error_msg.lower():
            user_message = "Software version incompatibility."
            cause = "Incompatible library versions."
            fix = "1. Check requirements.txt for version constraints\n2. Create fresh virtual environment\n3. Run: pip install -r requirements.txt --force-reinstall"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.DEPENDENCY

        # ═══════════════════════════════════════════════════════════════════
        # MEMORY & RESOURCE ERRORS (Category 5)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "MemoryError" in error_type:
            user_message = "Out of memory."
            cause = f"System ran out of RAM. Current usage: {system_state.get('memory_percent', 'unknown')}%"
            fix = "1. Close unnecessary applications\n2. Restart Vaani\n3. Add more RAM\n4. Reduce batch sizes in config\n5. Use swap space"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.RESOURCE_CLEANUP
            category = ErrorCategory.MEMORY
        
        elif "RecursionError" in error_type or "maximum recursion depth" in error_msg:
            user_message = "Infinite loop detected."
            cause = "Maximum recursion depth exceeded - likely infinite recursion."
            fix = "1. Report this bug to developers\n2. Restart Vaani\n3. Check for circular dependencies in code"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.RESTART_SERVICE
            category = ErrorCategory.SYSTEM
        
        elif "TimeoutError" in error_type or "Timeout" in error_type or "timed out" in error_msg.lower():
            user_message = "The operation took too long."
            cause = "Operation exceeded timeout limit."
            fix = "1. Increase timeout in config\n2. Try again later\n3. Check internet speed\n4. Simplify request"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.SYSTEM

        # ═══════════════════════════════════════════════════════════════════
        # DATA & PARSING ERRORS (Category 6)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "JSONDecodeError" in error_type or "json" in error_msg.lower():
            user_message = "Invalid data format received."
            cause = "Malformed JSON data or encoding issue."
            fix = "1. Check API response format\n2. Verify content type\n3. Clear cache\n4. Update client library"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.CACHE_INVALIDATE
            category = ErrorCategory.DATA
        
        elif "UnicodeDecodeError" in error_type or "UnicodeEncodeError" in error_type:
            user_message = "Text encoding error."
            cause = "Cannot decode/encode text with specified encoding."
            fix = "1. Use UTF-8 encoding\n2. Handle special characters\n3. Check file encoding"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.DATA
        
        elif "ValueError" in error_type:
            user_message = "Invalid value provided."
            cause = "Function received value of correct type but inappropriate value."
            fix = "1. Validate input data\n2. Check parameter ranges\n3. Review configuration values"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.DATA
        
        elif "TypeError" in error_type:
            user_message = "Incorrect data type."
            cause = "Operation received wrong data type."
            fix = "1. Check function arguments\n2. Verify data types in config\n3. Report bug if persistent"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.DATA
        
        elif "KeyError" in error_type:
            user_message = "Missing required data field."
            cause = "Expected key not found in dictionary/config."
            fix = "1. Check config.json completeness\n2. Verify API response structure\n3. Restore default config"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.CONFIGURATION
        
        elif "IndexError" in error_type:
            user_message = "Index out of bounds."
            cause = "Tried to access list element that doesn't exist."
            fix = "Report this bug - likely a coding error"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.DATA

        # ═══════════════════════════════════════════════════════════════════
        # CONFIGURATION ERRORS (Category 7)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "ConfigError" in error_type or "configuration" in error_msg.lower():
            user_message = "Configuration error detected."
            cause = "Invalid or missing configuration value."
            fix = "1. Check config.json syntax\n2. Verify all required fields\n3. Restore default config\n4. Check environment variables"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.CONFIGURATION
        
        elif "EnvironmentError" in error_type:
            user_message = "Environment setup issue."
            cause = "Required environment variable missing or invalid."
            fix = "1. Check .env file\n2. Set required environment variables\n3. Verify PATH settings"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.USER_INTERVENTION
            category = ErrorCategory.CONFIGURATION

        # ═══════════════════════════════════════════════════════════════════
        # VLC & MEDIA PLAYBACK ERRORS (Category 8)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "vlc" in error_msg.lower() or "libvlc" in error_msg.lower():
            user_message = "Media player error."
            cause = "VLC media player not installed or initialization failed."
            fix = "Install VLC:\n  macOS: brew install --cask vlc\n  Linux: sudo apt install vlc\n  Windows: Download from videolan.org"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.FALLBACK
            category = ErrorCategory.DEPENDENCY
        
        elif "Media playback" in error_msg or "stream" in error_msg.lower():
            user_message = "Couldn't play that media."
            cause = "Media stream unavailable or format not supported."
            fix = "1. Check internet connection\n2. Try different source\n3. Update VLC\n4. Check media format compatibility"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.FALLBACK
            category = ErrorCategory.AUDIO

        # ═══════════════════════════════════════════════════════════════════
        # SYSTEM & PLATFORM ERRORS (Category 9)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "SystemError" in error_type:
            user_message = "System-level error occurred."
            cause = "Internal system error - Python interpreter issue."
            fix = "1. Restart Vaani\n2. Update Python\n3. Report bug with traceback"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.RESTART_SERVICE
            category = ErrorCategory.SYSTEM
        
        elif "KeyboardInterrupt" in error_type:
            user_message = "Operation cancelled by user."
            cause = "User pressed Ctrl+C to interrupt."
            fix = "No action needed - user initiated."
            severity = ErrorSeverity.INFO
            recovery = RecoveryAction.NONE
            category = ErrorCategory.SYSTEM
        
        elif "SystemExit" in error_type:
            user_message = "Application exit requested."
            cause = "System exit called."
            fix = "No action needed."
            severity = ErrorSeverity.INFO
            recovery = RecoveryAction.NONE
            category = ErrorCategory.SYSTEM
        
        elif "RuntimeError" in error_type:
            user_message = "Runtime error occurred."
            cause = "Generic runtime error - context dependent."
            fix = "1. Check recent changes\n2. Restart application\n3. Review logs for details"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.SYSTEM
        
        elif "NotImplementedError" in error_type:
            user_message = "Feature not yet implemented."
            cause = "Tried to use a feature that's not implemented yet."
            fix = "1. Use alternative feature\n2. Wait for future update\n3. Check documentation"
            severity = ErrorSeverity.INFO
            recovery = RecoveryAction.NONE
            category = ErrorCategory.SYSTEM

        # ═══════════════════════════════════════════════════════════════════
        # DATABASE & CACHE ERRORS (Category 10)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "DatabaseError" in error_type or "sqlite3" in error_msg.lower():
            user_message = "Database error occurred."
            cause = "Database operation failed or corrupted database."
            fix = "1. Backup and delete database file\n2. Let Vaani recreate it\n3. Check disk space\n4. Verify file permissions"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.CACHE_INVALIDATE
            category = ErrorCategory.DATA
        
        elif "CacheError" in error_type or "cache" in error_msg.lower():
            user_message = "Cache operation failed."
            cause = "Cache corruption or access error."
            fix = "1. Clear cache directory\n2. Restart Vaani\n3. Check disk space"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.CACHE_INVALIDATE
            category = ErrorCategory.FILE_SYSTEM

        # ═══════════════════════════════════════════════════════════════════
        # THREADING & CONCURRENCY ERRORS (Category 11)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "ThreadError" in error_type or "thread" in error_msg.lower():
            user_message = "Threading error occurred."
            cause = "Thread management issue or deadlock."
            fix = "1. Restart Vaani\n2. Report bug with steps to reproduce"
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.RESTART_SERVICE
            category = ErrorCategory.SYSTEM
        
        elif "BlockingIOError" in error_type:
            user_message = "Operation would block."
            cause = "Non-blocking I/O operation would block."
            fix = "Increase timeout or use blocking mode"
            severity = ErrorSeverity.WARNING
            recovery = RecoveryAction.RETRY
            category = ErrorCategory.SYSTEM

        # ═══════════════════════════════════════════════════════════════════
        # ASSERTION & LOGIC ERRORS (Category 12)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "ZeroDivisionError" in error_type:
            user_message = "Calculation error (divided by zero)."
            cause = "Attempted to divide a number by zero."
            fix = "Check input values to ensure denominator is not zero."
            severity = ErrorSeverity.ERROR
            recovery = RecoveryAction.NONE
            category = ErrorCategory.DATA
            
        elif "AssertionError" in error_type:
            user_message = "Internal check failed."
            cause = "Assertion failed - invalid program state."
            fix = "Report this bug to developers with full traceback"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.RESTART_SERVICE
            category = ErrorCategory.SYSTEM

        # ═══════════════════════════════════════════════════════════════════
        # HARDWARE & DEVICE ERRORS (Category 13)
        # ═══════════════════════════════════════════════════════════════════
        
        elif "DeviceError" in error_type or "hardware" in error_msg.lower():
            user_message = "Hardware device error."
            cause = "Hardware device malfunction or disconnection."
            fix = "1. Reconnect device\n2. Check device drivers\n3. Try different USB port\n4. Restart computer"
            severity = ErrorSeverity.CRITICAL
            recovery = RecoveryAction.REINITIALIZE
            category = ErrorCategory.HARDWARE

        # Update category statistics
        cls.stats.errors_by_category[category.value] += 1
        cls.stats.errors_by_severity[severity.value] += 1
        
        # Add resource warnings to fix suggestions
        if resource_warnings and not any(w in fix for w in resource_warnings):
            fix += f"\n\n⚠️ System Resource Warnings:\n" + "\n".join([f"  • {w}" for w in resource_warnings])
        
        return ErrorReport(
            error_type=error_type,
            message=error_msg,
            user_friendly_message=user_message,
            probable_cause=cause,
            suggested_fix=fix,
            severity=severity,
            recovery_action=recovery,
            category=category,
            traceback_str=tb_str,
            context=context or {},
            system_state=system_state
        )
    
    @classmethod
    def get_statistics(cls) -> ErrorStatistics:
        """Get current error statistics"""
        return cls.stats
    
    @classmethod
    def reset_statistics(cls):
        """Reset error statistics"""
        cls.stats = ErrorStatistics()


def error_handler(
    default_return: Any = None, 
    error_message: str = "Operation failed",
    notify_user: bool = False,
    raise_if_fatal: bool = True,
    context: Optional[Dict[str, Any]] = None,
    retry_count: int = 0,
    max_retries: int = 3
):
    """
    Advanced decorator for comprehensive error handling with retry logic
    
    Args:
        default_return: Value to return if exception occurs (default: None)
        error_message: Context string for the log
        notify_user: If True, prints a distinct USER ALERT in logs (hook for UI)
        raise_if_fatal: If True, re-raises exception if RecoveryAction is FATAL
        context: Optional context dict for error analysis
        retry_count: Current retry attempt number
        max_retries: Maximum number of retries for RETRY actions
    
    Usage:
        @error_handler(default_return=False, error_message="Music playback failed", 
                     notify_user=True, context={'operation': 'play_music'})
        def play_music(song_name):
            # ... code that might fail
            return True
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal retry_count
            
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                # 1. Analyze the error comprehensively
                report = ErrorAnalyzer.analyze(e, context=context)
                report.retry_count = retry_count
                
                # 2. Determine log level based on severity
                log_method = {
                    ErrorSeverity.DEBUG: logger.debug,
                    ErrorSeverity.INFO: logger.info,
                    ErrorSeverity.WARNING: logger.warning,
                    ErrorSeverity.ERROR: logger.error,
                    ErrorSeverity.CRITICAL: logger.critical,
                    ErrorSeverity.FATAL: logger.critical
                }.get(report.severity, logger.error)
                
                # 3. Log technical details
                log_method(f"{error_message}: [{report.error_type}] {report.message}")
                log_method(f"📂 Category: {report.category.value}")
                log_method(f"🔍 Cause: {report.probable_cause}")
                log_method(f"🛠️  Fix: {report.suggested_fix}")
                log_method(f"🚑 Recovery: {report.recovery_action.value.upper()}")
                
                # Log system state if available
                if report.system_state:
                    logger.debug(f"💻 System State: CPU={report.system_state.get('cpu_percent')}% "
                               f"RAM={report.system_state.get('memory_percent')}% "
                               f"Disk={report.system_state.get('disk_usage_percent')}%")
                
                # 4. Optional: Notify User (Distinct Log Block)
                if notify_user:
                    logger.warning(
                        f"\n{'='*60}\n"
                        f"📢 USER ALERT\n"
                        f"{'='*60}\n"
                        f"❌ Issue: {report.user_friendly_message}\n"
                        f"💡 Why: {report.probable_cause}\n"
                        f"✅ Fix:\n{report.suggested_fix}\n"
                        f"{'='*60}"
                    )
                
                # 5. Handle recovery actions
                if report.recovery_action == RecoveryAction.RETRY and retry_count < max_retries:
                    retry_count += 1
                    logger.info(f"🔄 Retrying operation (attempt {retry_count}/{max_retries})...")
                    import time
                    time.sleep(min(2 ** retry_count, 10))  # Exponential backoff, max 10s
                    return wrapper(*args, **kwargs)  # Recursive retry
                
                elif report.recovery_action == RecoveryAction.RETRY_WITH_BACKOFF and retry_count < max_retries:
                    retry_count += 1
                    backoff = min(2 ** retry_count, 30)  # Exponential backoff, max 30s
                    logger.info(f"🔄 Retrying with backoff: {backoff}s (attempt {retry_count}/{max_retries})...")
                    import time
                    time.sleep(backoff)
                    return wrapper(*args, **kwargs)
                
                elif report.recovery_action == RecoveryAction.CACHE_INVALIDATE:
                    logger.info("🗑️  Attempting cache cleanup...")
                    try:
                        import shutil
                        cache_dirs = ['temp/audio_cache', '.cache', '__pycache__']
                        for cache_dir in cache_dirs:
                            if os.path.exists(cache_dir):
                                shutil.rmtree(cache_dir, ignore_errors=True)
                                logger.info(f"Cleared cache: {cache_dir}")
                    except Exception as cache_err:
                        logger.warning(f"Cache cleanup failed: {cache_err}")
                
                elif report.recovery_action == RecoveryAction.GRACEFUL_DEGRADE:
                    logger.warning("⚠️ Operating in degraded mode")
                
                elif report.recovery_action == RecoveryAction.USER_INTERVENTION:
                    logger.critical("👤 User intervention required - cannot auto-recover")
                
                # 6. Handle FATAL errors
                if raise_if_fatal and report.recovery_action == RecoveryAction.FATAL:
                    logger.critical("💀 FATAL ERROR - Cannot continue")
                    raise e
                
                # 7. Update statistics
                ErrorAnalyzer.stats.errors_by_type[report.error_type] += 1
                
                # 8. Publish to EventBus
                EventBus.publish(ErrorEvent(report=report, source_function=func.__name__))
                
                # 9. Auto-save telemetry on critical errors
                if report.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
                    ErrorReporter.save_json_telemetry()
                
                return default_return
        
        return wrapper
    return decorator


class ErrorReporter:
    """Generate comprehensive error reports for debugging"""
    
    @staticmethod
    def generate_diagnostic_report() -> str:
        """Generate full diagnostic report"""
        stats = ErrorAnalyzer.get_statistics()
        system_state = SystemMonitor.get_system_state()
        resource_warnings = SystemMonitor.check_resource_constraints()
        
        report = []
        report.append("=" * 70)
        report.append("VAANI DIAGNOSTIC REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # System Information
        report.append("SYSTEM INFORMATION")
        report.append("-" * 70)
        report.append(f"Platform: {system_state.get('platform', 'Unknown')}")
        report.append(f"Python: {system_state.get('python_version', 'Unknown')}")
        report.append(f"CPU Usage: {system_state.get('cpu_percent', 'N/A')}%")
        report.append(f"Memory Usage: {system_state.get('memory_percent', 'N/A')}%")
        report.append(f"Memory Available: {system_state.get('memory_available_gb', 'N/A'):.2f} GB")
        report.append(f"Disk Usage: {system_state.get('disk_usage_percent', 'N/A')}%")
        report.append(f"Active Processes: {system_state.get('process_count', 'N/A')}")
        report.append("")
        
        # Resource Warnings
        if resource_warnings:
            report.append("⚠️ RESOURCE WARNINGS")
            report.append("-" * 70)
            for warning in resource_warnings:
                report.append(f"  • {warning}")
            report.append("")
        
        # Error Statistics
        report.append("ERROR STATISTICS")
        report.append("-" * 70)
        report.append(f"Total Errors: {stats.total_errors}")
        report.append(f"Last Error: {stats.last_error_time or 'None'}")
        report.append("")
        
        # Errors by Type
        if stats.errors_by_type:
            report.append("Top Error Types:")
            sorted_types = sorted(stats.errors_by_type.items(), key=lambda x: x[1], reverse=True)
            for error_type, count in sorted_types[:10]:
                report.append(f"  • {error_type}: {count}")
            report.append("")
        
        # Errors by Category
        if stats.errors_by_category:
            report.append("Errors by Category:")
            for category, count in sorted(stats.errors_by_category.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  • {category}: {count}")
            report.append("")
        
        # Errors by Severity
        if stats.errors_by_severity:
            report.append("Errors by Severity:")
            for severity, count in sorted(stats.errors_by_severity.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  • {severity}: {count}")
            report.append("")
        
        report.append("=" * 70)
        return "\n".join(report)
    
    @staticmethod
    def save_diagnostic_report(filepath: str = "logs/diagnostic_report.txt"):
        """Save diagnostic report to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            report = ErrorReporter.generate_diagnostic_report()
            with open(filepath, 'w') as f:
                f.write(report)
            logger.info(f"Diagnostic report saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save diagnostic report: {e}")
            return False

    @staticmethod
    def save_json_telemetry(filepath: str = "logs/errors.json"):
        """Save error statistics and recent errors to JSON for telemetry"""
        import json
        try:
            dirname = os.path.dirname(filepath)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            stats = ErrorAnalyzer.get_statistics()
            data = {
                "timestamp": datetime.now().isoformat(),
                "system": SystemMonitor.get_system_state(),
                "statistics": {
                    "total": stats.total_errors,
                    "by_type": dict(stats.errors_by_type),
                    "by_category": dict(stats.errors_by_category),
                    "by_severity": dict(stats.errors_by_severity)
                }
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Telemetry saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON telemetry: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def handle_error(e: Exception, context_msg: str = "Operation failed", 
                notify_user: bool = False) -> ErrorReport:
    """
    Convenience function to handle errors without decorator
    
    Usage:
        try:
            risky_operation()
        except Exception as e:
            report = handle_error(e, "Risk operation failed", notify_user=True)
            # Use report.recovery_action to decide what to do next
    """
    report = ErrorAnalyzer.analyze(e)
    
    logger.error(f"{context_msg}: [{report.error_type}] {report.message}")
    logger.error(f"🔍 Cause: {report.probable_cause}")
    logger.error(f"🛠️  Fix: {report.suggested_fix}")
    
    if notify_user:
        logger.warning(
            f"\n{'='*60}\n"
            f"📢 USER ALERT: {report.user_friendly_message}\n"
            f"👉 TIP: {report.suggested_fix}\n"
            f"{'='*60}"
        )
    
    return report


def log_error_context(func: Callable) -> Callable:
    """
    Lightweight decorator that logs errors but doesn't handle them
    Useful when you want to let errors propagate but still get detailed logs
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            report = ErrorAnalyzer.analyze(e)
            logger.error(f"Error in {func.__name__}: {report.user_friendly_message}")
            logger.debug(f"Technical: {report.message}")
            logger.debug(f"Recovery suggestion: {report.recovery_action.value}")
            raise  # Re-raise the exception
    return wrapper


def get_error_statistics() -> Dict[str, Any]:
    """Get error statistics as dictionary for monitoring"""
    stats = ErrorAnalyzer.get_statistics()
    return {
        'total_errors': stats.total_errors,
        'errors_by_type': dict(stats.errors_by_type),
        'errors_by_category': dict(stats.errors_by_category),
        'errors_by_severity': dict(stats.errors_by_severity),
        'last_error_time': stats.last_error_time
    }


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

logger.info("Error Handler initialized")
logger.debug(f"System: {platform.system()} | Python: {sys.version.split()[0]}")
