Contributing to Vaani
======================

Thank you for your interest in improving Vaani. Contributions of all types are welcome.

Before Contributing
-------------------

**This project is primarily maintained by its creator.** While contributions are welcome, understand:

- Response times may vary
- Not all suggestions will be accepted
- The vision and direction are set by the creator
- Major features should be discussed in issues first

This doesn't mean we don't appreciate you—it means we want to be realistic about capacity.

Ways to Contribute
------------------

**Report Issues**

Found a bug or have a feature idea? Create an issue:

1. Check if the issue already exists
2. Provide clear reproduction steps
3. Include your system info (OS, Python version)
4. Attach relevant log output

**Improve Documentation**

Documentation improvements are always welcome:

- Fix typos and unclear sections
- Add examples to existing docs
- Document undocumented behaviors
- Improve installation guides for your platform

**Small Bug Fixes**

Small, focused bug fixes are ideal for first contributions:

- One fix per pull request
- Include test case if possible
- Update documentation if behavior changes

**Code Quality**

Improvements that don't add features:

- Refactoring for clarity
- Performance improvements with measurements
- Test coverage additions
- Dependency updates

Setup for Contributing
----------------------

**Clone and Install**

.. code-block:: bash

   git clone https://github.com/paman7647/Vaani.git
   cd Vaani
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-full.txt
   pip install black flake8

**Verify Your Setup**

.. code-block:: bash

   # Test the installation
   python3 main.py
   
   # Check code quality tools work
   black --version
   flake8 --version

**Create a Feature Branch**

.. code-block:: bash

   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-you-fixed

Branch naming:
- ``feature/`` - New features
- ``fix/`` - Bug fixes
- ``docs/`` - Documentation only
- ``refactor/`` - Code improvements

Making Changes
--------------

**Follow the Style Guide**

See :doc:`coding_style` for detailed guidelines.

**Keep Changes Focused**

.. code-block:: bash

   # Good - one fix
   git commit -m "Fix timeout error in speech recognition"
   
   # Okay - related changes
   git commit -m "Add timeout configuration and improve error handling"
   
   # Bad - multiple unrelated changes
   git commit -m "Fix timeout, update docs, refactor audio player"

**Write Clear Commit Messages**

.. code-block:: text

   [Brief description - 50 chars max]
   
   [Longer explanation if needed]
   
   - Why this change?
   - What problem does it solve?
   - Any side effects or considerations?

**Example**

.. code-block:: text

   Fix timeout error in speech recognition module
   
   The speech recognition module was not respecting the timeout
   parameter when connecting to the audio device, causing hangs
   on systems with slow audio hardware.
   
   - Add timeout to device initialization
   - Test with different timeout values
   - Update documentation with timeout guidance

**Test Your Changes**

.. code-block:: bash

   # Run the code you changed
   python3 main.py
   
   # Check code style
   black vaani_assistant/
   flake8 vaani_assistant/ --max-line-length=100
   
   # If you changed a specific module:
   python3 << 'EOF'
   from vaani_assistant.core.your_module import YourClass
   obj = YourClass()
   # Test it
   EOF

**Update Documentation**

If your change affects behavior or adds features:

.. code-block:: bash

   # Update relevant .rst files in docs/
   # Run Sphinx to check it builds
   cd docs
   make html
   cd ..

**Add Docstrings**

Every new function should have a docstring:

.. code-block:: python

   def new_function(parameter: int) -> str:
       """
       Brief one-line description.
       
       Longer description of what it does and why you'd use it.
       
       Args:
           parameter: What it represents.
       
       Returns:
           What gets returned.
       
       Raises:
           ValueError: When something is invalid.
       """
       pass

Creating a Pull Request
-----------------------

**Before Submitting**

Checklist:

- [ ] Code follows :doc:`coding_style` guidelines
- [ ] Changes are tested and working
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No unrelated changes in the branch
- [ ] Feature branch is rebased to latest main

**Creating the PR**

1. Push your branch: ``git push origin feature/your-feature-name``
2. Create a PR on GitHub
3. Fill out the PR template completely
4. Reference any related issues: "Fixes #123"

**PR Template**

.. code-block:: markdown

   ## Description
   
   What does this PR do?
   
   ## Type of Change
   
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring
   - [ ] Dependency update
   
   ## How to Test
   
   Steps to verify the change works.
   
   ## Related Issues
   
   Fixes #123
   
   ## Screenshots
   
   If applicable, add screenshots.
   
   ## Checklist
   
   - [ ] Code follows style guidelines
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] No new warnings

