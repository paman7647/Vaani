# Vaani - The Natural Voice Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey?style=for-the-badge&logo=linux)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

**Vaani** is an advanced, context-aware voice assistant designed to bridge the gap between human interaction and machine intelligence. It prioritizes privacy, speed, and natural conversation flow.

> **"Every interaction should feel like talking to a helpful friend, not commanding a machine."**

---

## ✨ Key Features

### 🧠 **Natural Intelligence**
- **Context-Aware Listening**: Distinguishes between casual conversation and commands. It knows when you are talking *to* it versus *near* it.
- **Smart Wake Word**: Supports relaxed triggers like *"Hey Vaani"*, *"Hi Vani"*, or *"Hey Google"* (catching common mistakes).
- **Grounded Information**: Uses real-time web search (DuckDuckGo/Google) to provide up-to-date answers, not just training data hallucinations.

### ⚡ **Triple-Layer Recognition Engine**
1.  **Vosk (Local & Fast)**: Offline recognizer for immediate privacy and sub-100ms latency.
2.  **Google Speech (Cloud High-Fidelity)**: Falls back to cloud recognition for complex, multi-sentence queries.
3.  **PocketSphinx (Backup)**: Functions completely offline when internet is unavailable.

### 🎵 **Media & Entertainment**
- **Native VLC Integration**: Plays music from YouTube with full playback controls (Play, Pause, Skip, Volume).
- **Music Ducking**: Automatically lowers volume when you speak to it.

### 🇮🇳 **Indian Context Optimized**
- **Voice Mapping**: specific TTS voices mapped to languages (`hi` -> Veena, `ta` -> Vani).
- **Accent Support**: Tuned for Indian English accents.

---

## 🛠️ Technology Stack

Vaani is built on a robust stack of open-source technologies:

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Generative AI** | Google Gemini 2.5 Flash | The conversational brain. |
| **Recognition** | Vosk + SpeechRecognition | Hybrid offline/online ASR engine. |
| **Response** | Google TTS + PyTTSx3 | Natural sounding voice synthesis. |
| **Media** | VLC + yt-dlp | High-quality streaming audio engine. |
| **Search** | DuckDuckGo | Privacy-focused real-time information. |
| **Memory** | JSON / Local | Session-based context retention. |

---

## 🚀 Installation & Setup

### Prerequisites
- **OS**: macOS, Linux (Ubuntu, Fedora, Arch), or **Windows 10/11**.
- **Python**: 3.10+.
- **System Libraries**: `portaudio`, `ffmpeg`, `vlc`.

### Quick Start (Automated)

#### 🍎 macOS / 🐧 Linux
We provide a universal setup script that handles everything:

```bash
# 1. Clone the repository
git clone https://github.com/paman7647/vaani.git
cd vaani

# 2. Run the installer
chmod +x setup.sh
./setup.sh
```

#### 🪟 Windows (PowerShell)
Run as **Administrator**:

```powershell
# 1. Clone the repository
git clone https://github.com/paman7647/vaani.git
cd vaani

# 2. Run the setup script
.\setup.ps1
```

### Configuration
After installation, configure your environment in `.env`:

```ini
# Required: Get key from makersuite.google.com
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Weather Services
WEATHER_API_KEY=your_openweathermap_key
```

### ⚙️ Advanced Config (`config.json`)
You can fine-tune the assistant's behavior in `config.json`:

| Key | Default | Description |
| :--- | :--- | :--- |
| `WAKE_WORDS` | `["hey vani", "vani"]` | List of triggers to activate the assistant. |
| `ENERGY_THRESHOLD` | `300` | Sensitivity of microphone (Lower = more sensitive). |
| `SPEECH_RATE` | `160` | Speed of the text-to-speech voice. |
| `MUSIC_DUCK_VOLUME` | `0.15` | Volume level (15%) when Assistant talks over music. |
| `Use_GOOGLE_SEARCH_GROUNDING` | `true` | Enable real-time web access for answers. |

---

## 📚 Documentation

For deep dives into architecture, modules, and advanced usage, check out the **[docs/](docs/)** directory.

- [Installation Guide](docs/installation.rst)
- [Architecture Overview](docs/architecture.rst)
- [Voice System Details](docs/voice_system.rst)
- [Intelligence & NLP](docs/intelligence.rst)

### Directory Structure

- **`vaani/core/`**: The brain of the assistant.

## 🎮 Usage Guide

### Starting the Assistant
```bash
source venv/bin/activate
python3 main.py
```

### Common Commands
- **Music**: *"Play some lo-fi beats."*, *"Stop the music."*, *"Next song."*
- **Information**: *"Who won the cricket world cup?"*, *"Search for python tutorials."*
- **Utility**: *"Set a timer for 10 minutes."*, *"What is the time?"*
- **General**: *"Tell me a joke."*, *"How are you doing?"*

---

## 🔧 Troubleshooting

**Microphone not listening?**
- Check `ENERGY_THRESHOLD` in `config.json`. Increase to `500` for noisy environments.
- Ensure your system mic input is not muted.

**"Vosk model not found"?**
- Run `./setup.sh` again to redownload missing models.
- Ensure `models/` directory exists in the root.

**Music not playing?**
- Ensure `vlc` is installed (`brew install --cask vlc` or `apt install vlc`).

---

## 🗺️ Roadmap

- [x] Multi-engine Speech Recognition
- [x] Basic Music Playback
- [ ] **GUI Interface**: A visual dashboard for interactions.
- [ ] **Home Automation**: MQTT/HomeAssistant integration.
- [ ] **Memory Persistence**: Long-term memory of user preferences (Vector DB).



## ⚠️ Project Status

**🚧 Under Development 🚧**

Vaani is currently in **Alpha**. Core features are functional, but you may encounter bugs or incomplete features. APIs and configuration structures may change.

### Known Issues
- Wake word detection may struggle in noisy environments (tuning `ENERGY_THRESHOLD` helps).
- Response latency depends heavily on internet connection speed (for Gemini + Google TTS).

### Reporting Bugs
Found a bug? Have a feature request?
1.  Check the **[Issues](https://github.com/paman7647/vaani/issues)** tab to see if it's already reported.
2.  If not, open a new issue with:
    - Steps to reproduce.
    - Error logs (check the console output).
    - Your OS and Python version.

---

## 🤝 Contribution

We welcome contributions! Please open an issue first to discuss major changes.

1.  Fork the repo and create your branch (`git checkout -b feature/cool-new-thing`).
2.  Commit your changes (`git commit -m 'Add some cool-new-thing'`).
3.  Push to the branch (`git push origin feature/cool-new-thing`).
4.  Open a Pull Request.

## 👤 Author

**Aman Kumar Pandey**
- GitHub: [@paman7647](https://github.com/paman7647)

## 📄 License

**Proprietary Software**. Copyright © 2026 Aman Kumar Pandey. All Rights Reserved.
Unauthorized copying or distribution of this code is strictly prohibited.
