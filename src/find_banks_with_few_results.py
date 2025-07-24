import os
import json

SEARCH_RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'data', 'search_results')

def count_total_results(data):
    total = 0
    for search_result in data.get('search_results', []):
        for sr in search_result.get('search_result', []):
            web_list = sr.get('results', {}).get('web', [])
            total += len(web_list)
    return total

def main():
    banks_with_few_results = []
    files = [f for f in os.listdir(SEARCH_RESULTS_DIR) if f.endswith('.json')]
    for fname in files:
        file_path = os.path.join(SEARCH_RESULTS_DIR, fname)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_results = count_total_results(data)
        if total_results <= 5:
            bank_name = data.get('Bank Name', fname.replace('.json', ''))
            banks_with_few_results.append({
                'bank_name': bank_name,
                'total_results': total_results
            })
    out_path = os.path.join(os.path.dirname(__file__), 'data', 'banks_with_few_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(banks_with_few_results, f, ensure_ascii=False, indent=2)
    print(f"Saved banks with few results to {out_path}")

if __name__ == "__main__":
    main()
