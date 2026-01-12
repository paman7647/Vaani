Detailed Installation Guide
===========================

This guide provides exhaustive, step-by-step instructions for installing Vaani on macOS, Linux, and Windows. It covers both the **Automated** method (recommended) and the **Manual** method (for custom environments).

.. contents:: Table of Contents
   :depth: 2
   :local:

System Prerequisites
--------------------

Before beginning, ensure your system meets the following requirements:

*   **Operating System**:
    *   macOS 12.0+ (Monterey or newer) - Intel or Apple Silicon
    *   Linux (Ubuntu 22.04+, Fedora 38+, Arch Linux, Debian 11+)
    *   Windows 10 (21H2+) or Windows 11
*   **Hardware**:
    *   **CPU**: Any modern dual-core processor (x86_64 or ARM64).
    *   **RAM**: 4GB minimum (8GB recommended).
    *   **Microphone**: A working USB or internal microphone.
    *   **Internet**: Required for Google Gemini and Search features.
*   **Software**:
    *   **Git**: For cloning the repository.
    *   **Python**: Version 3.10 or higher.

Method 1: Automated Installation (Recommended)
----------------------------------------------

We provide scripts that automatically detect your OS, install system libraries (FFmpeg, PortAudio, VLC), set up the Python virtual environment, and download the necessary speech models.

Option A: macOS & Linux
^^^^^^^^^^^^^^^^^^^^^^^

Supported Shells: ``bash``, ``zsh``.

1.  **Clone the Repository**:
    Open your terminal and run:

    .. code-block:: bash

        git clone https://github.com/paman7647/vaani.git
        cd vaani

2.  **Make Script Executable**:
    Grant run permissions to the setup script.

    .. code-block:: bash

        chmod +x setup.sh

3.  **Run the Installer**:
    Execute the script. You may be prompted for your ``sudo`` password to install system packages.

    .. code-block:: bash

        ./setup.sh

    *What this does:*
    *   Updates ``apt``/``brew``/``dnf``.
    *   Installs ``python3-venv``, ``ffmpeg``, ``portaudio``, ``vlc``.
    *   Creates ``.venv/``.
    *   Pip installs ``requirements.txt``.
    *   Downloads Vosk models to ``models/``.

Option B: Windows (PowerShell)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1.  **Open PowerShell as Administrator**:
    Right-click the Start button -> **Windows Terminal (Admin)** or **PowerShell (Admin)**.

2.  **Clone the Repository**:

    .. code-block:: powershell

        git clone https://github.com/paman7647/vaani.git
        cd vaani

3.  **Set Execution Policy** (If needed):
    If scripts are blocked, allow local scripts to run.

    .. code-block:: powershell

        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

4.  **Run the Installer**:

    .. code-block:: powershell

        .\setup.ps1

Method 2: Manual Installation (Step-by-Step)
--------------------------------------------

Use this method if the automated script fails or if you prefer full control over the environment.

Step 1: Install System Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Vaani relies on C-level libraries for audio and media.

**macOS (Homebrew)**

.. code-block:: bash

    # Install main libraries
    brew install portaudio ffmpeg
    
    # Install VLC media player (required for playback)
    brew install --cask vlc

**Ubuntu / Debian**

.. code-block:: bash

    sudo apt update
    sudo apt install -y \
        python3-dev \
        python3-venv \
        build-essential \
        libasound2-dev \
        libportaudio2 \
        portaudio19-dev \
        ffmpeg \
        vlc

**Fedora / RHEL**

.. code-block:: bash

    sudo dnf install -y \
        python3-devel \
        portaudio-devel \
        alsa-lib-devel \
        ffmpeg \
        vlc

**Arch Linux**

.. code-block:: bash

    sudo pacman -S --needed \
        base-devel \
        python \
        portaudio \
        ffmpeg \
        vlc

**Windows**

1.  Download and install **Python 3.10+** from `Python.org <https://www.python.org/downloads/>`_. *Ensure you check "Add Python to PATH" during installation.*
2.  Install **VLC Media Player** from `VideoLAN.org <https://www.videolan.org/vlc/>`_.
3.  Install **FFmpeg**:
    *   *Option A (Chocolatey)*: ``choco install ffmpeg``
    *   *Option B (Manual)*: Download binaries, extract, and add the ``bin`` folder to your System PATH.

Step 2: Set Up Python Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Always use a virtual environment to avoid polluting your system Python.

.. code-block:: bash

    # Create the environment named '.venv'
    python3 -m venv .venv
    
    # Activate it (macOS/Linux)
    source .venv/bin/activate
    
    # Activate it (Windows)
    .\.venv\Scripts\Activate

Step 3: Install Python Packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the virtual environment active, install the dependencies.

.. code-block:: bash

    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

*Note for Raspbian/Arm users*: If ``piwheel`` fails, you may need to build ``pyaudio`` from source, which is handled by the ``portaudio19-dev`` apt package installed earlier.

