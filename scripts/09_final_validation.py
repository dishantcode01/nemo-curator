import json
from pathlib import Path

INPUT = Path("data/processed/rbi_kyc_deduplicated.jsonl")

records = []
invalid_json = 0
missing_text = 0
missing_id = 0

with INPUT.open("r", encoding="utf-8") as f:
    for line in f:
        try:
            record = json.loads(line)
            records.append(record)

            if not record.get("id"):
                missing_id += 1

            if not record.get("text"):
                missing_text += 1

        except json.JSONDecodeError:
            invalid_json += 1

ids = [r["id"] for r in records if r.get("id")]
texts = [r["text"] for r in records if r.get("text")]

unique_ids = len(ids) == len(set(ids))
unique_texts = len(texts) == len(set(texts))

valid = (
    len(records) > 0
    and invalid_json == 0
    and missing_id == 0
    and missing_text == 0
    and unique_ids
    and unique_texts
)

print()
print("===== FINAL DATASET VALIDATION =====")
print(f"Input file          : {INPUT}")
print(f"Total records       : {len(records)}")
print(f"Invalid JSON        : {invalid_json}")
print(f"Missing IDs         : {missing_id}")
print(f"Missing text        : {missing_text}")
print(f"Unique IDs          : {unique_ids}")
print(f"Unique text records : {unique_texts}")
print(f"VALID DATASET       : {'PASS' if valid else 'FAIL'}")

if valid:
    print("\nFinal dataset is ready for downstream use.")
else:
    print("\nFinal dataset requires correction.")
