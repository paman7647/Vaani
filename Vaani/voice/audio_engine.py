"""
Audio Engine - Music & Media Playback
========================================

Features:
- YouTube streaming via yt-dlp
- Multi-backend support (VLC primary, pygame fallback)
- Playback controls (play, pause, resume, stop, skip)
- Volume control and automatic ducking during voice interaction
- Queue management for multiple songs
- Thread-safe state management
- URL extraction and validation
- Error recovery and automatic backend fallback
- Playback status monitoring

Handles all audio playback including music streaming from YouTube.
Automatically lowers volume when you talk to Vaani and restores it
after, providing seamless voice interaction during playback.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

"""
Music Playback and Audio Control Module

Handles music playback using VLC and pygame with proper synchronization.

Features:
- YouTube audio extraction with yt-dlp
- Dual-backend playback (VLC primary, pygame fallback)
- Dynamic volume control and ducking
- Queue management and track history
- Maximum volume (100%) by default for immersive experience


"""

import time
import threading
import tempfile
import os
import json
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from collections import deque
from ..config import settings
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Audio Engine")

# Import optional audio libraries
try:
    import vlc
    VLC_AVAILABLE = True
except (ImportError, OSError) as e:
    VLC_AVAILABLE = False
    logger.warning(f"VLC not available: {e}")

try:
    # Set SDL to use dummy video driver to avoid display issues on macOS
    import os
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'coreaudio'
    
    import pygame
    PYGAME_AVAILABLE = True
    # Don't initialize mixer here - do it lazily when needed
except ImportError as e:
    PYGAME_AVAILABLE = False
    logger.warning(f"Pygame not available: {e}")

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    logger.warning("yt-dlp not available - YouTube streaming disabled")


def _init_pygame_mixer():
    """Lazy initialization of pygame mixer"""
    global PYGAME_AVAILABLE
    if not PYGAME_AVAILABLE:
        return False
    
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=settings.BUFFER_SIZE)
            logger.info("Pygame mixer initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize pygame mixer: {e}")
        PYGAME_AVAILABLE = False
        return False


class AudioEngine:
    """Thread-safe audio engine with queue management"""
    
    def __init__(self):
        self.audio_engine: Optional[any] = None
        self.is_playing = False
        self.is_paused = False
        self.current_song = ""
        self.current_url = ""
        self.current_file = None  # Path to downloaded file
        self.volume = settings.DEFAULT_VOLUME
        self.queue: deque = deque(maxlen=settings.MAX_QUEUE_SIZE)
        self.history: List[str] = []
        self.audio_engine_lock = threading.Lock()
        self.audio_engine_type = None  # 'vlc' or 'pygame'
        
        # Create temp directory for audio files
        self.temp_dir = Path(getattr(settings, 'TEMP_AUDIO_DIR', 'temp/audio'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create cache directory for downloaded songs
        self.cache_dir = Path('temp/audio_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache management
        self.cache_index = {}  # {song_name: (file_path, title, timestamp)}
        self._load_cache_index()
        
        logger.debug("Audio player initialized")
    
    @error_handler(default_return=(None, None, None))
    def get_youtube_audio_url(self, song_name: str, language: str = 'en') -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Get YouTube audio URL for streaming with multilingual support
        
        Args:
            song_name: Name of song to search
            language: Language code for better search results (en, hi, es, fr, de, ja, ko, zh, ru, ar, pt)
        
        Returns:
            Tuple of (audio_url, title, duration) or (None, None, None) if not found
        """
        if not YTDLP_AVAILABLE:
            logger.error("yt-dlp not available for YouTube streaming")
            return None, None, None
        
        try:
            # Construct search query with language-specific keywords
            music_keywords = {
                # Indian Languages (Priority)
                'en': 'song music official audio',
                'en-IN': 'song music official audio',
                'hi': 'gana song music',
                'hi-IN': 'गाना song music',
                'ta': 'பாடல் song music',
                'ta-IN': 'பாடல் song music',
                'te': 'పాట song music',
                'te-IN': 'పాట song music',
                'bn': 'গান song music',
                'bn-IN': 'গান song music',
                'mr': 'गाणे song music',
                'mr-IN': 'गाणे song music',
                'gu': 'ગીત song music',
                'gu-IN': 'ગીત song music',
                'kn': 'ಹಾಡು song music',
                'kn-IN': 'ಹಾಡು song music',
                'ml': 'പാട്ട് song music',
                'ml-IN': 'പാട്ട് song music',
                'pa': 'ਗੀਤ song music',
                'pa-IN': 'ਗੀਤ song music',
                'ur': 'گانا song music',
                'ur-IN': 'گانا song music',
                
                # Global Languages
                'es': 'canción música official',
                'fr': 'chanson musique official',
                'de': 'lied musik official',
                'ja': '音楽 曲 official',
                'ko': '노래 음악 official',
                'zh': '歌曲 音乐 official',
                'ru': 'песня музыка official',
                'ar': 'أغنية موسيقى',
                'pt': 'música canção official'
            }
            keywords = music_keywords.get(language, 'song music official audio')
            search_query = f"{song_name.strip()} {keywords}"
            logger.info(f"YouTube search ({language}): '{search_query}'")
            
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 20,
                'retries': 3,
                'geo_bypass': True,  # Bypass geographic restrictions
                'prefer_free_formats': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(
                    f"ytsearch3:{search_query}",
                    download=False
                )
                
                if search_results and 'entries' in search_results and search_results['entries']:
                    # Get first result
                    video = search_results['entries'][0]
                    audio_url = video.get('url')
                    title = video.get('title', song_name)
                    duration = video.get('duration', 0)
                    
                    if audio_url:
                        logger.info(f"Found YouTube audio: {title}")
                        return audio_url, title, duration
        
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
        
        return None, None, None
    
    @error_handler(default_return=(None, None))
    def download_audio(self, song_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Download audio file from YouTube with caching
        
        Returns:
            Tuple of (file_path, title) or (None, None) if download fails
        """
        # Check cache first
        cached = self._check_cache(song_name)
        if cached:
            return cached
        
        if not YTDLP_AVAILABLE:
            logger.error("yt-dlp not available for audio download")
            return None, None
        
        try:
            # Construct search query
            search_query = f"{song_name.strip()} song music official audio"
            logger.info(f"Downloading: '{search_query}'")
            
            # Generate temp filename
            safe_name = "".join(c for c in song_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name[:50]  # Limit length
            output_path = self.temp_dir / f"{safe_name}.%(ext)s"
            
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
                'outtmpl': str(output_path),
                'noplaylist': True,
                'quiet': True,  # Suppress verbose output
                'no_warnings': True,  # Suppress yt-dlp warnings (including JS challenge warnings)
                'extract_flat': False,
                'socket_timeout': 30,
                'retries': 3,
                'ignoreerrors': True,  # Continue on errors
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }] if os.path.exists('/usr/local/bin/ffmpeg') or os.path.exists('/opt/homebrew/bin/ffmpeg') else [],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search and download
                search_results = ydl.extract_info(
                    f"ytsearch1:{search_query}",
                    download=True
                )
                
                if search_results and 'entries' in search_results and search_results['entries']:
                    video = search_results['entries'][0]
                    title = video.get('title', song_name)
                    
                    # Find the downloaded file
                    possible_extensions = ['mp3', 'm4a', 'webm', 'opus']
                    for ext in possible_extensions:
                        file_path = self.temp_dir / f"{safe_name}.{ext}"
                        if file_path.exists():
                            logger.info(f"Downloaded: {file_path}")
                            
                            # Add to cache for future use
                            self._add_to_cache(song_name, str(file_path), title)
                            
                            # Return the cached path
                            cached = self._check_cache(song_name)
                            if cached:
                                return cached
                            return str(file_path), title
                    
                    logger.error("Downloaded file not found")
                    return None, None
        
        except Exception as e:
            logger.error(f"Audio download error: {e}")
        
        return None, None
    
    @error_handler(default_return=False)
    def play_url(self, url: str, title: str) -> bool:
        """Play audio from URL using VLC or pygame"""
        with self.audio_engine_lock:
            try:
                # Stop any current playback (call internal method to avoid deadlock)
                self._stop_internal()
                
                logger.info(f"Attempting to play: {title}")
                logger.info(f"URL type: {'HTTP stream' if url.startswith('http') else 'Local file'}")
                
                # Check if it's a local file
                is_local_file = not url.startswith('http')
                
                # If DOWNLOAD_AUDIO is enabled and it's a stream URL, download first
                if getattr(settings, 'DOWNLOAD_AUDIO', False) and not is_local_file:
                    logger.info("Download mode enabled - attempting to download audio...")
                    # Extract song name from title for download
                    song_name = title.split('·')[0].strip() if '·' in title else title
                    file_path, downloaded_title = self.download_audio(song_name)
                    
                    if file_path:
                        logger.info(f"Downloaded successfully, playing local file")
                        url = file_path
                        is_local_file = True
                        self.current_file = file_path
                    else:
                        logger.warning("Download failed, falling back to streaming")
                
                # Try VLC first (better for both streaming and local files)
                if VLC_AVAILABLE:
                    logger.info("Trying VLC player...")
                    try:
                        success = self._play_vlc(url, title)
                        if success:
                            logger.info("VLC playback successful")
                            return True
                        else:
                            logger.warning("VLC playback failed")
                            
                            # If streaming failed and we haven't downloaded yet, try downloading
                            if not is_local_file and not getattr(settings, 'DOWNLOAD_AUDIO', False):
                                logger.info("Trying download method as fallback...")
                                song_name = title.split('·')[0].strip() if '·' in title else title
                                file_path, downloaded_title = self.download_audio(song_name)
                                
                                if file_path:
                                    logger.info("Downloaded, retrying with local file...")
                                    success = self._play_vlc(file_path, title)
                                    if success:
                                        self.current_file = file_path
                                        return True
                            
                            logger.warning("All VLC attempts failed, trying pygame...")
                    except Exception as e:
                        logger.error(f"VLC exception: {e}")
                
                # Fallback to pygame (works better with local files)
                if PYGAME_AVAILABLE and is_local_file:
                    logger.info("Trying Pygame player...")
                    try:
                        success = self._play_pygame(url, title)
                        if success:
                            logger.info("Pygame playback successful")
                            return True
                    except Exception as e:
                        logger.error(f"Pygame exception: {e}")
                
                logger.error("No audio player available or all players failed")
                return False
                
            except Exception as e:
                logger.error(f"Play error: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    @error_handler(default_return=False)
    def _play_vlc(self, url: str, title: str) -> bool:
        """Play audio using VLC"""
        try:
            logger.info(f"Playing with VLC: {title}")
            logger.info(f"URL: {url[:100]}...")
            
            # Create VLC instance with verbose error reporting
            vlc_args = [
                '--intf', 'dummy',
                '--no-video',
                '--aout=auhal',  # Use macOS CoreAudio output
                f'--network-caching={settings.VLC_NETWORK_CACHING}',
                '--sout-mux-caching=2000',
                '--http-reconnect',
                '--verbose=2' if settings.DEBUG_MODE else '--quiet'
            ]
            
            vlc_instance = vlc.Instance(vlc_args)
            player = vlc_instance.media_player_new()
            media = vlc_instance.media_new(url)
            media.add_option(f'network-caching={settings.VLC_NETWORK_CACHING}')
            player.set_media(media)
            
            # Set volume (0-100)
            volume_level = int(self.volume * 100)
            player.audio_set_volume(volume_level)
            logger.info(f"Volume set to: {volume_level}%")
            
            # Start playback
            play_result = player.play()
            if play_result == -1:
                logger.error("VLC play() returned error code -1")
                return False
            
            logger.info("Waiting for playback to start...")
            
            # Wait for playback to start with detailed state logging
            time.sleep(1.5)
            for attempt in range(10):
                state = player.get_state()
                logger.debug(f"VLC state (attempt {attempt + 1}): {state}")
                
                if state == vlc.State.Playing:
                    self.audio_engine = player
                    self.audio_engine_type = 'vlc'
                    self.is_playing = True
                    self.is_paused = False
                    self.current_song = title
                    self.current_url = url
                    logger.info(f"VLC playback started successfully: {title}")
                    return True
                
                if state in [vlc.State.Error, vlc.State.Ended, vlc.State.Stopped]:
                    logger.error(f"VLC playback failed with state: {state}")
                    return False
                
                time.sleep(1)
            
            logger.error("VLC playback timeout - state never reached 'Playing'")
            return False
            
        except Exception as e:
            logger.error(f"VLC playback error: {e}")
            return False
    
    def _play_pygame(self, url: str, title: str) -> bool:
        """Play audio using pygame (best for local files)"""
        try:
            logger.info(f"Playing with pygame: {title}")
            
            # Initialize pygame mixer if needed
            if not _init_pygame_mixer():
                logger.error("Pygame mixer not available")
                return False
            
            # Pygame works best with local files
            if not url.startswith('http'):
                logger.info(f"Loading local file: {url}")
                pygame.mixer.music.load(url)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                
                # Wait a moment to ensure playback started
                time.sleep(0.5)
                if pygame.mixer.music.get_busy():
                    self.audio_engine = 'pygame'
                    self.audio_engine_type = 'pygame'
                    self.is_playing = True
                    self.is_paused = False
                    self.current_song = title
                    self.current_url = url
                    
                    logger.info(f"Pygame playback started: {title}")
                    return True
                else:
                    logger.error("Pygame playback failed to start")
                    return False
            else:
                logger.warning("Pygame cannot stream URLs directly")
                return False
            
        except Exception as e:
            logger.error(f"Pygame playback error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @error_handler(default_return=False)
    def pause(self) -> bool:
        """Pause current playback"""
        with self.audio_engine_lock:
            try:
                if not self.is_playing:
                    return False
                
                if self.audio_engine_type == 'vlc' and self.audio_engine:
                    self.audio_engine.pause()
                    self.is_paused = True
                    logger.info("Playback paused (VLC)")
                    return True
                
                elif self.audio_engine_type == 'pygame':
                    pygame.mixer.music.pause()
                    self.is_paused = True
                    logger.info("Playback paused (pygame)")
                    return True
                
            except Exception as e:
                logger.error(f"Pause error: {e}")
            
            return False
    
    @error_handler(default_return=False)
    def resume(self) -> bool:
        """Resume paused playback"""
        with self.audio_engine_lock:
            try:
                if not self.is_paused:
                    return False
                
                if self.audio_engine_type == 'vlc' and self.audio_engine:
                    self.audio_engine.play()
                    self.is_paused = False
                    logger.info("Playback resumed (VLC)")
                    return True
                
                elif self.audio_engine_type == 'pygame':
                    pygame.mixer.music.unpause()
                    self.is_paused = False
                    logger.info("Playback resumed (pygame)")
                    return True
                
            except Exception as e:
                logger.error(f"Resume error: {e}")
            
            return False
    
    def _stop_internal(self) -> bool:
        """Internal stop method without lock (called when lock already held)"""
        try:
            if self.audio_engine_type == 'vlc' and self.audio_engine:
                self.audio_engine.stop()
                self.audio_engine = None
                logger.info("Playback stopped (VLC)")
            
            elif self.audio_engine_type == 'pygame':
                pygame.mixer.music.stop()
                logger.info("Playback stopped (pygame)")
            
            # Clean up downloaded file if it exists
            if self.current_file and os.path.exists(self.current_file):
                try:
                    os.remove(self.current_file)
                    logger.debug(f"Cleaned up temp file: {self.current_file}")
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")
            
            self.is_playing = False
            self.is_paused = False
            self.audio_engine_type = None
            self.current_file = None
            
            return True
            
        except Exception as e:
            logger.error(f"Stop error: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop current playback and cleanup"""
        with self.audio_engine_lock:
            return self._stop_internal()
    
    def set_volume(self, volume: float) -> bool:
        """Set volume (0.0 to 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))
            self.volume = volume
            
            if self.audio_engine_type == 'vlc' and self.audio_engine:
                self.audio_engine.audio_set_volume(int(volume * 100))
            elif self.audio_engine_type == 'pygame':
                pygame.mixer.music.set_volume(volume)
            
            logger.info(f"Volume set to {volume:.1%}")
            return True
            
        except Exception as e:
            logger.error(f"Volume error: {e}")
            return False
    
    def duck_volume(self) -> float:
        """Temporarily lower volume for voice detection, returns original volume"""
        original_volume = self.volume
        if self.is_playing and not self.is_paused:
            self.set_volume(settings.MUSIC_DUCK_VOLUME)
            logger.debug(f"Music ducked: {original_volume:.0%} -> {settings.MUSIC_DUCK_VOLUME:.0%}")
        return original_volume
    
    def restore_volume(self, volume: float):
        """Restore volume to original level"""
        if self.is_playing and not self.is_paused:
            self.set_volume(volume)
            logger.debug(f"Music restored to {volume:.0%}")
    
    def add_to_queue(self, song_name: str):
        """Add song to queue"""
        if len(self.queue) >= settings.MAX_QUEUE_SIZE:
            logger.warning("Queue is full")
            return False
        
        self.queue.append(song_name)
        logger.info(f"Added to queue: {song_name}")
        return True
    
    def play_next(self) -> bool:
        """Play next song from queue"""
        if not self.queue:
            logger.info("Queue is empty")
            return False
        
        next_song = self.queue.popleft()
        logger.info(f"Playing next from queue: {next_song}")
        
        url, title, duration = self.get_youtube_audio_url(next_song)
        if url:
            return self.play_url(url, title)
        
        return False
    
    def get_status(self) -> dict:
        """Get current player status"""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_song': self.current_song,
            'volume': self.volume,
            'queue_length': len(self.queue),
            'player_type': self.audio_engine_type
        }
    
    def get_whats_playing(self) -> Optional[str]:
        """Get currently playing song description"""
        if self.is_playing and self.current_song:
            status = "paused" if self.is_paused else "playing"
            return f"{self.current_song} ({status})"
        return None
    
    @error_handler(default_return=False)
    def play_mood_music(self, mood: str) -> bool:
        """
        Play music based on mood
        
        Args:
            mood: Mood keyword (relaxing, energetic, happy, sad, focus, etc.)
        
        Returns:
            True if successful
        """
        mood_mappings = {
            'relaxing': 'relaxing music ambient calm',
            'calm': 'calm peaceful music',
            'energetic': 'energetic upbeat music',
            'happy': 'happy cheerful music',
            'sad': 'sad emotional music',
            'focus': 'focus concentration music',
            'workout': 'workout gym music',
            'sleep': 'sleep music peaceful',
            'party': 'party dance music'
        }
        
        query = mood_mappings.get(mood.lower(), f"{mood} music")
        logger.info(f"Playing {mood} mood music")
        
        # Get and play music
        file_path, title = self.download_audio(query)
        if file_path and title:
            return self.play_url(file_path, title)
        
        return False
    
    def shutdown(self):
        """Shutdown the audio player"""
        self.stop()
        self._save_cache_index()
        logger.info("Audio player shut down")
    
    def _load_cache_index(self):
        """Load cache index from disk"""
        cache_file = self.cache_dir / 'cache_index.json'
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    self.cache_index = json.load(f)
                logger.info(f"Loaded cache index: {len(self.cache_index)} cached songs")
        except Exception as e:
            logger.warning(f"Could not load cache index: {e}")
            self.cache_index = {}
    
    def _save_cache_index(self):
        """Save cache index to disk"""
        cache_file = self.cache_dir / 'cache_index.json'
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
            logger.debug("Cache index saved")
        except Exception as e:
            logger.warning(f"Could not save cache index: {e}")
    
    def _get_cache_key(self, song_name: str) -> str:
        """Generate cache key from song name"""
        return hashlib.md5(song_name.lower().strip().encode()).hexdigest()
    
    def _check_cache(self, song_name: str) -> Optional[Tuple[str, str]]:
        """Check if song is in cache and return (file_path, title)"""
        cache_key = self._get_cache_key(song_name)
        if cache_key in self.cache_index:
            cached_file = self.cache_index[cache_key].get('file')
            cached_title = self.cache_index[cache_key].get('title')
            cache_path = Path(cached_file) if cached_file else None
            
            if cache_path and cache_path.exists():
                logger.info(f"Cache HIT: {cached_title}")
                return str(cache_path), cached_title
            else:
                # Clean up invalid cache entry
                del self.cache_index[cache_key]
                logger.debug(f"Removed invalid cache entry: {cache_key}")
        
        return None
    
    def _add_to_cache(self, song_name: str, file_path: str, title: str):
        """Add downloaded song to cache"""
        try:
            cache_key = self._get_cache_key(song_name)
            
            # Move file to cache directory if not already there
            source_path = Path(file_path)
            if not str(source_path).startswith(str(self.cache_dir)):
                # Generate safe cached filename
                ext = source_path.suffix
                cache_file = self.cache_dir / f"{cache_key}{ext}"
                
                # Move file to cache
                import shutil
                shutil.move(str(source_path), str(cache_file))
                file_path = str(cache_file)
                logger.info(f"Cached: {title} -> {cache_file.name}")
            
            # Update cache index
            self.cache_index[cache_key] = {
                'file': file_path,
                'title': title,
                'song_name': song_name,
                'timestamp': time.time()
            }
            self._save_cache_index()
            
        except Exception as e:
            logger.warning(f"Could not cache file: {e}")


# Global audio player instance
# Global audio engine instance
_audio_engine: Optional[AudioEngine] = None

def get_audio_engine() -> AudioEngine:
    """Get or create global audio engine instance"""
    global _audio_engine
    if _audio_engine is None:
        _audio_engine = AudioEngine()
    return _audio_engine
