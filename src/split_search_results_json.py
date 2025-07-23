import os
import regex
import json
import re

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
        bank_name = obj.get('Bank Name', f'unknown_{idx}')
        # Clean bank name for filesystem
        bank_name_clean = re.sub(r'[^\w\- ]', '', bank_name, flags=re.ASCII).strip().replace(' ', '_')
        new_filename = f"{idx:03d}_{bank_name_clean}.json"
        out_path = os.path.join(output_dir, new_filename)
        with open(out_path, 'w', encoding='utf-8') as out_f:
            json.dump(obj, out_f, indent=2, ensure_ascii=False)
        print(f"Wrote {new_filename}")
    except Exception as e:
        print(f"Failed to parse object {idx}: {e}")
