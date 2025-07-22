
import os
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Logging setup
LOG_PATH = os.path.join(os.path.dirname(__file__), 'logs', 'score_with_llm.log')
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Load Gemini API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(model_name=MODEL)

INPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'search_results.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs','scored_results.json')

PROMPT = (
    "You are an expert at identifying whether a web page contains the publications, reports, drafts, or similar official documents, where we can find the full text of the document, or a download link. "
    "do not consider pages that only contain summaries or brief descriptions without links to the full document, like the homepage, about page or contacts page etc."
    "the web metadata must hint that we can find the links to download the publications or reports"
    "Given the following web page metadata (title, url, and snippet text), assign a score from 0 to 1 for how likely it is that the page contains such content. "
    "Return only a JSON object with the url as key and the score as value, without markdown formatting or any additional text."
)

def score_urls_with_llm(web_results):
    scored = {}
    if not web_results:
        return scored
    # Only process the first entry (region)
    entry = web_results[0]
    region = entry.get("Country/Region") or entry.get("Bank Name")
    scored[region] = {}
    search_data = entry.get("search_result", {}).get("data", [])
    if not search_data:
        return scored
    web_items = search_data[0].get("results", {}).get("web", [])
    for item in web_items:
        url = item.get("url")
        title = item.get("title", "")
        text = item.get("text", "")
        if not url:
            continue
        llm_input = f"Title: {title}\nURL: {url}\nText: {text}"
        print(f"Scoring URL: {url}")
        logging.info(f"Scoring URL: {url} | Title: {title}")
        response = model.generate_content(
            contents=[{"role": "user", "parts": [PROMPT + "\n" + llm_input]}],
            generation_config={"temperature": 0.2}
        )
        try:
            score_json = json.loads(response.text)
            scored[region].update(score_json)
            print(f"Score for {url}: {score_json}")
            logging.info(f"Score for {url}: {score_json}")
        except Exception as e:
            scored[region][url] = None
            print(f"Failed to parse score for {url}: {e}")
            print(f"Raw response for {url}: {response.text}")
            logging.error(f"Failed to parse score for {url}: {e}")
            logging.error(f"Raw response for {url}: {response.text}")
    print(f"Analysis for {region}: {json.dumps(scored[region], indent=2)}")
    logging.info(f"Analysis for {region}: {json.dumps(scored[region], indent=2)}")
    return scored

def main():
    with open(INPUT_PATH, encoding='utf-8') as f:
        web_results = json.load(f)

    # Load already scored regions if present
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, encoding='utf-8') as sf:
                already_scored = json.load(sf)
        except (json.JSONDecodeError, OSError):
            already_scored = {}
    else:
        already_scored = {}

    # Find regions to skip
    processed_regions = set(already_scored.keys())
    to_process = [entry for entry in web_results if (entry.get("Country/Region") or entry.get("Bank Name")) not in processed_regions]

    # Only process the first unscored region for testing
    if to_process:
        scores = score_urls_with_llm([to_process[0]])
        already_scored.update(scores)
    else:
        print("No new regions to process.")
        return

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(already_scored, f, ensure_ascii=False, indent=2)
    print(f"Scored results written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
