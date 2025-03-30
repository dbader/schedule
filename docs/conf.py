import os
import sys
from sphinx.application import Sphinx

# Ensure the project root is in the system path
sys.path.insert(0, os.path.abspath(".."))

# Sphinx extensions for documentation generation
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
]

# Path configurations
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

# Project information
project = "Schedule"
copyright = "2020, Daniel Bader"
author = "Daniel Bader"

# Versioning
version = "1.2.2"
release = "1.2.2"

# Language settings
language = "en"

# Exclude specific files and directories from the build process
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Include TODO notes in the output
todo_include_todos = True

# HTML output configurations
html_theme = "alabaster"
html_theme_options = {
    "show_powered_by": False,
    "github_user": "dbader",
    "github_repo": "schedule",
    "github_banner": True,
    "github_button": True,
    "github_type": "star",
    "show_related": False,
}

# Static files path
html_static_path = ["_static"]
html_use_smartypants = True

# Sidebar configuration
html_sidebars = {
    "**": [
        "about.html",
        "globaltoc.html",
        "sidebarintro.html",
        "relations.html",
        "searchbox.html",
    ],
}

# Visibility settings
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True

# Documentation output name
htmlhelp_basename = "schedule_doc"

# LaTeX output configuration
latex_elements = {}
latex_documents = [
    (
        master_doc,
        "schedule.tex",
        "Schedule Documentation",
        "Daniel Bader",
        "manual",
    ),
]

# Man page output
man_pages = [(master_doc, "schedule", "Schedule Documentation", [author], 1)]

# Texinfo output
texinfo_documents = [
    (
        master_doc,
        "schedule",
        "Schedule Documentation",
        author,
        "schedule",
        "Comprehensive documentation for the Schedule module.",
        "Miscellaneous",
    ),
]

# Autodoc settings
autodoc_member_order = "bysource"
suppress_warnings = ["image.nonlocal_uri"]
