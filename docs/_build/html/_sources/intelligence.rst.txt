How Vaani Thinks
=================

Let me explain how Vaani figures out what you want and responds.

The Three Steps
---------------

When you say something, three things happen:

1. **Figure out what you want** - Is this a music request? A question? Just chatting?
2. **Get information if needed** - Search the web for current stuff, or use what it already knows
3. **Generate a response** - Put together an answer that actually makes sense

That's basically it. Let's break down each part.

Intent Classification
---------------------

**What Is Intent?**

Intent is what the user is trying to accomplish:

.. code-block:: text

   Intent: GET_WEATHER
   Input: "What's the weather?"
   
   Intent: PLAY_MUSIC
   Input: "Play some jazz"
   
   Intent: GENERAL_QUESTION
   Input: "Who was Einstein?"
   
   Intent: GET_TIME
   Input: "What time is it?"

**How Vaani Classifies Intent**

1. **Text Analysis**
   - Analyzes words in the user's query
   - Looks for keywords (weather, music, time, etc.)
   - Considers context from previous messages

2. **Pattern Matching**
   - Matches against known patterns
   - Weather keywords: "weather", "forecast", "temperature", "rain"
   - Music keywords: "play", "music", "song", "artist"
   - Time keywords: "time", "date", "when", "what time"

3. **Context Integration**
   - Remembers previous queries
   - Understands references: "How about Tokyo?" after weather in NYC
   - Uses conversation history for disambiguation

**Intent Examples**

.. code-block:: text

   Q: "What's the capital of France?"
   Intent: KNOWLEDGE_QUERY
   Action: Search web, provide answer
   
   Q: "Play rock music"
   Intent: PLAY_MUSIC
   Action: Search YouTube, play music
   
   Q: "Tell me about yourself"
   Intent: PERSONALITY_QUERY
   Action: Generate response from personality config
   
   Q: "What time is it?"
   Intent: GET_TIME
   Action: Return system time
   
   Q: "How tall is Mount Everest?"
   Intent: KNOWLEDGE_QUERY
   Action: Search web, provide answer

Web Search Integration
----------------------

**When Vaani Searches the Web**

Vaani searches the web when:

1. **Current Information Needed**
   - Time-sensitive queries (news, weather, prices)
   - Recent events ("Who won the World Cup last year?")
   - Up-to-date facts (stock prices, sports scores)

2. **General Knowledge Questions**
   - Facts Vaani isn't trained on
   - Detailed information (biographies, dates, numbers)
   - Complex topics needing sources

3. **Specific Queries**
   - Product information
   - Location-specific data (weather, restaurants)
   - Technical topics

**When Vaani Doesn't Search**

Vaani uses internal knowledge for:

1. **Conversation Maintenance**
   - Continuing discussion
   - Acknowledging previous context
   - Social interactions ("Hi!", "How are you?")

2. **Personality Responses**
   - Self-description ("Tell me about yourself")
   - Capabilities list ("What can you do?")
   - Basic greetings

**Search Results**

When searching, Vaani:

1. Sends query to search engine (Bing, Google, or similar)
2. Gets back 5-10 results with titles and snippets
3. Selects most relevant results
4. Extracts key information
5. Composes response based on results

**Search Confidence**

Vaani indicates uncertainty when:

.. code-block:: text

   "I found that Mount Everest is approximately 29,032 feet tall,
   though some measurements vary slightly."
   
   "Based on search results, the current temperature is..."
   
   "According to recent reports, India won the cricket series..."

Response Generation
-------------------

**The AI Engine**

Vaani uses Google's Gemini API for response generation:

.. code-block:: text

   Input: "What's Python used for?"
   
   1. Intent: KNOWLEDGE_QUERY
   2. Search: "Python programming language uses"
   3. Results: Wikipedia, Stack Overflow, blogs
   4. Prompt sent to Gemini:
      "Based on this information, explain what Python is used for"
   5. Gemini generates response
   6. Convert to speech
   7. User hears: "Python is used for web development,
      data science, artificial intelligence..."

**System Prompt**

Vaani uses a system prompt that tells Gemini:

- Who Vaani is (an AI assistant)
- How to communicate (conversational, helpful)
- What to do (answer questions, help users)
- Limitations (cannot take actions, not always accurate)

**Customizable Personality**

The system prompt includes personality settings:

.. code-block:: text

   Formal: "Certainly. To address your inquiry, Python is..."
   Casual: "Oh, cool question! Python's actually super useful for..."
   Professional: "Python serves multiple roles including..."

See :doc:`../customization` for personality options.

**Response Format**

Responses are:

1. **Conversational** - Natural, spoken language
2. **Concise** - 1-3 sentences typically
3. **Contextual** - Uses conversation history
4. **Helpful** - Directly addresses the question

Bad response examples (Vaani avoids these):

.. code-block:: text

   ✗ Technical jargon: "Python employs dynamic typing paradigms"
   ✗ Too long: 5+ minute monologues
   ✗ Off-topic: Answering different question
   ✗ Uncertain: "I'm not sure, maybe, possibly, perhaps"

