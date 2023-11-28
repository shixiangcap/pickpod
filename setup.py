#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import setup


# Package meta-data.
NAME = "pickpod"
DESCRIPTION = "Integrated tools to transfer internet audio to text, extract unpopular views, and pick up podcasts for you."
URL = "https://github.com/shixiangcap/pickpod"
EMAIL = "it@shixiangcap.com"
AUTHOR = "shixiangcap"
REQUIRES_PYTHON = ">=3.8.0"
VERSION = "1.0.4"

# What packages are required for this module to be executed?
REQUIRED = [
    "faster_whisper>=0.10.0",
    "opencc-python-reimplemented>=0.1.7",
    "pyannote.audio>=3.0.0",
    "pydub>=0.25.1",
    "torch>=2.0.0",
    "torchaudio>=2.0.0",
    "torchvision>=0.15.0",
    "yt_dlp>=2023.10.7"
]

# What packages are optional?
EXTRAS = {
    "app": ["python-dotenv", "streamlit"],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!


here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README_PYPI.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=["pickpod"],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    zip_safe = True,
    include_package_data=True,
    license="MIT",
    project_urls={
        "Bug Tracker": (
            "https://github.com/shixiangcap/" "pickpod/issues"
        ),
        "Source Code": "https://github.com/shixiangcap/pickpod/",
    },
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
