"""
Response Generator - Template-Based Replies
==============================================

Features:
- Pre-defined response templates for common scenarios
- Randomized variation to avoid repetition
- Context-aware response selection
- Personality-driven tone
- Error message formatting
- Acknowledgment phrases
- Fallback responses for failures
- Natural language formatting

Generates natural-sounding responses using templates and variations.
Provides consistent personality while avoiding robotic repetition.

Vaani Voice Assistant
Copyright (c) 2026 Aman Kumar Pandey.
All Rights Reserved.

This file is part of the Vaani Voice Assistant core and is proprietary.
"""

"""
Natural Response Templates

Provides natural language response templates for the assistant.

Features:
- Dynamic response generation
- Context-aware replies
- Personality-consistent messaging

"""

import random
from typing import List, Dict


class NaturalResponses:
    """
    Human-written responses for every situation.
    
    Why this exists:
    AI-generated text often sounds stiff or templated. This module ensures
    every spoken word feels intentionally crafted by a human designer who
    cares about how the assistant sounds.
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WAKE WORD ACKNOWLEDGMENTS
    # Short, natural confirmations that we heard the user
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    WAKE_ACKNOWLEDGMENTS: List[str] = [
        "Yes?",
        "I'm here.",
        "What's up?",
        "How can I help?",
        "Go ahead.",
        "I'm listening.",
        "What do you need?",
        "Yep?",
        "Mmhm?",
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONFIRMATIONS
    # Casual ways to say "got it" without sounding robotic
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    CONFIRMATIONS: List[str] = [
        "Got it.",
        "Sure thing.",
        "On it.",
        "Okay.",
        "Alright.",
        "No problem.",
        "You got it.",
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MUSIC RESPONSES
    # Natural ways to acknowledge music requests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    MUSIC_SEARCHING: List[str] = [
        "Let me find that for you.",
        "Looking that up.",
        "Give me a second.",
        "Searching now.",
        "One moment.",
    ]
    
    MUSIC_PLAYING: List[str] = [
        "Here we go.",
        "Playing now.",
        "Enjoy.",
        "There you go.",
        "This one's great.",
    ]
    
    MUSIC_PAUSED: List[str] = [
        "Paused.",
        "Stopping for now.",
        "Alright, paused.",
    ]
    
    MUSIC_RESUMED: List[str] = [
        "Continuing.",
        "Back on.",
        "There we go.",
    ]
    
    MUSIC_STOPPED: List[str] = [
        "Stopped.",
        "Music's off.",
        "Done.",
    ]
    
    MUSIC_NOT_FOUND: List[str] = [
        "Hmm, I couldn't find that one.",
        "I'm not seeing that song. Want to try something else?",
        "Can't find that. Got another one in mind?",
    ]
    
    MUSIC_ERRORS: List[str] = [
        "Had trouble playing that. Want to try something else?",
        "That didn't work. Got another song in mind?",
        "I couldn't get that one to play. Try another?",
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ERROR HANDLING
    # Calm, apologetic, reassuring - never expose technical details
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    GENERAL_ERRORS: List[str] = [
        "Something didn't work there. Want to try again?",
        "Hmm, that didn't go through. One more time?",
        "I had trouble with that. Let's try again.",
        "That didn't quite work. Can you repeat that?",
    ]
    
    UNCLEAR_SPEECH: List[str] = [
        "I didn't catch that. Could you say it again?",
        "Sorry, I missed that. One more time?",
        "I couldn't hear you clearly. Try again?",
        "Mind repeating that?",
    ]
    
    TIMEOUT_RESPONSES: List[str] = [
        "I didn't hear anything. Still there?",
        "No response. Want to try again?",
        "Didn't get that. Say it again when you're ready.",
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSATIONAL RESPONSES
    # Natural, friendly answers to common queries
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    GREETINGS: List[str] = [
        "Hey! How can I help?",
        "Hi there! What's up?",
        "Hello! What do you need?",
        "Hey! I'm here.",
    ]
    
    THANKS_RESPONSES: List[str] = [
        "You're welcome!",
        "Anytime!",
        "Happy to help.",
        "Of course!",
        "No problem at all.",
    ]
    
    HOW_ARE_YOU: List[str] = [
        "I'm good, thanks! What can I do for you?",
        "Doing great! How about you?",
        "I'm here and ready to help!",
    ]
    
    GOODBYE: List[str] = [
        "See you later!",
        "Take care!",
        "Bye!",
        "Catch you later!",
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELP & CAPABILITIES
    # Explaining what we can do in plain language
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    CAPABILITIES: str = (
        "I can help you with music, answer questions, tell you the time, "
        "give you weather updates, and more. Just ask!"
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HELPER METHODS
    # Smart response selection based on context
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @staticmethod
    def get_random(response_list: List[str]) -> str:
        """Pick a random response to avoid repetition."""
        return random.choice(response_list)
    
    @staticmethod
    def wake_acknowledgment() -> str:
        """Natural way to acknowledge the wake word."""
        return NaturalResponses.get_random(NaturalResponses.WAKE_ACKNOWLEDGMENTS)
    
    @staticmethod
    def confirmation() -> str:
        """Quick confirmation that we understood."""
        return NaturalResponses.get_random(NaturalResponses.CONFIRMATIONS)
    
    @staticmethod
    def music_searching() -> str:
        """Let them know we're looking for music."""
        return NaturalResponses.get_random(NaturalResponses.MUSIC_SEARCHING)
    
    @staticmethod
    def music_playing(song_name: str = None) -> str:
        """Announce we're starting playback."""
        base = NaturalResponses.get_random(NaturalResponses.MUSIC_PLAYING)
        if song_name and len(song_name) < 50:
            return base
        return base
    
    @staticmethod
    def error() -> str:
        """Calm, apologetic error message."""
        return NaturalResponses.get_random(NaturalResponses.GENERAL_ERRORS)
    
    @staticmethod
    def unclear_speech() -> str:
        """When we couldn't understand."""
        return NaturalResponses.get_random(NaturalResponses.UNCLEAR_SPEECH)
    
    @staticmethod
    def timeout() -> str:
        """When we didn't hear anything."""
        return NaturalResponses.get_random(NaturalResponses.TIMEOUT_RESPONSES)
    
    @staticmethod
    def greeting() -> str:
        """Friendly hello."""
        return NaturalResponses.get_random(NaturalResponses.GREETINGS)
    
    @staticmethod
    def thanks() -> str:
        """Response to thank you."""
        return NaturalResponses.get_random(NaturalResponses.THANKS_RESPONSES)
    
    @staticmethod
    def goodbye() -> str:
        """Friendly farewell."""
        return NaturalResponses.get_random(NaturalResponses.GOODBYE)
    
    @staticmethod
    def polish_ai_response(raw_text: str) -> str:
        """
        Take raw AI output and make it sound human.
        
        Why this matters:
        AI models often generate technically correct but emotionally flat text.
        This function adds warmth, breaks up long sentences, and ensures
        natural pacing for speech.
        """
        if not raw_text:
            return raw_text
        
        # Remove common AI-isms
        text = raw_text.replace("As an AI", "")
        text = text.replace("I cannot", "I can't")
        text = text.replace("I am not", "I'm not")
        text = text.replace("I am", "I'm")
        text = text.replace("You are", "You're")
        text = text.replace("It is", "It's")
        text = text.replace("That is", "That's")
        text = text.replace("There is", "There's")
        text = text.replace("do not", "don't")
        text = text.replace("cannot", "can't")
        text = text.replace("will not", "won't")
        
        # Remove overly formal phrases
        text = text.replace("However,", "But")
        text = text.replace("Furthermore,", "Also,")
        text = text.replace("Additionally,", "And")
        text = text.replace("In conclusion,", "So,")
        
        # Trim excess whitespace
        text = " ".join(text.split())
        
        return text.strip()


# Global instance for easy access
responses = NaturalResponses()
