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
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'final_output', '176_Qatar_Central_Bank.listing_urls.json')

PROMPT = (
    "You are an expert at identifying whether a web page is a listing/collection page for publications, news articles, reports, research papers or similar official documents on a central bank website. "
    "A listing page contains links to multiple documents or downloadable items, not just a single article, report, or news post. "
    "Given the following JSON containing a list of URL blocks (with title, url, and text), for each block, append two new fields: "
    "1. 'topics': a list describing the main topics or types of documents covered in the listing, assign from news, annual_reports, monetary_policy, statistical_bulletins, economic_reviews, research_papers, working_papers, financial_stability, inflation_reports, exchange_rate, press_releases, speeches, regulatory_updates, publications_misc, or NA if not applicable "
    "2. 'listing_probability': a score between 0 and 1 indicating how likely it is that the page is a listing or collection page for publications/reports. "
    "Do not give a high score to single document pages or home/about/contact/FAQ pages."
    "Return the same JSON structure, but with the two new fields added to each block. Do not use markdown formatting or any extra text."
)


def filter_listing_urls(bank_name, url_blocks):
    # Prepare input for LLM: send the full JSON structure
    llm_input = json.dumps({
        "Bank Name": bank_name,
        "unique_internal_blocks": url_blocks
    }, ensure_ascii=False, indent=2)
    response = model.generate_content(
        contents=[{"role": "user", "parts": [PROMPT + "\n" + llm_input]}],
        generation_config={"temperature": 0.2}
    )
    try:
        resp_text = response.text.strip()
        # Remove markdown code block if present
        if resp_text.startswith('```'):
            lines = resp_text.splitlines()
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            resp_text = '\n'.join(lines).strip()
        result = json.loads(resp_text)
        logging.info(f"LLM-augmented blocks for {bank_name}: {result}")
        return result
    except Exception as e:
        logging.error(f"Failed to parse LLM response: {e}")
        logging.error(f"Raw response: {response.text}")
        return None


def main():
    urls_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'urls')
    final_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'final_output')
    os.makedirs(final_dir, exist_ok=True)
    files = [f for f in os.listdir(urls_dir) if f.endswith('.unique_webs.json')]
    files = sorted(files)[:50]
    for fname in files:
        input_path = os.path.join(urls_dir, fname)
        with open(input_path, encoding='utf-8') as f:
            data = json.load(f)
        bank_name = data.get("Bank Name", "Unknown Bank")
        url_blocks = data.get("unique_internal_blocks", [])
        result = filter_listing_urls(bank_name, url_blocks)
        output_path = os.path.join(final_dir, fname.replace('.unique_webs.json', '.listing_urls.json'))
        if result:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"LLM-augmented listing info written to {output_path}")
        else:
            print(f"Failed to process {fname}, see log for details.")

if __name__ == "__main__":
    main()
