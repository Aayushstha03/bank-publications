
import json
import os

OBJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs/objects'))
URLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs/filtered_' \
'urls'))
os.makedirs(URLS_DIR, exist_ok=True)

# File extensions to filter out (add more as needed)
# Improved regex: match extension at end, before ? or #, or end of string
import re
FILE_EXTENSIONS = re.compile(r"\.(pdf|pptx?|docx?|xlsx?|zip|rar|csv|json|xml|jpg|jpeg|png|gif|mp4|mp3|avi|mov|wmv|txt|rtf|epub|mobi|xlsm|xlsb|tar|gz|7z|exe|bin|iso)(?=($|[?#]))", re.IGNORECASE)

def is_valid_url(url, seen):
    if url in seen:
        return False
    # Remove query and fragment for extension check
    url_base = url.split('?', 1)[0].split('#', 1)[0]
    if FILE_EXTENSIONS.search(url_base):
        return False
    # Filter out login/logout/session URLs
    lower_url = url.lower()
    if any(x in lower_url for x in ["wp-login.php", "logout", "login", "session", "auth", "signin", "signup"]):
        return False
    # Remove URLs with ?id=... or &id=... or similar (single entry pages)
    # Also handle case-insensitive 'id', 'sid', 'prid', 'page', 'pageno', etc.
    query = ''
    if '?' in url:
        query = url.split('?', 1)[1].lower()
    # List of parameter names to filter
    param_names = ["id", "sid", "prid", "page", "pageno", "doc", "item", "ref", "no", "num"]
    for param in param_names:
        if re.search(rf'(^|[&?]){param}=[^&]+', query):
            return False
    # Remove URLs containing about, contact, home, etc (case-insensitive, path or query)
    blocklist = [
        "about", "contact", "home", "sitemap", "disclaimer", "privacy", "terms", "help", "faq", "feedback", "careers", "jobs", "login", "register", "signup", "signin", "support", "unsubscribe", "accessibility", "copyright", "cookies", "legal", "security", "admin", "dashboard", "profile", "settings", "preferences", "account", "user", "mypage", "myaccount", "myprofile"
    ]
    for word in blocklist:
        if re.search(rf"[\/_-]{word}[\/_-]|[\/_-]{word}$|[?&]{word}=", lower_url):
            return False
    seen.add(url)
    return True

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
        if topic is not None:
            results.append({
                'topic': topic,
                'entries': entries
            })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def process_all_files():
    files = [f for f in os.listdir(OBJECTS_DIR) if f.endswith('.json')]
    for fname in files:
        input_path = os.path.join(OBJECTS_DIR, fname)
        output_path = os.path.join(URLS_DIR, fname.replace('.json', '.unique_webs.json'))
        process_file(input_path, output_path)

if __name__ == '__main__':
    process_all_files()
