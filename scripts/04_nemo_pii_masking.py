import json
import re
from pathlib import Path

from nemo_curator.stages.base import ProcessingStage


class RBIPiiMaskingStage(ProcessingStage):

    name = "rbi_pii_masking"

    def __init__(self):
        super().__init__()

        self.patterns = {
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

    def process(self, data):
        text = data["text"]

        counts = {
            "EMAIL": 0,
            "PHONE": 0,
            "PAN": 0,
            "AADHAAR": 0,
        }

        for pii_type, pattern in self.patterns.items():

            matches = pattern.findall(text)
            counts[pii_type] = len(matches)

            text = pattern.sub(
                f"[{pii_type}]",
                text
            )

        data["text"] = text
        data["pii_detected"] = sum(counts.values()) > 0
        data["pii_counts"] = counts

        return data


def main():

    input_file = Path("data/processed/pii_demo.jsonl")
    output_file = Path("data/processed/nemo_pii_masked.jsonl")

    stage = RBIPiiMaskingStage()

    total = 0
    records_with_pii = 0

    totals = {
        "EMAIL": 0,
        "PHONE": 0,
        "PAN": 0,
        "AADHAAR": 0,
    }

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with input_file.open("r", encoding="utf-8") as fin, \
         output_file.open("w", encoding="utf-8") as fout:

        for line in fin:

            record = json.loads(line)

            result = stage.process(record)

            if result["pii_detected"]:
                records_with_pii += 1

            for key in totals:
                totals[key] += result["pii_counts"][key]

            fout.write(
                json.dumps(
                    result,
                    ensure_ascii=False
                ) + "\n"
            )

            total += 1

    print()
    print("===== NeMo CURATOR PII REPORT =====")
    print(f"Stage               : {stage.name}")
    print(f"Input records       : {total}")
    print(f"Records with PII    : {records_with_pii}")
    print(f"Records without PII : {total - records_with_pii}")

    print()
    print("PII detected:")

    for key, value in totals.items():
        print(f"{key:10}: {value}")

    print()
    print(f"Output              : {output_file}")


if __name__ == "__main__":
    main()
