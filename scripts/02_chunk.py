import json
from pathlib import Path

input_file = Path("data/raw/kyc_raw.txt")
output_file = Path("data/processed/kyc_documents.jsonl")

text = input_file.read_text(encoding="utf-8")

# Normalize whitespace
words = text.split()

# Target approximately 750 words per chunk
chunk_size = 750

chunks = []

for i in range(0, len(words), chunk_size):
    chunk = " ".join(words[i:i + chunk_size])
    chunks.append(chunk)

with output_file.open("w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks, 1):
        record = {
            "id": f"kyc_{i:03d}",
            "text": chunk
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Total words : {len(words):,}")
print(f"Chunks      : {len(chunks)}")
print(f"Output      : {output_file}")
