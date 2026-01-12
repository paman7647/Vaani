Deployment
==========

This section outlines the deployment strategies and operational considerations for the Vaani Voice Assistant. As a real-time system involving audio processing, network requests, and hardware integration, proper deployment is critical for ensuring low latency and reliability.

System Architecture in Deployment
---------------------------------

Vaani operates as a hybrid edge-cloud application. The deployment environment must support:
- **Local Processing**: Vosk ASR and Wake Word detection require local CPU resources.
- **Network I/O**: Gemini API and Google Speech fallback require stable internet connectivity.
- **Audio Hardware**: Direct access to ALSA (Linux), CoreAudio (macOS), or WASAPI (Windows).

Environment Setup
-----------------

To ensure reproducibility and stability, we support two primary deployment methodologies: an automated shell-script based approach for standard environments, and a comprehensive manual process for custom configurations.

Method A: Automated Deployment (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For valid POSIX-compliant systems (macOS, Debian/Ubuntu, Fedora, Arch), the `setup.sh` script provides a "one-click" provisioning experience. It handles system-level dependencies, Python environment creation, and model acquisition.

**Execution:**

.. code-block:: bash

   # 1. Ensure execution permissions
   chmod +x setup.sh

   # 2. Run the provisioner
   ./setup.sh

**Operations Performed:**
1. **System Detection**: Identifies the OS and package manager (`apt`, `dnf`, `brew`, `pacman`).
2. **Dependency Injection**: Installs `portaudio`, `ffmpeg`, and `vlc` via the native package manager.
3. **Environment Isolation**: Creates a local `.venv` and installs pinned Python dependencies.
4. **Asset Acquisition**: Downloads and validates the `Vosk` speech models into the `models/` directory.

Method B: Manual Deployment (Step-by-Step)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For environments requiring granular control or non-standard paths, follow this strictly ordered procedure.

**1. System Dependencies**
Ensure the following libraries are present in the library path/linker path:

- **PortAudio**: Required for PyAudio microphone access.
- **FFmpeg**: Required for audio transcoding (via `yt-dlp`).
- **VLC (libvlc)**: Required for the media playback engine.

*Example (Ubuntu):*

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y portaudio19-dev ffmpeg vlc libportaudio2

**2. Python Environment**
We enforce the use of virtual environments to prevent `sys.path` pollution.

.. code-block:: bash

   # Create the virtual environment
   python3 -m venv .venv
   
   # Activate the environment (Bash/Zsh)
   source .venv/bin/activate

**3. Application Dependencies**
Install the application-specific libraries defined in the manifest.

.. code-block:: bash

   pip install -r requirements.txt

**4. Model Provisioning**
The application requires local ASR models to function.
1. Create a `models/` directory in the project root.
2. Download a compatible Vosk model (e.g., `vosk-model-small-en-in-0.4`).
3. Extract the archive such that the model folder is directly inside `models/`.

Service Daemonization
---------------------

For a "always-on" assistant experience, Vaani should be run as a background daemon. We provide configurations for the two most common init systems: **systemd** (Linux) and **launchd** (macOS).

Linux: Systemd Service
^^^^^^^^^^^^^^^^^^^^^^

Systemd offers robust process supervision. The following unit file ensures Vaani starts after the network and sound subsystems are initialized.

**File Location**: ``/etc/systemd/system/vaani.service``

.. code-block:: ini

    [Unit]
    Description=Vaani Voice Assistant Service
    # Critical: Wait for network and audio to be ready to avoid startup race conditions
    After=network.target sound.target

    [Service]
    Type=simple
    User=myuser
    # Set the working directory to the project root to ensure relative paths (like models/) resolve correctly
    WorkingDirectory=/home/myuser/vaani
    # Unbuffered output ensures logs appear immediately in journalctl
    Environment="PYTHONUNBUFFERED=1"
    ExecStart=/home/myuser/vaani/.venv/bin/python /home/myuser/vaani/main.py
    # Auto-restart logic for resilience
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=multi-user.target

**Management Commands**:

.. code-block:: bash

    sudo systemctl daemon-reload      # Reload configuration
    sudo systemctl enable vaani       # Enable on boot
    sudo systemctl start vaani        # Start immediately
    journalctl -u vaani -f            # Follow logs in real-time

macOS: LaunchAgent
^^^^^^^^^^^^^^^^^^

On macOS, `launchd` manages user-session agents. Unlike system daemons, a LaunchAgent has access to the graphical user session, which is often required for audio permission validation.

**File Location**: ``~/Library/LaunchAgents/com.vaani.assistant.plist``

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.vaani.assistant</string>
        
        <key>ProgramArguments</key>
        <array>
            <string>/Users/myuser/vaani/.venv/bin/python</string>
            <string>/Users/myuser/vaani/main.py</string>
        </array>
        
        <key>WorkingDirectory</key>
        <string>/Users/myuser/vaani</string>
        
        <key>RunAtLoad</key>
        <true/>
        
        <key>KeepAlive</key>
        <true/>
        
        <!-- Log redirection for debugging -->
        <key>StandardOutPath</key>
        <string>/Users/myuser/vaani/logs/vaani.out</string>
        <key>StandardErrorPath</key>
        <string>/Users/myuser/vaani/logs/vaani.err</string>
    </dict>
    </plist>

**Management Commands**:

.. code-block:: bash

    launchctl load ~/Library/LaunchAgents/com.vaani.assistant.plist
    launchctl start com.vaani.assistant

Operational Considerations
--------------------------

Security & API Keys
^^^^^^^^^^^^^^^^^^^
Vaani relies on external APIs (Google Gemini). **Never** hardcode API keys in the source. We utilize a `.env` file strategy:

- Production keys are injected via the environment or a secure execution context.
- File permissions on `.env` should be restricted (``chmod 600 .env``).

Model Management
^^^^^^^^^^^^^^^^
The ASR (Automatic Speech Recognition) models are significant artifacts (~50MB - 100MB).
- **Update Checks**: The ``setup.sh`` script includes checksum logic to only download models if they are missing or corrupted.
- **Path Resolution**: The codebase dynamically resolves model paths relative to the project root. Ensure the working directory is set correctly in service files.
