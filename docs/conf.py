# Configuration file for Sphinx documentation builder.
# Full list of options: https://www.sphinx-doc.org/en/master/config.html

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

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
autodoc_mock_imports = [
    'pyttsx3',
    'speech_recognition',
    'pyaudio',
    'vosk',
    'pocketsphinx',
    'rapidfuzz',
    'google',
    'google.genai',
    'yt_dlp',
    'vlc',
    'pygame',
    'duckduckgo_search',
    'wikipedia',
    'bs4',
    'lxml',
    'deep_translator',
    'dotenv',
    'psutil',
    'numpy',
    'spacy',
    'textblob',
    'googlesearch',
]

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
