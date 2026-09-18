# AI Lead Qualification Bot — LangChain Component
**Project:** AI Lead Qualification Bot for a Retail Chain
**Role:** Member 2 — Individual Contributor
**Tool:** LangChain

## Mini-Plan
My piece of the project is the **Lead Scoring Engine**: given one raw customer
message (from chat/web-form), extract structured buying signals using LangChain,
then convert those signals into a final **Hot / Warm / Cold** label with a
one-line reason. This runs standalone and can be plugged into whatever
front-end / API the rest of the group builds.

## Approach
1. **PromptTemplate** — `ChatPromptTemplate` wraps the raw customer message
   into a consistent instruction to the model, so the same prompt structure
   is reused for every lead instead of writing a new string each time.
2. **Structured output (`PydanticOutputParser`)** — Instead of trusting the
   model to always reply in the same free-text format, a `LeadSignals`
   Pydantic schema (`budget_mentioned`, `urgency`, `product_interest`,
   `intent_to_buy`, `reasoning`) forces the output into a strict, parseable
   shape. This avoids fragile regex/string-matching on LLM text.
3. **LCEL chain** — `prompt | llm | parser` composes the three steps into a
   single pipeline (standard LangChain pattern).
4. **Scoring logic** — a simple point system converts the structured signals
   into a final label:
   - urgency: immediate=+2, soon=+1
   - budget: high=+2, medium=+1
   - intent: strong=+2, moderate=+1
   - 4+ points = Hot, 2-3 = Warm, 0-1 = Cold
5. **Two run modes:**
   - **LIVE** — if `OPENAI_API_KEY` is set, uses `ChatOpenAI` (gpt-4o-mini)
     through the real LangChain chain.
   - **OFFLINE DEMO** — if no key is available, a rule-based fallback fills
     the same `LeadSignals` schema so the full pipeline (input → structured
     extraction → scoring → output) is still demoable end-to-end without
     needing a paid API key. Every result is labeled with which mode
     produced it, so this is never mistaken for real model output.
6. **Error handling** — `qualify_lead()` validates input before doing any
   work: rejects `None`, non-string types, empty strings, and whitespace-only
   strings, returning a clear `{"error": ...}` instead of crashing.

## Files
- `lead_qualifier.py` — core LangChain pipeline (`qualify_lead()` function)
- `run_tests.py` — sample dataset (10 realistic leads + 5 bad-input cases) and test runner
- `results.md` — saved output of all test runs

## How to Run
```bash
pip install langchain langchain-openai langchain-core pydantic

# Optional: for real LLM output instead of offline demo mode
export OPENAI_API_KEY="your-key-here"

python run_tests.py
```

## Sample Input/Output
**Input:** `"Ready to purchase a flagship TV, money is not an issue, want it asap."`
```json
{
  "mode": "OFFLINE DEMO (rule-based fallback, no API key found)",
  "extracted_signals": {
    "budget_mentioned": "high",
    "urgency": "immediate",
    "product_interest": "tv",
    "intent_to_buy": "strong",
    "reasoning": "Offline rule-based scan found urgency=immediate, budget=high, intent=strong."
  },
  "final_label": "Hot",
  "score_points": 6
}
```

## What Worked
- All 10 realistic sample leads were scored consistently (Hot/Warm/Cold) with
  sensible reasoning.
- The structured schema (Pydantic) made scoring logic trivial — no parsing of
  raw text needed.

## Issues Faced & Fixed
- **No paid API key available before the deadline** → solved by adding an
  offline rule-based fallback that fills the exact same schema, so the full
  LangChain pipeline (prompt → parser → schema → scoring) is still fully
  demoable and testable end-to-end; swapping in `OPENAI_API_KEY` later
  switches to real LLM calls with zero code changes.
- **Bad input (None, int, empty string) crashing the pipeline** → added
  explicit validation at the top of `qualify_lead()` before any LangChain
  calls are made.

## What I Learned
- How to define a structured output schema with Pydantic and enforce it on
  LLM responses using `PydanticOutputParser`.
- How LangChain's LCEL (`prompt | llm | parser`) composes a pipeline instead
  of manually chaining function calls.
- Why validating input *before* calling an LLM saves API cost and avoids
  confusing errors deep inside a chain.