Multi-Turn Conversations
------------------------

**Context Retention**

Vaani remembers:

.. code-block:: text

   Turn 1:
   User: "What's the weather in New York?"
   Vaani: "It's 72°F and sunny"
   Context saved: location=New York, query=weather
   
   Turn 2:
   User: "How about Tokyo?"
   Vaani: Understands "Tokyo" as the new location
   Vaani: "In Tokyo it's 28°C with some clouds"
   Context updated: location=Tokyo
   
   Turn 3:
   User: "Will it rain?"
   Vaani: Knows you're asking about Tokyo (from context)
   Vaani: "The forecast shows 20% chance of rain in Tokyo"

**Context Limitations**

Context is:

- **Temporary** - Resets when Vaani restarts
- **Session-based** - Limited to current conversation
- **Bounded** - Keeps last 50 exchanges (configurable)
- **Local** - Not shared across devices

**Context Information**

Stored context includes:

.. code-block:: python

   {
       "timestamp": "2024-01-15 14:30:00",
       "user_input": "What's the weather in New York?",
       "detected_intent": "WEATHER_QUERY",
       "entity_location": "New York",
       "vaani_response": "It's 72°F and sunny in New York",
       "web_search_performed": True,
       "search_sources": ["weather.com", "accuweather"],
   }

Knowledge Cutoff
----------------

**What Vaani Knows**

Vaani has two sources of knowledge:

1. **Training Data** - Information known to Gemini at training time
   - General knowledge (history, science, facts)
   - Cultural information
   - Published information up to training cutoff

2. **Web Search** - Current information retrieved during conversation
   - News and recent events
   - Updated facts (prices, scores, weather)
   - Real-time data

**Knowledge Gaps**

Vaani has limited or no knowledge about:

1. **Very Recent Events** - Breaking news minutes old
2. **Your Personal Data** - Your files, emails, accounts
3. **Proprietary Information** - Company secrets, paywalled content
4. **Changing Information** - Stock prices (timestamp dependent)

**How Vaani Indicates Uncertainty**

.. code-block:: text

   "I'm not sure, but based on what I know..."
   "My information might be outdated, but..."
   "I couldn't find specific information about that, however..."
   "That's outside my knowledge base, but I can tell you about..."

Gemini API Integration
----------------------

**How It Works**

.. code-block:: python

   from google import genai
   
   client = genai.Client(api_key="your_key_here")
   
   response = client.models.generate_content(
       model="gemini-2.0-flash",  # Latest Gemini model
       contents=[
           {
               "role": "user",
               "parts": [{"text": user_query}]
           }
       ]
   )
   
   generated_text = response.text

**Model Selection**

Vaani uses Gemini 2.0 Flash because:

- **Fast** - 200-500ms response time
- **Capable** - Understands complex queries
- **Affordable** - Cost-effective for continuous use
- **Reliable** - Stable production model

**API Configuration**

Set your Gemini API key:

.. code-block:: bash

   # Get key from https://aistudio.google.com/apikey
   echo "GEMINI_API_KEY=your_key_here" >> .env

Without a key, Vaani falls back to simpler responses.

**Rate Limits**

Gemini API has limits:

- Free tier: 60 requests per minute
- Paid: Higher limits depending on plan

Vaani handles limits gracefully with fallback responses.

**Cost**

Gemini API is:

- **Free** - For reasonable use (60 RPM)
- **Paid** - For high-volume use ($0.075/MTok input, $0.3/MTok output)

Example costs:

.. code-block:: text

   10 conversations/day × 365 days = 3,650 conversations
   Average: 200 tokens per conversation
   = 730,000 tokens/year ≈ $0.50/year

Very affordable for personal use.

Fallback Behavior
-----------------

**When APIs Fail**

If Gemini API is unavailable:

.. code-block:: text

   1. Try Gemini API
   2. If fails → Try alternative API (if configured)
   3. If fails → Use template-based responses
   4. If fails → Return "I'm having trouble responding"

**Template Responses**

When all APIs unavailable:

.. code-block:: text

   Q: "What's the weather?"
   A: "I'm unable to fetch current weather data right now.
       Please check a weather service directly."
   
   Q: "Play music"
   A: "I'm having trouble connecting to music services.
       Try playing music through your audio app instead."

**Error Handling**

.. code-block:: python

   try:
       response = generate_response(user_input)
   except APIError:
       logger.warning("Gemini API failed, using fallback")
       response = fallback_response(user_input)
   except Exception as e:
       logger.error(f"Response generation failed: {e}")
       response = "I encountered an error. Please try again."

Intent-Specific Behaviors
--------------------------

**WEATHER_QUERY**

.. code-block:: text

   Trigger: "weather", "forecast", "temperature", "rain", "sunny"
   Search: Location + weather forecast
   Response: Current conditions + 24-hour forecast
   
   Example:
   Q: "What's the weather in London?"
   Response: "In London it's currently 16°C with overcast skies.
             Tonight the temperature will drop to 12°C with
             possible showers expected tomorrow."

