import json
from pathlib import Path

INPUT = Path("data/processed/rbi_kyc_pii_masked.jsonl")
OUTPUT = Path("data/processed/rbi_kyc_with_duplicates.jsonl")

records = []

with INPUT.open("r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))

# Intentionally duplicate the first 5 records
duplicate_records = records[:5]

combined = records + duplicate_records

with OUTPUT.open("w", encoding="utf-8") as f:
    for record in combined:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print("===== DUPLICATE CREATION =====")
print(f"Original records       : {len(records)}")
print(f"Intentional duplicates : {len(duplicate_records)}")
print(f"Records before dedup   : {len(combined)}")
print(f"Expected after dedup   : {len(records)}")
print(f"Output                 : {OUTPUT}")
