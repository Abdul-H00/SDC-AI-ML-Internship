"""
Test runner: 10+ sample leads + bad-input cases for the Lead Qualification Bot.
Run: python run_tests.py
Results are printed and also saved to results.md for the write-up / screenshots.
"""

import json
from lead_qualifier import qualify_lead

# ---------------------------------------------------------------------------
# Sample dataset — realistic retail-chain lead messages
# ---------------------------------------------------------------------------
sample_leads = [
    "Hi, I want to buy a new iPhone today, budget is not a problem.",
    "Just browsing, might get a laptop someday, not sure yet.",
    "Need a washing machine urgently, ours broke down today.",
    "Looking for an affordable pair of shoes, tight budget please.",
    "I'm interested in your premium sofa collection for my new house.",
    "Can you tell me the store timings?",
    "I want to order a fridge this week, price should be reasonable.",
    "Just checking prices for now, no rush at all.",
    "Ready to purchase a flagship TV, money is not an issue, want it asap.",
    "Do you have any jackets under 2000 rupees?",
    "Hello",  # very short / vague
    "",  # empty input -> error handling test
    None,  # invalid type -> error handling test
    12345,  # invalid type -> error handling test
    "   ",  # whitespace only -> error handling test
]

def run():
    results = []
    for i, lead in enumerate(sample_leads, start=1):
        output = qualify_lead(lead)
        results.append({"test_case": i, "input": lead, "output": output})
        print(f"\n--- Test Case {i} ---")
        print(f"Input : {lead!r}")
        print(f"Output: {json.dumps(output, indent=2)}")

    with open("results.md", "w") as f:
        f.write("# Test Results — AI Lead Qualification Bot (LangChain)\n\n")
        for r in results:
            f.write(f"## Test Case {r['test_case']}\n")
            f.write(f"**Input:** `{r['input']!r}`\n\n")
            f.write(f"**Output:**\n```json\n{json.dumps(r['output'], indent=2)}\n```\n\n")

    print(f"\n\nSaved {len(results)} test results to results.md")


if __name__ == "__main__":
    run()
