"""
AI Lead Qualification Bot for a Retail Chain
Role: Member 2 - Individual Contributor
Primary Tool: LangChain
"""

from langchain_core.prompts import PromptTemplate
from langchain_community.llms.fake import FakeListLLM

# STEP 1: Sample dataset - example customer inquiries
sample_leads = [
    "Hi, do you have the red sneakers in size 9? I want to buy today if in stock.",
    "Just checking out your website, nice collection!",
    "Can I get a discount if I buy 3 jackets? Planning to purchase this week.",
    "What are your store timings?",
    "I need 50 uniforms for my staff by next Monday, please send a quote.",
    "",  # bad/empty input, to test error handling
]

# STEP 2: Prompt design
qualification_prompt = PromptTemplate(
    input_variables=["message"],
    template="""
You are a lead qualification assistant for a retail chain.
Classify the customer message below as HOT, WARM, or COLD based on:
- HOT: mentions buying now, urgent need, specific quantity/date, ready to pay
- WARM: shows interest, asks about price/discount, but no urgency
- COLD: casual browsing, general questions, no buying intent

Customer message: "{message}"

Respond with one word: HOT, WARM, or COLD.
""",
)

# STEP 3: Fake LLM (no API key needed)
fake_responses = ["HOT", "COLD", "WARM", "COLD", "HOT", "COLD"]
llm = FakeListLLM(responses=fake_responses)

chain = qualification_prompt | llm

# STEP 4: Core function with error handling
def qualify_lead(message: str) -> str:
    try:
        if not isinstance(message, str):
            raise TypeError("Input must be a string.")
        cleaned = message.strip()
        if cleaned == "":
            raise ValueError("Empty message received.")

        result = chain.invoke({"message": cleaned})
        return result.strip().upper()

    except (TypeError, ValueError) as e:
        return f"ERROR: {e}"

# STEP 5: Run test cases
print("=== AI Lead Qualification Bot - Test Run ===\n")
for i, msg in enumerate(sample_leads, start=1):
    display_msg = msg if msg else "(empty input)"
    result = qualify_lead(msg)
    print(f"Test {i}")
    print(f"  Input : {display_msg}")
    print(f"  Output: {result}")
    print("-" * 50)

extra_tests = [
    "Do you deliver internationally?",
    "I want to place a bulk order of 200 t-shirts, need it urgently.",
    "Not interested right now, maybe later.",
    None,
]
for i, msg in enumerate(extra_tests, start=len(sample_leads) + 1):
    result = qualify_lead(msg)
    print(f"Test {i}")
    print(f"  Input : {msg}")
    print(f"  Output: {result}")
    print("-" * 50)
