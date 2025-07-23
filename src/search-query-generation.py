import os
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai
import csv
import requests

# Setup paths

BANKS_PATH = os.path.join(os.path.dirname(__file__),'websites_deduped.csv')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, 'search_query_generation.log')
QUERIES_PATH = os.path.join(OUTPUT_DIR, 'generated_queries.json')
RESULTS_PATH = os.path.join(OUTPUT_DIR, 'query_results.json')

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Gemini setup
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(model_name=MODEL)

API_URL = "https://laterical.com/api/call/"

PROMPT = (
    "You are an expert in crafting search engine queries to find structured index pages (not individual documents).\n\n"
    "Given the name and official website of a central bank, generate from 3 to 5 Google-style search queries that will help discover *main listing or archive pages* on that website — such as pages for publications, economic reports, bulletins, statistical releases, or news announcements.\n\n"
    "**Important requirements:**\n"
    "- The goal is to find structured *listing pages*, not individual files (avoid direct links to PDF, XLS, DOC, etc.).\n"
    "- Use advanced search operators like `site:`, `inurl:`, `intitle:`, and logical ORs.\n"
    "- Focus queries on the official website domain.\n"
    "- If the bank is from a non-English-speaking country, try including native terms like 'publicaciones' (Spanish), 'rapports' (French), or 'statistik' (German), depending on the country, include both english and native language queries for these queries\n"
    "- Return the queries as a json array of strings.\n\n"
    "Here is the information:\n\n"
)

def generate_queries(bank_name, bank_url):
    llm_input = f"Bank Name: {bank_name}\nBank URL: {bank_url}"
    response = model.generate_content(
        contents=[{"role": "user", "parts": [PROMPT + "\n" + llm_input]}],
        generation_config={"temperature": 0.2}
    )
    try:
        resp_text = response.text.strip()
        # Remove markdown code block if present
        if resp_text.startswith('```'):
            # Remove first line (```json or ```)
            lines = resp_text.splitlines()
            # Remove the first and last line if they are code block markers
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            resp_text = '\n'.join(lines).strip()
        queries = json.loads(resp_text)
        logging.info(f"Generated queries for {bank_name}: {queries}")
        return queries
    except Exception as e:
        logging.error(f"Failed to parse queries for {bank_name}: {e}")
        logging.error(f"Raw response: {response.text}")
        return []

def main():
    # Read banks
    with open(BANKS_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        banks = [(row['Bank Name'], row['Bank URL']) for row in reader]
    # Load existing queries if present
    if os.path.exists(QUERIES_PATH):
        try:
            with open(QUERIES_PATH, encoding='utf-8') as f:
                all_queries = json.load(f)
        except (json.JSONDecodeError, OSError):
            print(f"Warning: {QUERIES_PATH} is empty or invalid. Starting with empty queries.")
            all_queries = {}
    else:
        all_queries = {}

    banks = banks[:10]  # Only process the top 10 banks
    total_banks = len(banks)
    for idx, (bank_name, bank_url) in enumerate(banks, 1):
        if bank_name in all_queries:
            print(f"[{idx}/{total_banks}] Skipping {bank_name} (already present)")
            continue
        print(f"[{idx}/{total_banks}] Generating queries for {bank_name}")
        queries = generate_queries(bank_name, bank_url)
        all_queries[bank_name] = queries
        print(f"Queries for {bank_name}: {queries}")
        # Write to file after each region
        with open(QUERIES_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_queries, f, ensure_ascii=False, indent=2)
        print(f"Progress saved to {QUERIES_PATH}")
        import time
        time.sleep(1)
    print(f"Saved queries to {QUERIES_PATH}")

if __name__ == "__main__":
    main()
