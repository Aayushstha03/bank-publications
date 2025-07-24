import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
search_results_dir = os.path.join(data_dir, 'search_results')
final_output_dir = os.path.join(data_dir, 'final_output')
os.makedirs(final_output_dir, exist_ok=True)

# --- Gemini Setup ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(model_name=MODEL)

FILE_EXTENSIONS = re.compile(r"\.(pdf|pptx?|docx?|xlsx?|zip|rar|csv|json|xml|jpg|jpeg|png|gif|mp4|mp3|avi|mov|wmv|txt|rtf|epub|mobi|xlsm|xlsb|tar|gz|7z|exe|bin|iso)(?=($|[?#]))", re.IGNORECASE)

def is_valid_url(url, seen):
    if url in seen:
        return False
    url_base = url.split('?', 1)[0].split('#', 1)[0]
    if FILE_EXTENSIONS.search(url_base):
        return False
    lower_url = url.lower()
    if any(x in lower_url for x in ["wp-login.php", "logout", "login", "session", "auth", "signin", "signup"]):
        return False
    query = ''
    if '?' in url:
        query = url.split('?', 1)[1].lower()
    param_names = ["id", "sid", "prid", "page", "pageno", "doc", "item", "ref", "no", "num"]
    for param in param_names:
        if re.search(rf'(^|[&?]){param}=[^&]+', query):
            return False
    blocklist = [
        "about", "contact", "home", "sitemap", "disclaimer", "privacy", "terms", "help", "faq", "feedback", "careers", "jobs", "login", "register", "signup", "signin", "support", "unsubscribe", "accessibility", "copyright", "cookies", "legal", "security", "admin", "dashboard", "profile", "settings", "preferences", "account", "user", "mypage", "myaccount", "myprofile"
    ]
    for word in blocklist:
        if re.search(rf"[\\/_-]{word}[\\/_-]|[\\/_-]{word}$|[?&]{word}=", lower_url):
            return False
    seen.add(url)
    return True

LISTING_PROMPT = (
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
        contents=[{"role": "user", "parts": [LISTING_PROMPT + "\n" + llm_input]}],
        generation_config={"temperature": 0.2}
    )
    try:
        resp_text = response.text.strip()
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
        print(f"Failed to parse LLM response: {e}")
        print(f"Raw response: {response.text}")
        return []

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    for search_result in data.get('search_results', []):
        topic = search_result.get('topic', None)
        entries = []
        seen_urls = set()
        for sr in search_result.get('search_result', []):
            web_list = sr.get('results', {}).get('web', [])
            for entry in web_list:
                url = entry.get('url')
                if url and is_valid_url(url, seen_urls):
                    entries.append({
                        'url': url,
                        'title': entry.get('title'),
                        'text': entry.get('text')
                    })
        if topic is not None and entries:
            print(f"  Topic '{topic}': Sending {len(entries)} entries to LLM...")
            llm_augmented = filter_listing_entries(entries)
            results.append({
                'topic': topic,
                'entries': llm_augmented
            })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def process_all_files():
    files = [f for f in os.listdir(search_results_dir) if f.endswith('.json')]
    for fname in files:
        output_path = os.path.join(final_output_dir, fname.replace('.json', '.listing_urls.json'))
        if os.path.exists(output_path):
            print(f"Skipping {fname}, already processed.")
            continue
        input_path = os.path.join(search_results_dir, fname)
        print(f"Processing {fname}...")
        process_file(input_path, output_path)

if __name__ == '__main__':
    process_all_files()
