import subprocess
import sys
import os

# List of scripts to run in order
scripts = [
    '1.search-query-generation.py',
    '2.search.py',
    '3.dedupe_and_filter_web_blocks.py',
    '4.filter_listing_pages_with_llm.py'
]

src_dir = os.path.dirname(os.path.abspath(__file__))

for script in scripts:
    script_path = os.path.join(src_dir, script)
    print(f"Running {script_path} ...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        print(f"Error running {script}: exit code {result.returncode}")
        break
print("All scripts completed.")
