"""
AI-Assisted Website Quality Auditor for Furniture Websites
Member 2 — Individual Contribution (Tool: LangChain)

WHAT THIS DOES
---------------
Given a list of furniture website URLs, this tool:
  1. FETCHES each site's homepage HTML (requests) — falls back to a locally
     cached snapshot if the site can't be reached (see "Network note" below).
  2. EXTRACTS FACTUAL SIGNALS with plain HTML parsing (BeautifulSoup):
     number of internal links found, presence of a contact form / phone /
     email, presence of social media icons, number of CTA buttons, and a
     basic mobile-responsiveness indicator (viewport meta tag).
  3. Sends those facts (not raw HTML) to an LLM through LangChain, asking it
     to produce a JUDGMENT-based score (0-100), missing features, and
     recommendations — clearly labeled as AI-generated opinion, never
     mixed with the facts from step 2.
  4. Outputs a structured report: Website -> Score -> Problems ->
     Missing Features -> Recommendations -> Priority

WHY THIS SEPARATION MATTERS (the core requirement of this task)
-----------------------------------------------------------------
"Number of pages found" or "has a contact form" are FACTS — they don't need
an opinion, they need code that checks for them. "Is this professional
enough for 2026" is a JUDGMENT — it depends on taste, industry norms, and
context, so it's appropriate to hand to an LLM, but it must be labeled as
an opinion, not presented as ground truth. Mixing the two would make the
report look more objective than it actually is.

NETWORK NOTE
------------
This script tries a live `requests.get()` first. If that fails (e.g. no
internet, or a sandboxed environment with restricted network access), it
falls back to a locally cached HTML snapshot of that same page (saved in
sample_pages/) so the rest of the pipeline can still be demoed end-to-end.
Every result clearly states which source was used.
"""

import os
import re
import json
from urllib.parse import urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

SAMPLE_PAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_pages")


# ---------------------------------------------------------------------------
# 1. FACT EXTRACTION (no AI involved — pure HTML parsing)
# ---------------------------------------------------------------------------
def fetch_html(url: str, timeout: int = 8) -> tuple[str, str]:
    """
    Returns (html, source) where source is 'live' or 'cached_fallback'.
    Raises ValueError for genuinely bad input.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string.")
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL (must start with http:// or https://): {url!r}")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WebsiteAuditorBot/1.0)"}
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        return resp.text, "live"
    except Exception:
        # Fall back to a cached local snapshot if we have one for this domain
        domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
        cached_path = os.path.join(SAMPLE_PAGES_DIR, f"{domain}.html")
        if os.path.exists(cached_path):
            with open(cached_path, "r", encoding="utf-8") as f:
                return f.read(), "cached_fallback"
        raise ConnectionError(
            f"Could not fetch '{url}' live, and no cached fallback snapshot exists for it."
        )


def extract_facts(html: str, base_url: str) -> dict:
    """Pure fact extraction — no AI, no judgment. Just what's literally in the HTML."""
    soup = BeautifulSoup(html, "html.parser")

    links = soup.find_all("a", href=True)
    internal_links = [a for a in links if urlparse(base_url).netloc.split(".")[-2:] == urlparse(base_url).netloc.split(".")[-2:]]

    # Contact info detection
    text_blob = soup.get_text(" ", strip=True).lower()
    has_phone = bool(re.search(r"(tel:|\+?\d[\d\-\s]{7,}\d)", html))
    has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html))
    has_contact_form = bool(soup.find("form")) or "contact us" in text_blob or "contact-us" in html.lower()

    # Social links
    social_domains = ["facebook.com", "instagram.com", "twitter.com", "x.com",
                       "pinterest.com", "linkedin.com", "wa.me", "whatsapp.com", "youtube.com"]
    social_links_found = sorted({d for a in links for d in social_domains if d in a["href"]})

    # CTA buttons (rough heuristic: <button> tags + links with class containing 'cta')
    cta_buttons = soup.find_all("button")
    cta_like_links = [a for a in links if "cta" in " ".join(a.get("class", [])).lower()]
    cta_count = len(cta_buttons) + len(cta_like_links)

    # Mobile responsiveness indicator
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    has_viewport_meta = bool(viewport_tag)

    # Title / meta description presence (basic SEO/professionalism signal)
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else None

    return {
        "url": base_url,
        "page_links_found": len(links),
        "has_contact_form_or_page": has_contact_form,
        "has_phone_number": has_phone,
        "has_email": has_email,
        "social_links_found": social_links_found,
        "cta_button_count": cta_count,
        "has_mobile_viewport_meta": has_viewport_meta,
        "has_page_title": title is not None,
        "page_title": title,
        "has_meta_description": meta_description is not None,
    }


# ---------------------------------------------------------------------------
# 2. AI JUDGMENT (LangChain) — clearly separated from facts above
# ---------------------------------------------------------------------------
class AIJudgment(BaseModel):
    professionalism_score: int = Field(description="0-100 score of overall professionalism and business functionality")
    missing_features: list[str] = Field(description="Short list of features/signals missing or weak")
    problems: list[str] = Field(description="Short list of specific problems noticed")
    recommendations: list[str] = Field(description="Short list of concrete recommendations")
    priority: str = Field(description="'High', 'Medium', or 'Low' — how urgently these issues should be fixed")

