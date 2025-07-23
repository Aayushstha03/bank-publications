import csv

# Path to the CSV file
import os
csv_path = os.path.join(os.path.dirname(__file__), "websites.csv")

unique_banks = set()
with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bank_name = row["Bank Name"].strip().lower()
        unique_banks.add(bank_name)

print(f"Unique banks (normalized): {len(unique_banks)}")
