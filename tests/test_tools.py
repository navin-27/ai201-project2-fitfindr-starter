import os

import pytest

import tools
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


def test_search_listings_filters_by_description_and_price():
    results = search_listings("graphic tee", max_price=30)
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(item["price"] <= 30 for item in results)


def test_search_listings_filters_by_size():
    results = search_listings("jacket", size="M")
    assert isinstance(results, list)
    assert all("m" in str(item["size"]).lower() for item in results)


def test_search_listings_no_results_returns_empty():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_suggest_outfit_with_empty_wardrobe(monkeypatch):
    monkeypatch.setattr(tools, "_call_llm", lambda messages, temperature=0.75, max_tokens=250: "This item would look great with neutral basics and layered textures.")
    new_item = {
        "title": "Vintage Graphic Tee",
        "category": "tops",
        "price": 22.0,
        "condition": "good",
        "platform": "depop",
        "colors": ["black"],
        "style_tags": ["vintage", "graphic"],
        "description": "A cool thrifted band tee.",
    }
    wardrobe = get_empty_wardrobe()
    result = suggest_outfit(new_item, wardrobe)
    assert isinstance(result, str)
    assert "style" in result.lower() or "pair" in result.lower() or "look" in result.lower()


def test_create_fit_card_rejects_empty_outfit():
    new_item = {"title": "Vintage Graphic Tee", "price": 22.0, "platform": "depop"}
    result = create_fit_card("", new_item)
    assert "couldn’t create a fit card" in result.lower()


def test_create_fit_card_returns_caption(monkeypatch):
    monkeypatch.setattr(tools, "_call_llm", lambda messages, temperature=0.9, max_tokens=200: "Thrifted this vintage graphic tee from Depop and paired it with my favorite jeans for an effortless streetwear look.")
    new_item = {"title": "Vintage Graphic Tee", "price": 22.0, "platform": "depop", "category": "tops", "colors": ["black"], "style_tags": ["vintage"]}
    result = create_fit_card("Pair it with your favorite jeans for a vintage street look.", new_item)
    assert isinstance(result, str)
    assert "depop" in result.lower()
    assert "vintage" in result.lower() or "street" in result.lower()
