# Configuration file for the Sphinx documentation builder.

import os
import sys

import tomllib

sys.path.insert(0, os.path.abspath("../src"))


def get_version():
    """Load version from pyproject.toml"""
    pyproject_path = os.path.join(
        os.path.dirname(__file__), "..", "pyproject.toml"
    )
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

        return pyproject_data.get("project", {}).get("version", "unknown")


# -- Project information -----------------------------------------------------

project = "NOAA API"
copyright = "2024, Andreas Sagen"
author = "Andreas Sagen"
version = get_version()

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.coverage",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

os.makedirs("_static", exist_ok=True)

# -- Extension configuration -------------------------------------------------
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# The suffix(es) of source filenames.
source_suffix = {".rst": "restructuredtext"}
