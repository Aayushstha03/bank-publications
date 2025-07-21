import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load Gemini API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(model_name=MODEL)

INPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'search_results.json')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scored_results.json')

PROMPT = (
    "You are an expert at identifying whether a web page contains publications, reports, drafts, or similar official documents. "
    "Given the following web page metadata (title, url, and snippet text), assign a score from 0 to 1 for how likely it is that the page contains such content. "
    "Return only a JSON object with the url as key and the score as value."
)

def score_urls_with_llm(web_results):
    scored = {}
    for entry in web_results:
        search_data = entry.get("search_result", {}).get("data", [])
        if not search_data:
            continue
        web_items = search_data[0].get("results", {}).get("web", [])
        for item in web_items:
            url = item.get("url")
            title = item.get("title", "")
            text = item.get("text", "")
            if not url:
                continue
            # Prepare LLM input
            llm_input = f"Title: {title}\nURL: {url}\nText: {text}"
            response = model.generate_content(
                contents=[{"role": "user", "parts": [PROMPT + "\n" + llm_input]}],
                generation_config={"temperature": 0.2}
            )
            try:
                score_json = json.loads(response.text)
                scored.update(score_json)
            except Exception as e:
                scored[url] = None
    return scored

def main():
    with open(INPUT_PATH, encoding='utf-8') as f:
        web_results = json.load(f)
    scores = score_urls_with_llm(web_results)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)
    print(f"Scored results written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
