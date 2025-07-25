import os
import json

FINAL_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data', 'final_output')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'high_confidence_listing_urls.json')
TOPICS = ["publications", "statistics", "monetary_policy", "news", "research"]

def main():
    flat_list = []
    files = [f for f in os.listdir(FINAL_OUTPUT_DIR) if f.endswith('.listing_urls.json')]
    for fname in files:
        bank_name = fname.replace('.listing_urls.json', '')
        file_path = os.path.join(FINAL_OUTPUT_DIR, fname)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for topic_block in data:
            topic = topic_block.get('topic')
            if topic not in TOPICS:
                continue
            entries = topic_block.get('entries', [])
            for entry in entries:
                prob = entry.get('listing_probability', 0)
                if prob > 0.75:
                    flat_list.append({
                        'url': entry.get('url'),
                        'title': entry.get('title'),
                        'text': entry.get('text'),
                        'listing_probability': prob,
                        'topics': [topic]
                    })
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(flat_list, f, ensure_ascii=False, indent=2)
    print(f"Saved high confidence listing URLs to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
