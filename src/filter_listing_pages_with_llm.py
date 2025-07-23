import os
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Logging setup
LOG_PATH = os.path.join(os.path.dirname(__file__), 'logs', 'filter_listing_pages_with_llm.log')
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Load Gemini API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(model_name=MODEL)

# Input/output paths (edit as needed)
INPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'urls', '176_Qatar_Central_Bank.unique_webs.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'final_urls', '176_Qatar_Central_Bank.listing_urls.json')

PROMPT = (
    "You are an expert at identifying whether a web page URL is a listing or collection page (such as a directory of publications, reports, press releases, or document archives) on an official central bank website. "
    "A listing page contains links to multiple documents or items, not just a single article, report, or news post."
    "Given the following list of URLs and their metadata (title, url, and snippet text), return a JSON array of only those URLs that are likely to be listing or collection pages. DONOT MODIFY THE URLS"
    "Do not include single document pages, news articles, or home/about/contact pages."
    "Return only a JSON object with the bank name as the key and the array of listing URLs as the value."
)

def filter_listing_urls(bank_name, url_blocks):
    # Prepare input for LLM
    url_entries = [
        {"title": b.get("title", ""), "url": b.get("url", ""), "text": b.get("text", "")}
        for b in url_blocks if b.get("url")
    ]
    llm_input = f"Bank Name: {bank_name}\nURL Metadata List: {json.dumps(url_entries, ensure_ascii=False, indent=2)}"
    response = model.generate_content(
        contents=[{"role": "user", "parts": [PROMPT + "\n" + llm_input]}],
        generation_config={"temperature": 0.2}
    )
    try:
        resp_text = response.text.strip()
        # Remove markdown code block if present
        if resp_text.startswith('```'):
            lines = resp_text.splitlines()
            # Remove the first and last line if they are code block markers
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            resp_text = '\n'.join(lines).strip()
        result = json.loads(resp_text)
        logging.info(f"Filtered listing URLs for {bank_name}: {result}")
        return result
    except Exception as e:
        logging.error(f"Failed to parse LLM response: {e}")
        logging.error(f"Raw response: {response.text}")
        return {bank_name: []}

def main():
    with open(INPUT_PATH, encoding='utf-8') as f:
        data = json.load(f)
    bank_name = data.get("Bank Name", "Unknown Bank")
    url_blocks = data.get("unique_internal_blocks", [])
    result = filter_listing_urls(bank_name, url_blocks)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Filtered listing URLs written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
