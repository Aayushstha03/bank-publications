import os
import json
import re

def is_file_url(url):
    # Remove query params/fragments for extension check
    url = url.split('?')[0].split('#')[0]
    return re.search(r'\.(pdf|docx?|xlsx?|zip|rar|csv|pptx?)$', url, re.IGNORECASE)

INPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'search_results.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'search_results_deduped.json')

def parse_json_objects(filepath):
    buffer = ''
    brace_count = 0
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            brace_count += line.count('{')
            brace_count -= line.count('}')
            buffer += line + '\n'
            if brace_count == 0 and buffer.strip():
                try:
                    yield json.loads(buffer)
                except json.JSONDecodeError:
                    print('Warning: Skipping invalid JSON object')
                buffer = ''

def filter_and_dedup_urls(bank_entry):
    seen = set()
    filtered_results = []
    for result in bank_entry.get('search_results', []):
        urls = []
        sr = result.get('search_result', {})
        for item in sr.get('data', []):
            url = item.get('url')
            if url and url not in seen and not is_file_url(url):
                seen.add(url)
                urls.append(url)
        # Only keep non-empty url lists
        if urls:
            filtered_results.append({
                'query': result.get('query'),
                'urls': urls
            })
    return {
        'Bank Name': bank_entry.get('Bank Name'),
        'filtered_results': filtered_results
    }

def main():
    banks = []
    for entry in parse_json_objects(INPUT_PATH):
        banks.append(filter_and_dedup_urls(entry))
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for bank in banks:
            f.write(json.dumps(bank, ensure_ascii=False, indent=2) + '\n')
    print(f'Filtered results written to {OUTPUT_PATH}')

if __name__ == '__main__':
    main()