**PLAY_MUSIC**

.. code-block:: text

   Trigger: "play", "music", "song", "artist"
   Search: Song name on YouTube
   Response: Confirm playback + enjoy message
   
   Example:
   Q: "Play some jazz"
   Response: "Playing jazz music for you..."
   [Music starts playing]

**GENERAL_QUESTION**

.. code-block:: text

   Trigger: Any question not matching specific intent
   Search: Web search for relevant information
   Response: Answer based on search results
   
   Example:
   Q: "Who invented electricity?"
   Response: "Electricity wasn't invented by a single person,
             but many scientists contributed. Benjamin Franklin,
             Michael Faraday, and Thomas Edison all made
             important discoveries about electricity."

**PERSONALITY_QUERY**

.. code-block:: text

   Trigger: "about yourself", "who are you", "what's your name"
   Search: None (use internal response)
   Response: Personality description from config
   
   Example:
   Q: "Who are you?"
   Response: "I'm Vaani, an AI assistant designed to help you
             with information, music, and conversation. I can
             search the web, answer questions, and keep our
             conversation going with context and memory."

Advanced Features
-----------------

**Entity Extraction**

Vaani identifies key entities:

.. code-block:: text

   Input: "What's the weather in Paris tomorrow?"
   
   Entities:
   - Entity: "Paris"
     Type: LOCATION
   - Entity: "tomorrow"
     Type: TIME
   - Entity: "weather"
     Type: INTENT

**Coreference Resolution**

Vaani understands references:

.. code-block:: text

   Q: "Who's the president of France?"
   A: "Emmanuel Macron"
   
   Q: "When was he born?"
   A: "Emmanuel Macron was born on December 21, 1977"
   
   Note: "he" correctly refers to "Emmanuel Macron"

**Sentiment Analysis**

Vaani recognizes tone:

.. code-block:: text

   "That's amazing!" → Positive sentiment
   "That's terrible" → Negative sentiment
   
   Adjusts response tone accordingly

Configuration and Tuning
------------------------

**Adjust Response Length**

.. code-block:: bash

   echo "RESPONSE_LENGTH=short" >> .env    # 1-2 sentences
   echo "RESPONSE_LENGTH=medium" >> .env   # 3-5 sentences
   echo "RESPONSE_LENGTH=long" >> .env     # 5+ sentences

**Enable/Disable Web Search**

.. code-block:: bash

   # Always search for information
   echo "WEB_SEARCH_ENABLED=true" >> .env
   
   # Use only trained knowledge
   echo "WEB_SEARCH_ENABLED=false" >> .env

**Set Search Budget**

.. code-block:: bash

   # Maximum time to wait for search results
   echo "WEB_SEARCH_TIMEOUT=5" >> .env

**Customize System Prompt**

.. code-block:: bash

   # Edit the system message Gemini receives
   echo "SYSTEM_PROMPT='You are a helpful AI assistant...'" >> .env

Limitations
-----------

**What the Intelligence System Cannot Do**

- **Real-time computation** - Can't do complex math mid-conversation
- **Image understanding** - Can't see or describe images
- **Code execution** - Can't run code or verify correctness
- **Persistent learning** - Can't learn new information long-term
- **Emotion recognition** - Can't truly understand how you feel
- **Fact verification** - Can't verify all search results
- **Action execution** - Can't actually do things (send emails, etc.)

**Why These Limitations Exist**

- **Safety** - Prevent misuse
- **Privacy** - Don't need/want user data
- **Capability** - Some tasks need human judgment
- **Cost** - Advanced features cost more
- **Simplicity** - Simpler to maintain and support

Performance Metrics
-------------------

**Response Time**

Typical end-to-end response:

.. code-block:: text

   Speech recognition: 1-3 seconds
   Intent classification: 100ms
   Web search (if needed): 1-2 seconds
   Response generation: 500ms-1 second
   Text-to-speech: 1-2 seconds
   
   Total: 3-10 seconds (depends on query complexity)

**Accuracy**

- Speech recognition: 85-95% (varies by accent/noise)
- Intent classification: 90%+ (95% for common intents)
- Web search relevance: 70-80%
- Response appropriateness: 80-90% (subjective)

Debugging and Logs
------------------

**Enable Debug Logging**

.. code-block:: bash

   LOG_LEVEL=DEBUG python3 main.py

**View Intent Classification**

.. code-block:: bash

   # Check what intent was detected
   tail -50 logs/error.log | grep "intent"

**Analyze Search Results**

.. code-block:: bash

   # See what web search returned
   tail -50 logs/error.log | grep "search"

**Check API Responses**

.. code-block:: bash

   LOG_LEVEL=DEBUG python3 main.py 2>&1 | grep "gemini"

Next Steps
----------

- See :doc:`../memory_context` for conversation handling
- Read :doc:`../customization` for tuning behavior
- Check :doc:`project_structure` for code details
- Review :doc:`../troubleshooting` for common issues
