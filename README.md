# FitFindr — Starter Kit

FitFindr is a toolkit for searching secondhand clothing listings, selecting a top thrift find, recommending an outfit from your existing wardrobe, and generating a social-media-ready fit caption.

## Project Structure

```
ai201-project2-fitfindr-starter/
├── agent.py              # Planning loop and session state orchestration
├── app.py                # Gradio UI and query handling
├── tools.py              # search_listings, suggest_outfit, create_fit_card
├── data/                 # mock dataset and wardrobe schema
│   ├── listings.json
│   └── wardrobe_schema.json
├── utils/
│   └── data_loader.py    # helpers to load listings and wardrobes
├── tests/                # unit tests for tools, agent, and app
├── requirements.txt      # Python dependencies
├── planning.md           # design template and specs
└── README.md             # project documentation
```

## Setup

```powershell
cd C:\ai201-project2-fitfindr-starter
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a `.env` file with your Groq API key:

```text
GROQ_API_KEY=your_key_here
```

## How It Works

FitFindr is built around a planning loop that passes state through three tools:

1. `search_listings(description, size, max_price)`
2. `suggest_outfit(new_item, wardrobe)`
3. `create_fit_card(outfit, new_item)`

The planner stores every step in a session dictionary so later tools use the output of earlier tools.

## Tool Inventory

### `search_listings(description, size, max_price)`
- **Inputs**:
  - `description` (str)
  - `size` (str | None)
  - `max_price` (float | None)
- **Returns**: `list[dict]`
- **Purpose**: filters the local `data/listings.json` dataset by keywords, optional size, and optional price, then ranks results by relevance and price.
- **Failure mode**: returns `[]` if no matching items exist.

### `suggest_outfit(new_item, wardrobe)`
- **Inputs**:
  - `new_item` (dict)
  - `wardrobe` (dict)
- **Returns**: `str`
- **Purpose**: asks the Groq LLM to suggest 1–2 outfit combinations using the selected thrifted item and wardrobe contents.
- **Failure mode**: returns a friendly message if it cannot produce a suggestion. If the wardrobe is empty, it offers general styling advice instead of failing.

### `create_fit_card(outfit, new_item)`
- **Inputs**:
  - `outfit` (str)
  - `new_item` (dict)
- **Returns**: `str`
- **Purpose**: asks the Groq LLM for a casual social-media caption that mentions the item, price, platform, and vibe.
- **Failure mode**: returns a descriptive error message if the outfit text is missing or invalid.

## Planning Loop

The planner in `agent.py` follows these steps:

1. Parse the query into `description`, `size`, and `max_price`.
2. Call `search_listings()`.
3. If no search results, stop early and return a helpful error.
4. Set `selected_item` to the top result.
5. Call `suggest_outfit()` using that selected item and the chosen wardrobe.
6. If outfit generation fails, stop early and return an error.
7. Call `create_fit_card()` with the outfit text and selected item.
8. Return the completed session with all state.

This ensures state flows forward, and later tools are not called if earlier steps fail.

## State Management

The session dictionary includes:
- `query`
- `parsed`
- `search_results`
- `selected_item`
- `wardrobe`
- `outfit_suggestion`
- `fit_card`
- `error`

Each tool's output becomes the next tool's input:
- `selected_item` flows into `suggest_outfit()`
- `outfit_suggestion` flows into `create_fit_card()`

## Error Handling

### `search_listings` no-results
Returns:

> "I couldn’t find any listings matching that description, size, or price. Try a broader description, a different size, or a higher max price."

This stops the pipeline before `suggest_outfit()` or `create_fit_card()`.

### Empty wardrobe
`suggest_outfit()` still returns helpful styling advice when the wardrobe is empty.

### Missing outfit text
`create_fit_card()` returns a clear error message string instead of throwing an exception.

## Running the App

```powershell
cd C:\ai201-project2-fitfindr-starter
.\.venv\Scripts\python.exe app.py
```

Open the local URL shown in the terminal.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

All tests should pass if the environment is configured correctly.

## Groq Model

The Groq client uses the supported chat model:
- `llama-3.1-8b-instant`

If this model is deprecated later, update it in `tools.py` inside `_call_llm()`.

## AI Usage

I used AI assistance for two main tasks:

1. **Planning loop implementation**
- Input: the completed `planning.md` spec, the session/state diagram, and `run_agent()` TODO steps.
- Output: code that parses the query, conditionally calls tools, and stores results in the session dict.
- Review: I confirmed it does not call all three tools unconditionally and that it branches correctly on empty `search_results`.

2. **Tool implementation design**
- Input: the tool specs and dataset schema from `utils/data_loader.py`.
- Output: implementations for `search_listings()`, `suggest_outfit()`, and `create_fit_card()`.
- Review: I ensured search filtering works, empty wardrobes are handled, and caption generation gracefully handles missing outfit text.

## Demo Recording Checklist

Record these items in your Loom:

1. Show the repo root and mention you’re using the local venv.
2. Run `python app.py` and open the browser.
3. Enter a happy-path query like: `vintage graphic tee under $30`.
4. Show all three output panels populate.
5. Explain the planning loop: query parsing → search → selected item → outfit → fit card.
6. Trigger one failure mode, such as:
   - `designer ballgown size XXS under $5`
   - or `Empty wardrobe (new user)` with a normal item
7. Call out that the agent stops early on no-results and still returns a helpful message.

## Notes

- The app is built to demonstrate real state passing between tools.
- The `session` dict is the single source of truth for a completed interaction.
- The UX is intentionally simple: one query, one wardrobe choice, and three result panels.
