"""Config-driven text preprocessing for research corpora."""

from textprep.core import Config, lemmatize, normalise, preprocess, tokenize

__all__ = ["Config", "lemmatize", "normalise", "preprocess", "tokenize"]
__version__ = "0.1.0"
