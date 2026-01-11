Installation
============

Getting Vaani up and running represents the first step in your journey. We offer two primary methods: an automated installer for speed, and a manual process for control.

choose the path that best suits your workflow.

Automated Installation (Recommended)
------------------------------------

The provided setup scripts handle system dependencies (FFmpeg, VLC), Python environment creation, and model downloading automatically.

**macOS & Linux**
^^^^^^^^^^^^^^^^^

Supported: macOS (Intel/Silicon), Ubuntu, Debian, Fedora, Arch.

.. code-block:: bash

   cd vaani
   chmod +x setup.sh
   ./setup.sh

**Windows 10/11**
^^^^^^^^^^^^^^^^^

Requires PowerShell 5.1+ (Run as Administrator).

.. code-block:: powershell

   cd vaani
   .\setup.ps1

What the script does:
1.  **Checks Prerequisites**: Verifies Python 3.10+ installation.
2.  **System Deps**: Installs FFmpeg, VLC, and PortAudio via native package managers (Homebrew, apt, dnf, choco).
3.  **Environment**: Creates a compliant virtual environment (`venv`).
4.  **Models**: Downloads the required Vosk speech models to `models/`.
5.  **Config**: Generates a `.env` file for your API keys.

Manual Installation
-------------------

If you prefer to configure the environment yourself or are on a non-standard system.

**1. System Dependencies**
^^^^^^^^^^^^^^^^^^^^^^^^^^

Before installing Python packages, ensure these system tools are present:

*   **FFmpeg**: Required for audio processing.
*   **VLC**: Required for media playback.
*   **PortAudio**: Required for microphone access.

*   **macOS**: `brew install ffmpeg portaudio --cask vlc`
*   **Ubuntu**: `sudo apt install ffmpeg vlc portaudio19-dev`
*   **Windows**: Install via `choco install ffmpeg vlc` or manually from official sites.

**2. Python Environment**
^^^^^^^^^^^^^^^^^^^^^^^^^

Create a fresh virtual environment to avoid conflicts.

.. code-block:: bash

   # Create venv
   python3 -m venv venv

   # Activate (macOS/Linux)
   source venv/bin/activate

   # Activate (Windows)
   .\venv\Scripts\Activate

**3. Install Libraries**
^^^^^^^^^^^^^^^^^^^^^^^^

Install the core Python dependencies.

.. code-block:: bash

   pip install -r requirements.txt

**4. Download Speech Models**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Vaani uses **Vosk** for offline recognition. You must download the models manually:

1.  Create a folder named `models` in the root directory.
2.  Download **vosk-model-small-en-in-0.4** (Indian English) from `Vosk Models <https://alphacephei.com/vosk/models>`_.
3.  Extract it into `models/` so the path is `models/vosk-model-small-en-in-0.4/`.

**5. Configuration**
^^^^^^^^^^^^^^^^^^^^

Copy the example configuration:

.. code-block:: bash

   # macOS/Linux
   cp .env.example .env

   # Windows
   copy .env.example .env

Edit `.env` and add your **GOOGLE_API_KEY** (Get one from Google AI Studio).

Verifying Installation
----------------------

To confirm everything works:

.. code-block:: bash

   python3 main.py

**Success Indicators:**
1.  "VANI Voice Assistant Ready" appears in console.
2.  No errors about missing modules.
3.  Microphone starts listening (indicated by logs).

Troubleshooting
---------------

**"PortAudio not found" / "PyAudio install failed"**
This usually means the system header files are missing.
- **Ubuntu**: `sudo apt install portaudio19-dev`
- **macOS**: `brew install portaudio`

**"Vosk model not found"**
Ensure the directory structure matches exactly: `models/vosk-model-small-en-in-0.4/`.

**"GoogleGenerativeAI Error"**
Ensure your `.env` file has a valid `GOOGLE_API_KEY`.
