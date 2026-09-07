# AI Lead Qualification Bot for a Retail Chain
**Role:** Member 2 — Individual Contributor
**Primary Tool:** LangChain

## What I Built
A lead qualification component that takes a customer's inquiry message
(from chat, WhatsApp, or a website form) and classifies it as **HOT**,
**WARM**, or **COLD**, so the retail chain's sales team knows which leads
to follow up with first.

## Approach
1. **Prompt design (`PromptTemplate`)** — I wrote a single, structured
   prompt that gives the model clear qualification rules:
   - HOT: urgent, specific buying intent (dates, quantities, "buy today")
   - WARM: interest shown, but no urgency (asks about discounts/price)
   - COLD: casual browsing, general questions, no buying signal
2. **Chain (`prompt | llm`)** — Using LangChain's Expression Language, the
   prompt is piped directly into a language model. This keeps the logic
   modular: swapping the LLM (e.g. to a real GPT/Claude model) later
   requires changing only one line of code.
3. **No-cost testing with `FakeListLLM`** — Since this is a quick
   internship demo without an API key, I used LangChain's built-in
   `FakeListLLM` to simulate model responses. This let me test the full
   pipeline logic (prompt building, chaining, error handling) without
   any external cost or setup delay. In production this would be swapped
   for `ChatOpenAI` or `ChatAnthropic`.
4. **Error handling** — The `qualify_lead()` function checks for empty
   strings and wrong input types, returning a clear `ERROR:` message
   instead of crashing.

## Test Results
Ran 10 test cases covering normal inquiries, edge cases (empty string,
`None` input), and different intent levels. All passed as expected —
see console output in `lead_qualification_bot.py` when run directly.

## What I Learned
- How LangChain's `PromptTemplate` and Expression Language (`|` chaining)
  work together to build a reusable pipeline.
- How to design a classification prompt with explicit, mutually exclusive
  categories so the output stays consistent.
- How to swap in `FakeListLLM` for fast, cost-free testing before wiring
  up a real LLM provider.

## How to Run
```bash
pip install langchain langchain-community
python lead_qualification_bot.py
```
