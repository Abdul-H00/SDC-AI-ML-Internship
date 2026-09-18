# AI-Assisted Website Quality Auditor — Furniture Websites
**Project:** AI-Assisted Website Quality Auditor for Furniture Websites (Week 2)
**Role:** Member 2 — Individual Contributor
**Tool:** LangChain

## Sites Audited
1. `https://www.ashleyfurniture.com` — Ashley Furniture (large global retail brand)
2. `https://www.wayfair.com` — Wayfair (large online-only home goods retailer)
3. `https://interwood.pk` — Interwood (Pakistan's largest furniture brand)

Chosen deliberately across different scales (global brand, online-only marketplace,
regional retailer) so the audit has a realistic range of scores to compare, not
three near-identical sites.

## Methodology — Facts vs. AI Judgment (the core requirement)

**Step 1 — Automated fact extraction (no AI, no opinion).**
`extract_facts()` in `website_auditor.py` parses each homepage's HTML with
BeautifulSoup and records only things that are objectively true or false:
number of links found, whether a contact form/phone/email is present,
which social platforms are linked, how many CTA buttons exist, and whether
a mobile-viewport meta tag is present. None of this involves an LLM.

**Step 2 — AI-generated judgment (clearly labeled as opinion).**
Those facts (not the raw HTML) are handed to an LLM through a LangChain
LCEL pipeline (`prompt | llm | PydanticOutputParser`). The model is asked
to give a 0-100 professionalism score, list problems/missing
features/recommendations, and set a priority. This step is explicitly an
*opinion informed by facts*, not a fact itself — the output schema and the
report both keep it under a separate "AI-Generated Judgment" heading.

**Step 3 — Structured report.** `run_audit.py` renders a Markdown table +
per-site breakdown: Website → Score → Problems → Missing Features →
Recommendations → Priority, with facts and AI judgment visually separated.

## Run Modes
- **LIVE:** if `OPENAI_API_KEY` is set, the real LangChain chain calls
  `ChatOpenAI` (gpt-4o-mini) for the judgment step.
- **OFFLINE DEMO:** if no key is available, a rule-based fallback fills the
  exact same schema so the pipeline is fully demoable end-to-end. Every
  result logs which mode produced it.
- **Fetching:** the tool tries a live `requests.get()` on each URL first.
  If the network is unavailable (e.g. a sandboxed environment), it falls
  back to a locally cached HTML snapshot in `sample_pages/` for the same
  three URLs, and clearly logs `fetch_source: "cached_fallback"` so this
  is never confused with a live result. On a normal internet-connected
  machine, `fetch_source` will show `"live"`.

## How to Run
```bash
pip install langchain langchain-openai langchain-core pydantic requests beautifulsoup4

# Optional: for real LLM judgment instead of offline demo mode
export OPENAI_API_KEY="your-key-here"

python run_audit.py
```
This prints per-site JSON results to the terminal and writes the final
formatted report to `audit_report.md`.

## Results Summary

| Website | Score | Priority |
|---|---|---|
| ashleyfurniture.com | 100/100 | Low |
| wayfair.com | 55/100 | Medium |
| interwood.pk | 85/100 | Low |

(Full per-site facts, problems, missing features, and recommendations are
in `audit_report.md`.)

## Manual Review of AI Output (required step — at least 2 adjustments)

I reviewed each AI-generated score against my own judgment of the sites
and found two places I'd adjust the automated output:

**1. Ashley Furniture scored 100/100 — I'd adjust this down to ~90.**
The facts show `has_email: false` — no direct email address was detected
anywhere in the homepage HTML, only a phone number. A fully professional
site should expose both channels. The rule-based fallback only checks
"phone OR email" as one combined signal, so it didn't penalize this gap.
A real LLM judgment (or a smarter rule) should treat "phone present but
no email" as a minor deduction, not a free pass to a perfect score. This
also highlights a general limitation: a perfect 100 should be rare — if
an automated tool routinely gives 100/100, that's usually a sign the
checklist itself isn't strict enough, not that the site is flawless.

**2. Wayfair scored 55/100 (Medium priority) — I'd adjust this up to ~75-80.**
Wayfair is one of the largest, most established furniture e-commerce
platforms in the world, and in practice it clearly has contact/help pages,
an active social media presence, and strong mobile support. The low score
here is a **false negative caused by the detection method, not a real
problem with the site**: `extract_facts()` only looks at the raw homepage
HTML fetch, and large sites like Wayfair often load their footer (where
contact links and social icons usually live) via JavaScript after the
initial page load, or paginate/lazy-load content that a simple
`requests.get()` never sees. This is an important, honest limitation to
flag in a real audit tool: a static-HTML-only fetch under-detects features
on JavaScript-heavy sites, and a production version of this tool should
either render the page with a headless browser (e.g. Selenium/Playwright)
or note this caveat explicitly in the report so a reader doesn't take the
score at face value.

**What I'd change next:** add a `js_rendered: bool` flag to the facts
output so the report itself tells the reader whether a low score might be
a detection blind spot vs. a genuine site weakness.

## Error Handling
`audit_website()` validates input before doing any network or AI work:
- Empty string or non-string URL → `{"error": "URL must be a non-empty string."}`
- URL missing `http://`/`https://` → clear invalid-URL error
- Unreachable URL with no cached fallback → `ConnectionError` message
- Malformed AI output (schema mismatch) → caught and reported instead of crashing

Two invalid inputs (`"not-a-real-url"` and `""`) were run through the
pipeline in `run_audit.py` and both returned clean error messages instead
of crashing — see terminal output / screenshots.

## What I Learned
- How to keep an LLM's output strictly separated from factual, code-checked
  data in the same report — labeling matters as much as the code itself.
- How `PydanticOutputParser` forces an LLM to return a specific schema
  (score, missing features, problems, recommendations, priority) instead of
  free-form text that would be fragile to parse.
- Why manually reviewing AI output against your own judgment matters: both
  adjustments above came from noticing the *automated facts* didn't fully
  support the *AI's confidence* in its score — a good auditor (human or AI)
  should be more skeptical of a perfect score and more careful about
  under-detecting on JavaScript-heavy sites.
