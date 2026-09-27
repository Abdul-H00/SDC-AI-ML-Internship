"""
AI-Powered Document Parser & Structuring Tool
National Tutoring Center
------------------------------------------------
This script reads unstructured documents (forms, receipts, applications)
from the sample_documents folder, uses an LLM (via LangChain) to extract
structured fields, and saves the results into a single Excel/CSV file.
"""

import os
import re
import json
import glob
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import pandas as pd

# Load the API key from the .env file
load_dotenv()

# Set up the AI model (Gemini, via LangChain)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

prompt_template = PromptTemplate(
    input_variables=["document_text"],
    template="""
You are a data extraction assistant for a National Tutoring Center.
Read the document below and extract the relevant fields as a JSON object.

Rules:
- Detect the document type first: "admission_form", "fee_receipt", or "application"
- Only include fields that are actually present in the document
- Use these field names when relevant: document_type, name, guardian_or_father_name,
  contact_number, email, grade_or_class, subjects, amount, receipt_no, payment_date,
  date_submitted, notes
- If a field is missing, leave it out of the JSON (do not guess)
- Respond with ONLY valid JSON. No explanation, no markdown, no code fences.

Document:
---
{document_text}
---
"""
)


def clean_json_text(raw_output):
    """Extract a clean JSON string from whatever the model returned."""
    # If content came back as a list of parts, join them into a string
    if isinstance(raw_output, list):
        raw_output = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in raw_output
        )

    text = str(raw_output).strip()

    # Remove markdown code fences like ```json ... ```
    text = re.sub(r"^```(?:json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    text = text.strip()

    # Extract just the {...} portion, in case there's extra text around it
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return text


def extract_fields(document_text):
    """Send one document's text to the LLM and get back structured JSON."""
    prompt = prompt_template.format(document_text=document_text)
    response = llm.invoke(prompt)

    cleaned = clean_json_text(response.content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("  [WARNING] Could not parse JSON for this document.")
        print("  Raw model output was:")
        print(cleaned)
        return {"document_type": "PARSE_ERROR", "notes": cleaned}


def main():
    input_folder = "sample_documents"
    output_file = "extracted_data.xlsx"

    files = glob.glob(os.path.join(input_folder, "*.txt"))

    if not files:
        print(f"No .txt files found in '{input_folder}'. Please add some documents first.")
        return

    all_results = []

    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"Processing: {file_name} ...")

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        extracted = extract_fields(text)
        extracted["source_file"] = file_name
        all_results.append(extracted)

    df = pd.DataFrame(all_results)
    df.to_excel(output_file, index=False)
    print(f"\n[DONE] Extracted data saved to '{output_file}'")
    print(df)


if __name__ == "__main__":
    main()
