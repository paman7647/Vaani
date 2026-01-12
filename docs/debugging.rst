Debugging & Troubleshooting
===========================

This section details the methodologies for diagnosing and resolving issues within the Vaani system. Given the asynchronous nature of voice assistants (input -> processing -> output), debugging requires a systematic isolation of components.

Log Analysis
------------

Logs are the primary source of truth. Vaani uses the standard Python `logging` module.

Log Levels
^^^^^^^^^^

- **INFO** (Default): High-level flow events (e.g., "Wake word detected", "Playing song").
- **DEBUG**: Verbose output including raw ASR transcripts, API payloads, and audio buffer states.
- **ERROR**: Critical failures that stop a specific interaction.

To enable debug logging, modify the `.env` file or set the environment variable:

.. code-block:: bash

    export LOG_LEVEL=DEBUG
    python main.py

Common Error Patterns
---------------------

1. **"Vosk model path not found"**
   - **Cause**: The `models/` directory is missing or empty.
   - **Fix**: Run `setup.sh` again to download models, or manually extract the zip files to the root.

2. **"Input Overflowed" (PyAudio)**
   
   - **Cause**: The application is not processing the audio buffer fast enough.
   - **Fix**:
   
     - Increase `CHUNK` size in configuration.
     - Move heavy processing (like API calls) to a background thread (already implemented in core, but check for custom modifications).

3. **"ALSA lib pcm.c:..." (Linux)**
   - **Cause**: Low-level audio driver warnings. Often harmless but can indicate device contention.
   - **Fix**: Ensure no other application has exclusive lock on the microphone.

Component Isolation
-------------------

If the system is unresponsive, test each subsystem independently.

Testing Audio Input
^^^^^^^^^^^^^^^^^^^
Verify that Python can "hear" the microphone.

.. code-block:: python

    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    print("Heard something")

Testing TTS (Text-to-Speech)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Verify that the system can speak.

.. code-block:: python

    import pyttsx3
    engine = pyttsx3.init()
    engine.say("System check initiated.")
    engine.runAndWait()

Testing Network/API
^^^^^^^^^^^^^^^^^^^
Isolate the Gemini API client.

.. code-block:: python

    import os
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello")
    print(response.text)

Debugging Process Checklist
---------------------------

1. **Reproduce**: Can you trigger the bug consistently?
2. **Isolate**: Is it the Mic, the Brain, or the Speaker?
3. **Log**: What happened right before the failure?
4. **Environment**: Did the Python version or dependencies change?

Reporting Issues
----------------

When opening a GitHub issue, include:
- `python --version`
- OS Details (`uname -a`)
- The last 20 lines of the log file.

