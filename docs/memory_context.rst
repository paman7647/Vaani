Memory and Conversation Context
=================================

How Vaani remembers and understands conversations.

Overview
--------

Vaani's memory system enables:

1. **Context Awareness** - Understanding references to previous messages
2. **Multi-turn Dialogue** - Natural back-and-forth conversations
3. **Entity Memory** - Remembering people, places, topics mentioned
4. **Conversation State** - Tracking the current discussion

This makes conversations feel natural rather than disjointed.

Memory Architecture
-------------------

**Three-Layer Memory System**

.. code-block:: text

   Layer 1: Short-term Buffer (Last 5-10 messages)
   ├─ Most recent exchanges
   ├─ Used for immediate context
   └─ Rapidly fades if not referenced
   
   Layer 2: Active Context (Last 20-50 messages)
   ├─ Current conversation thread
   ├─ Entities and topics mentioned
   └─ Used for understanding references
   
   Layer 3: Session History (Entire session)
   ├─ All previous messages
   ├─ Available if needed
   └─ Cleared when Vaani restarts

**Memory Storage**

Memory is stored in memory:

.. code-block:: python

   {
       "session_id": "1234567890",
       "created": "2024-01-15 14:00:00",
       "messages": [
           {
               "timestamp": "2024-01-15 14:00:05",
               "user": "What's the weather in New York?",
               "vaani": "It's 72°F and sunny",
               "intent": "WEATHER_QUERY",
               "entities": [{"type": "LOCATION", "value": "New York"}]
           },
           {
               "timestamp": "2024-01-15 14:00:12",
               "user": "How about Tokyo?",
               "vaani": "In Tokyo it's 28°C with clouds",
               "intent": "WEATHER_QUERY",
               "entities": [{"type": "LOCATION", "value": "Tokyo"}]
           }
       ]
   }

Context Usage
-------------

**Example: Weather Conversation**

.. code-block:: text

   Turn 1 (Context is empty)
   User: "What's the weather in New York?"
   Vaani: Searches for "weather New York"
   Vaani: "It's 72°F and sunny in New York"
   
   [Context updated: location=New York, query=weather]
   
   Turn 2 (Context includes previous location)
   User: "How about Tokyo?"
   Vaani: Recognizes "Tokyo" as a location
   Vaani: Searches for "weather Tokyo" (not "weather how about Tokyo")
   Vaani: "In Tokyo it's 28°C with clouds"
   
   [Context updated: location=Tokyo]
   
   Turn 3 (Context remembers current focus)
   User: "Will it rain?"
   Vaani: Knows you're asking about Tokyo (from context)
   Vaani: Searches for "Tokyo rain forecast"
   Vaani: "The forecast shows 20% chance of rain in Tokyo tomorrow"

**How Context Helps**

Without context:

.. code-block:: text

   Q: "How about Tokyo?"
   Vaani: "How about Tokyo what? Can you clarify?"
   
   Q: "Will it rain?"
   Vaani: "Will what rain? Where?"

With context:

.. code-block:: text

   Q: "How about Tokyo?"
   Vaani: "In Tokyo it's 28°C with clouds"
   
   Q: "Will it rain?"
   Vaani: "The forecast shows 20% chance of rain in Tokyo"

Entity Recognition and Tracking
--------------------------------

**Entity Types**

Vaani tracks different entity types:

.. code-block:: text

   PERSON: Names and references
   "Who is Stephen Hawking?" → Entity: Stephen Hawking
   
   LOCATION: Places
   "What's in Paris?" → Entity: Paris
   
   ORGANIZATION: Companies and institutions
   "Tell me about Google" → Entity: Google
   
   DATE/TIME: When something happens
   "What's tomorrow's weather?" → Entity: tomorrow
   
   TOPIC: Subject of discussion
   "Tell me about Python" → Entity: Python

**Pronoun Resolution**

Vaani resolves pronouns using context:

.. code-block:: text

   Turn 1:
   User: "Who's Albert Einstein?"
   Vaani: "Albert Einstein was a theoretical physicist..."
   [Entity added: Albert Einstein]
   
   Turn 2:
   User: "When was he born?"
   Vaani: Sees "he" refers to Albert Einstein (from context)
   Vaani: "Albert Einstein was born on March 14, 1879"

**Reference Resolution**

Vaani understands indirect references:

.. code-block:: text

   Turn 1:
   User: "What's Python?"
   Vaani: "Python is a programming language..."
   [Entity added: Python, type: PROGRAMMING_LANGUAGE]
   
   Turn 2:
   User: "How do I learn it?"
   Vaani: Sees "it" refers to Python
   Vaani: "You can learn Python through..."

Conversation Flow
-----------------

**Natural Continuation**

Context enables natural conversation flow:

.. code-block:: text

   User: "Tell me about the solar system"
   Vaani: "The solar system consists of the Sun and 8 planets..."
   
   User: "How far is Earth from the Sun?"
   Vaani: (Context: discussing solar system, Earth mentioned)
   "Earth is about 93 million miles from the Sun"
   
   User: "What about Mars?"
   Vaani: (Context: discussing distances in solar system)
   "Mars is about 142 million miles from the Sun"

