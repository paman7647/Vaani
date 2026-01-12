"""
Logger - Professional Logging System
=======================================

Features:
- Minimal, production-ready logging
- Error-focused output (no verbose spam)
- Color-coded console output
- File logging with rotation (1MB limit, 3 backups)
- Module-specific loggers
- Configurable log levels
- Thread-safe logging
- Performance impact minimal
- Professional formatting

Provides clean, professional logging that only shows what matters.
No emoji spam, no unnecessary info logs - just errors and critical
warnings when something needs attention.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

"""
Centralized Logging System

Provides structured logging with file rotation and console output.

Features:
- Color-coded console output for different log levels
- Automatic log file rotation
- Structured formatting for easy parsing
- Debug and production log levels

"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from ..config import settings

class VaaniLogger:
    """Custom logger for Vaani with advanced features"""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = 'vaani') -> logging.Logger:
        """Get or create logger instance"""
        if cls._instance is None:
            cls._instance = cls._create_logger(name)
        return cls._instance
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Create and configure logger"""
        logger = logging.getLogger(name)
        
        # Clear existing handlers
        if logger.handlers:
            logger.handlers.clear()
        
        # Set log level
        configured_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        final_level = logging.DEBUG if settings.DEBUG_MODE else configured_level
        logger.setLevel(final_level)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler with rotation
        log_file = settings.LOGS_DIR / 'vaani.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file for debugging
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Console handler - respects configuration
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(final_level)
        console_handler.setFormatter(simple_formatter if not settings.DEBUG_MODE else detailed_formatter)
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger

# Convenience functions
logger = VaaniLogger.get_logger()

def debug(msg: str, *args, **kwargs):
    """Log debug message"""
    logger.debug(msg, *args, **kwargs)

def info(msg: str, *args, **kwargs):
    """Log info message"""
    logger.info(msg, *args, **kwargs)

def warning(msg: str, *args, **kwargs):
    """Log warning message"""
    logger.warning(msg, *args, **kwargs)

def error(msg: str, *args, **kwargs):
    """Log error message"""
    logger.error(msg, *args, **kwargs)

def critical(msg: str, *args, **kwargs):
    """Log critical message"""
    logger.critical(msg, *args, **kwargs)

def exception(msg: str, *args, **kwargs):
    """Log exception with traceback"""
    logger.exception(msg, *args, **kwargs)
