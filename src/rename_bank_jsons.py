import os
import json
import re

objects_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'objects')
files = [f for f in os.listdir(objects_dir) if f.endswith('.json')]

for idx, filename in enumerate(sorted(files), 1):
    file_path = os.path.join(objects_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Skipping {filename}: {e}")
            continue
    bank_name = data.get('Bank Name', f'unknown_{idx}')
    # Clean bank name for filesystem
    bank_name_clean = re.sub(r'[^\w\- ]', '', bank_name).strip().replace(' ', '_')
    new_filename = f"{idx:03d}_{bank_name_clean}.json"
    new_path = os.path.join(objects_dir, new_filename)
    os.rename(file_path, new_path)
    print(f"Renamed {filename} -> {new_filename}")
