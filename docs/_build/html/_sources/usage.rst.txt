Using Vaani
===========

How to interact with Vaani and use its capabilities.

First Interaction
-----------------

**Start Vaani**

.. code-block:: bash

   python3 main.py

You'll see:

.. code-block:: text

   Vaani Assistant starting...
   Listening...
   [Microphone icon]

**Say Something**

Speak naturally to the microphone. Say:

- "Hey Aria, what time is it?"
- "What's the weather like?"
- "Play some music"

Vaani will:

1. Recognize your speech
2. Think about your request
3. Speak a response
4. Play audio/music if needed

**Common First Commands**

.. code-block:: text

   "What's your name?"
   → Vaani tells you about itself
   
   "What can you do?"
   → Lists capabilities
   
   "Tell me about yourself"
   → Personality introduction
   
   "Play some rock music"
   → Finds and plays YouTube music
   
   "What's the weather in London?"
   → Searches and reports weather

Core Commands
-------------

**Information Queries**

Ask Vaani questions and it searches the web for answers:

.. code-block:: text

   "What's the capital of France?"
   "How tall is Mount Everest?"
   "When was the internet invented?"
   "Who won the World Cup?"
   "What's the temperature outside?"

Vaani will search the web and provide current information.

**Time and Reminders**

.. code-block:: text

   "What time is it?"
   → Current time in your timezone
   
   "What's today's date?"
   → Today's date
   
   "Set a reminder for lunch"
   → Sets a reminder (supported in some configurations)

**Music Playback**

Vaani can find and play music from YouTube:

.. code-block:: text

   "Play some jazz"
   → Random jazz playlist
   
   "Play [Artist Name] [Song Name]"
   → Specific song, e.g. "Play The Beatles Let It Be"
   
   "Play rock music"
   → Random rock songs
   
   "Play movie soundtracks"
   → Instrumental/theme music

Music plays through your system audio.

**Conversation**

Vaani remembers conversation context:

.. code-block:: text

   You: "What's the weather in New York?"
   Aria: "It's 72°F and sunny"
   
   You: "How about Tokyo?"
   Aria: "In Tokyo it's 28°C and partly cloudy"
   
   Vaani understands "Tokyo" refers to your previous question
   about weather, not a separate query.

**About Vaani**

.. code-block:: text

   "Tell me about yourself"
   → Vaani's background and purpose
   
   "What's your personality like?"
   → Description of Vaani's communication style
   
   "How do you work?"
   → Technical explanation of capabilities

Advanced Usage
--------------

**Multi-Turn Conversations**

Vaani maintains conversation context across turns:

.. code-block:: text

   You: "Who's the president of the United States?"
   Aria: "As of 2024, it's Joe Biden"
   
   You: "How old is he?"
   Aria: "He was born on November 20, 1942, making him 81 years old"
   
   You: "What about his vice president?"
   Aria: "That would be Kamala Harris"

Each response uses the previous context.

**Fact-Based Queries**

For questions requiring current information, Vaani searches the web:

.. code-block:: text

   "What's trending on Twitter?"
   "What are the latest tech news?"
   "How's the stock market doing?"
   "What's happening in Ukraine?"

**Specific Artist/Song Requests**

For exact songs, use the full song name:

.. code-block:: text

   ✓ "Play Hotel California by the Eagles"
   ✓ "Play Bohemian Rhapsody Queen"
   ✓ "Play Stairway to Heaven"
   
   ✗ "Play that song from the 80s" (too vague)
   ✗ "Play something I heard on the radio" (too vague)

**Conversation About Results**

After Vaani provides information, discuss it:

.. code-block:: text

   You: "What's Python?"
   Aria: "Python is a programming language known for..."
   
   You: "What are its main uses?"
   Aria: "The main uses are web development, data science..."
   
   You: "Can I learn it quickly?"
   Aria: "Yes, Python is known for being beginner-friendly..."

**Clarifying Follow-ups**

If Vaani misunderstands:

.. code-block:: text

   You: "Tell me about Java"
   Aria: "Java is an island in Indonesia..."
   
   You: "No, Java the programming language"
   Aria: "Java is an object-oriented programming language..."

Vaani learns from corrections within the conversation.

What Vaani Can Do
-----------------

**✓ Speech Recognition**

- Understands multiple languages (32 total)
- Works with accents and dialects
- Handles background noise (with some limitation)

**✓ Web Search**

- Current information (weather, news, facts)
- Real-time data (stock prices, sports scores)
- General knowledge questions

**✓ Music**

- Find music on YouTube
- Play audio through your speakers
- Queue and playback control

**✓ Conversation**

- Multi-turn dialogue
- Context retention across messages
- Personality-driven responses
- Natural language understanding

**✓ Customization**

- Language preference (32 languages)
- Voice preference (male/female/other)
- Response style (professional/casual)
- API configuration

