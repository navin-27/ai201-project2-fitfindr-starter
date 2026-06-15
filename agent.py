"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import re

from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    description = query.strip()
    size = None
    max_price = None

    price_match = re.search(
        r"(?:under|below|less than|up to|<=|<)\s*\$?\s*(\d+(?:\.\d+)?)",
        query,
        re.IGNORECASE,
    )
    price_text = None
    if price_match:
        price_text = price_match.group(0)
        max_price = float(price_match.group(1))
    else:
        money_match = re.search(r"\$\s*(\d+(?:\.\d+)?)", query)
        if money_match:
            price_text = money_match.group(0)
            max_price = float(money_match.group(1))

    size_match = re.search(r"(?:size|sz)\s*([A-Za-z0-9\-/+]+)", query, re.IGNORECASE)
    if size_match:
        size = size_match.group(1).strip()

    cleaned = description
    if size:
        cleaned = re.sub(rf"(?:size|sz)\s*{re.escape(size)}", "", cleaned, flags=re.IGNORECASE)
    if price_text:
        cleaned = re.sub(re.escape(price_text), "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[,$]", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)

    if cleaned:
        description = cleaned

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


def _is_tool_error(text: str) -> bool:
    lower = text.strip().lower()
    return (
        not lower
        or "i couldn’t" in lower
        or "i couldn't" in lower
        or "i could not" in lower
        or "please try again" in lower
    )


def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.
    """
    session = _new_session(query, wardrobe)
    parsed = _parse_query(query)
    session["parsed"] = parsed

    search_results = search_listings(
        description=parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )
    session["search_results"] = search_results

    if not search_results:
        session["error"] = (
            "I couldn’t find any listings matching that description, size, or price. "
            "Try a broader description, a different size, or a higher max price."
        )
        return session

    selected_item = search_results[0]
    session["selected_item"] = selected_item

    outfit_suggestion = suggest_outfit(selected_item, wardrobe)
    if _is_tool_error(outfit_suggestion):
        session["error"] = (
            "I found a matching item, but I couldn’t generate an outfit suggestion right now. "
            "Please try again later."
        )
        return session
    session["outfit_suggestion"] = outfit_suggestion

    fit_card = create_fit_card(outfit_suggestion, selected_item)
    if _is_tool_error(fit_card):
        session["error"] = (
            "I found a matching item and outfit suggestion, but I couldn’t create a fit card right now. "
            "Please try again later."
        )
        return session
    session["fit_card"] = fit_card

    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
