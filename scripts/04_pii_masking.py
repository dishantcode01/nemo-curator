import json
import re
from pathlib import Path

INPUT = Path("data/processed/pii_demo.jsonl")
OUTPUT = Path("data/processed/pii_masked.jsonl")


# ---------- PII DETECTION PATTERNS ----------

PATTERNS = {
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "PHONE": re.compile(
        r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)"
    ),

    "PAN": re.compile(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    ),

    "AADHAAR": re.compile(
        r"(?<!\d)\d{4}[-\s]?\d{4}[-\s]?\d{4}(?!\d)"
    ),
}


def mask_pii(text):
    counts = {
        "EMAIL": 0,
        "PHONE": 0,
        "PAN": 0,
        "AADHAAR": 0,
    }

    # Detect and replace each PII type
    for pii_type, pattern in PATTERNS.items():
        matches = pattern.findall(text)
        counts[pii_type] = len(matches)

        text = pattern.sub(f"[{pii_type}]", text)

    return text, counts


# ---------- PROCESS DATA ----------

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

total_records = 0
records_with_pii = 0

total_counts = {
    "EMAIL": 0,
    "PHONE": 0,
    "PAN": 0,
    "AADHAAR": 0,
}

with INPUT.open("r", encoding="utf-8") as fin, \
     OUTPUT.open("w", encoding="utf-8") as fout:

    for line in fin:
        record = json.loads(line)

        original_text = record["text"]

        masked_text, counts = mask_pii(original_text)

        if sum(counts.values()) > 0:
            records_with_pii += 1

        for key in total_counts:
            total_counts[key] += counts[key]

        record["text"] = masked_text

        fout.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )

        total_records += 1


print("\n===== PII MASKING REPORT =====")
print(f"Total records       : {total_records}")
print(f"Records with PII    : {records_with_pii}")
print(f"Records without PII : {total_records - records_with_pii}")

print("\nPII detected:")
for key, value in total_counts.items():
    print(f"{key:10}: {value}")

print(f"\nOutput              : {OUTPUT}")
