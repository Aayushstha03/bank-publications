import csv
import requests
import os
import json
import time
import logging


CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'websites.csv')
API_URL = "https://laterical.com/api/call/"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'search_results.json')
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'search.log')

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def search_publications(bank_name, bank_url, max_retries=2, delay=3):
    query = f"{bank_name} site:{bank_url} publications OR reports OR drafts OR research OR press releases OR statements OR announcements"
    payload = {
        "path": "search",
        "entity": [query]
    }
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            # Check for API error in 'data' field
            if 'data' in data and data['data']:
                first = data['data'][0]
                if isinstance(first, dict) and 'error' in first:
                    print(f"Search failed for {bank_name} (API error: {first['error'].get('code', '')}), retrying...")
                    logging.warning(f"API error for {bank_name}: {first['error']}")
                    if attempt < max_retries:
                        time.sleep(delay)
                        continue
                    else:
                        return data
                return data
            else:
                raise ValueError("No data in response")
        except Exception as e:
            logging.warning(f"Attempt {attempt} failed for {bank_name}: {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                return {"error": str(e)}
        time.sleep(delay)


def main():
    # Load existing results if present
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, encoding='utf-8') as f:
                results = json.load(f)
        except (json.JSONDecodeError, OSError):
            print(f"Warning: {OUTPUT_PATH} is empty or invalid. Starting with empty results.")
            results = []
    else:
        results = []

    # Build a set of banks already searched (with non-error results)
    searched = set()
    for entry in results:
        if entry.get('search_result') and 'data' in entry['search_result'] and entry['search_result']['data']:
            searched.add((entry['Bank Name'], entry['Bank URL']))

    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bank_name = row['Bank Name']
            bank_url = row['Bank URL']
            if (bank_name, bank_url) in searched:
                print(f"Skipping {bank_name} ({bank_url}) - already has results.")
                continue
            print(f"Searching for publications for: {bank_name} ({bank_url})")
            result = search_publications(bank_name, bank_url)
            entry = {
                "Country/Region": row['Country/Region'],
                "Bank Name": bank_name,
                "Bank URL": bank_url,
                "search_result": result
            }
            results.append(entry)
            # Log after each bank
            logging.info(f"{bank_name} ({bank_url}): {json.dumps(result)[:500]}")
            # Save progress after each bank
            with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results written to {OUTPUT_PATH}")

main()