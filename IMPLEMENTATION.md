# FitFindr Implementation — Quick Reference

## ✓ Completed Milestone 3 & 4

### Milestone 3: Individual Tool Implementations
- **tools.py** — All 3 required tools implemented and tested:
  - `search_listings()`: Filters mock listings by description/size/price
  - `suggest_outfit()`: LLM-powered outfit suggestions (handles empty wardrobe)
  - `create_fit_card()`: LLM-powered social media captions
  - Helper functions: `_normalize_text()`, `_score_listing()`, `_call_llm()`, `_get_groq_client()`

### Milestone 4: Planning Loop & State Management
- **agent.py** — Planning loop with early error exits:
  - `run_agent()`: Orchestrates search → suggest → fit card
  - `_parse_query()`: Regex-based extraction of description/size/max_price
  - `_new_session()`: State tracking through the pipeline
  - Error handling at each step with descriptive messages

### Bonus: Gradio UI + App Layer
- **app.py** — Full UI integration:
  - `handle_query()`: Connects Gradio form to agent
  - `build_interface()`: 3-panel layout (listing + outfit + fit card)
  - Example queries for testing

### Testing: 16 Tests, All Passing
- **tests/test_tools.py** (6 tests): Search, outfit, fit card behavior
- **tests/test_agent.py** (6 tests): Query parsing and planning loop
- **tests/test_app.py** (4 tests): Gradio integration
- All LLM calls mocked to avoid API costs during testing

---

## Running the Application

### Prerequisites
```bash
# Ensure .env has your Groq API key
cat .env  # Should contain: GROQ_API_KEY=your_key_here
```

### Start Gradio UI (localhost:7860)
```bash
python app.py
```
Then open http://localhost:7860 in your browser.

### Test Everything
```bash
pytest tests/ -q
```

### Example Queries to Try
- "vintage graphic tee under $30"
- "90s track jacket in size M"
- "flowy midi skirt under $40"
- "black combat boots size 8"
- "designer ballgown size XXS under $5" (deliberate no-results test)

---

## How It Works

### Query → Results Pipeline
```
User: "vintage band tee size M under $25"
         ↓
Parse: description="vintage band tee", size="M", max_price=25.0
         ↓
Search: Find 7 listings matching query (sorted by relevance + price)
         ↓
Select: Top result = "Y2K Baby Tee – Butterfly Print" ($18)
         ↓
Outfit: LLM suggests 1-2 outfits using wardrobe + new item
         ↓
Caption: LLM generates Instagram-style fit card
         ↓
UI Panels:
  🛍️ Listing: Title, Price, Condition, Colors, Description
  👗 Outfit: "Pair with your wide-leg jeans for 90s vibes..."
  ✨ Caption: "Thrifted this butterfly tee for $18 on Depop..."
```

### Error Handling
- No search results → "I couldn't find any listings... try a broader description"
- LLM fails on outfit → "I found a matching item, but couldn't generate outfit... try again later"
- LLM fails on caption → Early exit with error message
- Empty query → Guard check in `handle_query()`

---

## Key Implementation Choices

1. **Regex Query Parsing**: Fast, deterministic; works without LLM call
2. **Keyword Scoring**: Simple but effective; searches title + desc + tags + colors
3. **Empty Description Support**: Valid use case (e.g., "size M under $50" → all small items under $50)
4. **Session State Dict**: Single source of truth for the entire request flow
5. **Early Exit Pattern**: Stop immediately if any step fails; don't propagate None/empty
6. **LLM Mocking in Tests**: All tests pass without requiring a real API key
7. **Gradio UI**: Pre-built layout with examples; no custom CSS needed

---

## File Structure
```
c:\ai201-project2-fitfindr-starter\
├── tools.py              # 3 tools + helper functions (170 lines)
├── agent.py              # Planning loop + state mgmt (150 lines)
├── app.py                # Gradio UI + handler (100 lines)
├── requirements.txt      # groq, python-dotenv, gradio, pytest
├── .env                  # GROQ_API_KEY=...
├── tests/
│   ├── test_tools.py     # 6 tests
│   ├── test_agent.py     # 6 tests
│   └── test_app.py       # 4 tests
├── data/
│   ├── listings.json     # 40 mock items
│   └── wardrobe_schema.json
└── utils/
    └── data_loader.py    # load_listings(), get_example_wardrobe(), etc.
```

---

## Next Steps (Stretch Features)
- [ ] Use semantic embeddings for better search matching
- [ ] Add image upload for wardrobe items
- [ ] Cache fit cards to avoid duplicate LLM calls
- [ ] Add user authentication + persistent wardrobe storage
- [ ] Implement multi-turn conversation (refine suggestions)
- [ ] Add price trend analysis across platforms
- [ ] Support size conversion (US ↔ EU ↔ UK)
