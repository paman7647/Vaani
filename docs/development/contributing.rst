Contributing Guide
==================

Thank you for your interest in contributing to Vaani Assistant! This document provides guidelines for contributing to the project.

Ways to Contribute
------------------

**Code Contributions**

- Implement new features
- Fix bugs
- Improve performance
- Add tests
- Refactor code

**Documentation**

- Improve existing docs
- Add usage examples
- Create tutorials
- Translate documentation
- Fix typos and clarifications

**Testing and Quality**

- Report bugs
- Test on different platforms
- Improve test coverage
- Performance testing
- Security auditing

**Community**

- Answer questions
- Help other users
- Share use cases
- Provide feedback
- Spread the word

Getting Started
---------------

**1. Fork the Repository**

.. code-block:: bash

   # Fork on GitHub, then clone
   git clone https://github.com/YOUR_USERNAME/vaani.git
   cd vaani
   
   # Add upstream remote
   git remote add upstream https://github.com/paman7647/vaani.git

**2. Set Up Development Environment**

.. code-block:: bash

   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest pytest-cov black flake8 mypy

**3. Create a Branch**

.. code-block:: bash

   # Update your fork
   git checkout main
   git pull upstream main
   
   # Create feature branch
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description

**4. Make Your Changes**

Follow the :doc:`coding_style` guidelines while making changes.

**5. Test Your Changes**

.. code-block:: bash

   # Run tests
   pytest tests/
   
   # Run with coverage
   pytest --cov=vaani_assistant tests/
   
   # Test manually
   python3 main.py

**6. Commit Your Changes**

.. code-block:: bash

   # Stage changes
   git add .
   
   # Commit with descriptive message
   git commit -m "feat(speech): Add Vosk recognition support"
   
   # Push to your fork
   git push origin feature/your-feature-name

**7. Submit Pull Request**

1. Go to your fork on GitHub
2. Click "Pull Request" button
3. Select your branch
4. Fill out the PR template
5. Wait for review

Pull Request Guidelines
-----------------------

**PR Title Format**

Use conventional commit format:

.. code-block:: text

   <type>(<scope>): <description>
   
   Examples:
   feat(voice): Add multi-language TTS support
   fix(audio): Resolve buffer overflow in audio capture
   docs(installation): Update macOS setup instructions

**PR Description Template**

.. code-block:: markdown

   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   Describe how you tested these changes
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Tests added/updated
   - [ ] All tests passing
   - [ ] No breaking changes (or documented)
   
   ## Related Issues
   Fixes #123
   Related to #456

**What Makes a Good PR**

✓ **Small and Focused**

.. code-block:: text

   Good:  Add Vosk recognition engine (150 lines, 1 feature)
   Bad:   Add Vosk, refactor audio, update docs (800 lines, 3 features)

✓ **Well Tested**

.. code-block:: python

   # Include tests demonstrating your changes work
   def test_vosk_recognition():
       recognizer = VoskRecognizer()
       result = recognizer.recognize(sample_audio)
       assert result == "expected text"

✓ **Documented**

.. code-block:: python

   def new_function(param: str) -> bool:
       """Clear docstring explaining purpose.
       
       Args:
           param: Description of parameter
       
       Returns:
           Description of return value
       """

✓ **Clear Commit History**

.. code-block:: bash

   # Good commit history
   feat(speech): Add Vosk recognizer class
   feat(speech): Integrate Vosk into recognition pipeline
   test(speech): Add tests for Vosk integration
   docs(speech): Document Vosk configuration
   
   # Bad commit history  
   wip
   fixes
   more fixes
   final version

**Review Process**

1. **Automated Checks** - CI runs tests, linting, type checking
2. **Code Review** - Maintainer reviews code quality, design, tests
3. **Testing** - Changes tested on multiple platforms if applicable
4. **Feedback** - Reviewer provides feedback, requests changes
5. **Approval** - Once approved, PR is merged

**Addressing Review Feedback**

.. code-block:: bash

   # Make requested changes
   # ... edit files ...
   
   # Commit changes
   git add .
   git commit -m "refactor: Address review feedback"
   
   # Push update
   git push origin feature/your-feature-name

Bug Reports
-----------

**Before Reporting**

1. Check if bug already reported (GitHub Issues)
2. Verify bug exists in latest version
3. Try to reproduce with minimal example
4. Check documentation for expected behavior

**Bug Report Template**

.. code-block:: markdown

   ## Description
   Clear description of the bug
   
   ## To Reproduce
   Steps to reproduce:
   1. Start Vaani with config X
   2. Say command Y
   3. Observe error Z
   
   ## Expected Behavior
   What should happen
   
   ## Actual Behavior
   What actually happens
   
   ## Environment
   - OS: macOS 13.0
   - Python: 3.11.2
   - Vaani Version: 1.0.0
   - Installation Method: pip / git clone
   
   ## Logs
   ```
   Paste relevant log output here
   ```
   
   ## Additional Context
   - Screenshots if applicable
   - Related issues
   - Attempted workarounds

