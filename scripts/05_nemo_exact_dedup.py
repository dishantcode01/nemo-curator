import json
import hashlib
from pathlib import Path

from nemo_curator.stages.base import ProcessingStage


class RBIExactDedupStage(ProcessingStage):

    name = "rbi_exact_deduplication"

    def __init__(self):
        super().__init__()

    def process(self, data):
        """
        Calculate an exact content fingerprint for a record.
        """
        text = data["text"].strip()

        fingerprint = hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

        data["_dedup_fingerprint"] = fingerprint

        return data


def main():

    input_file = Path(
        "data/processed/rbi_kyc_with_duplicates.jsonl"
    )

    output_file = Path(
        "data/processed/rbi_kyc_deduplicated.jsonl"
    )

    stage = RBIExactDedupStage()

    seen = set()

    total = 0
    duplicates = 0
    unique = 0

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with input_file.open("r", encoding="utf-8") as fin, \
         output_file.open("w", encoding="utf-8") as fout:

        for line in fin:

            record = json.loads(line)

            record = stage.process(record)

            total += 1

            fingerprint = record["_dedup_fingerprint"]

            if fingerprint in seen:
                duplicates += 1
                continue

            seen.add(fingerprint)

            unique += 1

            fout.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    print()
    print("===== RBI EXACT DEDUPLICATION =====")
    print(f"Stage                  : {stage.name}")
    print(f"Input records           : {total}")
    print(f"Unique records          : {unique}")
    print(f"Duplicate records      : {duplicates}")
    print(f"Output records          : {unique}")
    print(f"Duplicates removed     : {duplicates}")
    print(f"Output                  : {output_file}")


if __name__ == "__main__":
    main()
