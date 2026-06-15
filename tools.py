"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


def _normalize_text(text: str) -> list[str]:
    tokens = [token.lower() for token in re.findall(r"\w+", text)]
    return [token for token in tokens if len(token) > 1]


def _score_listing(listing: dict, query_tokens: list[str]) -> int:
    fields = []
    fields.append(listing.get("title", ""))
    fields.append(listing.get("description", ""))
    fields.append(listing.get("category", ""))
    fields.extend(listing.get("style_tags", []))
    fields.extend(listing.get("colors", []))
    brand = listing.get("brand")
    if brand:
        fields.append(brand)

    combined = " ".join(str(value).lower() for value in fields)
    score = 0
    for token in query_tokens:
        if token in combined:
            score += 1
    return score


def _call_llm(messages: list[dict], temperature: float = 0.75, max_tokens: int = 250) -> str:
    client = _get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    if not response.choices:
        return ""
    choice = response.choices[0]
    content = getattr(choice.message, "content", None)
    if not content:
        return ""
    return content.strip()


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.
    """
    listings = load_listings()
    normalized_description = description or ""
    query_tokens = _normalize_text(normalized_description)

    results = []
    for listing in listings:
        if max_price is not None and listing.get("price", float("inf")) > max_price:
            continue

        listing_size = str(listing.get("size", "")).lower()
        if size:
            size_query = size.strip().lower()
            if size_query not in listing_size:
                continue

        score = _score_listing(listing, query_tokens)
        if not query_tokens:
            score = 1
        if score <= 0:
            continue

        results.append((score, listing.get("price", 0.0), listing))

    results.sort(key=lambda item: (-item[0], item[1]))
    return [listing for _, _, listing in results]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.
    """
    wardrobe_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []

    item_details = [
        f"title: {new_item.get('title', 'Unknown')}",
        f"category: {new_item.get('category', 'Unknown')}",
        f"price: ${new_item.get('price', '')}",
        f"condition: {new_item.get('condition', '')}",
        f"platform: {new_item.get('platform', '')}",
        f"colors: {', '.join(new_item.get('colors', []))}",
        f"style_tags: {', '.join(new_item.get('style_tags', []))}",
        f"description: {new_item.get('description', '')}",
    ]
    item_summary = "\n".join(item_details)

    if not wardrobe_items:
        system_prompt = "You are a fashion assistant providing general outfit advice for a new thrifted item."
        user_prompt = (
            "The user is considering buying this item:\n"
            f"{item_summary}\n\n"
            "Offer general styling advice for this item, including what kinds of pieces would pair well with it and the overall vibe."
        )
    else:
        wardrobe_lines = []
        for item in wardrobe_items:
            wardrobe_lines.append(
                f"- {item.get('name', 'Unknown')} ({item.get('category', 'Unknown')}), colors: {', '.join(item.get('colors', []))}, style_tags: {', '.join(item.get('style_tags', []))}, notes: {item.get('notes', '')}"
            )
        wardrobe_block = "\n".join(wardrobe_lines)
        system_prompt = (
            "You are a fashion assistant suggesting specific outfit combinations. "
            "Use the new thrifted item together with pieces from the user's wardrobe."
        )
        user_prompt = (
            "The user is considering buying this item:\n"
            f"{item_summary}\n\n"
            "The user's wardrobe contains these items:\n"
            f"{wardrobe_block}\n\n"
            "Suggest 1-2 outfit combinations using the new item and named wardrobe pieces. "
            "Mention which wardrobe items to pair, and describe the resulting look."
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    result = _call_llm(messages, temperature=0.75, max_tokens=250)
    return result or "I couldn’t generate an outfit suggestion right now. Please try again." 


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.
    """
    if not outfit or not outfit.strip():
        return (
            "I couldn’t create a fit card because the outfit details are incomplete. "
            "Please try again with a selected item and outfit suggestion."
        )

    item_name = new_item.get("title", "this item")
    item_price = new_item.get("price")
    item_platform = new_item.get("platform", "the platform")
    item_info = [
        f"title: {item_name}",
        f"price: ${item_price}" if item_price is not None else "price: unknown",
        f"platform: {item_platform}",
        f"category: {new_item.get('category', '')}",
        f"colors: {', '.join(new_item.get('colors', []))}",
        f"style_tags: {', '.join(new_item.get('style_tags', []))}",
    ]
    item_summary = "\n".join(item_info)

    system_prompt = (
        "You are a fashion copywriter creating a casual, authentic fit card caption. "
        "Use the item details and suggested outfit to write a short social media caption."
    )
    user_prompt = (
        "Write a 2-4 sentence Instagram/TikTok style caption for this thrifted find. "
        "Mention the item name, price, and platform naturally once, and describe the outfit vibe. "
        "Use a casual, authentic tone as if the user is sharing a new look.\n\n"
        "Item details:\n"
        f"{item_summary}\n\n"
        "Outfit suggestion:\n"
        f"{outfit}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    result = _call_llm(messages, temperature=0.9, max_tokens=200)
    return result or (
        "I couldn’t create a fit card because the outfit details are incomplete. "
        "Please try again with a selected item and outfit suggestion."
    )
