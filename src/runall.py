import subprocess
import sys
import os

scripts = [
    "1.search.py",
    "2.filter_urls.py",
    "3.collect_high_confidence_listing_urls.py",
]

src_dir = os.path.dirname(os.path.abspath(__file__))

for script in scripts:
    script_path = os.path.join(src_dir, script)
    print(f"\n=== Running {script} ===")
    result = subprocess.run([sys.executable, script_path])
print("\nAll scripts completed.")
