"""
AI Lead Qualification Bot for a Retail Chain
Member 2 — Individual Contribution (Tool: LangChain)

WHAT THIS DOES
---------------
Takes a raw customer message (a "lead") coming from chat/web-form/WhatsApp
and uses LangChain to:
  1. Build a structured prompt (PromptTemplate)
  2. Ask an LLM to extract lead signals (budget, urgency, product interest, intent)
  3. Parse the LLM's response into a strict structured object (PydanticOutputParser)
  4. Convert those signals into a final label: Hot / Warm / Cold, with reasoning

WHY LANGCHAIN
-------------
LangChain is used here for exactly what it's good at:
  - PromptTemplate  -> keeps the prompt reusable/parametrized instead of hardcoded strings
  - PydanticOutputParser -> forces the LLM's free-text answer into a strict schema
    (budget, urgency, product_interest, intent_to_buy) instead of unreliable
    string-matching / regex on raw text
  - LCEL chain ( prompt | llm | parser ) -> composes these steps into one pipeline

RUN MODES
---------
- LIVE MODE: if OPENAI_API_KEY is set in the environment, real OpenAI model is used
  through langchain-openai (ChatOpenAI).
- OFFLINE DEMO MODE: if no API key is found, a lightweight rule-based fallback
  produces the same structured schema, so the pipeline and I/O demo still runs
  end-to-end without needing a paid key. This is clearly logged so it's never
  presented as "real LLM output" when it isn't.
"""

import os
import json
from typing import Optional
from pydantic import BaseModel, Field, ValidationError
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


# ---------------------------------------------------------------------------
# 1. Structured schema for what we want the LLM to return
# ---------------------------------------------------------------------------
class LeadSignals(BaseModel):
    budget_mentioned: str = Field(description="'high', 'medium', 'low', or 'unknown'")
    urgency: str = Field(description="'immediate', 'soon', 'exploring', or 'unknown'")
    product_interest: str = Field(description="Product or category the lead is asking about")
    intent_to_buy: str = Field(description="'strong', 'moderate', 'weak', or 'unknown'")
    reasoning: str = Field(description="One short sentence explaining the signals found")


parser = PydanticOutputParser(pydantic_object=LeadSignals)

PROMPT_TEXT = """You are a retail sales assistant analyzing an incoming customer lead message.
Read the message and extract structured signals about the customer's buying intent.

Customer message:
\"\"\"{lead_message}\"\"\"

{format_instructions}

Respond with ONLY the structured data, nothing else.
"""

prompt = ChatPromptTemplate.from_template(
    PROMPT_TEXT,
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


# ---------------------------------------------------------------------------
# 2. LLM backend selection (LIVE vs OFFLINE fallback)
# ---------------------------------------------------------------------------
def _get_live_chain():
    """Builds the real LangChain LCEL chain using OpenAI, if a key is available."""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return prompt | llm | parser


def _offline_extract(lead_message: str) -> LeadSignals:
    """
    Rule-based fallback so the pipeline is fully demoable without an API key.
    Not an LLM call — used only when OPENAI_API_KEY is missing, and clearly
    logged as OFFLINE MODE so it's never confused with real model output.
    """
    text = lead_message.lower()

    if any(w in text for w in ["today", "now", "urgent", "asap", "right away"]):
        urgency = "immediate"
    elif any(w in text for w in ["this week", "soon", "few days"]):
        urgency = "soon"
    elif any(w in text for w in ["just looking", "browsing", "someday", "not sure"]):
        urgency = "exploring"
    else:
        urgency = "unknown"

    if any(w in text for w in ["no budget issue", "money is not a problem", "budget is not a problem", "expensive", "premium", "flagship"]):
        budget = "high"
    elif any(w in text for w in ["cheap", "low budget", "tight budget", "affordable", "under"]):
        budget = "low"
    elif any(w in text for w in ["budget", "price", "cost"]):
        budget = "medium"
    else:
        budget = "unknown"

    if any(w in text for w in ["want to buy", "ready to buy", "purchase", "book", "order"]):
        intent = "strong"
    elif any(w in text for w in ["interested", "looking for", "need"]):
        intent = "moderate"
    elif any(w in text for w in ["just looking", "just browsing", "maybe"]):
        intent = "weak"
    else:
        intent = "unknown"

    products = ["iphone", "laptop", "tv", "shoes", "jacket", "fridge", "washing machine", "phone", "sofa", "watch"]
    found = next((p for p in products if p in text), "not specified")

    return LeadSignals(
        budget_mentioned=budget,
        urgency=urgency,
        product_interest=found,
        intent_to_buy=intent,
        reasoning=f"Offline rule-based scan found urgency={urgency}, budget={budget}, intent={intent}.",
    )


# ---------------------------------------------------------------------------
# 3. Scoring logic: signals -> Hot / Warm / Cold
# ---------------------------------------------------------------------------
def score_lead(signals: LeadSignals) -> dict:
    points = 0
    if signals.urgency == "immediate":
        points += 2
    elif signals.urgency == "soon":
        points += 1

    if signals.budget_mentioned == "high":
        points += 2
    elif signals.budget_mentioned == "medium":
        points += 1

    if signals.intent_to_buy == "strong":
        points += 2
    elif signals.intent_to_buy == "moderate":
        points += 1

    if points >= 4:
        label = "Hot"
    elif points >= 2:
        label = "Warm"
    else:
        label = "Cold"

    return {"score_points": points, "label": label}


# ---------------------------------------------------------------------------
# 4. Public function: qualify_lead()
# ---------------------------------------------------------------------------
def qualify_lead(lead_message: str) -> dict:
    """
    Main entry point. Takes a raw lead message string and returns a structured
    qualification result. Includes basic input validation / error handling.
    """
    # --- basic error handling for bad input ---
    if lead_message is None:
        return {"error": "No input provided. 'lead_message' cannot be None."}
    if not isinstance(lead_message, str):
        return {"error": f"Invalid input type: expected str, got {type(lead_message).__name__}."}
    if not lead_message.strip():
        return {"error": "Empty message received. Cannot qualify an empty lead."}
    if len(lead_message.strip()) < 3:
        return {"error": "Message too short to analyze meaningfully."}

    use_live = bool(os.environ.get("OPENAI_API_KEY"))

    try:
        if use_live:
            chain = _get_live_chain()
            signals = chain.invoke({"lead_message": lead_message})
            mode = "LIVE (OpenAI via LangChain)"
        else:
            signals = _offline_extract(lead_message)
            mode = "OFFLINE DEMO (rule-based fallback, no API key found)"
    except ValidationError as ve:
        return {"error": f"Model output did not match expected schema: {ve}"}
    except Exception as e:
        return {"error": f"Unexpected failure while qualifying lead: {e}"}

    result = score_lead(signals)
    return {
        "mode": mode,
        "input_message": lead_message,
        "extracted_signals": signals.dict(),
        "final_label": result["label"],
        "score_points": result["score_points"],
    }


if __name__ == "__main__":
    demo_message = "Hi, I want to buy a new iPhone today, budget is not a problem."
    output = qualify_lead(demo_message)
    print(json.dumps(output, indent=2))
