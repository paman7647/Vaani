# Vaani - My Personal AI Voice Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Vaani** (वाणी - meaning "voice" in Hindi) is an AI voice assistant I built from scratch as a personal project. It's privacy-focused, works offline, and supports 32 languages!

> **"I wanted a voice assistant I could actually trust and customize - so I built one."** - Aman Kumar Pandey

---

## ✨ Why I Built This

I got tired of voice assistants that:
- Send all my data to the cloud
- Don't work without internet
- Only work well in English
- Are locked down and can't be customized

So I built Vaani to solve these issues. It's been an amazing learning experience!

## 🚀 What Makes It Cool

### 🔒 **Privacy First**
- Most stuff runs on YOUR computer, not some company's server
- Only uses cloud when you need smart AI responses or web search
- You can go fully offline if you want
- No data collection, no tracking - just you and your assistant

### 🎯 **Actually Works**
- **Three recognition engines**: Google API, Vosk (offline), and Sphinx (backup)
- Switches automatically if one fails - you won't even notice
- Fast responses (2-5 seconds typically)
- Understands context from your previous questions

### 🌏 **Multilingual**
- Supports 32 languages (Hindi, English, Spanish, French, and many more)
- Switch languages anytime
- Great for multilingual households

### 🎵 **Plays Music**
- Stream from YouTube (because everyone uses YouTube for music!)
- Natural controls: "play", "pause", "skip", "volume up"
- Automatically lowers music when talking to you

---

## 🛠️ What's Inside

Built with some amazing open-source tools:

| What It Does | What I Used |
| :--- | :--- |
| **Smart Conversations** | Google Gemini AI |
| **Speech Recognition** | Vosk + Google Speech API + Sphinx |
| **Text-to-Speech** | pyttsx3 + Edge TTS |
| **Music Player** | VLC + yt-dlp |
| **Web Search** | DuckDuckGo (privacy-friendly!) |

---

## � Getting Started

### What You'll Need
- **Computer**: macOS, Linux, or Windows 10/11
- **Python**: Version 3.10 or newer
- **Audio**: A microphone and speakers (even laptop built-ins work!)
- **Internet**: Optional - core features work offline

### Super Easy Installation

I made setup scripts so you don't have to worry about dependencies:

#### 🍎 macOS / 🐧 Linux

```bash
# Grab the code
git clone https://github.com/paman7647/vaani.git
cd vaani

# Run my setup script (it handles everything)
chmod +x setup.sh
./setup.sh

# Start it up!
python3 main.py
```

#### 🪟 Windows

Open PowerShell as Administrator:

```powershell
git clone https://github.com/paman7647/vaani.git
cd vaani
.\setup.ps1
python main.py
```

### Quick Configuration

Want AI features? Add this to `.env` file:

```ini
# Get a free key from makersuite.google.com
GEMINI_API_KEY=your_key_here
```

That's it! Everything else works with defaults, but you can customize tons of stuff in `config.json`.

---

## 📚 Documentation

For deep dives into architecture, modules, and advanced usage, check out the **[docs/](docs/)** directory.

- [Installation Guide](docs/installation.rst)
- [Architecture Overview](docs/architecture.rst)
- [Voice System Details](docs/voice_system.rst)
- [Intelligence & NLP](docs/intelligence.rst)

### Hosted Docs (Read the Docs)

The project is configured for Read the Docs.

- Config file: [.readthedocs.yaml](.readthedocs.yaml)
- Build dependencies: [docs/requirements.txt](docs/requirements.txt)

To enable hosted docs:

1. Sign in at https://readthedocs.org with your GitHub account.
2. Import this repository into Read the Docs.
3. The default configuration will build Sphinx using `docs/conf.py`.
4. Your docs will be available at a URL like `https://<project-slug>.readthedocs.io`.

Optional: If you prefer the legacy config filename, [readthedocs.yml](readthedocs.yml) mirrors the main config.

### Directory Structure

- **`vaani/core/`**: The brain of the assistant.

## 💬 How to Use It

### Starting Up
```bash
# Activate the virtual environment (if you set one up)
source .venv/bin/activate

# Run it!
python3 main.py
```

### Try These Commands
- **Music**: "Play some jazz" / "Pause" / "Next song" / "Volume up"
- **Questions**: "What's the weather?" / "Tell me about quantum computing"
- **General Chat**: "Tell me a joke" / "Good morning" / "How are you?"
- **Time**: "What time is it?" / "What's the date?"

Just talk naturally - it understands context!

---

## 🐛 Having Issues?

**Microphone not working?**
- Make sure your mic isn't muted in system settings
- Try adjusting `ENERGY_THRESHOLD` in `config.json` (higher = less sensitive)

**Can't find Vosk model?**
- Run the setup script again: `./setup.sh`
- Models should be in the `models/` folder

**Music won't play?**
- Install VLC: `brew install --cask vlc` (macOS) or `apt install vlc` (Linux)
- Check your internet connection (YouTube needs it)

**Other issues?**
- Check the [full troubleshooting guide](docs/troubleshooting.rst)
- Or open an issue on GitHub - I'm happy to help!

---

## 🎯 What's Next?

Things I'm working on or planning:

- [x] Multi-engine speech recognition (Done!)
- [x] Music playback (Done!)
- [x] Web search integration (Done!)
- [ ] **GUI interface** - Visual dashboard
- [ ] **Smart home control** - HomeAssistant integration
- [ ] **Better memory** - Remember things across sessions
- [ ] **Voice profiles** - Multiple users
- [ ] **Mobile app** - Control from phone

Got ideas? Let me know in GitHub Discussions!

---

## 🤝 Want to Help?

I'd love contributions! Whether it's:
- Fixing bugs
- Adding features
- Improving documentation
- Testing on different systems
- Just giving feedback

**How to contribute:**
1. Fork the repo
2. Create a branch (`git checkout -b feature/awesome-thing`)
3. Make your changes
4. Test it out
5. Submit a pull request

Or just star the repo if you find it useful - it really motivates me to keep working on it!

---

## 👤 About Me

**Aman Kumar Pandey**

I'm a developer who loves working on AI and voice technology. Built Vaani as a personal learning project and to solve problems I had with existing assistants.

- GitHub: [@paman7647](https://github.com/paman7647)
- Email: paman7647@gmail.com

Feel free to reach out if you have questions or just want to chat about the project!

## 📄 License

MIT License - Free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

**Made with ❤️ by Aman Kumar Pandey**

*If you find Vaani useful, give it a star on GitHub! It really helps.* ⭐
Unauthorized copying or distribution of this code is strictly prohibited.
