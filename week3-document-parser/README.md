# AI-Powered Document Parser & Structuring Tool
### National Tutoring Center — Week 3 Project

## 1. What I Built and Why

This tool solves a real operational problem for a National Tutoring Center: staff
receive many unstructured documents (admission forms, fee receipts, scholarship
applications) that currently require manual data entry into spreadsheets. This
tool reads a folder of plain-text documents, uses an LLM to identify the document
type and extract the relevant fields, and outputs everything into a single,
organized Excel file - removing the need for manual re-typing and reducing
data-entry errors.

## 2. Tools and Techniques Used

- LangChain (langchain-google-genai) to structure the prompt and manage the
  call to the LLM
- Google Gemini (gemini-3.8-flash) as the underlying language model
- Prompt engineering: a single, reusable prompt template instructs the model
  to (a) detect the document type, (b) extract only fields that are actually
  present, and (c) respond with strict JSON - no explanations or markdown
- pandas to convert the extracted JSON objects into a single structured
  table, and openpyxl to export it to Excel
- Custom JSON-cleaning logic (clean_json_text) to handle real-world LLM
  output quirks - for example, responses wrapped in markdown code fences, or
  returned as a list of content parts instead of a plain string

## 3. What I Tested and What I Found

Happy-path testing: Ran the tool against three realistic sample documents -
an admission form, a fee receipt, and a scholarship application. All three were
correctly classified by document type and had their key fields (name, contact
number, amounts, dates, etc.) extracted accurately into the output spreadsheet.

Edge-case testing:
- Incomplete document (only a name, no other fields): tested to confirm the
  tool does not crash and does not invent/hallucinate missing fields.
- Irrelevant/unrelated text (not a form at all): tested to confirm the tool
  handles non-form input gracefully rather than forcing incorrect data into the
  output.

Issues found and fixed during development:
1. langchain.prompts import failed on the installed LangChain version - fixed
   by switching to langchain_core.prompts.
2. The initial Gemini model name (gemini-2.0-flash) had been deprecated by
   Google since this project started - fixed by updating to the current model
   name (gemini-3.8-flash).
3. The model occasionally returns its answer as a list of content parts rather
   than a plain string, which broke direct .strip() calls - fixed by adding
   type-checking and a dedicated clean_json_text() cleaning step before
   parsing.
4. Windows console could not print certain Unicode characters in status
   messages - fixed by using plain ASCII status tags (e.g. [DONE]) instead
   of emoji.
5. Free-tier API rate limits were hit during repeated testing - documented here
   as a known constraint rather than a code defect; production use would
   require a paid tier or request throttling.

## 4. What I Would Improve With More Time

- Add support for PDF and scanned-image inputs (using OCR) in addition to plain
  text files, since real tutoring center documents will often be scans
- Add automatic retry logic with backoff for rate-limit and transient API
  errors
- Add a lightweight validation layer (e.g. checking phone number formats, date
  formats) before writing to the final spreadsheet
- Build a simple web interface (e.g. Streamlit) so non-technical staff could
  upload documents directly, rather than running the script from a terminal

## How to Run This Project

1. Create a .env file with GOOGLE_API_KEY=your_key_here
2. Install dependencies: pip install langchain langchain-google-genai pandas python-dotenv openpyxl
3. Place .txt documents in the sample_documents/ folder
4. Run: python parser.py
5. Output will be saved to extracted_data.xlsx
