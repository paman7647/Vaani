# Vaani Installation Guide

## Automated Installation (Recommended)

### For macOS and Linux

Run the automated installation script from the project root:

```bash
cd vaani  # Navigate to your cloned vaani directory
./install_vaani.sh
```

**What it does:**
- Detects your operating system (macOS, Ubuntu/Debian, Fedora, Arch)
- Installs Python 3.10+ if not present
- Installs Homebrew on macOS (if needed)
- Installs system dependencies (PortAudio, FFmpeg, VLC)
- Creates a Python virtual environment (`venv/`)
- Upgrades pip, setuptools, wheel
- Installs all Python packages from requirements.txt
- Creates .env template for API key configuration

**Supported Operating Systems:**
- macOS (Intel & Apple Silicon)
- Ubuntu/Debian Linux
- Fedora/RHEL Linux
- Arch Linux

### Install Indian Language Models (Optional but Recommended)

For enhanced offline recognition optimized for Indian accents:

```bash
./install_indian_models.sh
```

**Downloads:**
- Indian English model: `vosk-model-small-en-in-0.4` (36MB)
- Hindi model: `vosk-model-small-hi-0.22` (42MB)
- US English fallback: `vosk-model-small-en-us-0.15` (39MB)

These models are saved to `models/` directory (automatically gitignored).

---

## Manual Installation

If you prefer to install manually or the automated script doesn't work:

### Step 1: Install Python 3.10+

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip
```

**Fedora:**
```bash
sudo dnf install -y python3.11 python3-pip
```

**Arch:**
```bash
sudo pacman -Sy python python-pip
```

### Step 2: Install System Dependencies

**macOS:**
```bash
brew install portaudio ffmpeg
brew install --cask vlc
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg vlc \
    libportaudio2 libasound2-dev build-essential libssl-dev libffi-dev
```

**Fedora:**
```bash
sudo dnf install -y portaudio-devel ffmpeg vlc alsa-lib-devel gcc \
    python3-devel openssl-devel libffi-devel
```

**Arch:**
```bash
sudo pacman -Sy portaudio ffmpeg vlc base-devel openssl libffi
```

### Step 3: Create Virtual Environment

```bash
cd vaani  # Your vaani directory
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Packages

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 5: Download Vosk Models (Manual)

If you didn't run `install_indian_models.sh`, download models manually:

```bash
mkdir -p models
cd models

# Indian English (Recommended)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip
unzip vosk-model-small-en-in-0.4.zip

# Hindi (Optional)
wget https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip
unzip vosk-model-small-hi-0.22.zip

# US English Fallback (Optional)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip

cd ..
```

### Step 6: Configure API Keys

Create a `.env` file in the project root:

```bash
nano .env
```

Add your Google Gemini API key:

```env
# Google Gemini API Key (Required for AI responses)
GOOGLE_API_KEY=your_actual_api_key_here

# Optional Configuration
LOG_LEVEL=INFO
```

**Get your API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `.env` file

---

## Configuration

### Voice Settings (config.json)

Vaani automatically creates `config.json` on first run. To customize:

```json
{
  "PREFERRED_VOICES": ["Veena", "Rishi", "Samantha", "Lekha"],
  "LANGUAGE_VOICE_MAP": {
    "hi": "Veena",
    "en": "Veena"
  },
  "ENERGY_THRESHOLD": 300,
  "COMMAND_TIMEOUT": 10
}
```

**Voice Options (macOS):**
- **Veena** - Indian English Female (Primary)
- **Rishi** - Indian English Male
- **Lekha** - Hindi Female
- **Samantha** - US English Female (Fallback)

**Check available voices:**
```bash
say -v ? | grep -E "(hi_IN|en_IN)"
```

### Recognition Settings

**Timing Parameters (in config.json):**
```json
{
  "ENERGY_THRESHOLD": 300,      // Microphone sensitivity (100-4000)
  "PAUSE_THRESHOLD": 0.8,       // Silence duration to end phrase (seconds)
  "PHRASE_THRESHOLD": 0.3,      // Minimum speech before capture (seconds)
  "NON_SPEAKING_DURATION": 0.6, // Silence to confirm end (seconds)
  "COMMAND_TIMEOUT": 10         // Max command length (seconds)
}
```

---

## Running Vaani

### First Time

```bash
cd vaani  # Your project directory
source venv/bin/activate
python3 main.py
```

**Expected Output:**
```
VANI Voice Assistant Ready
```

### Quick Start (After First Run)

```bash
cd vaani && source venv/bin/activate && python3 main.py
```

### Create an Alias (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias vaani='cd /path/to/your/vaani && source venv/bin/activate && python3 main.py'
```

Reload shell config:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

Then just run:
```bash
vaani
```

---

## Troubleshooting

### Python Not Found
```bash
# Check Python version
python3 --version