**Topic Switching**

When users switch topics, context updates:

.. code-block:: text

   [Discussing solar system...]
   
   User: "Actually, tell me about dinosaurs"
   Vaani: (Topic change detected)
   "Dinosaurs were remarkable prehistoric creatures..."
   [Context shifted: solar system → dinosaurs]
   
   User: "When did they go extinct?"
   Vaani: (Context: dinosaur discussion)
   "Dinosaurs went extinct about 66 million years ago"

Memory Limits
-------------

**Size Limitations**

Context is limited to prevent:

1. **Performance Degradation** - Large context slows API calls
2. **Cost Increase** - More context = more tokens = higher cost
3. **Confusion** - Irrelevant old context interfering

**Default Limits**

.. code-block:: bash

   # Maximum messages to keep in active context
   MAX_CONTEXT_MESSAGES = 50
   
   # Maximum total context size
   MAX_CONTEXT_SIZE = 8000 tokens (approximately 2000 words)
   
   # Time limit on old messages
   CONTEXT_TIMEOUT = 30 minutes

**What Gets Dropped**

When limits reached:

1. Oldest messages are dropped first
2. Important entities are retained longer
3. Recent messages are always kept
4. User can explicitly clear memory if needed

**Configure Memory Limits**

.. code-block:: bash

   # .env configuration
   echo "MAX_CONTEXT_MESSAGES=100" >> .env
   echo "MAX_CONTEXT_SIZE=16000" >> .env
   echo "CONTEXT_TIMEOUT=60" >> .env  # 1 hour

Context Reset
-------------

**When Context Is Cleared**

Context resets when:

1. **Vaani Restarts**
   - Session ends
   - Process terminates
   - System reboots

2. **Explicit Reset**
   - User says "Clear memory" or "Forget everything"
   - Vaani detects new session start
   - System is shut down

3. **Timeout** (if configured)
   - 30+ minutes of inactivity
   - Vaani automatically clears old context

**Clearing Memory Manually**

.. code-block:: bash

   # Will clear at next restart
   rm -f vaani_assistant/memory.db
   
   # Or tell Vaani
   # "Clear your memory" or "Forget everything"

**After Memory Clear**

.. code-block:: text

   Turn 1 (Before clear):
   User: "My name is Alice"
   Vaani: "Nice to meet you, Alice"
   
   Turn 2 (After clear/restart):
   User: "Do you remember my name?"
   Vaani: "I'm sorry, I don't have memory of previous sessions.
          Could you remind me?"

Context in Multi-Language
--------------------------

**Language Tracking**

Context includes language information:

.. code-block:: text

   Message 1: English
   "What's the weather?"
   
   Message 2: Spanish
   "¿Cómo estás?" (How are you?)
   
   Context: Detects language switch
   Vaani: Responds in Spanish

**Code-Switching**

Vaani handles code-switching (mixing languages):

.. code-block:: text

   User: "Hola, what's the weather?" (Spanish + English mix)
   Vaani: (Detects mix)
   Responds: "The weather is... hace buen tiempo" (mixed response)

Conversation State
------------------

**State Tracking**

Vaani tracks conversation state:

.. code-block:: python

   state = {
       "topic": "weather",
       "location": "New York",
       "entities": ["New York", "weather", "tomorrow"],
       "sentiment": "neutral",
       "urgency": "low",
       "user_satisfaction": None,
       "conversation_length": 3,
       "last_search_time": "2024-01-15 14:05:23"
   }

**State-Based Responses**

Vaani adjusts based on state:

.. code-block:: text

   Low conversation_length (early in chat):
   Vaani: "What would you like to know about?"
   
   High conversation_length (long chat):
   Vaani: "We've been chatting about this for a while.
          Anything else you'd like to know?"
   
   Negative sentiment:
   Vaani: Uses more apologetic/helpful tone
   
   High urgency (user seems in hurry):
   Vaani: Provides shorter, quicker responses

Technical Implementation
------------------------

**Memory Storage**

Vaani stores memory in RAM (fast, temporary):

.. code-block:: python

   class Memory:
       def __init__(self):
           self.messages = []  # List of all messages
           self.entities = {}   # Map of entities to references
           self.state = {}      # Current conversation state
           self.created_at = datetime.now()
       
       def add_message(self, user_input, vaani_response):
           self.messages.append({
               "user": user_input,
               "vaani": vaani_response,
               "timestamp": datetime.now()
           })
           self._update_entities(user_input)
       
       def get_context(self, max_messages=50):
           # Return recent context for API
           return self.messages[-max_messages:]

**Context Formatting**

Memory is formatted for API calls:

.. code-block:: text

   [Assistant]: Hi, I'm Vaani, how can I help?
   [User]: What's the weather in New York?
   [Assistant]: It's 72°F and sunny
   [User]: How about Tokyo?
   [Assistant]: In Tokyo it's 28°C with clouds

