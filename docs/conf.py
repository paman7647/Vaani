# Configuration file for Sphinx documentation builder.
# Full list of options: https://www.sphinx-doc.org/en/master/config.html

import os
import sys

# Add parent directory to path so we can import Vaani package
sys.path.insert(0, os.path.abspath('..'))

# Verify the path was added correctly (for debugging)
import pathlib
vaani_path = pathlib.Path(__file__).parent.parent / 'Vaani'
if not vaani_path.exists():
    print(f"WARNING: Vaani package not found at {vaani_path}")
else:
    print(f"✓ Vaani package found at {vaani_path}")

project = 'Vaani'
copyright = '2026, Aman Kumar Pandey'
author = 'Aman Kumar Pandey'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_logo = None
html_favicon = None

html_theme_options = {
    'github_url': 'https://github.com/paman7647/vaani',
    'navbar_start': ['navbar-logo'],
    'navbar_center': ['navbar-nav'],
    'navbar_end': ['navbar-icon-links'],
    'secondary_sidebar_items': [],
    'show_nav_level': 2,
}

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
}

# Mock heavy or platform-specific imports during autodoc to avoid build failures
# This prevents import errors when dependencies aren't installed in the docs build environment
autodoc_mock_imports = [
    # Speech and audio
    'pyttsx3',
    'speech_recognition',
    'pyaudio',
    'vosk',
    'pocketsphinx',
    # AI and NLP
    'rapidfuzz',
    'google',
    'google.genai',
    'spacy',
    'textblob',
    # Media and web
    'yt_dlp',
    'vlc',
    'pygame',
    'duckduckgo_search',
    'wikipedia',
    'googlesearch',
    # Utilities
    'bs4',
    'lxml',
    'deep_translator',
    'dotenv',
    'psutil',
    'numpy',
]

# Suppress warnings about missing imports during autosummary
suppress_warnings = ['autosummary']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_attr_annotations = True

# Generate autosummary pages from documented modules/classes
autosummary_generate = True
