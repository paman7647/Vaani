"""
Lifecycle Manager - System Startup & Shutdown
================================================

Features:
- Professional startup sequence with minimal logging
- Component initialization (config, speech, TTS, wake word)
- Health checks and dependency validation
- Graceful shutdown coordination
- Resource cleanup (threads, audio devices, temp files)
- Error handling during startup/shutdown
- State verification before entering main loop

Manages the system's lifecycle from initialization through shutdown,
ensuring all components start cleanly and shut down gracefully.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

"""
System Health Monitoring

Provides health lifecycleing and recovery functionality for the Vaani voice assistant.

Features:
- Real-time subsystem health tracking
- Automatic failure detection and recovery
- Health metrics reporting
- Configurable check intervals and failure thresholds

"""

import threading
import time
from typing import Dict, Any, Optional, Callable
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Lifecycle Manager")


class HealthMonitor:
    """Monitors system health and performs recovery"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.running = False
        self.lifecycle_thread: Optional[threading.Thread] = None
        
        # Subsystem health tracking
        self.subsystems: Dict[str, Dict[str, Any]] = {}
        self.recovery_callbacks: Dict[str, Callable] = {}
        
        # Failure tracking
        self.failure_counts: Dict[str, int] = {}
        self.max_failures = 3
        
        logger.info("System lifecycle initialized")
    
    def register_subsystem(self, name: str, health_check: Callable[[], bool],
                          recovery_callback: Optional[Callable] = None):
        """
        Register a subsystem to lifecycle
        
        Args:
            name: Subsystem name
            health_check: Function that returns True if healthy
            recovery_callback: Optional function to call for recovery
        """
        self.subsystems[name] = {
            'health_check': health_check,
            'last_check': time.time(),
            'healthy': True,
            'check_count': 0
        }
        
        if recovery_callback:
            self.recovery_callbacks[name] = recovery_callback
        
        self.failure_counts[name] = 0
        
        logger.info(f"Registered subsystem: {name}")
    
    @error_handler(default_return=None)
    def start(self):
        """Start lifecycle lifecycleing"""
        if self.running:
            logger.warning("Watchdog already running")
            return
        
        self.running = True
        self.lifecycle_thread = threading.Thread(target=self._lifecycle_loop, daemon=True)
        self.lifecycle_thread.start()
        
        logger.info("🐕 Watchdog started")
    
    def stop(self):
        """Stop lifecycle lifecycleing"""
        self.running = False
        if self.lifecycle_thread:
            self.lifecycle_thread.join(timeout=5)
        
        logger.info("Watchdog stopped")
    
    @error_handler(default_return=None)
    def _lifecycle_loop(self):
        """Main lifecycleing loop"""
        while self.running:
            try:
                self._check_all_subsystems()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Watchdog error: {e}")
                time.sleep(self.check_interval)
    
    def _check_all_subsystems(self):
        """Check health of all registered subsystems"""
        for name, info in self.subsystems.items():
            try:
                health_check = info['health_check']
                is_healthy = health_check()
                
                info['last_check'] = time.time()
                info['check_count'] += 1
                
                if is_healthy:
                    # System is healthy
                    if not info['healthy']:
                        logger.info(f"✅ Subsystem recovered: {name}")
                        self.failure_counts[name] = 0
                    info['healthy'] = True
                else:
                    # System is unhealthy
                    logger.warning(f"⚠️ Subsystem unhealthy: {name}")
                    info['healthy'] = False
                    self.failure_counts[name] += 1
                    
                    # Attempt recovery
                    self._attempt_recovery(name)
                    
            except Exception as e:
                logger.error(f"Error checking subsystem {name}: {e}")
    
    @error_handler(default_return=None)
    def _attempt_recovery(self, name: str):
        """Attempt to recover a failed subsystem"""
        failure_count = self.failure_counts[name]
        
        if failure_count > self.max_failures:
            logger.error(f"❌ Subsystem {name} exceeded max failures ({self.max_failures})")
            return
        
        if name in self.recovery_callbacks:
            try:
                logger.info(f"🔧 Attempting recovery for: {name}")
                recovery_callback = self.recovery_callbacks[name]
                recovery_callback()
                logger.info(f"✅ Recovery attempted for: {name}")
            except Exception as e:
                logger.error(f"Recovery failed for {name}: {e}")
        else:
            logger.warning(f"No recovery callback for: {name}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health report"""
        total = len(self.subsystems)
        healthy = sum(1 for info in self.subsystems.values() if info['healthy'])
        
        return {
            'overall_health': 'healthy' if healthy == total else 'degraded',
            'subsystems_total': total,
            'subsystems_healthy': healthy,
            'subsystems_unhealthy': total - healthy,
            'details': {
                name: {
                    'healthy': info['healthy'],
                    'last_check': time.time() - info['last_check'],
                    'failure_count': self.failure_counts[name]
                }
                for name, info in self.subsystems.items()
            }
        }
    
    @error_handler(default_return=None)
    def force_recovery(self, subsystem_name: str):
        """Manually trigger recovery for a subsystem"""
        if subsystem_name in self.recovery_callbacks:
            logger.info(f"🔧 Manual recovery triggered for: {subsystem_name}")
            try:
                self.recovery_callbacks[subsystem_name]()
                self.failure_counts[subsystem_name] = 0
                logger.info(f"✅ Manual recovery completed for: {subsystem_name}")
            except Exception as e:
                logger.error(f"Manual recovery failed for {subsystem_name}: {e}")
        else:
            logger.error(f"No recovery callback for: {subsystem_name}")


class ThreadMonitor:
    """Monitor threads for stalling"""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self.thread_heartbeats: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def heartbeat(self, thread_name: str):
        """Update heartbeat for a thread"""
        with self.lock:
            self.thread_heartbeats[thread_name] = time.time()
    
    def check_thread(self, thread_name: str) -> bool:
        """Check if thread is alive (has recent heartbeat)"""
        with self.lock:
            if thread_name not in self.thread_heartbeats:
                return False
            
            last_beat = self.thread_heartbeats[thread_name]
            age = time.time() - last_beat
            
            return age < self.timeout
    
    def get_stalled_threads(self) -> list:
        """Get list of stalled threads"""
        stalled = []
        
        with self.lock:
            for thread_name, last_beat in self.thread_heartbeats.items():
                age = time.time() - last_beat
                if age >= self.timeout:
                    stalled.append((thread_name, age))
        
        return stalled


# Global lifecycle
_health_lifecycle: Optional[HealthMonitor] = None
_thread_lifecycle: Optional[ThreadMonitor] = None

def get_health_lifecycle() -> HealthMonitor:
    """Get singleton health lifecycle"""
    global _health_lifecycle
    if _health_lifecycle is None:
        _health_lifecycle = HealthMonitor()
    return _health_lifecycle

def get_thread_lifecycle() -> ThreadMonitor:
    """Get or create global thread lifecycle"""
    global _thread_lifecycle
    if _thread_lifecycle is None:
        _thread_lifecycle = ThreadMonitor()
    return _thread_lifecycle
