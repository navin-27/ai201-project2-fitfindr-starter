import app
import tools
import pytest

from app import handle_query
from utils.data_loader import get_example_wardrobe


def test_handle_query_returns_tuple_of_strings():
    result = handle_query("", "Example wardrobe")
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert all(isinstance(s, str) for s in result)


def test_handle_query_rejects_empty_query():
    result = handle_query("", "Example wardrobe")
    assert result[0]  # first element (listing_text) should have an error message
    assert result[1] == ""
    assert result[2] == ""


def test_handle_query_happy_path(monkeypatch):
    monkeypatch.setattr(tools, "_call_llm", lambda messages, temperature=0.75, max_tokens=250: "Pair it with jeans.")
    result = handle_query("graphic tee under $30", "Example wardrobe")
    assert result[0]  # listing text should be non-empty
    assert result[1]  # outfit suggestion should be non-empty
    assert result[2]  # fit card should be non-empty


def test_handle_query_selects_empty_wardrobe(monkeypatch):
    monkeypatch.setattr(tools, "_call_llm", lambda messages, temperature=0.75, max_tokens=250: "Pair it with neutral basics.")
    result = handle_query("vintage jacket", "Empty wardrobe (new user)")
    assert isinstance(result, tuple)
    assert len(result) == 3
