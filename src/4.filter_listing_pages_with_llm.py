
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

PROMPT = (
    "You are an expert at identifying whether a web page is a listing/collection page for publications, news articles, reports, research papers or similar official documents on a central bank website. "
    "A listing page contains links to multiple documents or downloadable items, not just a single article, report, or news post. "
    "Given the following JSON array of entries (with title, url, and text), for each entry, append a new field: "
    "'listing_probability': a score between 0 and 1 indicating how likely it is that the page is a listing or collection page for publications/reports. "
    "Do not give a high score to single document pages or home/about/contact/FAQ pages. "
    "Return the same JSON array, but with the new field added to each entry. Do not use markdown formatting or any extra text."
)

def filter_listing_entries(entries):
    llm_input = json.dumps(entries, ensure_ascii=False, indent=2)
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
        return result
    except Exception as e:
        logging.error(f"Failed to parse LLM response: {e}")
        logging.error(f"Raw response: {response.text}")
        return None

def main():
    urls_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'filtered_urls')
    final_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'final_output')
    os.makedirs(final_dir, exist_ok=True)
    files = [f for f in os.listdir(urls_dir) if f.endswith('.unique_webs.json')]
    files = sorted(files)[:50]
    for fname in files:
        input_path = os.path.join(urls_dir, fname)
        with open(input_path, encoding='utf-8') as f:
            data = json.load(f)
        # data is a list of topic blocks, each with 'topic' and 'entries'
        output = []
        for topic_block in data:
            topic = topic_block.get('topic')
            entries = topic_block.get('entries', [])
            if not entries:
                continue
            llm_augmented = filter_listing_entries(entries)
            if llm_augmented is not None:
                output.append({
                    'topic': topic,
                    'entries': llm_augmented
                })
        output_path = os.path.join(final_dir, fname.replace('.unique_webs.json', '.listing_urls.json'))
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"LLM-augmented listing info written to {output_path}")

if __name__ == "__main__":
    main()