**What Gets Reviewed**

PRs are reviewed for:

- Code correctness
- Alignment with project vision
- Code quality and style
- Documentation completeness
- Test coverage
- Performance impact

**After Submission**

You'll get feedback. Common types:

- **Requests for changes** - Usually phrased as questions, refactor code
- **Suggestions** - Nice to have but not required
- **Concerns** - Changes needed before merge

Address feedback by pushing new commits to your branch—the PR updates automatically.

Common Scenarios
----------------

**"I want to add X feature"**

1. Create an issue describing the feature first
2. Discuss approach with maintainers
3. Get agreement on design
4. Implement with confidence

**"I found a bug"**

1. Create an issue with reproduction steps
2. If you can fix it, create a PR
3. Link the PR to the issue

**"I want to update documentation"**

1. Create a PR directly (no issue needed)
2. Make one logical change per PR
3. Improve clarity and examples

**"I want to refactor a module"**

1. Create an issue explaining why
2. Get feedback before investing time
3. Keep refactoring separate from feature PRs

**"The project doesn't build on my system"**

1. Create an issue with:
   - Your OS and version
   - Python version
   - Full error message
   - Steps to reproduce
2. We'll work through it together
3. Documentation might need updating

Development Workflow Example
----------------------------

**Scenario: Fix a speech recognition timeout bug**

.. code-block:: bash

   # 1. Create an issue (if not already done)
   # "Speech recognition hangs on slow audio devices"
   
   # 2. Set up your branch
   git checkout -b fix/speech-recognition-timeout
   
   # 3. Reproduce the bug
   python3 main.py
   # Confirms: hangs when audio device is slow
   
   # 4. Find and fix the issue
   vim vaani_assistant/core/speech_recognition.py
   # Add timeout parameter to device initialization
   
   # 5. Test the fix
   python3 main.py
   # Test with: "Hey Aria, what time is it?"
   # Confirms: no hang, works correctly
   
   # 6. Verify code quality
   black vaani_assistant/core/speech_recognition.py
   flake8 vaani_assistant/core/speech_recognition.py
   
   # 7. Update documentation
   vim docs/troubleshooting.rst
   # Add section about timeout configuration
   
   # 8. Commit
   git add vaani_assistant/core/speech_recognition.py
   git add docs/troubleshooting.rst
   git commit -m "Fix speech recognition timeout on slow audio devices
   
   The speech recognition module was not respecting timeouts
   on slow audio devices, causing the system to hang.
   
   - Add timeout parameter to audio device initialization
   - Default to 10 seconds, configurable via settings
   - Document timeout configuration in troubleshooting guide"
   
   # 9. Push and create PR
   git push origin fix/speech-recognition-timeout

Getting Help
------------

**Questions About Code**

- Comment in the issue you're working on
- Check the :doc:`../architecture` documentation
- Look at the :doc:`project_structure` for module details
- Read existing code in the same module

**Questions About Contributing**

- Create an issue labeled "question"
- Check CONTRIBUTING.md in the repo
- Look for similar PRs to see what was accepted

**Something Not Working**

.. code-block:: bash

   # Enable debug logging
   LOG_LEVEL=DEBUG python3 main.py
   
   # Check error logs
   tail -100 logs/error.log
   
   # Try a simple test
   python3 << 'EOF'
   from vaani_assistant.core import your_module
   your_module.test_function()
   EOF

Code of Conduct
---------------

We are committed to providing a welcoming and inspiring community for all. Be respectful.

Recognition
-----------

Contributors to Vaani are recognized in:

- The README.md file
- Release notes for their contributions
- Git history (forever!)

See :doc:`../credits` for the current list.

Legal
-----

By contributing to Vaani, you agree that:

- Your contributions can be used under the project's license
- You have the right to grant these rights
- You won't contribute code you don't have rights to

No contributor agreement needed—just contribute!

Summary
-------

1. **Pick something** to work on (from issues or your own idea)
2. **Discuss** if it's a major change
3. **Make changes** following :doc:`coding_style`
4. **Test thoroughly** and check code quality
5. **Create a PR** with clear description
6. **Respond to feedback** and iterate
7. **Celebrate** when it merges! 🎉

Questions?
----------

- Create an issue on GitHub
- Check existing issues/discussions
- Email the maintainer (see README.md)

Thank you for contributing to Vaani!
