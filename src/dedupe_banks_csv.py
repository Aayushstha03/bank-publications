import csv
import os
from collections import defaultdict

# Input and output paths
in_path = os.path.join(os.path.dirname(__file__), "websites.csv")
out_path = os.path.join(os.path.dirname(__file__), "websites_deduped.csv")

# Map: normalized bank name -> { 'Bank Name': original, 'Bank URL': url, 'Country/Region': [list] }
bank_map = {}

with open(in_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bank_name_norm = row["Bank Name"].strip().lower()
        country = row["Country/Region"].strip()
        url = row["Bank URL"].strip()
        if bank_name_norm not in bank_map:
            bank_map[bank_name_norm] = {
                'Bank Name': row["Bank Name"].strip(),
                'Bank URL': url,
                'Country/Region': [country]
            }
        else:
            if country not in bank_map[bank_name_norm]['Country/Region']:
                bank_map[bank_name_norm]['Country/Region'].append(country)

# Write deduped CSV
with open(out_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Bank Name", "Country/Region", "Bank URL"])
    for bank in bank_map.values():
        countries = "; ".join(bank['Country/Region'])
        writer.writerow([bank['Bank Name'], countries, bank['Bank URL']])

print(f"Deduped file written to {out_path} with {len(bank_map)} unique banks.")