Step 4: Download Speech Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Vaani requires offline models for Wake Word detection.

1.  Create a ``models`` directory in the project root:
    
    .. code-block:: bash
        
        mkdir models

2.  Download the **Indian English** model (recommended):
    *   **URL**: `https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip <https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip>`_
    *   **Action**: Download and extract the zip file.
    *   **Move**: Move the extracted folder ``vosk-model-small-en-in-0.4`` *inside* the ``models/`` directory.

3.  (Optional) Download **Hindi** model:
    *   **URL**: `https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip <https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip>`_
    *   **Action**: Extract to ``models/``.

*Directory Structure should look like this:*

.. code-block:: text

    vaani/
    ├── main.py
    ├── models/
    │   ├── vosk-model-small-en-in-0.4/
    │   └── vosk-model-small-hi-0.22/
    └── .venv/

Post-Installation Configuration
-------------------------------

1.  **API Keys**:
    Copy the example environment file.

    .. code-block:: bash

        cp .env.example .env

    Edit `.env` and add your keys:

    .. code-block:: ini

        GOOGLE_API_KEY=AIzaSy...    # Required for smart chat
        WEATHER_API_KEY=...         # Optional (OpenWeatherMap)

2.  **Verify Setup**:
    Run the application.

    .. code-block:: bash

        python main.py

    You should see:
    ``INFO:root:Vaani initialized successfully. Listening...``

Installation Troubleshooting
----------------------------

**1. "fatal error: portaudio.h: No such file or directory"**
This occurs during ``pip install pyaudio``. It means the C headers are missing.
*   **Fix**: Re-run the system dependency install step for your OS (e.g., ``sudo apt install portaudio19-dev``).

**2. "No module named 'vlc'"**
Ensure you installed the OS-level VLC application, not just the pip library.
*   **Fix**: Install VLC from `videolan.org <https://www.videolan.org/>`_.

**3. "Vosk model path not found"**
The application cannot find the model folder.
*   **Fix**: Ensure the folder is named exactly ``vosk-model-small-en-in-0.4`` and is inside ``models/``.

Method 3: Docker Installation (Containerized)
---------------------------------------------

For isolation and easy deployment, you can run Vaani in a Docker container.

1.  **Create a `Dockerfile`**
    Create a file named ``Dockerfile`` in the project root:

    .. code-block:: dockerfile

        FROM python:3.10-slim

        # Install system dependencies (ALSA, PortAudio, VLC, git, build tools)
        RUN apt-get update && apt-get install -y \
            git \
            build-essential \
            libasound2-dev \
            portaudio19-dev \
            libportaudio2 \
            ffmpeg \
            vlc \
            && rm -rf /var/lib/apt/lists/*

        # Set working directory
        WORKDIR /app

        # Install Python dependencies
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        # Copy application code
        COPY . .

        # Create models directory (expecting volume mount or download here)
        RUN mkdir -p models

        # Environment variables
        ENV PYTHONUNBUFFERED=1

        # Command to run
        CMD ["python", "main.py"]

2.  **Build the Image**

    .. code-block:: bash

        docker build -t vaani-assistant .

3.  **Run the Container**
    Running with audio support requires passing device privileges.

    *Linux (ALSA)*:

    .. code-block:: bash

        docker run -it \
            --device /dev/snd \
            -v $(pwd)/models:/app/models \
            -v $(pwd)/.env:/app/.env \
            vaani-assistant

    *Note: Audio passthrough on macOS/Windows Docker Desktop is experimental and complex. We recommend native installation for those platforms.*

Advanced: Offline / Air-Gapped Installation
-------------------------------------------

If you need to install Vaani on a machine without internet access:

1.  **On a connected machine**:
    Download all wheels and models.

    .. code-block:: bash

        # Download python packages
        mkdir vaani-pkg
        pip download -r requirements.txt -d vaani-pkg

        # Download Models manually from https://alphacephei.com/vosk/models
        # Save zip files

2.  **Transfer files** (USB/SCP) to the offline machine.

3.  **On the offline machine**:

    .. code-block:: bash

        # Install packages
        pip install --no-index --find-links=vaani-pkg -r requirements.txt

        # Extract models
        unzip vosk-model-small-en-in-0.4.zip -d models/

Development Environment Setup
-----------------------------

Setting up your IDE for the best experience.

**Visual Studio Code**

1.  **Extensions**: Install the "Python" and "Pylance" extensions.
2.  **Interpreter**: Command Palette (``Ctrl+Shift+P``) -> "Python: Select Interpreter" -> Select ``.venv/bin/python``.
3.  **Linting**: Enable ``flake8`` or ``pylint`` to catch errors early.
4.  **Debugging**:
    Create ``.vscode/launch.json``:

    .. code-block:: json

        {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Vaani: Run",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/main.py",
                    "console": "integratedTerminal",
                    "envFile": "${workspaceFolder}/.env"
                }
            ]
        }