This is sent to Gemini API to understand context.

**Entity Indexing**

Entities are indexed for quick lookup:

.. code-block:: python

   entities = {
       "New York": {"type": "LOCATION", "mentions": 2, "first_mentioned": 14000},
       "Tokyo": {"type": "LOCATION", "mentions": 1, "first_mentioned": 14012},
       "weather": {"type": "INTENT", "mentions": 3}
   }

Advanced Features
-----------------

**Conversation Summarization**

For long conversations, Vaani can summarize:

.. code-block:: text

   Last 50 messages summarized to:
   "User asked about weather in multiple cities (New York, Tokyo,
   Paris). Current topic is weather forecasting for these locations."

**Relevant Context Selection**

Vaani selects only relevant context:

.. code-block:: text

   Q: "Play music"
   Uses context: [previous music requests]
   Ignores context: [weather discussion from 20 minutes ago]

**Entity Linking**

Vaani links similar entities:

.. code-block:: text

   "Albert" + "Albert Einstein" → Same entity
   "NYC" + "New York" → Same entity
   "States" + "United States" → Same entity

Debugging Memory Issues
-----------------------

**View Current Context**

.. code-block:: bash

   # Enable debug logging
   LOG_LEVEL=DEBUG python3 main.py
   
   # Check memory in logs
   tail -100 logs/error.log | grep -i memory

**Clear Memory**

.. code-block:: bash

   # Force clear memory at startup
   rm -f vaani_assistant/memory_*.json
   
   # Then restart
   python3 main.py

**Check Memory Size**

.. code-block:: bash

   # See how many messages are stored
   python3 << 'EOF'
   from vaani_assistant.core.memory import get_memory
   memory = get_memory()
   print(f"Messages in memory: {len(memory.messages)}")
   print(f"Entities tracked: {len(memory.entities)}")
   EOF

**Memory Statistics**

.. code-block:: bash

   python3 << 'EOF'
   from vaani_assistant.core.memory import get_memory
   memory = get_memory()
   
   total_size = sum(len(str(m)) for m in memory.messages)
   print(f"Total context size: {total_size} characters")
   print(f"Average message size: {total_size / len(memory.messages)}")
   print(f"Oldest message: {memory.messages[0]['timestamp']}")
   print(f"Newest message: {memory.messages[-1]['timestamp']}")
   EOF

Limitations
-----------

**What Memory Cannot Do**

- **Persist** - Resets when Vaani restarts
- **Learn** - Doesn't improve understanding over sessions
- **Share** - Doesn't sync across devices
- **Disambiguate** - Struggles with truly ambiguous references
- **Forget Selectively** - All-or-nothing clearing

**Why These Limitations Exist**

- **Privacy** - Don't store data long-term
- **Simplicity** - Simpler architecture to maintain
- **Cost** - Persistent storage costs money
- **Complexity** - Cross-device sync is complicated
- **Safety** - Limited memory reduces error propagation

Best Practices
--------------

**For Users**

1. **Be Specific** - Use full names, places, not pronouns
2. **Provide Context** - Explain connections between queries
3. **Start Fresh** - Clear memory between unrelated topics
4. **Check Understanding** - Ask Vaani to confirm understanding

**For Developers**

1. **Test Context** - Test multi-turn conversations
2. **Monitor Size** - Keep memory within limits
3. **Handle Edge Cases** - Ambiguous references, code-switching
4. **Log Wisely** - Don't log sensitive memory content

Configuration
-------------

**Memory Behavior Configuration**

.. code-block:: bash

   # How many messages to keep
   echo "MEMORY_MAX_MESSAGES=50" >> .env
   
   # Maximum tokens in context
   echo "MEMORY_MAX_TOKENS=8000" >> .env
   
   # Clear memory after this many minutes idle
   echo "MEMORY_IDLE_TIMEOUT=30" >> .env
   
   # Enable memory compression (summarization)
   echo "MEMORY_COMPRESSION_ENABLED=true" >> .env
   
   # Save memory to disk (experimental)
   echo "MEMORY_PERSISTENCE_ENABLED=false" >> .env

Performance Impact
------------------

**Memory Overhead**

Current implementation:

- **RAM Usage** - ~1MB per 100 messages
- **API Cost** - ~200 tokens per message in context
- **Response Time** - +100-200ms for large context

**Optimization**

For slow systems:

.. code-block:: bash

   # Reduce context size
   echo "MEMORY_MAX_MESSAGES=20" >> .env
   
   # Enable compression
   echo "MEMORY_COMPRESSION_ENABLED=true" >> .env
   
   # Disable entity tracking
   echo "ENTITY_TRACKING_ENABLED=false" >> .env

Next Steps
----------

- See :doc:`../intelligence` for AI response details
- Read :doc:`../customization` for memory tuning
- Check :doc:`project_structure` for code implementation
- Review :doc:`../troubleshooting` for memory issues