What Vaani Cannot Do
---------------------

**✗ Real-time Actions**

Vaani cannot:

- Control your computer (open files, click buttons)
- Send emails or messages
- Make purchases or payments
- Download files
- Execute arbitrary commands

**✗ Complex Analysis**

Vaani cannot:

- Analyze images or documents you show
- Process large data sets
- Perform complex calculations (though it tries!)
- Debug your code (limited capability)

**✗ Persistent Storage**

Vaani cannot:

- Remember conversations between restarts
- Access your files or personal data
- Access the internet beyond web search
- Store files or create documents

**✗ Advanced Functions**

Vaani cannot:

- Make phone calls
- Send text messages
- Control smart home devices
- Access private accounts (email, banking)

(Some of these may be possible with custom development—see :doc:`../customization`)

Troubleshooting Common Issues
-----------------------------

**"Vaani doesn't hear me"**

Solutions:

1. Move closer to the microphone
2. Check microphone is enabled: ``Settings`` → ``Sound``
3. Reduce background noise
4. Check microphone volume in system settings
5. Verify microphone works: ``python3 test_audio_direct.py``

**"Vaani misunderstands my accent"**

Try:

1. Speak clearly and slowly
2. Rephrase after Vaani misunderstands
3. Change language setting if you're bilingual
4. Check ``docs/configuration.rst`` for speech recognition options

**"Music won't play"**

Check:

1. System volume isn't muted
2. Audio device is working: ``python3 test_music.py``
3. YouTube is accessible in your region
4. No firewall blocking YouTube access

**"Vaani gives wrong information"**

Remember:

1. Web searches can be inaccurate
2. Vaani doesn't verify information
3. You should verify important facts
4. Vaani might misunderstand your question

See :doc:`../troubleshooting` for more help.

Customization
--------------

Change how Vaani behaves:

**Change Language**

.. code-block:: bash

   # Interactive setup
   python3 -c "from vaani_assistant.config import global_config; global_config.setup_initial()"
   
   # Or edit .env file
   echo "VOICE_LANGUAGE=es" >> .env

See :doc:`../configuration` for all options.

**Change Voice**

.. code-block:: bash

   # Edit .env
   echo "TTS_ENGINE_VOICE_ID=female_deep" >> .env

See :doc:`../configuration` for voice options by language.

**Adjust Response Style**

Configuration includes personality settings:

.. code-block:: bash

   echo "ASSISTANT_PERSONALITY=formal" >> .env
   # or
   echo "ASSISTANT_PERSONALITY=casual" >> .env

See :doc:`../customization` for detailed options.

Tips and Tricks
---------------

**Phrasing Questions**

Instead of vague queries, be specific:

.. code-block:: text

   ✓ "What was the first iPhone model?"
   ✗ "Tell me about iPhones"
   
   ✓ "What's the population of Tokyo?"
   ✗ "Tell me about Tokyo"
   
   ✓ "Play songs by David Bowie"
   ✗ "Play some rock music"

**Waiting for Responses**

Vaani needs time to:

1. Recognize your speech
2. Send query to AI engine
3. Optionally search the web
4. Generate response
5. Convert response to speech

Typical response time: 2-5 seconds depending on query complexity.

**Handling Misunderstandings**

When Vaani misunderstands:

.. code-block:: text

   ✓ "No, I meant..." (gives context)
   ✓ "That's not what I asked" (corrects Vaani)
   ✓ Rephrase your question completely
   
   ✗ "You're wrong" (Vaani can't improve from this)

**Music Quality**

Music quality depends on:

1. YouTube source quality
2. Your internet bandwidth
3. Your audio device
4. Your speaker system

Expect MP3-quality audio (128-320 kbps).

**Long Conversations**

Vaani remembers conversation context, but:

1. Memory accumulates during a session
2. Context is reset when you restart Vaani
3. Very long conversations (100+ messages) may slow response
4. See :doc:`../memory_context` for technical details

Advanced Configuration
----------------------

For power users, see:

- :doc:`../configuration` - All configuration options
- :doc:`../customization` - Adapting Vaani for your needs
- :doc:`project_structure` - Understanding the code
- :doc:`../voice_system` - Audio input/output details

Getting Help
------------

If something isn't working:

1. Check :doc:`../troubleshooting` guide
2. Review :doc:`../faq` for common questions
3. Check logs: ``cat logs/error.log``
4. Enable debug logging: ``LOG_LEVEL=DEBUG python3 main.py``

See :doc:`../troubleshooting` for detailed help.

Next Steps
----------

- Explore :doc:`../customization` to adapt Vaani
- Read :doc:`../voice_system` for audio details
- Check :doc:`../intelligence` for how responses are generated
- See :doc:`../memory_context` for conversation handling
