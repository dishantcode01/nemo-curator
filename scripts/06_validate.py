import json
from pathlib import Path

input_file = Path("data/processed/kyc_deduplicated.jsonl")
output_file = Path("data/final/kyc_cleaned_dataset.jsonl")

output_file.parent.mkdir(parents=True, exist_ok=True)

valid = []
invalid = []

with input_file.open("r", encoding="utf-8") as f:
    for line_number, line in enumerate(f, 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            invalid.append((line_number, "Invalid JSON"))
            continue

        if not record.get("id"):
            invalid.append((line_number, "Missing ID"))
            continue

        if record.get("type") == "instruction":
            required = ["instruction", "input", "output"]
        elif record.get("type") == "qa":
            required = ["question", "answer"]
        else:
            invalid.append((line_number, "Invalid type"))
            continue

        if any(not record.get(field) for field in required):
            invalid.append((line_number, "Missing required field"))
            continue

        valid.append(record)

with output_file.open("w", encoding="utf-8") as f:
    for record in valid:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

ids = [r["id"] for r in valid]

print("===== DATASET VALIDATION =====")
print(f"Total records    : {len(valid) + len(invalid)}")
print(f"Valid records    : {len(valid)}")
print(f"Invalid records  : {len(invalid)}")
print(f"Unique IDs       : {len(ids) == len(set(ids))}")
print(f"JSONL structure  : {'PASS' if valid else 'FAIL'}")
print(f"Output           : {output_file}")

if invalid:
    print("\nInvalid records:")
    for item in invalid:
        print(item)
