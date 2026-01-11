"""
Music Client - YouTube Search & Streaming
============================================

Features:
- YouTube search for songs and artists
- URL extraction via yt-dlp
- Search result ranking by relevance
- Direct URL playback support
- Error handling and retry logic
- Format selection (audio-only for efficiency)
- Playlist support (future feature)
- Caching of frequently played songs

Searches YouTube for music and extracts streaming URLs.
Integrates with audio_engine for actual playback.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

"""
Music Manager

Manages music playback and queue operations.

Features:
- Queue management and history tracking
- Playback state management
- Track metadata handling
- Shuffle and repeat modes

"""

import threading
import time
from enum import Enum
from typing import Optional, List, Dict, Tuple
from collections import deque
from dataclasses import dataclass
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Music Client")
from ..config import settings


class PlaybackState(Enum):
    """Explicit playback states"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    BUFFERING = "buffering"


@dataclass
class Track:
    """Track metadata"""
    title: str
    url: str
    duration: Optional[int] = None
    source: str = "youtube"
    
    def __str__(self):
        return f"{self.title} ({self.duration}s)" if self.duration else self.title


class MusicManager:
    """
    Professional music player with state machine and queue
    
    Responsibilities:
    - Music playback state management
    - Queue operations (add, skip, clear)
    - Volume control (independent from TTS)
    - Track history
    - Auto-play next track
    """
    
    def __init__(self, player):
        """
        Initialize music manager
        
        Args:
            player: Audio player instance for playback
        """
        self.audio_engine = player
        self.state = PlaybackState.STOPPED
        self.state_lock = threading.RLock()
        
        # Queue management
        self.queue: deque = deque()
        self.current_track: Optional[Track] = None
        self.history: deque = deque(maxlen=50)
        self.queue_lock = threading.RLock()
        
        # Advanced playback features
        self.shuffle_mode = False
        self.repeat_mode = 'off'  # 'off', 'one', 'all'
        self.original_queue: List[Track] = []  # Store original order for shuffle
        
        # Volume management
        self.music_volume = settings.DEFAULT_VOLUME
        self.volume_lock = threading.Lock()
        
        # Monitoring
        self.lifecycle_thread = None
        self.lifecycle_active = False
        
        logger.info("Music Manager initialized")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATE MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _transition_state(self, new_state: PlaybackState, reason: str = ""):
        """Thread-safe state transition with logging"""
        with self.state_lock:
            old_state = self.state
            if old_state != new_state:
                self.state = new_state
                logger.info(f"Music state: {old_state.value} -> {new_state.value} {f'({reason})' if reason else ''}")
    
    def get_state(self) -> PlaybackState:
        """Get current playback state"""
        with self.state_lock:
            return self.state
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PLAYBACK CONTROL
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @error_handler(default_return=False)
    def play_track(self, track: Track, replace_current: bool = True) -> bool:
        """
        Play a track immediately
        
        Args:
            track: Track to play
            replace_current: If True, stop current and play. If False, add to queue.
        
        Returns:
            True if playback started successfully
        """
        if not replace_current and self.get_state() in [PlaybackState.PLAYING, PlaybackState.PAUSED]:
            return self.add_to_queue(track)
        
        self._transition_state(PlaybackState.BUFFERING, "loading track")
        
        try:
            # Stop current if playing
            if self.current_track:
                self._add_to_history(self.current_track)
            
            # Start playback
            success = self.audio_engine.play_url(track.url, track.title)
            
            if success:
                self.current_track = track
                self._transition_state(PlaybackState.PLAYING, "track started")
                self._start_lifecycle()
                return True
            else:
                self._transition_state(PlaybackState.STOPPED, "playback failed")
                return False
                
        except Exception as e:
            logger.error(f"Play track error: {e}")
            self._transition_state(PlaybackState.STOPPED, "error")
            return False
    
    @error_handler(default_return=(False, "Playback error"))
    def play_song(self, song_name: str) -> Tuple[bool, str]:
        """
        Search for and play a song by name
        
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Searching for: {song_name}")
        
        self._transition_state(PlaybackState.BUFFERING, "searching")
        
        # Get YouTube URL
        url, title, duration = self.audio_engine.get_youtube_audio_url(song_name)
        
        if not url:
            self._transition_state(PlaybackState.STOPPED, "not found")
            return False, f"Could not find '{song_name}'"
        
        # Create track and play
        track = Track(title=title, url=url, duration=duration)
        success = self.play_track(track)
        
        if success:
            return True, f"Now playing: {title}"
        else:
            return False, "Playback failed"
    
    def pause(self) -> bool:
        """Pause current playback"""
        if self.get_state() != PlaybackState.PLAYING:
            return False
        
        if self.audio_engine.pause():
            self._transition_state(PlaybackState.PAUSED, "user requested")
            return True
        return False
    
    def resume(self) -> bool:
        """Resume paused playback"""
        if self.get_state() != PlaybackState.PAUSED:
            return False
        
        if self.audio_engine.resume():
            self._transition_state(PlaybackState.PLAYING, "resumed")
            return True
        return False
    
    def stop(self) -> bool:
        """Stop playback and clear current track"""
        if self.get_state() == PlaybackState.STOPPED:
            return True
        
        if self.current_track:
            self._add_to_history(self.current_track)
        
        self.audio_engine.stop()
        self.current_track = None
        self._transition_state(PlaybackState.STOPPED, "user requested")
        return True
    
    def restart_current(self) -> bool:
        """Restart current track from beginning"""
        if not self.current_track:
            return False
        
        logger.info(f"🔄 Restarting: {self.current_track.title}")
        return self.play_track(self.current_track)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # QUEUE MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def add_to_queue(self, track: Track) -> bool:
        """Add track to end of queue"""
        with self.queue_lock:
            self.queue.append(track)
            logger.info(f"➕ Added to queue: {track.title} (position {len(self.queue)})")
            return True
    
    def add_song_to_queue(self, song_name: str) -> Tuple[bool, str]:
        """Search for and add song to queue"""
        url, title, duration = self.audio_engine.get_youtube_audio_url(song_name)
        
        if not url:
            return False, f"Could not find '{song_name}'"
        
        track = Track(title=title, url=url, duration=duration)
        self.add_to_queue(track)
        return True, f"Added to queue: {title}"
    
    @error_handler(default_return=(False, "Skip failed"))
    def skip_next(self) -> Tuple[bool, str]:
        """Skip to next track in queue"""
        with self.queue_lock:
            if not self.queue:
                self.stop()
                return False, "Queue is empty"
            
            next_track = self.queue.popleft()
            logger.info(f"⏭️  Skipping to: {next_track.title}")
            
            success = self.play_track(next_track)
            if success:
                return True, f"Now playing: {next_track.title}"
            else:
                return False, "Failed to play next track"
    
    def skip_previous(self) -> Tuple[bool, str]:
        """Go back to previous track"""
        with self.queue_lock:
            if not self.history:
                return False, "No previous tracks"
            
            prev_track = self.history.pop()
            logger.info(f"⏮️  Going back to: {prev_track.title}")
            
            # Put current track back at front of queue if playing
            if self.current_track and self.current_track != prev_track:
                self.queue.appendleft(self.current_track)
            
            success = self.play_track(prev_track)
            if success:
                return True, f"Now playing: {prev_track.title}"
            else:
                return False, "Failed to play previous track"
    
    def clear_queue(self) -> int:
        """Clear all queued tracks"""
        with self.queue_lock:
            count = len(self.queue)
            self.queue.clear()
            logger.info(f"🗑️  Cleared {count} tracks from queue")
            return count
    
    def remove_from_queue(self, index: int) -> Tuple[bool, str]:
        """Remove track at specific position"""
        with self.queue_lock:
            if index < 0 or index >= len(self.queue):
                return False, f"Invalid queue position: {index}"
            
            # Convert deque to list, remove, convert back
            queue_list = list(self.queue)
            removed_track = queue_list.pop(index)
            self.queue = deque(queue_list)
            
            return True, f"Removed: {removed_track.title}"
    
    def get_queue_info(self) -> Dict:
        """Get queue information"""
        with self.queue_lock:
            return {
                'queue_length': len(self.queue),
                'tracks': [str(track) for track in list(self.queue)[:10]],  # First 10
                'has_more': len(self.queue) > 10,
                'shuffle': self.shuffle_mode,
                'repeat': self.repeat_mode,
                'current': self.current_track.title if self.current_track else None
            }
    
    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode"""
        import random
        with self.queue_lock:
            self.shuffle_mode = not self.shuffle_mode
            
            if self.shuffle_mode:
                # Save original order and shuffle
                self.original_queue = list(self.queue)
                queue_list = list(self.queue)
                random.shuffle(queue_list)
                self.queue = deque(queue_list)
                logger.info("🔀 Shuffle mode: ON")
            else:
                # Restore original order
                if self.original_queue:
                    self.queue = deque(self.original_queue)
                    self.original_queue = []
                logger.info("🔀 Shuffle mode: OFF")
            
            return self.shuffle_mode
    
    def set_repeat_mode(self, mode: str) -> str:
        """Set repeat mode: 'off', 'one', 'all'"""
        if mode not in ['off', 'one', 'all']:
            mode = 'off'
        
        self.repeat_mode = mode
        logger.info(f"🔁 Repeat mode: {mode.upper()}")
        return self.repeat_mode
    
    def show_queue(self) -> List[str]:
        """Get formatted queue for display"""
        with self.queue_lock:
            if not self.queue:
                return ["Queue is empty"]
            
            lines = [f"Queue ({len(self.queue)} tracks):"]
            for i, track in enumerate(list(self.queue)[:5], 1):
                lines.append(f"{i}. {track.title}")
            
            if len(self.queue) > 5:
                lines.append(f"... and {len(self.queue) - 5} more")
            
            return lines
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # VOLUME CONTROL
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def set_volume(self, volume: float) -> bool:
        """Set music volume (0.0 - 1.0)"""
        with self.volume_lock:
            volume = max(0.0, min(1.0, volume))
            self.music_volume = volume
            self.audio_engine.set_volume(volume)
            logger.info(f"🔊 Music volume: {int(volume * 100)}%")
            return True
    
    def volume_up(self, delta: float = 0.1) -> bool:
        """Increase volume"""
        with self.volume_lock:
            new_volume = min(1.0, self.music_volume + delta)
            return self.set_volume(new_volume)
    
    def volume_down(self, delta: float = 0.1) -> bool:
        """Decrease volume"""
        with self.volume_lock:
            new_volume = max(0.0, self.music_volume - delta)
            return self.set_volume(new_volume)
    
    def get_volume(self) -> float:
        """Get current volume"""
        with self.volume_lock:
            return self.music_volume
    
    def duck_volume(self, duck_level: float = 0.3):
        """Temporarily reduce volume (for TTS)"""
        with self.volume_lock:
            if self.get_state() == PlaybackState.PLAYING:
                ducked = self.music_volume * duck_level
                self.audio_engine.set_volume(ducked)
                logger.debug(f"🔉 Volume ducked to {int(ducked * 100)}%")
    
    def restore_volume(self):
        """Restore volume after ducking"""
        with self.volume_lock:
            if self.get_state() == PlaybackState.PLAYING:
                self.audio_engine.set_volume(self.music_volume)
                logger.debug(f"🔊 Volume restored to {int(self.music_volume * 100)}%")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HISTORY & STATUS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _add_to_history(self, track: Track):
        """Add track to history"""
        with self.queue_lock:
            self.history.append(track)
            logger.debug(f"📜 Added to history: {track.title}")
    
    def get_current_track(self) -> Optional[str]:
        """Get currently playing track description"""
        if self.current_track:
            state_desc = self.get_state().value
            return f"{self.current_track.title} ({state_desc})"
        return None
    
    def get_status(self) -> Dict:
        """Get comprehensive status"""
        return {
            'state': self.get_state().value,
            'current_track': str(self.current_track) if self.current_track else None,
            'volume': int(self.music_volume * 100),
            'queue_length': len(self.queue),
            'has_previous': len(self.history) > 0
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PLAYBACK MONITORING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _start_lifecycle(self):
        """Start playback lifecycleing thread"""
        if not self.lifecycle_active:
            self.lifecycle_active = True
            self.lifecycle_thread = threading.Thread(
                target=self._lifecycle_playback,
                name="MusicMonitor",
                daemon=False
            )
            self.lifecycle_thread.start()
            logger.debug("📡 Playback lifecycle started")
    
    @error_handler(default_return=None)
    def _lifecycle_playback(self):
        """Monitor playback and auto-play next track"""
        while self.lifecycle_active:
            try:
                time.sleep(2)
                
                # Check if track ended
                if self.get_state() == PlaybackState.PLAYING:
                    if not self.audio_engine.is_playing:
                        logger.info("🔚 Track ended")
                        self._on_track_ended()
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
    
    def _on_track_ended(self):
        """Handle track end - auto-play next or stop"""
        with self.queue_lock:
            if self.queue:
                logger.info("▶️  Auto-playing next track")
                self.skip_next()
            else:
                logger.info("⏹️  Queue empty, stopping")
                self.stop()
                self.lifecycle_active = False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down music manager...")
        self.lifecycle_active = False
        self.stop()
        self.queue.clear()
        self.history.clear()


# Global music manager instance
_music_manager: Optional[MusicManager] = None

def get_music_manager(audio_engine=None) -> MusicManager:
    """Get or create global music manager instance"""
    global _music_manager
    if _music_manager is None:
        if audio_engine is None:
            from ..voice.audio_engine import get_audio_engine
            audio_engine = get_audio_engine()
        _music_manager = MusicManager(audio_engine)
    return _music_manager
