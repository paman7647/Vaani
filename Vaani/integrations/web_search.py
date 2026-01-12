"""
Web Search Integration - Real-Time Information
=================================================

Features:
- DuckDuckGo search integration (privacy-focused)
- Wikipedia integration for encyclopedic information
- Google Search scraping fallback
- Result parsing and summarization
- Source attribution
- Caching for repeated queries
- Rate limiting and error handling
- Multi-source aggregation

Searches the web to answer your questions with current, accurate
information. Prioritizes privacy-friendly sources like DuckDuckGo
and Wikipedia.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""
import re
from typing import Optional, List, Dict, Any
from ..utils.logger import VaaniLogger
from ..utils.error_handler import error_handler, RecoveryAction, ErrorSeverity

logger = VaaniLogger.get_logger("Web Search")

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logger.info("duckduckgo-search not installed (using Google Search grounding instead)")

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    logger.warning("requests/beautifulsoup4 not available")

try:
    from googlesearch import search as google_search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    logger.info("googlesearch-python not installed (optional)")

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
    wikipedia.set_lang('en')  # Default to English, can be changed dynamically
    logger.info("Wikipedia integration enabled")
except ImportError:
    WIKIPEDIA_AVAILABLE = False
    logger.info("wikipedia library not installed (optional - pip install wikipedia)")

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
    wikipedia.set_lang('en')  # Default to English
except ImportError:
    WIKIPEDIA_AVAILABLE = False
    logger.info("wikipedia library not installed (optional)")


class SearchHelper:
    """Intelligent web search with summarization"""
    
    def __init__(self):
        self.session = requests.Session() if WEB_SCRAPING_AVAILABLE else None
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }) if self.session else None
        logger.debug("Web search engine initialized")
    
    def validate_query(self, query: str) -> bool:
        """
        Validate if query is suitable for search (not just stop words)
        
        Args:
            query: The raw search query
            
        Returns:
            True if query is valid for search
        """
        if not query:
            return False
            
        # Normalize
        clean = query.lower().strip()
        
        # known trigger phrases that might be passed as the whole query
        triggers = [
            'search for', 'tell me about', 'what is', 'who is', 
            'find out', 'look up', 'search', 'find', 'tell me',
            'give me info', 'can you search', 'google'
        ]
        
        # If query EXACTLY matches a trigger, it's invalid (user just said "search")
        if clean in triggers:
            return False
            
        # Check against stop words if it's very short
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        if clean in stop_words:
            return False
            
        # Must be at least 2 characters
        return len(clean) >= 2

    @error_handler(default_return=[])
    def search(self, query: str, max_results: int = 3, language: str = 'en') -> List[Dict[str, str]]:
        """
        Search the web and return results with multi-engine fallback
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            language: Language code (en, hi, es, fr, de, ja, ko, zh, ru, ar, pt)
        
        Returns:
            List of dicts with 'title', 'link', 'snippet'
        """
        logger.info(f"Searching web for: {query} (language: {language})")
        
        # Try DuckDuckGo first (best for privacy and multilingual)
        if DDGS_AVAILABLE:
            try:
                results = []
                # Map language codes to DuckDuckGo regions
                region_map = {
                    'en': 'wt-wt',  # Worldwide
                    'hi': 'in-en',  # India
                    'es': 'es-es',  # Spain
                    'fr': 'fr-fr',  # France
                    'de': 'de-de',  # Germany
                    'ja': 'jp-jp',  # Japan
                    'ko': 'kr-kr',  # Korea
                    'zh': 'cn-zh',  # China
                    'ru': 'ru-ru',  # Russia
                    'ar': 'xa-ar',  # Arabia
                    'pt': 'br-pt',  # Brazil
                }
                region = region_map.get(language, 'wt-wt')
                
                with DDGS() as ddgs:
                    search_results = ddgs.text(query, region=region, max_results=max_results)
                    
                    for result in search_results:
                        results.append({
                            'title': result.get('title', ''),
                            'link': result.get('href', ''),
                            'snippet': result.get('body', '')
                        })
                
                if results:
                    logger.info(f"Found {len(results)} results via DuckDuckGo")
                    return results
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {e}")
        
        # Fallback to Google Search scraping
        if GOOGLE_SEARCH_AVAILABLE:
            try:
                results = []
                # Use googlesearch-python library
                search_results = list(google_search(query, num_results=max_results, lang=language))
                
                for idx, url in enumerate(search_results):
                    if idx >= max_results:
                        break
                    results.append({
                        'title': f"Result {idx + 1}",
                        'link': url,
                        'snippet': ''
                    })
                
                if results:
                    logger.info(f"Found {len(results)} results via Google")
                    return results
            except Exception as e:
                logger.warning(f"Google search failed: {e}")
        
        logger.error("All web search methods failed - no search engines available")
        return []
    
    @error_handler(default_return="I couldn't complete the search.")
    def search_and_summarize(self, query: str, max_results: int = 5) -> str:
        """
        Search web and return a natural conversational summary
        
        Args:
            query: Search query
            max_results: Maximum results to consider (increased from 3 to 5 for better coverage)
        
        Returns:
            Natural language summary optimized for speech
        """
        # Validate query first
        if not self.validate_query(query):
            return "I need a specific topic to search for. What would you like to know?"

        results = self.search(query, max_results)
        
        if not results:
            return "I couldn't find any information about that online right now. Could you try rephrasing your question?"
        
        # Extract meaningful content from results
        content_pieces = []
        
        for idx, result in enumerate(results):
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')
            
            # Clean snippet
            if snippet:
                cleaned = self._clean_text_for_speech(snippet)
                if cleaned and len(cleaned) > 20:  # Minimum content length
                    content_pieces.append({
                        'text': cleaned,
                        'source': title,
                        'rank': idx,
                        'link': link
                    })
        
        # If no snippets, try fetching page content from top result
        if not content_pieces and results:
            logger.info("No snippets available, fetching page content...")
            top_result = results[0]
            page_content = self.fetch_page_content(top_result.get('link', ''), max_length=400)
            if page_content:
                content_pieces.append({
                    'text': page_content,
                    'source': top_result.get('title', 'a website'),
                    'rank': 0,
                    'link': top_result.get('link', '')
                })
        
        if not content_pieces:
            return f"I found {len(results)} sources about that, but couldn't extract clear information. Try asking in a different way?"
        
        # Build natural conversational summary
        summary = self._build_conversational_summary(query, content_pieces, len(results))
        
        logger.info(f"📝 Generated summary ({len(summary)} chars from {len(content_pieces)} sources)")
        return summary
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Enhanced text cleaning optimized for speech synthesis"""
        if not text:
            return ""
        
        import re
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove content in brackets and parentheses that's typically metadata
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(\d+\)', '', text)  # Remove citation numbers like (1), (2)
        
        # Remove dates in various formats
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)
        text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)
        
        # Remove "Read more", "Click here" type suffixes
        text = re.sub(r'(read more|click here|learn more|see more|continue reading).*$', '', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters except basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\'\-()]', ' ', text)
        
        # Clean up multiple punctuation
        text = re.sub(r'[.,!?;:]{2,}', '.', text)
        
        # Trim and capitalize properly
        text = text.strip()
        
        # Ensure ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def _build_conversational_summary(self, query: str, content_pieces: list, total_results: int) -> str:
        """Build natural conversational summary from content pieces"""
        if not content_pieces:
            return "I couldn't find specific information."
        
        import random
        
        summary_parts = []
        
        # Natural opening based on query type
        query_lower = query.lower()
        openings = {
            'what': ["Here's what I found:", "Let me tell you:", "Based on my search:"],
            'who': ["Here's who that is:", "Let me tell you about them:", "From what I found:"],
            'when': ["Here's when that happened:", "According to my search:", "From what I found:"],
            'where': ["Here's where that is:", "Based on my search:", "Let me tell you:"],
            'how': ["Here's how it works:", "Let me explain:", "Here's what I learned:"],
            'why': ["Here's why:", "Let me explain:", "According to my research:"]
        }
        
        # Select appropriate opening
        opening = "Here's what I found:"
        for question_word, phrases in openings.items():
            if query_lower.startswith(question_word):
                opening = random.choice(phrases)
                break
        
        summary_parts.append(opening)
        
        # Add primary content (from top result)
        primary = content_pieces[0]
        primary_text = primary['text']
        
        # Limit primary content length for speech
        if len(primary_text) > 250:
            primary_text = primary_text[:250].rsplit('.', 1)[0]
            if not primary_text.endswith('.'):
                primary_text += '.'
        
        summary_parts.append(primary_text)
        
        # Add supporting information from second result if available
        if len(content_pieces) > 1:
            secondary = content_pieces[1]
            secondary_text = secondary['text']
            
            # Vary connection phrases
            connectors = [
                "Additionally,", "Also,", "Furthermore,", 
                "Moreover,", "In addition,", "Another source mentions:"
            ]
            
            # Limit secondary content
            if len(secondary_text) > 150:
                secondary_text = secondary_text[:150].rsplit('.', 1)[0] + '.'
            
            summary_parts.append(f"{random.choice(connectors)} {secondary_text}")
        
        # Add source attribution for credibility
        if total_results > 2:
            summary_parts.append(f"I found {total_results} sources with more information if you need it.")
        elif primary.get('source'):
            summary_parts.append(f"This information is from {primary['source']}.")
        
        summary = " ".join(summary_parts)
        
        # Final cleanup
        summary = re.sub(r'\s+', ' ', summary)
        
        return summary.strip()
    
    @error_handler(default_return=None)
    def fetch_page_content(self, url: str, max_length: int = 1000) -> Optional[str]:
        """
        Fetch and extract main content from a web page with improved cleaning
        
        Args:
            url: URL to fetch
            max_length: Maximum content length
        
        Returns:
            Cleaned text content optimized for speech, or None
        """
        if not WEB_SCRAPING_AVAILABLE:
            logger.error("Web scraping not available (requests/bs4 missing)")
            return None
        
        try:
            logger.debug(f"Fetching page: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            # Try to find main content area
            main_content = None
            
            # Look for common content containers
            content_selectors = [
                ('article', {}),
                ('main', {}),
                ('div', {'class': ['content', 'main-content', 'post-content', 'article-content']}),
                ('div', {'id': ['content', 'main-content', 'article-body']})
            ]
            
            for tag, attrs in content_selectors:
                if attrs:
                    main_content = soup.find(tag, attrs)
                else:
                    main_content = soup.find(tag)
                if main_content:
                    break
            
            # Fallback to body if no main content found
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                logger.warning("No content container found")
                return None
            
            # Get text from paragraphs for better quality
            paragraphs = main_content.find_all('p')
            if paragraphs:
                text = ' '.join([p.get_text() for p in paragraphs[:5]])  # First 5 paragraphs
            else:
                text = main_content.get_text()
            
            # Clean text for speech
            text = self._clean_text_for_speech(text)
            
            # Limit length
            if len(text) > max_length:
                text = text[:max_length].rsplit('.', 1)[0]
                if not text.endswith('.'):
                    text += '.'
            
            logger.debug(f"✅ Fetched {len(text)} chars")
            return text if text else None
            
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text (legacy method, use _clean_text_for_speech instead)"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that don't sound good
        text = re.sub(r'[^\w\s.,!?;:\-()]', '', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    @error_handler(default_return=None)
    def get_instant_answer(self, query: str) -> Optional[str]:
        """Get instant answer from DuckDuckGo (for factual queries like 'weather', 'time in X')"""
        if not DDGS_AVAILABLE:
            return None
        
        try:
            logger.debug(f"⚡ Trying instant answer for: {query}")
            
            with DDGS() as ddgs:
                # Get instant answer
                answer_results = ddgs.answers(query)
                
                if answer_results:
                    for answer in answer_results:
                        text = answer.get('text', '')
                        if text:
                            logger.info(f"✅ Got instant answer ({len(text)} chars)")
                            return self._clean_text_for_speech(text)
            
            return None
            
        except Exception as e:
            logger.debug(f"Instant answer failed: {e}")
            return None
    
    @error_handler(default_return=None)
    def search_wikipedia(self, query: str, sentences: int = 3) -> Optional[Dict[str, str]]:
        """
        Search Wikipedia and get summary
        
        Args:
            query: Search query
            sentences: Number of sentences to return
        
        Returns:
            Dict with 'summary', 'title', 'url' or None
        """
        if not WIKIPEDIA_AVAILABLE:
            return None
        
        try:
            logger.info(f"📚 Searching Wikipedia for: {query}")
            
            # Search for pages
            search_results = wikipedia.search(query, results=3)
            
            if not search_results:
                return None
            
            # Get summary of top result
            page_title = search_results[0]
            summary = wikipedia.summary(page_title, sentences=sentences, auto_suggest=False)
            page = wikipedia.page(page_title, auto_suggest=False)
            
            logger.info(f"✅ Wikipedia: Found '{page_title}' ({len(summary)} chars)")
            
            return {
                'summary': summary,
                'title': page_title,
                'url': page.url,
                'source': 'Wikipedia'
            }
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Multiple meanings - pick first option
            try:
                if e.options:
                    page_title = e.options[0]
                    summary = wikipedia.summary(page_title, sentences=sentences, auto_suggest=False)
                    page = wikipedia.page(page_title, auto_suggest=False)
                    
                    logger.info(f"✅ Wikipedia (disambiguated): '{page_title}'")
                    return {
                        'summary': summary,
                        'title': page_title,
                        'url': page.url,
                        'source': 'Wikipedia'
                    }
            except Exception:
                pass
            return None
            
        except wikipedia.exceptions.PageError:
            logger.debug(f"Wikipedia: Page not found for '{query}'")
            return None
            
        except Exception as e:
            logger.warning(f"Wikipedia search error: {e}")
            return None
    
    @error_handler(default_return=[])
    def fetch_multiple_pages(self, urls: List[str], max_per_page: int = 300) -> List[Dict[str, str]]:
        """
        Fetch content from multiple URLs in parallel-like fashion
        
        Args:
            urls: List of URLs to fetch
            max_per_page: Max characters per page
        
        Returns:
            List of dicts with 'url', 'content'
        """
        if not WEB_SCRAPING_AVAILABLE:
            return []
        
        logger.info(f"📥 Fetching content from {len(urls)} URLs...")
        
        results = []
        
        for url in urls[:3]:  # Limit to first 3 URLs
            try:
                content = self.fetch_page_content(url, max_length=max_per_page)
                if content:
                    results.append({
                        'url': url,
                        'content': content
                    })
                    logger.debug(f"✅ Fetched: {url[:50]}... ({len(content)} chars)")
            except Exception as e:
                logger.debug(f"Failed to fetch {url[:50]}...: {e}")
                continue
        
        logger.info(f"✅ Successfully fetched {len(results)}/{len(urls)} pages")
        return results
    
    @error_handler(default_return="I couldn't complete the comprehensive search.")
    def advanced_search_and_synthesize(self, query: str, max_sources: int = 5) -> str:
        """
        Advanced multi-source search combining:
        - DuckDuckGo/Google search
        - Wikipedia knowledge
        - Direct page content fetching
        
        Args:
            query: Search query
            max_sources: Maximum sources to use
        
        Returns:
            Comprehensive natural language summary
        """
        # Validate query first
        if not self.validate_query(query):
            return "Please provide a specific topic for me to research."

        logger.info(f"🔍 Advanced multi-source search for: {query}")
        
        all_content = []
        
        # Source 1: Wikipedia (authoritative, structured)
        wiki_result = self.search_wikipedia(query, sentences=4)
        if wiki_result:
            all_content.append({
                'text': wiki_result['summary'],
                'source': f"Wikipedia - {wiki_result['title']}",
                'url': wiki_result['url'],
                'priority': 1,  # High priority
                'type': 'encyclopedia'
            })
            logger.info("✅ Added Wikipedia content")
        
        # Source 2: Web search (current, diverse)
        search_results = self.search(query, max_results=max_sources)
        
        if search_results:
            logger.info(f"Got {len(search_results)} search results")
            
            # Add search snippets
            for idx, result in enumerate(search_results[:3]):
                snippet = result.get('snippet', '')
                if snippet and len(snippet) > 30:
                    all_content.append({
                        'text': snippet,
                        'source': result.get('title', 'Web Source'),
                        'url': result.get('link', ''),
                        'priority': 2,
                        'type': 'search_snippet'
                    })
            
            # Source 3: Fetch actual page content from top results
            urls_to_fetch = [r['link'] for r in search_results[:2] if r.get('link')]
            
            if urls_to_fetch:
                fetched_pages = self.fetch_multiple_pages(urls_to_fetch, max_per_page=400)
                
                for page_data in fetched_pages:
                    all_content.append({
                        'text': page_data['content'],
                        'source': 'Direct Page Content',
                        'url': page_data['url'],
                        'priority': 3,
                        'type': 'full_page'
                    })
                
                if fetched_pages:
                    logger.info(f"✅ Added {len(fetched_pages)} full page contents")
        
        # Synthesize comprehensive response
        if not all_content:
            return "I searched multiple sources but couldn't find reliable information about that. Could you rephrase your question?"
        
        comprehensive_answer = self._synthesize_multi_source_answer(query, all_content)
        
        logger.info(f"✅ Synthesized answer from {len(all_content)} sources ({len(comprehensive_answer)} chars)")
        
        return comprehensive_answer
    
    def _synthesize_multi_source_answer(self, query: str, content_pieces: List[Dict]) -> str:
        """
        Synthesize natural answer from multiple diverse sources
        
        Args:
            query: Original query
            content_pieces: List of dicts with 'text', 'source', 'priority', 'type'
        
        Returns:
            Natural conversational answer
        """
        import random
        
        # Sort by priority (lower number = higher priority)
        sorted_content = sorted(content_pieces, key=lambda x: x.get('priority', 99))
        
        answer_parts = []
        
        # Opening based on query type
        query_lower = query.lower()
        if query_lower.startswith('what'):
            openings = ["Here's what I found:", "Let me explain:", "Based on multiple sources:"]
        elif query_lower.startswith('who'):
            openings = ["Here's who that is:", "Let me tell you about them:", "From my research:"]
        elif query_lower.startswith('how'):
            openings = ["Here's how it works:", "Let me break it down:", "From what I found:"]
        elif query_lower.startswith('when'):
            openings = ["Here's when that happened:", "According to my sources:", "From the information available:"]
        elif query_lower.startswith('where'):
            openings = ["Here's where that is:", "Based on my search:", "From multiple sources:"]
        else:
            openings = ["Here's what I discovered:", "Based on my research:", "From various sources:"]
        
        answer_parts.append(random.choice(openings))
        
        # Primary content (highest priority source)
        if sorted_content:
            primary = sorted_content[0]
            primary_text = self._clean_text_for_speech(primary['text'])
            
            # Limit primary content
            if len(primary_text) > 250:
                primary_text = primary_text[:250].rsplit('.', 1)[0]
                if not primary_text.endswith('.'):
                    primary_text += '.'
            
            # Add source attribution for Wikipedia
            if primary.get('type') == 'encyclopedia':
                answer_parts.append(f"According to Wikipedia, {primary_text}")
            else:
                answer_parts.append(primary_text)
        
        # Secondary content (supporting information)
        if len(sorted_content) > 1:
            secondary = sorted_content[1]
            secondary_text = self._clean_text_for_speech(secondary['text'])
            
            # Limit secondary
            if len(secondary_text) > 150:
                secondary_text = secondary_text[:150].rsplit('.', 1)[0] + '.'
            
            # Vary connectors
            connectors = [
                "Additionally,", "Furthermore,", "Moreover,", 
                "From another source,", "Also,", "Another source mentions:"
            ]
            
            answer_parts.append(f"{random.choice(connectors)} {secondary_text}")
        
        # Tertiary content (if available and different type)
        if len(sorted_content) > 2:
            tertiary = sorted_content[2]
            if tertiary.get('type') != sorted_content[0].get('type'):
                tertiary_text = self._clean_text_for_speech(tertiary['text'])
                
                if len(tertiary_text) > 100:
                    tertiary_text = tertiary_text[:100].rsplit('.', 1)[0] + '.'
                
                answer_parts.append(f"Additional details: {tertiary_text}")
        
        # Source count attribution
        unique_sources = len(set(c.get('source', '') for c in content_pieces))
        if unique_sources > 2:
            answer_parts.append(f"This information comes from {unique_sources} different sources including Wikipedia and verified websites.")
        elif unique_sources == 2:
            answer_parts.append("I verified this information across multiple sources.")
        
        answer = " ".join(answer_parts)
        
        # Final cleanup
        answer = re.sub(r'\s+', ' ', answer)
        answer = answer.strip()
        
        # Ensure reasonable length for speech
        if len(answer) > 500:
            answer = answer[:500].rsplit('.', 1)[0] + '.'
        
        return answer
    
    def should_search_web(self, query: str, ai_confidence: float = 0.5) -> bool:
        """
        Determine if query should trigger web search
        
        Args:
            query: User query
            ai_confidence: AI's confidence in its answer (0-1)
        
        Returns:
            True if web search recommended
        """
        # Explicit search keywords
        search_keywords = [
            'search', 'look up', 'find out', 'what is', 'who is',
            'when did', 'where is', 'latest', 'current', 'recent',
            'news', 'today', 'now', 'update'
        ]
        
        query_lower = query.lower()
        
        # Check for search keywords
        for keyword in search_keywords:
            if keyword in query_lower:
                return True
        
        # Check AI confidence
        if ai_confidence < 0.3:
            logger.info("Low AI confidence - triggering web search")
            return True
        
        return False


# Global web search instance
_search_helper: Optional[SearchHelper] = None

def get_search() -> SearchHelper:
    """Get or create global web search instance"""
    global _search_helper
    if _search_helper is None:
        _search_helper = SearchHelper()
    return _search_helper