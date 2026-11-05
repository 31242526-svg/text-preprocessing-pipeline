"""Normalisation, tokenisation and lemmatisation with an explicit, serialisable config."""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import asdict, dataclass, fields

STOPWORDS = frozenset(
    """
    a about above after again against all am an and any are as at be because been before
    being below between both but by can could did do does doing down during each few for
    from further had has have having he her here hers herself him himself his how i if in
    into is it its itself just me more most my myself no nor not now of off on once only
    or other our ours ourselves out over own same she should so some such than that the
    their theirs them themselves then there these they this those through to too under
    until up very was we were what when where which while who whom why will with would you
    your yours yourself yourselves
    """.split()
)

# Plurals that end in "s" but are not plurals. Stripping them corrupts the token.
LEMMA_EXCEPTIONS = frozenset(
    """
    analysis basis bias business canvas class corpus diagnosis emphasis gas hypothesis
    mathematics news physics research series species status synthesis thesis
    """.split()
)

HTML_BREAK = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")
URL = re.compile(r"(?:https?://\S+|www\.\S+)", re.IGNORECASE)
WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class Config:
    lowercase: bool = True
    strip_html: bool = True
    remove_urls: bool = True
    remove_stopwords: bool = True
    lemmatize: bool = True
    min_token_length: int = 2
    keep_numbers: bool = False

    @classmethod
    def from_mapping(cls, data: dict | None) -> Config:
        """Build a config, rejecting unknown keys so typos cannot change results."""
        known = {f.name for f in fields(cls)}
        unknown = set(data or {}) - known
        if unknown:
            raise ValueError(f"unknown config keys: {', '.join(sorted(unknown))}")
        return cls(**(data or {}))

    def to_dict(self) -> dict:
        return asdict(self)


def normalise(text: str, cfg: Config | None = None) -> str:
    """Unicode-normalise, optionally strip HTML and URLs, collapse whitespace."""
    cfg = cfg or Config()
    text = unicodedata.normalize("NFKC", text)
    if cfg.strip_html:
        text = HTML_BREAK.sub(" ", text)
        text = html.unescape(HTML_TAG.sub(" ", text))
    if cfg.remove_urls:
        text = URL.sub(" ", text)
    text = text.replace("\u00a0", " ").replace("\u2019", "'")
    text = WHITESPACE.sub(" ", text).strip()
    if cfg.lowercase:
        text = text.lower()
    return text


def tokenize(text: str, *, keep_numbers: bool = False) -> list[str]:
    """Split on word characters, keeping internal apostrophes (don't, l'ensemble)."""
    pattern = r"[A-Za-z0-9]+(?:'[A-Za-z]+)?" if keep_numbers else r"[A-Za-z]+(?:'[A-Za-z]+)?"
    tokens = re.findall(pattern, text)
    return [t.lower() for t in tokens]


def lemmatize(token: str) -> str:
    """Light, deterministic English lemmatiser (plurals, -ing, -ed)."""
    if token in LEMMA_EXCEPTIONS or len(token) <= 3 or not token.isalpha():
        return token
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("sses"):
        return token[:-2]
    for suffix in ("ing", "ed"):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            stem = token[: -len(suffix)]
            if len(stem) >= 3 and stem[-1] == stem[-2]:
                stem = stem[:-1]
            return stem
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        return token[:-1]
    return token


def preprocess(text: str, cfg: Config | None = None) -> list[str]:
    """Full pipeline for one document or line."""
    cfg = cfg or Config()
    cleaned = normalise(text, cfg)
    tokens = [t for t in tokenize(cleaned, keep_numbers=cfg.keep_numbers)]
    tokens = [t for t in tokens if len(t) >= cfg.min_token_length]
    if cfg.remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    if cfg.lemmatize:
        tokens = [lemmatize(t) for t in tokens]
    return tokens
