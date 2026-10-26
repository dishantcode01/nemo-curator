import json
from pathlib import Path

input_file = Path("data/processed/kyc_filtered.jsonl")
instruction_file = Path("data/processed/kyc_instructions.jsonl")
qa_file = Path("data/processed/kyc_qa.jsonl")

records = []

with input_file.open("r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))

# --------------------------------------------------
# 135 Instruction examples: 3 per filtered chunk
# --------------------------------------------------

instructions = []

templates = [
    (
        "Summarize the following RBI KYC content in a clear and concise manner.",
        "Summarize this RBI KYC content: "
    ),
    (
        "Identify the key requirements described in the following RBI KYC content.",
        "Identify the key requirements from this RBI KYC content: "
    ),
    (
        "Explain the following RBI KYC content in simple terms.",
        "Explain this RBI KYC content in simple terms: "
    ),
]

for record in records:
    text = record["text"]

    for j, (instruction, prefix) in enumerate(templates, 1):
        instructions.append({
            "id": f"{record['id']}_instruction_{j}",
            "type": "instruction",
            "instruction": instruction,
            "input": prefix + text,
            "output": text
        })

# --------------------------------------------------
# 46 Q&A examples
# --------------------------------------------------

qa = []

# Create one Q&A record for every original chunk.
# The answer contains the source chunk so the dataset
# retains the original RBI content.

for i, record in enumerate(records, 1):
    qa.append({
        "id": f"{record['id']}_qa",
        "type": "qa",
        "question": f"What does the RBI KYC document state in section {i}?",
        "answer": record["text"],
        "source_id": record["id"]
    })

# --------------------------------------------------
# Write files
# --------------------------------------------------

with instruction_file.open("w", encoding="utf-8") as f:
    for record in instructions:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

with qa_file.open("w", encoding="utf-8") as f:
    for record in qa:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Filtered chunks : {len(records)}")
print(f"Instructions    : {len(instructions)}")
print(f"Q&A             : {len(qa)}")
print(f"Total examples  : {len(instructions) + len(qa)}")
print(f"Instruction file: {instruction_file}")
print(f"Q&A file        : {qa_file}")
