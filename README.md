# Vaani 🎙️

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=flat-square)](https://github.com/paman7647/vaani)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-ReadTheDocs-blue?style=flat-square)](https://vaani.readthedocs.io/)

> **Your personal, privacy-first AI voice assistant that actually works offline.**

**Vaani** (वाणी - "voice" in Hindi) is a proprietary voice assistant I built to solve my frustrations with existing options. It runs primarily on your machine, respects your privacy, speaks 32 languages, and you can customize everything.

```bash
# Quick Start
git clone https://github.com/paman7647/vaani.git
cd vaani && chmod +x setup.sh && ./setup.sh
python3 main.py
# Say "Hey Vaani" and start talking!
```

---

## Why Vaani?

**🔒 Privacy-Focused** → Most processing happens locally. Your voice stays on your device.  
**🗣️ 32 Languages** → English, Hindi, Spanish, French, and 28 more. Switch anytime.  
**🎵 Music Ready** → Stream from YouTube with voice control (pause, skip, volume).  
**🧠 Actually Smart** → Uses Google Gemini AI for natural conversations when you need it.  
**⚡ Fast & Reliable** → 3-engine recognition system (Google API → Vosk → Sphinx) with automatic fallback.

---

## What Can It Do?

- 🎤 **Voice Control**: Wake word detection, natural conversation flow
- 💬 **Smart Conversations**: Context-aware responses using AI
- 🔍 **Web Search**: Real-time information from DuckDuckGo
- 🎶 **Music Playback**: YouTube streaming with voice controls
- 🌍 **Multi-Language**: Switch between 32 languages seamlessly
- 🏠 **Runs Locally**: No cloud dependency for core features

---

## 🚀 Quick Setup

### Requirements
- Python 3.10+
- macOS, Linux, or Windows 10/11
- Microphone and speakers
- Internet (optional - works offline too!)

### Installation

**macOS / Linux:**
```bash
git clone https://github.com/paman7647/vaani.git
cd vaani
chmod +x setup.sh && ./setup.sh
```

**Windows (PowerShell as Admin):**
```powershell
git clone https://github.com/paman7647/vaani.git
cd vaani
.\setup.ps1
```

### Configuration (Optional)

Create a `.env` file for AI features:
```bash
# Get free key from makersuite.google.com
GEMINI_API_KEY=your_api_key_here
```

### Run It
```bash
python3 main.py
# Say "Hey Vaani" and start talking!
```

---

## 📚 Documentation

**Complete documentation is available at:** **[vaani.readthedocs.io](https://vaani.readthedocs.io/)**

- 📖 [Getting Started Guide](https://vaani.readthedocs.io/en/latest/getting_started.html)
- 🏗️ [Architecture Overview](https://vaani.readthedocs.io/en/latest/architecture.html)
- ⚙️ [Configuration Reference](https://vaani.readthedocs.io/en/latest/configuration.html)
- 🔧 [Troubleshooting](https://vaani.readthedocs.io/en/latest/troubleshooting.html)
- 💻 [Developer Guide](https://vaani.readthedocs.io/en/latest/development/project_structure.html)

---

## 💡 Usage Examples

```bash
# Start Vaani
python3 main.py

# Then try:
"Hey Vaani, play some jazz music"
"What's the weather today?"
"Tell me about quantum computing"
"Pause the music"
"What time is it?"
"Tell me a joke"
```

**Tip:** It understands context! You can have natural conversations without repeating "Hey Vaani" every time.

---

## 🛠️ Tech Stack

| Component | Technology |
|:---|:---|
| AI Brain | Google Gemini 2.5 Flash |
| Speech Recognition | Vosk + Google Speech API + Sphinx |
| Text-to-Speech | pyttsx3 + Edge TTS |
| Music Streaming | VLC + yt-dlp |
| Web Search | DuckDuckGo API |
| Audio Processing | PyAudio + sounddevice |

---

## 🗺️ Roadmap

- [x] Multi-engine speech recognition
- [x] YouTube music playback
- [x] Web search integration
- [ ] GUI interface
- [ ] Smart home integration (HomeAssistant)
- [ ] Voice profiles for multiple users
- [ ] Long-term memory persistence
- [ ] Mobile app

---

## 🐛 Troubleshooting

**Quick Fixes:**
- Microphone not working? → Check system permissions and `ENERGY_THRESHOLD` in `config.json`
- Vosk model missing? → Run `./setup.sh` again
- Music won't play? → Install VLC (`brew install vlc` or `apt install vlc`)

**Need more help?** Check the [full troubleshooting guide](https://vaani.readthedocs.io/en/latest/troubleshooting.html).

---

## 🤝 Contributing

Contributions are welcome! Whether you want to:
- 🐛 Fix bugs
- ✨ Add features
- 📝 Improve docs
- 🧪 Test on different platforms

**Check out the [Contributing Guide](https://vaani.readthedocs.io/en/latest/development/contributing.html) to get started.**

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

Free to use, modify, and distribute. No restrictions!

---

## 👤 Author

**Aman Kumar Pandey**

Built this as a personal project to learn about AI and voice technology. Feel free to reach out!

- 🐙 GitHub: [@paman7647](https://github.com/paman7647)
- 📚 Docs: [vaani.readthedocs.io](https://vaani.readthedocs.io/)

---

## 🌟 Show Your Support

If you find Vaani useful:
- ⭐ Star this repo
- 🐛 Report bugs
- 💡 Share ideas
- 🔀 Submit pull requests

**Made with ❤️ by Aman Kumar Pandey**
