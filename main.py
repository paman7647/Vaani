#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vaani - Natural Voice Assistant
Copyright © Aman Kumar Pandey 2026–2027. All rights reserved.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A thoughtfully designed voice assistant that feels natural and human.

What Vaani can do:
• Play music from YouTube
• Answer questions with real-time web search
• Have natural conversations with context context
• Provide information clearly and warmly
• Control playback (pause, resume, stop, skip)

Disclaimer:
Vaani is designed to help with everyday tasks and information.
It's not a substitute for professional advice in medical, legal,
financial, or other specialized domains.

Design philosophy:
Every interaction should feel like talking to a helpful friend,
not commanding a machine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import signal
from vaani import get_assistant


def signal_handler(sig, frame):
    """Handle Ctrl+C with grace"""
    print("\n\n✨ Thanks for using VANI. See you next time!\n")
    sys.exit(0)


def main():
    """Start Vaani"""
    signal.signal(signal.SIGINT, signal_handler)
    
    manager = get_assistant()
    manager.start()


if __name__ == "__main__":
    main()