**Good Bug Report Example**

.. code-block:: markdown

   ## Audio playback cuts off prematurely
   
   ### Description
   When Vaani responds with long sentences (>20 words), audio
   playback stops after ~10 seconds even though response is longer.
   
   ### To Reproduce
   1. Ask: "Explain quantum computing in detail"
   2. Wait for response
   3. Audio cuts off mid-sentence
   
   ### Expected
   Full response should play
   
   ### Actual
   Only first 10 seconds play, rest is silent
   
   ### Environment
   - macOS 13.0.1
   - Python 3.11.2
   - Vaani 1.0.0 (git main branch)
   
   ### Logs
   ```
   [INFO] Playing response audio (length: 45s)
   [ERROR] Audio player timeout after 10s
   [DEBUG] Audio buffer: 720KB remaining
   ```
   
   ### Context
   Works fine with short responses (<10s).
   Issue started after update to main branch yesterday.

Feature Requests
----------------

**Feature Request Template**

.. code-block:: markdown

   ## Feature Description
   Clear description of proposed feature
   
   ## Use Case
   Why is this feature needed?
   What problem does it solve?
   
   ## Proposed Solution
   How should it work?
   
   ## Alternatives Considered
   Other approaches you've thought about
   
   ## Additional Context
   - Mockups or examples
   - Related features
   - Similar features in other projects

**Good Feature Request Example**

.. code-block:: markdown

   ## Voice Profile Support (Multi-User)
   
   ### Description
   Add ability to recognize different users by voice and maintain
   separate preferences and conversation history for each.
   
   ### Use Case
   In a household with multiple people, everyone has different:
   - Music preferences
   - Language preferences
   - Conversation context
   
   Currently all users share same context and preferences.
   
   ### Proposed Solution
   
   1. **Training Phase**
      - User says "Train my voice"
      - Vaani records 5-10 sample phrases
      - Creates voice profile
   
   2. **Recognition**
      - On wake word, identify speaker
      - Load speaker's profile
      - Use speaker-specific preferences
   
   3. **Configuration**
      ```json
      {
        "profiles": {
          "user1": {
            "name": "Alice",
            "language": "en",
            "music_preferences": ["jazz", "classical"]
          },
          "user2": {
            "name": "Bob",
            "language": "hi",
            "music_preferences": ["bollywood", "rock"]
          }
        }
      }
      ```
   
   ### Alternatives
   
   1. **Manual Profile Selection**
      - Say "Switch to Alice's profile"
      - Simpler but less convenient
   
   2. **App-based Selection**
      - Select profile in mobile/web app
      - More complex setup
   
   ### References
   - Amazon Alexa has "Voice Profiles"
   - Google Home has "Voice Match"
   
   ### Implementation Notes
   Could use libraries like:
   - speechbrain for speaker recognition
   - resemblyzer for voice embeddings

Development Workflow
--------------------

**Branch Naming**

.. code-block:: text

   feature/feature-name    # New features
   fix/bug-description     # Bug fixes
   docs/doc-updates        # Documentation
   refactor/component-name # Code refactoring
   test/test-additions     # Test improvements

**Development Cycle**

::

   Update from upstream
           ↓
   Create feature branch
           ↓
   Make changes (commit often)
           ↓
   Write/update tests
           ↓
   Run tests locally
           ↓
   Update documentation
           ↓
   Push to your fork
           ↓
   Create pull request
           ↓
   Address review feedback
           ↓
   Get approval & merge

**Keeping Your Fork Updated**

.. code-block:: bash

   # Fetch upstream changes
   git fetch upstream
   
   # Update main branch
   git checkout main
   git merge upstream/main
   git push origin main
   
   # Update feature branch (if needed)
   git checkout feature/your-feature
   git rebase main
   git push origin feature/your-feature --force-with-lease

Code Review Guidelines
----------------------

**For Reviewers**

**Be Constructive**

.. code-block:: text

   ❌ "This code is bad"
   ✅ "Consider extracting this into a separate function for clarity"
   
   ❌ "Wrong approach"
   ✅ "Have you considered using X instead? It might be more efficient"

**Ask Questions**

.. code-block:: text

   - "Can you explain why you chose this approach?"
   - "How does this handle the edge case where X?"
   - "Is there a test for the error condition?"

**Provide Examples**

.. code-block:: python

   # Instead of just saying "use type hints"
   # Show example:
   
   # Current:
   def process(data):
       return result
   
   # Suggested:
   def process(data: Dict[str, any]) -> ProcessResult:
       return result

**For Authors**

**Respond Gracefully**

.. code-block:: text

   ✅ "Good point! I'll refactor that."
   ✅ "I chose this because X, but open to alternatives."
   ✅ "Added tests for that case in commit abc123."

**Don't Take It Personally**

- Reviews are about code, not you
- Everyone's code gets reviewed
- Goal is to improve the project

**Ask for Clarification**

.. code-block:: text

   "Can you elaborate on what you mean by 'more robust'?"
   "I'm not sure I understand the concern. Could you provide an example?"

