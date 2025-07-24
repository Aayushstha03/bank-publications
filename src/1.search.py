import os
import json
import csv
import requests
import time
import re

API_URL = "https://laterical.com/api/call/"
BANKS_PATH = os.path.join(os.path.dirname(__file__), 'websites_deduped.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)
OBJECTS_DIR = os.path.join(OUTPUT_DIR, 'search_results')
os.makedirs(OBJECTS_DIR, exist_ok=True)
FAILED_PATH = os.path.join(OUTPUT_DIR, 'search_failed.json')

def generate_queries(bank_url):
    return [
        {
            "topic": "publications",
            "query": f"site:{bank_url} (inurl:publications | inurl:reports) (intitle:publications | intitle:reports)"
        },
        {
            "topic": "statistics",
            "query": f"site:{bank_url} (inurl:statistics | inurl:bulletin | inurl:data) (intitle:statistics | intitle:data | intitle:bulletin)"
        },
        {
            "topic": "monetary_policy",
            "query": f"site:{bank_url} (inurl:policy | inurl:regulations | inurl:guidelines) (intitle:policy | intitle:regulations)"
        },
        {
            "topic": "news",
            "query": f"site:{bank_url} (inurl:news | inurl:speeches | inurl:press) (intitle:news | intitle:speeches | intitle:press)"
        },
        {
            "topic": "research",
            "query": f"site:{bank_url} (inurl:research | inurl:working-papers | inurl:papers) (intitle:research | intitle:'working papers')"
        }
    ]

def search_query(query):
    payload = {
        "path": "search",
        "entity": [query]
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            first = data['data'][0]
            if isinstance(first, dict) and 'error' in first:
                print(f"Search failed for query '{query}' (API error: {first['error'].get('code', '')})")
                return data
            return data
        else:
            raise ValueError("No data in response")
    except Exception as e:
        print(f"Search failed for query '{query}': {e}")
        return {"error": str(e)}

def main():
    # Read banks
    with open(BANKS_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        banks = [(row['Bank Name'], row['Bank URL']) for row in reader]

    # Load failed list if present
    if os.path.exists(FAILED_PATH):
        try:
            with open(FAILED_PATH, encoding='utf-8') as f:
                failed_banks = json.load(f)
        except (json.JSONDecodeError, OSError):
            failed_banks = []
    else:
        failed_banks = []

    total_banks = len(banks)
    for idx, (bank_name, bank_url) in enumerate(banks, 1):
        print(f"[{idx}/{total_banks}] Processing: {bank_name}")
        queries = generate_queries(bank_url)
        bank_results = []
        for query_obj in queries:
            query_str = query_obj['query']
            topic = query_obj['topic']
            print(f"  Running query: {query_str}")
            result = search_query(query_str)
            is_api_error = (
                isinstance(result, dict) and 'data' in result and result['data'] and
                isinstance(result['data'][0], dict) and 'error' in result['data'][0]
            )
            is_request_error = isinstance(result, dict) and 'error' in result
            if is_api_error or is_request_error:
                failed_banks.append({
                    "Bank Name": bank_name,
                    "query": query_str,
                    "error": result
                })
                with open(FAILED_PATH, 'w', encoding='utf-8') as f:
                    json.dump(failed_banks, f, ensure_ascii=False, indent=2)
                time.sleep(1)
                continue
            search_result = None
            if isinstance(result, dict) and 'data' in result and isinstance(result['data'], list):
                search_result = result['data']
            else:
                search_result = result
            if isinstance(search_result, list):
                for item in search_result:
                    if (
                        isinstance(item, dict)
                        and 'results' in item
                        and isinstance(item['results'], dict)
                        and 'web' in item['results']
                        and isinstance(item['results']['web'], list)
                    ):
                        item['results']['web'] = item['results']['web'][:3]
            bank_results.append({
                "topic": topic,
                "search_result": search_result
            })
            time.sleep(1)
        bank_name_clean = re.sub(r'[^\w\- ]', '', bank_name).strip().replace(' ', '_')
        out_path = os.path.join(OBJECTS_DIR, f"{bank_name_clean}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                "Bank Name": bank_name,
                "search_results": bank_results
            }, f, ensure_ascii=False, indent=2)
        print(f"Results for {bank_name} written to {out_path}")
    print(f"All results written to {OBJECTS_DIR}")

if __name__ == "__main__":
    main()
