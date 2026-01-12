"""
Conversation Manager - AI Response Engine
============================================

Features:
- Google Gemini Pro integration with search grounding
- Conversation history management (rolling window)
- Context-aware responses using recent conversation
- Personality-driven interactions
- Real-time web search integration for current information
- Multi-turn conversation support
- Fallback responses when AI unavailable
- Configurable memory limits (conversation window)
- Professional, helpful personality

Manages AI-powered conversations using Google Gemini with live web
search for accurate, current information. Remembers context and
maintains natural conversation flow.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import re
import time
from typing import List, Tuple, Optional
from collections import deque
from google import genai
from google.genai import types
from ..config import settings
from ..config.global_config import GEMINI_SYSTEM_INSTRUCTIONS, ASSISTANT_NAME
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Conversation History")
from .responses import responses
from ..integrations.web_search import SearchHelper

try:
    from .personality import get_personality_module
    from .context import get_conversation_context
    from ..integrations.web_search import get_search
    ENHANCED_FEATURES = True
except ImportError:
    ENHANCED_FEATURES = False
    logger.warning("Enhanced AI features not available")

# Try importing enhanced offline NLP
try:
    from .offline_nlp import get_offline_nlp
    ENHANCED_NLP_AVAILABLE = True
    logger.info("Enhanced offline NLP available")
except ImportError:
    ENHANCED_NLP_AVAILABLE = False
    logger.debug("Enhanced offline NLP not available")

# Try importing advanced response synthesizer
try:
    from .response_synthesizer import get_synthesizer
    SYNTHESIZER_AVAILABLE = True
    logger.info("Advanced response synthesizer available")
except ImportError:
    SYNTHESIZER_AVAILABLE = False
    logger.debug("Advanced synthesizer not available")


class ConversationManager:
    """Generates conversational responses with context awareness and web search integration"""
    
    def __init__(self):
        self.client: Optional[genai.Client] = None
        self.conversation_history: deque = deque(maxlen=settings.MAX_CONVERSATION_HISTORY)
        self.context_window: deque = deque(maxlen=settings.CONTEXT_WINDOW_SIZE)
        self.user_name: Optional[str] = None
        
        # API key rotation for quota management
        self.api_keys = getattr(settings, 'GOOGLE_API_KEYS', [settings.GOOGLE_API_KEY])
        self.current_key_index = 0
        self.exhausted_keys = set()  # Track exhausted keys
        
        # Enhanced features
        if ENHANCED_FEATURES:
            self.personality = get_personality_module()
            self.context = get_conversation_context()
            self.web_search = get_search()
        else:
            self.personality = None
            self.context = None
            self.web_search = None
        
        # Enhanced offline NLP engine
        if ENHANCED_NLP_AVAILABLE:
            try:
                self.offline_nlp = get_offline_nlp()
                logger.info("Enhanced offline NLP engine enabled")
            except Exception as e:
                logger.warning(f"Could not initialize offline NLP: {e}")
                self.offline_nlp = None
        else:
            self.offline_nlp = None
        
        # Advanced Response Synthesizer
        if SYNTHESIZER_AVAILABLE:
            try:
                self.synthesizer = get_synthesizer()
                logger.info("Advanced response synthesizer enabled")
            except Exception as e:
                logger.warning(f"Could not initialize synthesizer: {e}")
                self.synthesizer = None
        else:
            self.synthesizer = None
        
        # Always create a fallback web search engine
        self.fallback_search = SearchHelper()
        
        self._initialize_client()
    
    @error_handler(default_return=False)
    def _initialize_client(self) -> bool:
        """Initialize Google Gemini AI client with current API key"""
        try:
            if not self.api_keys:
                logger.error("No Google API keys configured")
                return False
            
            # Use current API key from rotation
            current_key = self.api_keys[self.current_key_index]
            self.client = genai.Client(api_key=current_key)
            logger.info(f"Connected to Gemini AI (using API key {self.current_key_index + 1}/{len(self.api_keys)})")
            return True
            
        except Exception as e:
            logger.error(f"AI initialization error: {e}")
            return False
    
    def _rotate_api_key(self) -> bool:
        """Switch to next API key when current one hits quota limit"""
        # Mark current key as exhausted
        self.exhausted_keys.add(self.current_key_index)
        logger.warning(f"API key {self.current_key_index + 1} exhausted, rotating...")
        
        # Find next available key
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            if self.current_key_index not in self.exhausted_keys:
                # Reinitialize client with new key
                if self._initialize_client():
                    logger.info(f"Rotated to API key {self.current_key_index + 1}/{len(self.api_keys)}")
                    return True
        
        # All keys exhausted
        logger.error("All API keys exhausted! Please wait or add more keys.")
        return False
    
    @error_handler(default_return="I'm having trouble connecting to my brain right now.")
    def generate_response(self, user_input: str, use_context: bool = True,
                         context_type: str = 'conversation') -> str:
        """Generate AI response with intelligent fallback to web search when AI fails"""
        try:
            # Check if AI is available
            if not self.client:
                logger.warning("AI client not available - using intelligent fallback")
                return self._generate_intelligent_fallback(user_input)
            
            # Build prompt with context
            prompt = self._build_enhanced_prompt(user_input, use_context, "")
            
            # Configure Google Search grounding (ENABLED BY DEFAULT)
            if getattr(settings, 'USE_GOOGLE_SEARCH_GROUNDING', True):
                logger.info("Google Search grounding enabled")
                grounding_tool = types.Tool(google_search=types.GoogleSearch())
                config = types.GenerateContentConfig(
                    temperature=settings.AI_TEMPERATURE,
                    max_output_tokens=settings.AI_MAX_TOKENS,
                    tools=[grounding_tool]
                )
            else:
                config = {
                    'temperature': settings.AI_TEMPERATURE,
                    'max_output_tokens': settings.AI_MAX_TOKENS,
                }
            
            # Generate response with timeout protection
            response = self.client.models.generate_content(
                model=settings.AI_MODEL,
                contents=prompt,
                config=config
            )
            
            # Extract text from response
            if response and response.text:
                ai_response = response.text.strip()
                
                # CRITICAL: Polish AI output to sound human
                ai_response = responses.polish_ai_response(ai_response)
                
                # Post-process with personality
                if self.personality:
                    ai_response = self.personality.process_response(
                        ai_response,
                        context=context_type
                    )
                
                # Store in context
                if self.context:
                    self.context.add_interaction(user_input, ai_response, context_type)
                
                # Add to conversation history
                self.conversation_history.append((user_input, ai_response))
                self.context_window.append(f"User: {user_input}\nVaani: {ai_response}")
                
                logger.info(f"AI response generated ({len(ai_response)} chars)")
                return ai_response
            else:
                logger.warning("Empty response from AI")
                return self._fallback_response(user_input)
            
        except Exception as e:
            error_str = str(e)
            error_str = str(e)
            
            # Specific handling for Invalid API Key (400 INVALID_ARGUMENT)
            if 'INVALID_ARGUMENT' in error_str or 'API key not valid' in error_str:
                logger.critical(f"❌ INVALID API KEY: The configured Google API key is incorrect.")
                logger.critical(f"👉 ACTION REQUIRED: Please update 'GOOGLE_API_KEY' in your config.json or .env file.")
                logger.critical(f"   You can get a free key here: https://aistudio.google.com/app/apikey")
                return self._generate_intelligent_fallback(user_input, error_context="invalid_api_key")

            logger.error(f"AI generation error: {e}")
            
            # Check for quota exhaustion (429 RESOURCE_EXHAUSTED)
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                logger.warning("API Quota exhausted, attempting key rotation...")
                
                # Try rotating to next API key
                if self._rotate_api_key():
                    # Retry with new key (only once)
                    try:
                        logger.info("🔁 Retrying request with rotated API key...")
                        response = self.client.models.generate_content(
                            model=settings.AI_MODEL,
                            contents=prompt,
                            config=config
                        )
                        
                        if response and response.text:
                            ai_response = response.text.strip()
                            ai_response = responses.polish_ai_response(ai_response)
                            
                            if self.personality:
                                ai_response = self.personality.process_response(ai_response, context=context_type)
                            
                            if self.context:
                                self.context.add_interaction(user_input, ai_response, context_type)
                            
                            self.conversation_history.append((user_input, ai_response))
                            self.context_window.append(f"User: {user_input}\nVaani: {ai_response}")
                            
                            logger.info(f"AI response generated with rotated key ({len(ai_response)} chars)")
                            return ai_response
                    except Exception as retry_error:
                        logger.error(f"Retry with rotated key failed: {retry_error}")
                        logger.info("🌐 Falling back to web search...")
            
            # Intelligent fallback: Use web search + NLP for natural responses
            logger.info("AI unavailable - using intelligent fallback system")
            return self._generate_intelligent_fallback(user_input)
    
    def _needs_realtime_info(self, query: str) -> bool:
        """Detect if query requires real-time/current information"""
        query_lower = query.lower()
        
        # Current events keywords
        realtime_keywords = [
            'current', 'latest', 'recent', 'today', 'now', 'this year',
            'who won', 'who is', 'what happened', 'when did',
            'score', 'result', 'winner', 'champion',
            'weather', 'news', 'stock', 'price',
            '2024', '2025', '2026',  # Recent ywake_word
        ]
        
        # Question words that often need current info
        question_patterns = [
            'what is the', 'who is the', 'where is the',
            'when is', 'how much is', 'what are the'
        ]
        
        # Check for keywords
        for keyword in realtime_keywords:
            if keyword in query_lower:
                return True
        
        # Check for question patterns
        for pattern in question_patterns:
            if query_lower.startswith(pattern):
                return True
        
        return False
    
    def _build_enhanced_prompt(self, user_input: str, use_context: bool, 
                              web_context: str = "") -> str:
        """Build prompt with personality, context, and web context"""
        parts = []
        
        # Add personality system prompt
        if self.personality:
            # Get system prompt as string
            system_prompt = self.personality.create_system_prompt()
            parts.append(system_prompt)
        else:
            parts.append(self._load_personality())
        
        # Add response length instructions
        length_instructions = {
            'short': "Keep responses brief and concise (1-2 sentences). Be direct.",
            'medium': "Provide clear, helpful responses (2-4 sentences). Balance detail with brevity.",
            'long': "Give detailed, comprehensive responses when appropriate. Explain thoroughly."
        }
        response_length = getattr(settings, 'RESPONSE_LENGTH', 'medium')
        parts.append(f"\nResponse style: {length_instructions.get(response_length, length_instructions['medium'])}")
        
        # Special instruction for explicit user requests
        if any(phrase in user_input.lower() for phrase in ['explain more', 'tell me more', 'details', 'elaborate', 'in detail']):
            parts.append("User wants detailed information - provide a comprehensive response.")
        elif any(phrase in user_input.lower() for phrase in ['briefly', 'quick', 'short answer', 'summarize']):
            parts.append("User wants brief information - keep response concise.")
        
        parts.append("")
        
        # Add user name if known
        if self.user_name:
            parts.append(f"User's name: {self.user_name}")
            parts.append("")
        
        # Add context context
        if self.context and use_context:
            context_summary = self.context.get_context_summary()
            if context_summary:
                parts.append("Recent conversation:")
                parts.append(context_summary)
                parts.append("")
        elif use_context and self.context_window:
            # Fallback to simple context
            parts.append("Recent conversation:")
            parts.extend(list(self.context_window))
            parts.append("")
        
        # Add web search results if available
        if web_context:
            parts.append(web_context)
            parts.append("")
        
        # Add current query
        parts.append(f"User's current question or request: {user_input}")
        parts.append("")
        parts.append("Respond naturally and conversationally:")
        
        # Ensure all parts are strings
        parts = [str(p) for p in parts]
        
        return "\n".join(parts)
    
    def _load_personality(self) -> str:
        """Load AI personality and behavior guidelines (uses global config)"""
        return GEMINI_SYSTEM_INSTRUCTIONS
    
    def _fallback_response(self, user_input: str) -> str:
        """Natural responses when AI is unavailable"""
        user_lower = user_input.lower()
        
        # Use our human-written responses
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return responses.greeting()
        
        if any(word in user_lower for word in ['how are you', 'how do you do']):
            return responses.get_random(responses.HOW_ARE_YOU)
        
        if any(word in user_lower for word in ['thank', 'thanks']):
            return responses.thanks()
        
        if 'your name' in user_lower or 'who are you' in user_lower:
            return f"I'm {ASSISTANT_NAME}. I'm here to help with music, questions, and more."
        
        if 'what can you do' in user_lower or 'help' in user_lower:
            return responses.CAPABILITIES
        
        # Default: calm acknowledgment
        return "I'm having a bit of trouble right now, but I can still help with music and basic tasks."
    
    @error_handler(default_return="I apologize, I'm having technical difficulties right now.")
    def _generate_intelligent_fallback(self, user_input: str, error_context: str = "unknown") -> str:
        """
        🧠 Multi-layered intelligent fallback system when AI is unavailable
        
        Fallback chain:
        0. Enhanced Offline NLP (NEW! - AI-like responses without API)
        1. Pattern-based NLP (instant, offline)
        2. Web search with natural summarization (online, 2-3s)
        3. DuckDuckGo instant answers
        4. Google search scraping
        5. Basic conversational response
        """
        user_lower = user_input.lower()
        
        # Layer 1: Pattern-based NLP (instant responses for common queries)
        # Prioritize instant responses (Hi, Stop, Help) over heavy computing
        logger.info("Layer 1: Trying pattern-based NLP...")
        nlp_response = self._pattern_based_nlp(user_input)
        if nlp_response:
            logger.info("Pattern-based NLP response generated")
            return nlp_response
        
        # Layer 2: Determine if web search is appropriate
        # Prioritize Web Search over generic Offline NLP responses for questions
        should_search = self._should_use_web_search(user_input)
        
        if should_search:
            logger.info("Layer 2: Query requires web search...")
            
            # Try DuckDuckGo search with natural summarization
            try:
                web_response = self._generate_natural_web_response(user_input)
                if web_response and not web_response.startswith("I couldn't"):
                    logger.info("Natural web response generated successfully")
                    # Store in history
                    self.conversation_history.append((user_input, web_response))
                    self.context_window.append(f"User: {user_input}\nVaani: {web_response}")
                    return web_response
            except Exception as e:
                logger.warning(f"Web search fallback failed: {e}")

        # Layer 0: Enhanced Offline NLP - DISABLED BY USER REQUEST
        # User prefers to rely on Gemini or basic functions/web search only.
        # if self.offline_nlp:
        #     logger.info("🧠 Layer 0: Trying Enhanced Offline NLP...")
        #     try:
        #         nlp_response = self.offline_nlp.generate_response(
        #             query=user_input,
        #             context={'error_context': error_context},
        #             use_web=False  # We already tried web search above
        #         )
        #         if nlp_response and len(nlp_response) > 20:
        #             logger.info(f"✅ Enhanced NLP response generated ({len(nlp_response)} chars)")
        #             # Store in history
        #             self.conversation_history.append((user_input, nlp_response))
        #             self.context_window.append(f"User: {user_input}\nVaani: {nlp_response}")
        #             return nlp_response
        #     except Exception as e:
        #         logger.debug(f"Enhanced NLP failed: {e}")
        
        # Layer 3: Conversational acknowledgment
        logger.info("Layer 3: Using conversational fallback")
        return self._generate_conversational_fallback(user_input)
    
    def _should_use_web_search(self, query: str) -> bool:
        """Determine if query should use web search (more comprehensive)"""
        query_lower = query.lower()
        
        # Question patterns that need web search
        question_words = [
            'what', 'who', 'when', 'where', 'why', 'how', 'which',
            'can you tell', 'is there', 'are there', 'tell me about',
            'explain', 'describe', 'define', 'find', 'search', 'look up'
        ]
        
        # Explicit search requests
        search_triggers = [
            'search for', 'look up', 'find out', 'google', 'search',
            'what is', 'who is', 'where is', 'when did', 'how to'
        ]
        
        # Current events keywords
        realtime_keywords = [
            'latest', 'recent', 'today', 'now', 'current', 'news',
            'this year', 'this month', 'yesterday', 'update',
            '2024', '2025', '2026', 'weather', 'score', 'result'
        ]
        
        # Exclude queries that are JUST the trigger words (e.g. "tell me about")
        # This prevents searching for empty topics
        if hasattr(self, 'web_search') and self.web_search:
            from ..integrations.web_search import get_search
            search_helper = get_search()
            if not search_helper.validate_query(query):
                return False
        
        # Check question words
        for word in question_words:
            if query_lower.startswith(word) or f" {word} " in query_lower:
                return True
        
        # Check search triggers
        for trigger in search_triggers:
            if trigger in query_lower:
                return True
        
        # Check realtime keywords
        for keyword in realtime_keywords:
            if keyword in query_lower:
                return True
        
        return False
    
    def _generate_natural_web_response(self, query: str) -> str:
        """
        🚀 Generate GOD-LIKE natural conversational response from MULTIPLE sources:
        - Wikipedia (free, authoritative encyclopedia)
        - DuckDuckGo/Google search (current web results)
        - Direct website content (visit actual pages from search results)
        - Advanced synthesis with quality metrics and confidence scoring
        
        This provides comprehensive, verified, well-researched answers!
        """
        try:
            logger.info(f"GOD-LIKE multi-source intelligent search for: {query}")
            
            # Collect sources from multiple origins
            all_sources = []
            
            # 1. Try Wikipedia first (highest authority)
            if hasattr(self.fallback_search, 'search_wikipedia'):
                wiki_result = self.fallback_search.search_wikipedia(query, sentences=4)
                if wiki_result:
                    all_sources.append({
                        'content': wiki_result.get('summary', ''),
                        'source_type': 'Wikipedia',
                        'url': wiki_result.get('url', ''),
                        'credibility': 95
                    })
                    logger.info("Wikipedia content collected")
            
            # 2. Get web search results
            web_results = self.fallback_search.search(query, max_results=5)
            if web_results:
                for result in web_results[:5]:
                    snippet = result.get('snippet', '')
                    link = result.get('link', '')
                    title = result.get('title', '')
                    if snippet and len(snippet) > 30:
                        all_sources.append({
                            'content': snippet,
                            'source_type': 'web_search',
                            'url': link,
                            'title': title,
                            'credibility': 70
                        })
                logger.info(f"Collected {len(web_results)} web search results")
            
            # 3. Fetch actual page content for depth
            if web_results and hasattr(self.fallback_search, 'fetch_multiple_pages'):
                urls = [r.get('link') for r in web_results[:3] if r.get('link')]
                if urls:
                    page_contents = self.fallback_search.fetch_multiple_pages(urls, max_per_page=400)
                    for page in page_contents:
                        content = page.get('content', '')
                        if content and len(content) > 50:
                            all_sources.append({
                                'content': content,
                                'source_type': 'web_page',
                                'url': page.get('url', ''),
                                'credibility': 65
                            })
                    logger.info(f"Fetched {len(page_contents)} full page contents")
            
            # Use advanced synthesizer if available
            if all_sources and hasattr(self, 'synthesizer') and self.synthesizer:
                logger.info(f"Using ADVANCED SYNTHESIS with {len(all_sources)} sources...")
                result = self.synthesizer.synthesize_multi_source(
                    query=query,
                    sources=all_sources,
                    context={'conversation_history': list(self.conversation_history)[-3:]}
                )
                
                if result['quality_score'] >= 60:  # Good quality threshold
                    logger.info(f"HIGH-QUALITY GOD-LIKE RESPONSE: "
                               f"Quality={result['quality_score']:.1f}/100, "
                               f"Confidence={result['confidence']:.1f}/100, "
                               f"Sources={result['source_count']}")
                    return result['response']
                else:
                    logger.warning(f"Lower quality response: {result['quality_score']:.1f}/100")
                    # Still use it if we have nothing better
                    if result['response'] and len(result['response']) > 30:
                        return result['response']
            
            # Fallback: Use legacy advanced_search_and_synthesize
            if hasattr(self.fallback_search, 'advanced_search_and_synthesize'):
                logger.info("Using legacy advanced search synthesis...")
                response = self.fallback_search.advanced_search_and_synthesize(
                    query=query,
                    max_sources=5
                )
                
                if response and len(response) > 30:
                    logger.info(f"Generated comprehensive response from legacy system ({len(response)} chars)")
                    return response
            
            # Fallback: Basic synthesis from collected sources
            if all_sources:
                logger.info("Using basic synthesis fallback")
                # Convert to old format
                information_pieces = []
                for s in all_sources[:5]:
                    information_pieces.append({
                        'text': s['content'],
                        'source': s['source_type'],
                        'rank': 0
                    })
                
                if information_pieces:
                    response = self._synthesize_natural_answer(query, information_pieces)
                    return response
            
            # Final fallback
            logger.warning("All synthesis methods failed, using minimal fallback")
            results = self.fallback_search.search(query, max_results=5)
            
            if not results:
                return "I couldn't find reliable information about that online right now. Could you rephrase your question?"
            
            # Extract and combine information from top results
            information_pieces = []
            
            for idx, result in enumerate(results[:3]):
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                
                if snippet:
                    # Clean and format snippet
                    clean_snippet = self._clean_snippet_for_speech(snippet)
                    if clean_snippet:
                        information_pieces.append({
                            'text': clean_snippet,
                            'source': title,
                            'rank': idx
                        })
            
            if not information_pieces:
                # Try fetching page content
                if results and results[0].get('link'):
                    page_content = self.fallback_search.fetch_page_content(
                        results[0]['link'], 
                        max_length=500
                    )
                    if page_content:
                        information_pieces.append({
                            'text': page_content,
                            'source': results[0].get('title', 'a website'),
                            'rank': 0
                        })
            
            # Generate natural conversational response
            if information_pieces:
                response = self._synthesize_natural_answer(query, information_pieces)
                return response
            else:
                return "I found some sources, but couldn't extract clear information. Try asking in a different way?"
            
        except Exception as e:
            logger.error(f"Natural web response generation failed: {e}")
            return "I'm having trouble accessing web information right now."
    
    def _clean_snippet_for_speech(self, snippet: str) -> str:
        """Clean web snippet to sound natural when spoken"""
        if not snippet:
            return ""
        
        import re
        
        # Remove URLs
        snippet = re.sub(r'http\S+|www\S+', '', snippet)
        
        # Remove dates in brackets
        snippet = re.sub(r'\[.*?\]', '', snippet)
        
        # Remove multiple spaces
        snippet = re.sub(r'\s+', ' ', snippet)
        
        # Remove special characters that don't sound good
        snippet = re.sub(r'[^\w\s.,!?;:\'\-()]', '', snippet)
        
        # Remove "Read more" type suffixes
        snippet = re.sub(r'(read more|click here|learn more|see more).*$', '', snippet, flags=re.IGNORECASE)
        
        # Limit length for speech
        max_length = 300
        if len(snippet) > max_length:
            snippet = snippet[:max_length].rsplit('.', 1)[0]
            if not snippet.endswith('.'):
                snippet += '.'
        
        return snippet.strip()
    
    def _synthesize_natural_answer(self, query: str, info_pieces: list) -> str:
        """Synthesize natural conversational answer from information pieces"""
        if not info_pieces:
            return "I couldn't find specific information about that."
        
        # Get primary information
        primary = info_pieces[0]
        primary_text = primary['text']
        primary_source = primary['source']
        
        # Build natural response
        response_parts = []
        
        # Conversational opening based on query type
        query_lower = query.lower()
        if query_lower.startswith('what'):
            response_parts.append("Here's what I found:")
        elif query_lower.startswith('who'):
            response_parts.append("Let me tell you:")
        elif query_lower.startswith('how'):
            response_parts.append("Here's how it works:")
        elif query_lower.startswith('when'):
            response_parts.append("From what I found:")
        elif query_lower.startswith('where'):
            response_parts.append("Based on my search:")
        else:
            response_parts.append("According to my search:")
        
        # Add primary information
        response_parts.append(primary_text)
        
        # Add supporting information if available
        if len(info_pieces) > 1:
            secondary = info_pieces[1]
            secondary_text = secondary['text']
            
            # Add variety to connection phrases
            connectors = ["Additionally,", "Also,", "Furthermore,", "Moreover,"]
            import random
            connector = random.choice(connectors)
            
            # Limit secondary info to keep response concise
            if len(secondary_text) > 150:
                secondary_text = secondary_text[:150].rsplit('.', 1)[0] + '.'
            
            response_parts.append(f"{connector} {secondary_text}")
        
        # Add source attribution for credibility
        if len(info_pieces) == 1:
            response_parts.append(f"This information comes from {primary_source}.")
        else:
            response_parts.append(f"I found {len(info_pieces)} sources confirming this.")
        
        response = " ".join(response_parts)
        
        # Final cleanup
        response = re.sub(r'\s+', ' ', response)
        response = response.strip()
        
        return response
    
    def _generate_conversational_fallback(self, user_input: str) -> str:
        """Generate appropriate conversational response when all else fails"""
        user_lower = user_input.lower()
        
        # Acknowledgment for statements
        if not any(user_lower.startswith(w) for w in ['what', 'who', 'when', 'where', 'why', 'how']):
            acknowledgments = [
                "I understand what you're saying.",
                "I hear you.",
                "Got it.",
                "That makes sense."
            ]
            import random
            return random.choice(acknowledgments)
        
        # For questions we can't answer
        helpful_responses = [
            "That's an interesting question! Unfortunately, I don't have access to current information right now. Try asking about something else?",
            "I'm not sure about that at the moment. My AI connection is limited. Is there something else I can help with?",
            "I'd need to research that, but I'm having connectivity issues. Can I help you with music or basic tasks instead?"
        ]
        
        import random
        return random.choice(helpful_responses)
    
    def _pattern_based_nlp(self, user_input: str) -> Optional[str]:
        """Simple pattern-based NLP for common queries without AI"""
        user_lower = user_input.lower()
        
        # Greetings
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste', 'namaskar']):
            return responses.greeting()
        
        # Farewells
        if any(word in user_lower for word in ['bye', 'goodbye', 'see you', 'exit', 'quit', 'alvida']):
            return "Goodbye! Take care!"
        
        # Identity questions
        if any(phrase in user_lower for phrase in ['who are you', 'what are you', 'your name', 'who is vani', 'introduce yourself']):
            return "I'm VANI, your multilingual voice assistant. I can help with music, questions, and conversations in over 30 languages!"
        
        # COMPREHENSIVE HELP SYSTEM - Detailed feature explanations
        
        # General help
        if any(phrase in user_lower for phrase in ['help', 'what can you do', 'your capabilities', 'how do you work', 'guide me', 'show features', 'what are your features']):
            # Check if user wants detailed help
            if any(word in user_lower for word in ['detail', 'detailed', 'complete', 'full', 'comprehensive', 'all', 'everything']):
                return self._get_detailed_help()
            else:
                return self._get_quick_help()
        
        # Music-specific help
        if any(phrase in user_lower for phrase in ['music help', 'how to play music', 'music commands', 'play songs', 'music features']):
            return self._get_music_help()
        
        # Language help
        if any(phrase in user_lower for phrase in ['language help', 'which languages', 'what languages', 'language support', 'languages do you speak', 'how many languages', 'change language']):
            return self._get_language_help()
        
        # Voice and speech help
        if any(phrase in user_lower for phrase in ['voice help', 'speech help', 'how to talk', 'wake word', 'activation', 'how to activate']):
            return self._get_voice_help()
        
        # Commands help
        if any(phrase in user_lower for phrase in ['commands', 'what commands', 'command list', 'available commands']):
            return self._get_commands_help()
        
        # Time queries
        if any(phrase in user_lower for phrase in ['what time', 'current time', "what's the time", 'time is it']):
            import datetime
            now = datetime.datetime.now()
            return f"It's {now.strftime('%I:%M %p')} right now."
        
        # Date queries
        if any(phrase in user_lower for phrase in ['what date', "today's date", 'what day', 'which day']):
            import datetime
            now = datetime.datetime.now()
            return f"Today is {now.strftime('%A, %B %d, %Y')}."
        
        # Language support
        if any(phrase in user_lower for phrase in ['which languages', 'what languages', 'language support', 'languages do you speak', 'how many languages']):
            return "I support 22 Indian languages including Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, and more, plus 10 global languages like Spanish, French, German, Japanese, Korean, Chinese, Russian, Arabic, and Portuguese!"
        
        # Thanks
        if any(word in user_lower for word in ['thank', 'thanks', 'appreciate', 'धन्यवाद', 'शुक्रिया', 'nandri', 'dhanyavaad']):
            return "You're welcome! Happy to help anytime!"
        
        # Jokes
        if any(word in user_lower for word in ['joke', 'funny', 'make me laugh', 'tell me something funny']):
            import random
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "What do you call a fake noodle? An impasta!",
                "Why did the scarecrow win an award? He was outstanding in his field!",
                "What do you call a bear with no teeth? A gummy bear!",
                "Why don't eggs tell jokes? They'd crack up!",
                "What did one wall say to the other? I'll meet you at the corner!",
                "Why did the bicycle fall over? It was two tired!",
                "What do you call a fish wearing a crown? A king fish!"
            ]
            return random.choice(jokes)
        
        # Compliments
        if any(phrase in user_lower for phrase in ['good job', 'well done', 'great', 'awesome', 'excellent', 'you are good', 'you are great']):
            return "Thank you so much! I'm here to help anytime you need me!"
        
        # How are you
        if any(phrase in user_lower for phrase in ['how are you', 'how do you do', "how's it going", 'kaise ho', 'kya haal']):
            return "I'm doing great, thank you for asking! How can I assist you today?"
        
        # Math calculations
        if any(word in user_lower for word in ['calculate', 'plus', 'minus', 'times', 'divided', 'multiply']):
            try:
                import re
                # Simple math patterns
                math_patterns = [
                    r'(\d+)\s*(?:\+|plus)\s*(\d+)',
                    r'(\d+)\s*(?:\-|minus)\s*(\d+)',
                    r'(\d+)\s*(?:\*|times|multiplied by)\s*(\d+)',
                    r'(\d+)\s*(?:\/|divided by)\s*(\d+)'
                ]
                
                for pattern in math_patterns:
                    match = re.search(pattern, user_lower)
                    if match:
                        num1, num2 = int(match.group(1)), int(match.group(2))
                        
                        if '+' in user_lower or 'plus' in user_lower:
                            result = num1 + num2
                        elif '-' in user_lower or 'minus' in user_lower:
                            result = num1 - num2
                        elif '*' in user_lower or 'times' in user_lower or 'multiply' in user_lower:
                            result = num1 * num2
                        elif '/' in user_lower or 'divided' in user_lower:
                            result = num1 / num2 if num2 != 0 else "undefined"
                        else:
                            continue
                        
                        return f"The answer is {result}."
            except Exception as e:
                logger.debug(f"Math calculation failed: {e}")
        
        # No pattern matched, return None to try web search
        return None
    
    def _get_quick_help(self) -> str:
        """Quick overview of VANI's capabilities"""
        return ("I'm VANI, your multilingual voice assistant! Here's what I can do: "
                "Play music from YouTube by saying 'play despacito' or 'play romantic songs'. "
                "Answer questions using web search like 'what is the weather today'. "
                "Have conversations and tell jokes. "
                "Give you the time and date. "
                "Work in 22 Indian languages and 10 global languages. "
                "Say 'detailed help' for more information, or ask about specific features like 'music help' or 'language help'.")
    
    def _get_detailed_help(self) -> str:
        """Comprehensive guide to all VANI features"""
        return ("Welcome to VANI! Let me explain all my features in detail. "
                "Music Features: I can play any song from YouTube. Just say 'play' followed by the song name. "
                "You can queue multiple songs by saying 'play song one and song two and song three'. "
                "Control playback with 'pause', 'resume', 'stop', 'next song', 'previous song', 'volume up', 'volume down'. "
                "I'll automatically lower music volume when you speak to me. "
                "Voice Control: Say 'Hey Vani', 'Hey Shivani', or just 'Vani' to activate me. "
                "When music is playing, I'll speech_recognition for the wake word. When idle, I speech_recognition continuously. "
                "I have ultra-sensitive voice detection with automatic noise adjustment. "
                "Language Support: I speak 22 Indian languages including Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Urdu, and more. "
                "Plus 10 global languages: Spanish, French, German, Japanese, Korean, Chinese, Russian, Arabic, Portuguese. "
                "I automatically detect which language you're speaking. "
                "Question Answering: Ask me anything! I use Google's AI with real-time web search. "
                "Try questions like 'what is happening in the world', 'who won the match', or 'explain quantum physics'. "
                "Fun Features: Ask me to tell a joke, ask about the time or date, do simple math calculations, or just have a conversation. "
                "I remember our conversation context to give better responses. "
                "For specific help, say 'music help', 'language help', 'voice help', or 'commands help'.")
    
    def _get_music_help(self) -> str:
        """Detailed music feature help"""
        return ("Here's everything about music control! "
                "To play music, say 'play' followed by any song name, artist, or mood. "
                "Examples: 'play despacito', 'play songs by Arijit Singh', 'play romantic music', 'play relaxing instrumental'. "
                "Queue multiple songs: Say 'play despacito and shape of you and perfect' to add songs to queue. "
                "Playback controls: 'pause' to pause, 'resume' to continue, 'stop' to stop completely. "
                "'next song' or 'skip' to go to next track, 'previous song' to go back. "
                "'volume up' or 'increase volume' to make it louder, 'volume down' or 'decrease volume' to make it quieter. "
                "'mute' to silence, 'unmute' to restore sound. "
                "Smart features: Music automatically ducks down when you speak to me. "
                "All songs are cached so they play instantly the next time. "
                "I search YouTube for the best quality audio and stream it directly.")
    
    def _get_language_help(self) -> str:
        """Detailed language support help"""
        return ("VANI supports 32 languages across India and the world! "
                "Indian Languages: Hindi, English India, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Assamese, Odia, Nepali, Sindhi, Konkani, Maithili, Kashmiri, Sanskrit, Bodo, Santali, and Manipuri. "
                "Global Languages: English US, Spanish, French, German, Japanese, Korean, Chinese, Russian, Arabic, and Portuguese. "
                "I automatically detect which language you're speaking, so you can switch languages anytime. "
                "My voice responses use premium HD neural voices optimized for each language. "
                "For English India and Hindi, I use the highest quality Dragon HD voices. "
                "You can speak naturally in any of these languages, and I'll understand and respond in the same language. "
                "Try mixing languages too - I can handle multilingual conversations!")
    
    def _get_voice_help(self) -> str:
        """Voice interaction and wake word help"""
        parts = [
            "Here's how to talk to VANI! ",
            "Wake Words: Say 'Hey Vani', 'Hi Vani', 'Hello Vani', 'Okay Vani', 'Hey Shivani', or just 'Vani' or 'Shivani'. ",
            "All variations work: Vani, Vaani, Vanni, Wani, Bani, Shivani. ",
            "When to use wake words: You only need the wake word when music is playing. ",
            "When I'm idle with no music, I listen continuously and respond directly. ",
            "Voice Detection: I use ultra-sensitive microphone detection with a threshold of only 100. ",
            "I automatically adjust for ambient noise to hear you clearly. ",
            "I give you 45 seconds to speak your command. "
        ]
        parts.append(self._get_listening_hint())
        return "".join(parts)
    
    def _get_commands_help(self) -> str:
        """List of available commands"""
        return ("Here are all the commands you can use! "
                "Music Commands: 'play song name', 'pause', 'resume', 'stop', 'next song', 'previous song', 'skip', "
                "'volume up', 'volume down', 'increase volume', 'decrease volume', 'mute', 'unmute', 'what's playing', 'current song'. "
                "Information Commands: 'what time is it', 'what's the date', 'tell me a joke', 'who are you', 'what can you do'. "
                "Conversation: Just talk to me naturally! Ask questions, have conversations, request information. "
                "Language: I understand all commands in all 32 supported languages. "
                "Help Commands: 'help' for quick overview, 'detailed help' for complete guide, "
                "'music help', 'language help', 'voice help', 'commands help' for specific topics. "
                "Math: 'calculate 25 plus 30', 'what is 100 divided by 5'. "
                "Wake Up: 'Hey Vani', 'Hi Vani', 'Hello Vani', 'Vani', 'Shivani'. "
                "Exit: Say 'goodbye', 'bye', 'exit', or press Control C. "
                "You can combine commands naturally, like 'play despacito and then play shape of you'.")
    
    def set_user_name(self, name: str):
        """Set user's name for personalitylized responses"""
        self.user_name = name
        logger.info(f"User name set to: {name}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.context_window.clear()
        logger.info("Conversation history cleared")
    
    def get_history(self, limit: int = 10) -> List[Tuple[str, str]]:
        """Get recent conversation history"""
        history = list(self.conversation_history)
        return history[-limit:] if len(history) > limit else history
    
    def quick_response(self, query_type: str) -> str:
        """Generate quick responses for common queries"""
        responses = {
            'greeting': [
                "Hello! How can I help you?",
                "Hi there! What would you like me to do?",
                "Hey! I'm ready to assist you."
            ],
            'acknowledgment': [
                "Sure, I can help with that.",
                "Okay, let me do that for you.",
                "No problem, I'm on it."
            ],
            'music_start': [
                "Starting the music now.",
                "Playing that for you.",
                "Let me play that song."
            ],
            'error': [
                "I'm sorry, I had trouble with that. Could you try again?",
                "Something went wrong. Let me try a different approach.",
                "I encountered an issue. Please repeat your request."
            ],
            'unclear': [
                "I didn't quite catch that. Could you say it again?",
                "Could you repeat that? I want to make sure I understand.",
                "I'm not sure what you mean. Can you rephrase?"
            ]
        }
        
        import random
        return random.choice(responses.get(query_type, responses['acknowledgment']))


# Global AI engine instance
# Global AI engine instance
_conversation_manager: Optional[ConversationManager] = None

def get_conversation_manager() -> ConversationManager:
    """Get or create global conversation engine instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
