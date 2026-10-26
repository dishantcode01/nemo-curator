import json
import hashlib
from pathlib import Path

instruction_file = Path("data/processed/kyc_instructions.jsonl")
qa_file = Path("data/processed/kyc_qa.jsonl")
output_file = Path("data/processed/kyc_deduplicated.jsonl")

records = []

for file in [instruction_file, qa_file]:
    with file.open("r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

unique_records = []
seen = set()

for record in records:
    # Use the actual content rather than the ID for duplicate detection
    if record["type"] == "instruction":
        content = record["instruction"] + record["input"]
    else:
        content = record["question"] + record["answer"]

    content_hash = hashlib.sha256(
        content.strip().lower().encode("utf-8")
    ).hexdigest()

    if content_hash not in seen:
        seen.add(content_hash)
        unique_records.append(record)

duplicates_removed = len(records) - len(unique_records)

with output_file.open("w", encoding="utf-8") as f:
    for record in unique_records:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Before deduplication : {len(records)}")
print(f"Duplicates removed   : {duplicates_removed}")
print(f"After deduplication  : {len(unique_records)}")
print(f"Output               : {output_file}")
