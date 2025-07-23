import os
import regex
import json

input_path = os.path.join(os.path.dirname(__file__), 'outputs', 'search_results.json')
output_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'objects')
os.makedirs(output_dir, exist_ok=True)

with open(input_path, 'r', encoding='utf-8') as f:
    data = f.read()
# Regex to match top-level JSON objects (non-greedy) using the 'regex' module
json_objects = regex.findall(r'{(?:[^{}]|(?R))*}', data, regex.DOTALL)

print(f"Found {len(json_objects)} objects.")

for idx, obj_str in enumerate(json_objects, 1):
    try:
        obj = json.loads(obj_str)
        with open(os.path.join(output_dir, f'final_bank_result_{idx}.json'), 'w', encoding='utf-8') as out_f:
            json.dump(obj, out_f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to parse object {idx}: {e}")
