# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
Searches the local mock listings dataset for secondhand clothing items that match a user description, size request, and maximum price.

**Input parameters:**
- `description` (str): a short text query describing the desired item (for example "vintage graphic tee" or "navy track jacket").
- `size` (str | None): the preferred garment size, such as "M", "S/M", or "W30". If omitted, the tool matches any size.
- `max_price` (float | None): the top price the user will pay. If omitted, all price points are allowed.

**What it returns:**
A list of listing dictionaries, sorted by relevance and then price, where each listing includes:
- `id` (str)
- `title` (str)
- `description` (str)
- `category` (str)
- `style_tags` (list[str])
- `size` (str)
- `condition` (str)
- `price` (float)
- `colors` (list[str])
- `brand` (str | None)
- `platform` (str)

**What happens if it fails or returns nothing:**
If the search returns no results, the agent stops the pipeline and returns a friendly message telling the user to broaden the description, try a different size, or increase the price limit.

---

### Tool 2: suggest_outfit

**What it does:**
Uses a selected new listing and the user’s wardrobe data to generate a compatible outfit recommendation.

**Input parameters:**
- `new_item` (dict): the top matching listing selected from `search_listings`.
- `wardrobe` (dict): a wardrobe object containing an `items` list, where each item has `id`, `name`, `category`, `colors`, `style_tags`, and optional `notes`.

**What it returns:**
A dictionary containing:
- `suggested_items` (list[dict]): the wardrobe pieces chosen to complement the new listing.
- `outfit_text` (str): a natural-language recommendation describing how to wear the new item with the selected wardrobe pieces.

**What happens if it fails or returns nothing:**
If the wardrobe is empty or no suitable outfit can be formed, the agent returns a clear message asking the user to add wardrobe items or choose a different listing.

---

### Tool 3: create_fit_card

**What it does:**
Generates a short fit-card caption and supporting text that presents the new item and suggested outfit in a social-media-ready format.

**Input parameters:**
- `outfit` (dict): the object returned by `suggest_outfit`, containing `suggested_items` and `outfit_text`.
- `new_item` (dict): the selected listing being styled.

**What it returns:**
A dictionary containing:
- `headline` (str): a concise caption or fit-card headline.
- `details` (str): a short social-style description referencing the new item's price, platform, and styling.

**What happens if it fails or returns nothing:**
If input is missing or incomplete, the agent returns an error response asking the user to retry with a valid selected item and outfit suggestion.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
The planner parses the user’s request into search inputs and then runs `search_listings()` first. If the search returns results, it selects the top listing and proceeds to `suggest_outfit()`. If that tool returns a valid outfit, the planner calls `create_fit_card()` and returns the assembled result. If any step fails, the planner stops early and returns a specific error or recovery message.

---

## State Management

**How does information from one tool get passed to the next?**
The session tracks the parsed search query, the `search_results`, the `selected_item`, the current `wardrobe`, the `outfit_suggestion`, and the final `fit_card`. Each tool’s output becomes the next tool’s input: `selected_item` flows into `suggest_outfit`, and both `outfit_suggestion` and `selected_item` flow into `create_fit_card`.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Return: "I couldn’t find any listings matching that description, size, or price. Try a broader description, a different size, or a higher max price." |
| suggest_outfit | Wardrobe is empty | Return: "I found a good item, but your wardrobe doesn’t have matching pieces yet. Add items to your wardrobe and I can suggest a complete outfit." |
| create_fit_card | Outfit input is missing or incomplete | Return: "I couldn’t create a fit card because the outfit details are incomplete. Please try again with a selected item and outfit suggestion." |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

## AI Tool Plan

**Milestone 3 — Individual tool implementations:**
- Use Copilot or ChatGPT with the completed `Tool 1`, `Tool 2`, and `Tool 3` blocks.
- Provide `search_listings` the tool spec plus the `utils/data_loader.py` helper functions and the `listings.json` schema.
- Ask the AI to implement filtering by query text, size, and max price, to return sorted matches, and to handle empty results.
- Verify by inspecting the generated code for explicit filter conditions and running tests against at least three search queries.
- Then implement `suggest_outfit` with the tool spec and the wardrobe schema, asking for compatible wardrobe selection and a clear `outfit_text` structure.
- Finally implement `create_fit_card` with the tool spec, expecting a concise `headline` and `details` output.

**Milestone 4 — Planning loop and state management:**
- Use Copilot or ChatGPT with the `Planning Loop`, `State Management`, `Error Handling`, and `Architecture` sections.
- Ask the AI to write a planner function that parses a user query, invokes each tool in order, handles early exit on failure, and returns a final structured response.
- Verify by checking the planner code for the exact branch logic and by running an example query through it.

---

## A Complete Interaction (Step by Step)

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
The planner parses the query into `description = "vintage graphic tee"`, `size = "M"`, and `max_price = 30.0`, then calls `search_listings(description, size, max_price)`.

**Step 2:**
`search_listings` returns matching listings sorted by relevance and price. The planner selects the top result as `selected_item`, for example a vintage band tee priced at $22.

**Step 3:**
The planner calls `suggest_outfit(new_item=selected_item, wardrobe=get_example_wardrobe())`. That tool returns `suggested_items` and `outfit_text`, recommending pieces like wide-leg jeans and chunky sneakers.

**Step 4:**
The planner calls `create_fit_card(outfit=outfit_result, new_item=selected_item)`. That tool returns a shareable caption and details describing the new item and styling.

**Final output to user:**
A single response combining the search result, styling recommendation, and fit card, for example:
- "I found a vintage graphic tee for $22 on Depop. Pair it with your wide-leg jeans and chunky sneakers for a relaxed 90s streetwear look."
- Fit card: "Thrifted this faded band tee off Depop for $22 — perfect with my baggy jeans and chunky sneakers."

