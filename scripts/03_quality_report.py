import json
from pathlib import Path

input_file = Path("data/processed/kyc_documents.jsonl")
output_dir = Path("data/processed/nemo_quality_filtered")

# Find NeMo's output JSONL
output_files = list(output_dir.glob("*.jsonl"))

if not output_files:
    raise FileNotFoundError("No NeMo Curator output JSONL found.")

output_file = output_files[0]

# Read input IDs
with input_file.open("r", encoding="utf-8") as f:
    input_records = [json.loads(line) for line in f]

# Read NeMo output IDs
with output_file.open("r", encoding="utf-8") as f:
    output_records = [json.loads(line) for line in f]

input_ids = {r["id"] for r in input_records}
passed_ids = {r["id"] for r in output_records}

failed_ids = input_ids - passed_ids

report = {
    "input_records": len(input_records),
    "passed_records": len(passed_ids),
    "failed_records": len(failed_ids),
    "pass_rate_percent": round(len(passed_ids) / len(input_records) * 100, 2),
    "fail_rate_percent": round(len(failed_ids) / len(input_records) * 100, 2),
    "failed_ids": sorted(failed_ids),
    "output_file": str(output_file),
}

Path("dashboard").mkdir(exist_ok=True)

Path("dashboard/quality_report.json").write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print("===== NEMO CURATOR QUALITY REPORT =====")
print(f"Input records  : {report['input_records']}")
print(f"Passed records : {report['passed_records']}")
print(f"Failed records : {report['failed_records']}")
print(f"Pass rate      : {report['pass_rate_percent']}%")
print(f"Fail rate      : {report['fail_rate_percent']}%")
print(f"Failed IDs     : {report['failed_ids']}")
print(f"NeMo output    : {report['output_file']}")
print()
print("Saved to dashboard/quality_report.json")
