import csv
import requests
import os
import json
import time
import logging

API_URL = "https://laterical.com/api/call/"
QUERIES_PATH = os.path.join(os.path.dirname(__file__), 'outputs', 'generated_queries.json')
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

    # Write each bank's results to outputs/objects/{bank_name}.json, overwriting previous files
    objects_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'objects')
    os.makedirs(objects_dir, exist_ok=True)

    for idx, (bank_name, queries) in enumerate(queries_by_bank.items(), 1):
        bank_name_norm = bank_name.strip().lower()
        print(f"[{idx}/{len(queries_by_bank)}] Searching for queries for: {bank_name}")
        bank_results = []
        for query_obj in queries:
            # Support new format: query_obj is a dict with 'query' key
            if isinstance(query_obj, dict) and 'query' in query_obj:
                query_str = query_obj['query']
                topic = query_obj.get('topic')
            else:
                query_str = query_obj
                topic = None
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
            # Only keep top 3 web results inside each search_result item
            search_result = None
            if isinstance(result, dict) and 'data' in result and isinstance(result['data'], list):
                search_result = result['data']
            else:
                search_result = result
            # If search_result is a list, trim web results inside each item
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
            logging.info(f"{bank_name} [{query_str}]: {json.dumps(search_result)[:500]}")
            time.sleep(1)
        # Clean bank name for filesystem
        import re
        bank_name_clean = re.sub(r'[^\w\- ]', '', bank_name, flags=re.ASCII).strip().replace(' ', '_')
        out_path = os.path.join(objects_dir, f"{bank_name_clean}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                "Bank Name": bank_name,
                "search_results": bank_results
            }, f, ensure_ascii=False, indent=2)
        print(f"Results for {bank_name} written to {out_path}")
    print(f"All results written to {objects_dir}")

main()