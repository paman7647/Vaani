Performance Analysis & Optimization
===================================

This section provides a detailed analysis of Vaani's performance characteristics, focusing on latency, resource utilization, and optimization strategies. Understanding these metrics is crucial for deploying a responsive voice assistant.

Architecture-Level Performance
------------------------------

Vaani utilizes a hybrid architecture that balances **privacy** (local processing) and **intelligence** (cloud processing).

1. **Wake Word Detection (Vosk)**:
   - **Mechanism**: Continuous listing stream processed by a lightweight Kalman filter-based model.
   - **Latency**: < 200ms.
   - **Resource Usage**: Low CPU footprint (~5-10% on a single core of a modern CPU).
   
2. **Speech Recognition (ASR)**:
   - **Offloaded** (Google Speech API): Used for complex queries. High accuracy but introduces network latency (200-800ms).
   - **Local** (Vosk): Used for command control and offline mode. Zero network latency but requires ~500MB RAM for the model.

3. **Inference (Gemini)**:
   - The primary bottleneck for complex interactions. Response generation time depends on query complexity and API load, typically ranging from 1s to 3s.

Latency Optimization
--------------------

Reducing "Time-to-Response" (TTR) is the primary optimization goal.

Network Configuration
^^^^^^^^^^^^^^^^^^^^^
Since intelligence is cloud-backed, network stability is paramount.
- **DNS Resolution**: Use fast DNS providers (1.1.1.1 or 8.8.8.8) to reduce API connection setup time.
- **Keep-Alive**: The `requests` session in `Vaani/intellegence` handles connection pooling to avoid SSL handshake overhead on every turn.

Audio Buffering
^^^^^^^^^^^^^^^
The `pyaudio` stream buffer size (chunk size) directly impacts input latency.
- **Default Config**: 4096 frames (~0.1s at 44.1kHz).
- **Optimization**: Reducing chunk size to 1024 frames offers faster wake-word reaction but increases CPU interrupt frequency.

Strategies:

.. code-block:: python

   # Example: Adjusting chunk size in config (if exposed)
   CHUNK_SIZE = 1024  # Lower latency
   CHUNK_SIZE = 4096  # Lower CPU usage

Resource Utilization
--------------------

Memory (RAM)
^^^^^^^^^^^^
- **Baseline**: ~60MB (Python runtime + core libraries).
- **With Vosk Model**: +50MB (Small model) to +1.5GB (Large model).
- **Recommendation**: A Raspberry Pi 4 (2GB+) or standard laptop is sufficient. For constrained environments (Pi Zero), stick to the 'small' Vosk models.

CPU Profiling
^^^^^^^^^^^^^
The most CPU-intensive operations are:
1. **FFT (Fast Fourier Transform)**: Run continuously by `Vosk` on the audio stream.
2. **SSL Encryption**: During API calls to Google.
3. **Audio Decoding**: When playing music via VLC.

Multi-threading
---------------
Vaani uses threading to ensure the UI (listening loop) never blocks.
- **Main Thread**: Handles the event loop and audio input.
- **Worker Threads**: Handle API requests and TTS synthesis.
- **Process Isolation**: Used for `subprocess` calls (e.g., system commands) to avoid Global Interpreter Lock (GIL) contention.

Benchmarking Methodology
------------------------
To objectively measure performance changes:

1. **Record TTR**: Measure the delta between `End-of-Speech` detection and `First-Byte-Audio` output.
2. **Profile**: Use `cProfile` to identify hot code paths.

   .. code-block:: bash

      python -m cProfile -o profile.stats main.py
      # Analyze with snakeviz
      snakeviz profile.stats

