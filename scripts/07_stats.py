import json
from pathlib import Path

raw_text = Path("data/raw/kyc_raw.txt").read_text(encoding="utf-8")

def count_lines(path):
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def count_types(path):
    instructions = 0
    qa = 0

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record.get("type") == "instruction":
                instructions += 1
            elif record.get("type") == "qa":
                qa += 1

    return instructions, qa

raw_words = len(raw_text.split())
initial_chunks = count_lines(
    Path("data/processed/kyc_documents.jsonl")
)
filtered_chunks = count_lines(
    Path("data/processed/kyc_filtered.jsonl")
)
instructions, qa = count_types(
    Path("data/processed/kyc_deduplicated.jsonl")
)
final_examples = count_lines(
    Path("data/final/kyc_cleaned_dataset.jsonl")
)

stats = {
    "raw_words": raw_words,
    "initial_chunks": initial_chunks,
    "filtered_chunks": filtered_chunks,
    "removed_chunks": initial_chunks - filtered_chunks,
    "instructions": instructions,
    "qa": qa,
    "before_deduplication": instructions + qa,
    "final_examples": final_examples
}

Path("dashboard").mkdir(exist_ok=True)

Path("dashboard/stats.json").write_text(
    json.dumps(stats, indent=2),
    encoding="utf-8"
)

print("===== DATASET STATISTICS =====")
for key, value in stats.items():
    print(f"{key:25}: {value}")

print("\nSaved to dashboard/stats.json")