# If not 3.10+, install manually (see Step 1)
```

### PortAudio Issues (macOS)
```bash
brew reinstall portaudio
```

### VLC Not Working
```bash
# macOS
brew reinstall --cask vlc

# Linux
sudo apt-get reinstall vlc  # Ubuntu/Debian
```

### Permission Denied on Scripts
```bash
chmod +x install_vaani.sh install_indian_models.sh
```

### Import Errors
```bash
# Activate venv first
source venv/bin/activate

# Reinstall packages
pip install --upgrade pip
pip install -r requirements.txt
```

### Microphone Not Detected
```bash
# macOS: Grant microphone permissions
# System Settings → Privacy & Security → Microphone → Terminal (enable)

# Linux: Check audio devices
arecord -l
```

### Google Speech API Errors
```bash
# Verify API key in .env
cat .env | grep GOOGLE_API_KEY

# Test internet connection
ping google.com

# System will fallback to Vosk if Google API unavailable
```

### Vosk Model Not Found
```bash
# Check models directory
ls -la models/

# Re-run model installation
./install_indian_models.sh

# Or download manually (see Step 5 in Manual Installation)
```

### Voice Not Working (macOS)
```bash
# Test voice synthesis
say -v Veena "Testing Indian voice"

# If Veena not available, system will use fallback voices
# Check available voices
say -v ?
```

### Performance Issues

**Recognition too slow:**
- Check internet connection (Google API requires network)
- Ensure Vosk models are properly extracted
- Reduce `ENERGY_THRESHOLD` in config.json (try 200-250)

**False wake word triggers:**
- Increase `ENERGY_THRESHOLD` in config.json (try 400-500)
- Adjust `PAUSE_THRESHOLD` to 1.0 or higher

**Speech cut off early:**
- Increase `PAUSE_THRESHOLD` to 1.0 or higher
- Increase `NON_SPEAKING_DURATION` to 0.8 or higher

---

## System Requirements

**Minimum:**
- Python 3.10 or higher
- 2GB RAM
- 500MB disk space (plus 100MB for models)
- Microphone input
- Internet connection (for Google API and music streaming)

**Recommended:**
- Python 3.11 or higher
- 4GB RAM
- 1GB disk space
- Quality USB microphone or headset
- Stable internet connection (10+ Mbps)

---

## Advanced Configuration

### Multiple Language Support

While Vaani's speech **input** is optimized for English, the AI can **respond** in multiple languages. Configure language in conversation:

**Example:**
- User: "Respond in Hindi from now on"
- Vaani: "ठीक है, मैं अब हिंदी में जवाब दूंगा।" (OK, I will respond in Hindi now)

### Custom Wake Word

Edit `config.json` to add custom wake word variations:

```json
{
  "WAKE_WORDS": ["hey vaani", "hey vani", "ok vaani"],
  "WAKE_WORD_THRESHOLD": 0.85
}
```

### Logging Configuration

Create/edit `.env` file:

```env
LOG_LEVEL=INFO     # Options: DEBUG, INFO, WARNING, ERROR
```

**Log file location:** `logs/vaani.log`

---

## Next Steps

1. **Test Recognition**: Say "Hello" when Vaani starts (no wake word needed initially)
2. **Play Music**: "Play some music" or "Play [song name]"
3. **Ask Questions**: "Tell me about [topic]" or "What is [question]"
4. **During Music**: Say "Hey Vaani" first, then your command

For more details, see [Usage Documentation](usage.rst).
- Microphone and speakers
- Internet connection (for AI responses)

**Recommended:**
- Python 3.11+
- 4GB RAM
- macOS 12+ or Ubuntu 20.04+
- Google Gemini API key

---

## Getting API Keys

### Google Gemini (Required)

1. Go to [Google AI Studio](https://aistudio.google.com/app/api-keys)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key and add to `.env` file

### OpenAI (Optional)

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create account and add payment method
3. Create new API key
4. Copy the key and add to `.env` file

---

## What Gets Installed

### Python Packages (from requirements.txt)
- `telethon` - Telegram integration
- `aiohttp` - Async HTTP client
- `moviepy` - Video processing
- `pytesseract` - OCR
- `SpeechRecognition` - Voice recognition
- `yt-dlp` - YouTube downloads
- `edge-tts` - Text-to-speech
- `google-genai` - Google AI
- And many more...

### System Dependencies
- **PortAudio** - Audio I/O library
- **FFmpeg** - Audio/video processing
- **VLC** - Media player (for music playback)
- **Build tools** - Compilers for native extensions

---

## Support

For issues:
1. Check that all dependencies are installed
2. Verify Python version is 3.10+
3. Ensure `.env` has valid API keys
4. Check logs in `logs/vaani.log`

© Aman Kumar Pandey 2026-2027
