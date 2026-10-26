import json
from pathlib import Path

input_file = Path("data/processed/kyc_documents.jsonl")
output_file = Path("data/processed/kyc_filtered.jsonl")

kept = []
removed = []

with input_file.open("r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)

        text = record.get("text", "").strip()

        # Remove chunks that are primarily the repealed-circulars appendix
        if record["id"] == "kyc_046":
            removed.append({
                "id": record["id"],
                "reason": "Appendix/list of repealed circulars; not substantive KYC guidance"
            })
            continue

        # Basic quality checks
        if not text:
            removed.append({
                "id": record["id"],
                "reason": "Empty text"
            })
            continue

        if len(text.split()) < 100:
            removed.append({
                "id": record["id"],
                "reason": "Too short"
            })
            continue

        kept.append(record)

with output_file.open("w", encoding="utf-8") as f:
    for record in kept:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Input chunks   : {len(kept) + len(removed)}")
print(f"Kept chunks    : {len(kept)}")
print(f"Removed chunks : {len(removed)}")

for item in removed:
    print(f"Removed: {item['id']} — {item['reason']}")

print(f"Output         : {output_file}")