Testing Contributions
---------------------

**Writing Tests**

Tests should go in ``tests/`` directory:

.. code-block:: text

   tests/
   ├── test_speech_recognition.py
   ├── test_intent_classifier.py
   ├── test_audio_engine.py
   └── fixtures/
       ├── sample_audio.wav
       └── test_configs.json

**Test Structure**

.. code-block:: python

   import unittest
   from unittest.mock import Mock, patch
   from vaani_assistant.voice.speech_recognition import SpeechRecognizer
   
   class TestSpeechRecognizer(unittest.TestCase):
       """Test suite for speech recognition."""
       
       def setUp(self):
           """Run before each test."""
           self.recognizer = SpeechRecognizer()
       
       def test_google_recognition_success(self):
           """Test successful recognition with Google API."""
           audio = self._load_test_audio("hello.wav")
           result = self.recognizer.recognize(audio, engine="google")
           self.assertEqual(result, "hello world")
       
       def test_fallback_when_google_fails(self):
           """Test fallback to Vosk when Google unavailable."""
           with patch('speech_recognition.Recognizer.recognize_google',
                      side_effect=Exception("API Error")):
               audio = self._load_test_audio("hello.wav")
               result = self.recognizer.recognize(audio)
               # Should still get result from fallback
               self.assertIsInstance(result, str)
       
       def test_empty_audio_raises_error(self):
           """Test that empty audio raises appropriate error."""
           with self.assertRaises(ValueError):
               self.recognizer.recognize(None)
       
       def _load_test_audio(self, filename):
           """Helper to load test audio files."""
           path = Path("tests/fixtures") / filename
           return AudioFile(path)
       
       def tearDown(self):
           """Run after each test."""
           self.recognizer.cleanup()

**Running Tests**

.. code-block:: bash

   # Run all tests
   pytest tests/
   
   # Run specific test file
   pytest tests/test_speech_recognition.py
   
   # Run specific test
   pytest tests/test_speech_recognition.py::TestSpeechRecognizer::test_google_recognition_success
   
   # Run with coverage
   pytest --cov=vaani_assistant --cov-report=html tests/
   
   # Run verbose
   pytest -v tests/

Documentation Contributions
---------------------------

**Documentation Structure**

.. code-block:: text

   docs/
   ├── index.rst              # Main page
   ├── installation.rst       # Setup guide
   ├── getting_started.rst    # Quick start
   ├── usage.rst              # Detailed usage
   ├── configuration.rst      # Config reference
   ├── architecture.rst       # System design
   └── development/           # Dev docs
       ├── setup.rst
       ├── coding_style.rst
       └── contributing.rst

**Writing Documentation**

Use clear, concise language:

.. code-block:: rst

   Good Practice
   -------------
   
   Brief description of the concept.
   
   **Example**
   
   .. code-block:: bash
   
      # Command with comment
      python3 main.py --verbose
   
   This will start Vaani in verbose mode, showing detailed logs.
   
   **Common Issues**
   
   - Issue 1: Description and solution
   - Issue 2: Description and solution

**Building Documentation Locally**

.. code-block:: bash

   # Install dependencies
   cd docs/
   pip install -r requirements.txt
   
   # Build HTML
   make html
   
   # View in browser
   open _build/html/index.html
   
   # Check for errors
   make clean && make html

Community Guidelines
--------------------

**Code of Conduct**

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

**Communication Channels**

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions
- **Email**: maintainer email for private matters

**Response Times**

- Bug reports: Usually within 48 hours
- Pull requests: Usually within 1 week
- Feature requests: May take longer to discuss

**Recognition**

Contributors are recognized in:

- ``CONTRIBUTORS.md`` file
- Release notes
- Documentation credits page

First-Time Contributors
-----------------------

**Good First Issues**

Look for issues tagged:

- ``good first issue`` - Beginner-friendly
- ``documentation`` - Doc improvements
- ``help wanted`` - Need contributors

**Getting Help**

If you're stuck:

1. Check documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Tag maintainers in your PR

**Learning Resources**

- :doc:`project_structure` - Understand codebase
- :doc:`coding_style` - Learn coding standards
- :doc:`setup` - Set up development environment
- :doc:`../architecture` - Understand system design

Release Process
---------------

**Versioning**

We use Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

Examples:
- ``1.0.0`` → ``1.0.1`` (bug fix)
- ``1.0.1`` → ``1.1.0`` (new feature)
- ``1.1.0`` → ``2.0.0`` (breaking change)

**Release Checklist**

1. Update version in ``__init__.py``
2. Update ``CHANGELOG.md``
3. Run full test suite
4. Build documentation
5. Create git tag
6. Create GitHub release
7. Publish to PyPI (if applicable)

Getting in Touch
----------------

**Maintainer**

- GitHub: @paman7647
- Project: https://github.com/paman7647/vaani

**Reporting Security Issues**

For security vulnerabilities, please email the maintainer directly rather than creating a public issue.

**Thank You**

Your contributions make Vaani better for everyone. We appreciate your time and effort! 🙏
