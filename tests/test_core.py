import pytest

from textprep import Config, lemmatize, normalise, preprocess, tokenize


def test_nfkc_normalisation_joins_ligatures():
    assert normalise("ﬁnance") == "finance"


def test_html_tags_and_entities_are_removed():
    assert normalise("<p>Hello&nbsp;<b>world</b></p>") == "hello world"


def test_script_blocks_are_dropped_whole():
    assert normalise("<script>var x = 1;</script>visible") == "visible"


def test_urls_are_removed():
    assert normalise("see https://example.com/x and www.foo.org now") == "see and now"


def test_tokenize_keeps_internal_apostrophes():
    assert tokenize("Don't stop.") == ["don't", "stop"]


def test_numbers_are_dropped_unless_requested():
    assert tokenize("2024 report") == ["report"]
    assert tokenize("2024 report", keep_numbers=True) == ["2024", "report"]


def test_stopwords_are_removed():
    tokens = preprocess("The study is about the effect of sleep")
    assert "the" not in tokens
    assert "study" in tokens


def test_lemmatiser_handles_plurals_and_gerunds():
    assert lemmatize("studies") == "study"
    assert lemmatize("running") == "run"
    assert lemmatize("cleaned") == "clean"
    assert lemmatize("tokens") == "token"
    assert lemmatize("analysis") == "analysis"


def test_min_token_length_filters_short_tokens():
    tokens = preprocess("a b cd efg", Config(min_token_length=3, remove_stopwords=False))
    assert tokens == ["efg"]


def test_full_pipeline_matches_readme_example():
    text = "<p>The studies were running&nbsp;late.</p>"
    assert preprocess(text) == ["study", "run", "late"]


def test_unknown_config_keys_are_rejected():
    with pytest.raises(ValueError, match="unknown config keys"):
        Config.from_mapping({"lowercase": True, "lower_case": True})


def test_config_round_trip():
    cfg = Config(remove_stopwords=False, min_token_length=4)
    assert Config.from_mapping(cfg.to_dict()) == cfg
