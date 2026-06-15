import agent
import tools
import pytest

from agent import run_agent, _parse_query
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


def test_parse_query_extracts_description():
    parsed = _parse_query("vintage graphic tee")
    assert "graphic" in parsed["description"].lower() or "vintage" in parsed["description"].lower()
    assert parsed["size"] is None
    assert parsed["max_price"] is None


def test_parse_query_extracts_price():
    parsed = _parse_query("jacket under $50")
    assert parsed["max_price"] == 50.0


def test_parse_query_extracts_size():
    parsed = _parse_query("size M jacket")
    assert parsed["size"] == "M"


def test_parse_query_extracts_all():
    parsed = _parse_query("vintage tee size L under $30")
    assert "vintage" in parsed["description"].lower() or "tee" in parsed["description"].lower()
    assert parsed["size"] == "L"
    assert parsed["max_price"] == 30.0


def test_run_agent_happy_path(monkeypatch):
    monkeypatch.setattr(tools, "_call_llm", lambda messages, temperature=0.75, max_tokens=250: "Pair it with your favorite jeans.")
    session = run_agent("graphic tee under $30", get_example_wardrobe())
    assert session["error"] is None
    assert session["selected_item"] is not None
    assert session["outfit_suggestion"] is not None
    assert session["fit_card"] is not None


def test_run_agent_no_results():
    session = run_agent("designer ballgown size XXS under $5", get_example_wardrobe())
    assert session["error"] is not None
    assert "couldn" in session["error"].lower()
