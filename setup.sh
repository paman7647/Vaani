#!/bin/bash
################################################################################
# Vaani Voice Assistant - Universal Setup Script
# Version 1.0
# Supports: macOS, Linux (Ubuntu/Debian, Fedora, Arch)
# 
# This script installs everything you need - system dependencies, Python 
# packages, and language models. No manual steps required.
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Vaani Voice Assistant Setup v1.0        ║${NC}"
echo -e "${CYAN}║   Universal Installer for macOS & Linux   ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${GREEN}✓${NC} Detected: macOS"
elif [[ -f /etc/os-release ]]; then
    . /etc/os-release
    if [[ -f /etc/debian_version ]]; then
        OS="debian"
        echo -e "${GREEN}✓${NC} Detected: $PRETTY_NAME"
    elif [[ -f /etc/fedora-release ]]; then
        OS="fedora"
        echo -e "${GREEN}✓${NC} Detected: $PRETTY_NAME"
    elif [[ -f /etc/arch-release ]]; then
        OS="arch"
        echo -e "${GREEN}✓${NC} Detected: Arch Linux"
    else
        OS="linux"
        echo -e "${YELLOW}⚠${NC} Unknown Linux distribution, attempting generic install"
    fi
else
    echo -e "${RED}✗${NC} Unsupported OS. Use setup.ps1 for Windows."
    exit 1
fi

# Check Python
echo ""
echo -e "${BLUE}[1/6]${NC} Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Installing..."
    if [[ "$OS" == "macos" ]]; then
        brew install python@3.11
    elif [[ "$OS" == "debian" ]]; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
    elif [[ "$OS" == "fedora" ]]; then
        sudo dnf install -y python3 python3-pip
    elif [[ "$OS" == "arch" ]]; then
        sudo pacman -Sy python python-pip
    fi
fi

# Install system dependencies
echo ""
echo -e "${BLUE}[2/6]${NC} Installing system dependencies..."

if [[ "$OS" == "macos" ]]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}⚠${NC} Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install portaudio ffmpeg
    brew install --cask vlc 2>/dev/null || echo "VLC already installed"
    echo -e "${GREEN}✓${NC} System dependencies installed"
    
elif [[ "$OS" == "debian" ]]; then
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg vlc \
        libportaudio2 libasound2-dev build-essential libssl-dev libffi-dev
    echo -e "${GREEN}✓${NC} System dependencies installed"
    
elif [[ "$OS" == "fedora" ]]; then
    sudo dnf install -y portaudio-devel ffmpeg vlc alsa-lib-devel gcc \
        python3-devel openssl-devel libffi-devel
    echo -e "${GREEN}✓${NC} System dependencies installed"
    
elif [[ "$OS" == "arch" ]]; then
    sudo pacman -Sy portaudio ffmpeg vlc base-devel openssl libffi
    echo -e "${GREEN}✓${NC} System dependencies installed"
fi

# Install Python packages
echo ""
echo -e "${BLUE}[4/6]${NC} Installing Python packages..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Python packages installed"

# Download language models
echo ""
echo -e "${BLUE}[5/6]${NC} Downloading Vosk language models..."
mkdir -p models
cd models

# Indian English Model
if [ ! -d "vosk-model-small-en-in-0.4" ]; then
    echo -e "${CYAN}→${NC} Downloading Indian English model (36MB)..."
    curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip -o en-in.zip
    unzip -q en-in.zip && rm en-in.zip
    echo -e "${GREEN}✓${NC} Indian English model installed"
else
    echo -e "${GREEN}✓${NC} Indian English model already exists"
fi

# Hindi Model
if [ ! -d "vosk-model-small-hi-0.22" ]; then
    echo -e "${CYAN}→${NC} Downloading Hindi model (42MB)..."
    curl -L https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip -o hi.zip
    unzip -q hi.zip && rm hi.zip
    echo -e "${GREEN}✓${NC} Hindi model installed"
else
    echo -e "${GREEN}✓${NC} Hindi model already exists"
fi

# US English Model (fallback)
if [ ! -d "vosk-model-small-en-us-0.15" ]; then
    echo -e "${CYAN}→${NC} Downloading US English model (39MB)..."
    curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o en-us.zip
    unzip -q en-us.zip && rm en-us.zip
    echo -e "${GREEN}✓${NC} US English model installed"
else
    echo -e "${GREEN}✓${NC} US English model already exists"
fi

cd ..

# Create .env file
echo ""
echo -e "${BLUE}[6/6]${NC} Creating environment configuration..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Google Gemini API Key (Required)
# Get your key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_api_key_here

# Optional: Logging level
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✓${NC} Created .env file"
    echo -e "${YELLOW}⚠${NC} Remember to add your Google API key to .env"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete! 🎉                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo -e "1. Add your API key: ${CYAN}nano .env${NC}"
echo -e "2. Activate environment: ${CYAN}source venv/bin/activate${NC}"
echo -e "3. Start Vaani: ${CYAN}python3 main.py${NC}"
echo ""
echo "Installed models:"
ls -1 models/ | grep vosk
echo ""
