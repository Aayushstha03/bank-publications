import csv
import requests
import os
import json
import time
import logging

API_URL = "https://laterical.com/api/call/"
QUERIES_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'generated_queries.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'search_results.json')
LOG_PATH = os.path.join(os.path.dirname(__file__), 'logs','search.log')
FAILED_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'search_failed.json')

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def search_query(query):
    payload = {
        "path": "search",
        "entity": [query]
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        # Check for API error in 'data' field
        if 'data' in data and data['data']:
            first = data['data'][0]
            if isinstance(first, dict) and 'error' in first:
                print(f"Search failed for query '{query}' (API error: {first['error'].get('code', '')})")
                logging.warning(f"API error for query '{query}': {first['error']}")
                return data
            return data
        else:
            raise ValueError("No data in response")
    except Exception as e:
        logging.warning(f"Search failed for query '{query}': {e}")
        return {"error": str(e)}


def main():
    # Load queries
    if not os.path.exists(QUERIES_PATH):
        print(f"Queries file not found: {QUERIES_PATH}")
        return
    with open(QUERIES_PATH, encoding='utf-8') as f:
        queries_by_bank = json.load(f)

    # Load failed list if present
    if os.path.exists(FAILED_PATH):
        try:
            with open(FAILED_PATH, encoding='utf-8') as f:
                failed_banks = json.load(f)
        except (json.JSONDecodeError, OSError):
            failed_banks = []
    else:
        failed_banks = []

    # Build a set of banks already searched (with non-error results)
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, encoding='utf-8') as f:
                results = json.load(f)
        except (json.JSONDecodeError, OSError):
            print(f"Warning: {OUTPUT_PATH} is empty or invalid. Starting with empty results.")
            results = []
    else:
        results = []
    searched = set()
    for entry in results:
        if entry.get('Bank Name') and entry.get('search_results'):
            searched.add(entry['Bank Name'])

    for bank_name, queries in queries_by_bank.items():
        if bank_name in searched:
            print(f"Skipping {bank_name} - already has results.")
            continue
        print(f"Searching for queries for: {bank_name}")
        bank_results = []
        for query in queries:
            print(f"  Running query: {query}")
            result = search_query(query)
            is_api_error = (
                isinstance(result, dict) and 'data' in result and result['data'] and
                isinstance(result['data'][0], dict) and 'error' in result['data'][0]
            )
            is_request_error = isinstance(result, dict) and 'error' in result
            if is_api_error or is_request_error:
                print(f"    Failed after all attempts: {query}")
                failed_banks.append({
                    "Bank Name": bank_name,
                    "query": query,
                    "error": result
                })
                with open(FAILED_PATH, 'w', encoding='utf-8') as f:
                    json.dump(failed_banks, f, ensure_ascii=False, indent=2)
                time.sleep(1)
                continue
            bank_results.append({
                "query": query,
                "search_result": result
            })
            logging.info(f"{bank_name} [{query}]: {json.dumps(result)[:500]}")
            time.sleep(1)
        # Write this bank's results immediately
        with open(OUTPUT_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "Bank Name": bank_name,
                "search_results": bank_results
            }, ensure_ascii=False, indent=2) + "\n")
        print(f"Results for {bank_name} written to {OUTPUT_PATH}")
    print(f"All results written to {OUTPUT_PATH}")

main()