judgment_parser = PydanticOutputParser(pydantic_object=AIJudgment)

JUDGMENT_PROMPT = """You are a website quality auditor reviewing a furniture retail website
for a client. You are given FACTUAL SIGNALS automatically detected from the site's homepage
(NOT your own browsing — trust only these facts). Based on these facts and general
e-commerce/retail best practices, give your professional judgment.

Facts detected on this site's homepage:
{facts_json}

{format_instructions}

Be specific and practical. Respond with ONLY the structured data.
"""

judgment_prompt = ChatPromptTemplate.from_template(
    JUDGMENT_PROMPT,
    partial_variables={"format_instructions": judgment_parser.get_format_instructions()},
)


def _get_live_judgment_chain():
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return judgment_prompt | llm | judgment_parser


def _offline_judgment(facts: dict) -> AIJudgment:
    """
    Rule-based fallback so the full pipeline is demoable without a paid API key.
    NOT a real LLM call — clearly labeled wherever it's used. Uses the same
    facts a real LLM prompt would receive, just with simpler logic.
    """
    score = 50
    problems, missing, recs = [], [], []

    if facts["has_contact_form_or_page"]:
        score += 10
    else:
        score -= 15
        problems.append("No clear contact form or contact page detected.")
        missing.append("Contact form / contact page")
        recs.append("Add a visible 'Contact Us' page or form so leads can reach the business.")

    if facts["has_phone_number"] or facts["has_email"]:
        score += 10
    else:
        missing.append("Visible phone number or email")
        recs.append("Display a phone number or support email prominently (footer/header).")

    if facts["social_links_found"]:
        score += 10
    else:
        score -= 5
        problems.append("No social media links detected on the homepage.")
        missing.append("Social media presence")
        recs.append("Link to active social media accounts to build trust and reach.")

    if facts["cta_button_count"] >= 2:
        score += 10
    else:
        score -= 10
        problems.append("Very few call-to-action buttons detected — may hurt conversion.")
        missing.append("Clear calls-to-action")
        recs.append("Add prominent CTA buttons (e.g. 'Shop Now', 'Get a Quote').")

    if facts["has_mobile_viewport_meta"]:
        score += 10
    else:
        score -= 15
        problems.append("No mobile viewport meta tag found — site may not be mobile-responsive.")
        missing.append("Mobile-responsive design")
        recs.append("Add a responsive viewport meta tag and test on mobile devices.")

    if facts["has_meta_description"]:
        score += 5
    else:
        missing.append("SEO meta description")
        recs.append("Add a meta description for better search engine visibility.")

    if facts["page_links_found"] < 5:
        score -= 10
        problems.append("Very few links found on homepage — site may be thin on content/navigation.")

    score = max(0, min(100, score))
    priority = "High" if score < 50 else ("Medium" if score < 75 else "Low")

    if not problems:
        problems.append("No major problems detected in the automatically-checked signals.")
    if not recs:
        recs.append("Maintain current standards; consider periodic UX audits.")

    return AIJudgment(
        professionalism_score=score,
        missing_features=missing or ["None detected"],
        problems=problems,
        recommendations=recs,
        priority=priority,
    )


# ---------------------------------------------------------------------------
# 3. MAIN PIPELINE
# ---------------------------------------------------------------------------
def audit_website(url: str) -> dict:
    """Runs the full pipeline for one URL. Returns a structured result dict."""
    try:
        html, source = fetch_html(url)
    except (ValueError, ConnectionError) as e:
        return {"url": url, "error": str(e)}
    except Exception as e:
        return {"url": url, "error": f"Unexpected error while fetching: {e}"}

    try:
        facts = extract_facts(html, url)
    except Exception as e:
        return {"url": url, "error": f"Failed to extract facts: {e}"}

    use_live_llm = bool(os.environ.get("OPENAI_API_KEY"))
    try:
        if use_live_llm:
            chain = _get_live_judgment_chain()
            judgment = chain.invoke({"facts_json": json.dumps(facts, indent=2)})
            judgment_mode = "LIVE (OpenAI via LangChain)"
        else:
            judgment = _offline_judgment(facts)
            judgment_mode = "OFFLINE DEMO (rule-based fallback, no API key found)"
    except ValidationError as ve:
        return {"url": url, "error": f"AI output did not match expected schema: {ve}"}
    except Exception as e:
        return {"url": url, "error": f"Unexpected failure during AI judgment: {e}"}

    return {
        "url": url,
        "fetch_source": source,          # 'live' or 'cached_fallback'
        "judgment_mode": judgment_mode,  # which backend produced the AI judgment
        "facts_detected": facts,         # <-- FACTS (no opinion)
        "ai_judgment": judgment.model_dump(),  # <-- AI-GENERATED JUDGMENT (clearly separate)
    }


def audit_websites(urls: list[str]) -> list[dict]:
    if not urls or not isinstance(urls, list):
        return [{"error": "Input must be a non-empty list of URLs."}]
    return [audit_website(u) for u in urls]


if __name__ == "__main__":
    demo_urls = ["https://www.ashleyfurniture.com"]
    print(json.dumps(audit_websites(demo_urls), indent=2))
