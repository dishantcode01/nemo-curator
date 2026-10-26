import json
from pathlib import Path

from nemo_curator.pipeline import Pipeline
from nemo_curator.stages.text.io.reader import JsonlReader
from nemo_curator.stages.text.io.writer import JsonlWriter
from nemo_curator.stages.text.filters import ScoreFilter, DocumentFilter
from nemo_curator.stages.text.filters.heuristic import (
    WordCountFilter,
    NonAlphaNumericFilter,
)


INPUT = "data/processed/kyc_documents.jsonl"
OUTPUT_DIR = "data/processed/nemo_quality_filtered"


class RBICustomQualityFilter(DocumentFilter):
    """
    Custom quality rule designed specifically for the RBI KYC dataset.

    Reject chunks that are dominated by the repealed-circular appendix.
    """

    def __init__(self):
        super().__init__()
        self._name = "rbi_custom_quality"

    def score_document(self, text: str) -> float:
        text_lower = text.lower()

        # Count indicators that the chunk is the repealed-circular appendix
        indicators = [
            "list of circulars repealed",
            "circular no.",
            "dnbs (pd)",
            "dnbr",
            "rpcd.",
        ]

        matches = sum(indicator in text_lower for indicator in indicators)

        return float(matches)

    def keep_document(self, score: float) -> bool:
        # Reject if 3 or more appendix indicators are present
        return score < 3


# ---------------------------------------------------------
# Build NeMo Curator pipeline
# ---------------------------------------------------------

pipeline = Pipeline(
    name="rbi_kyc_quality_filtering",
    description="RBI KYC quality filtering using NeMo Curator"
)

# Read JSONL
pipeline.add_stage(
    JsonlReader(
        file_paths=INPUT,
        fields=["id", "text"],
        files_per_partition=1,
    )
)

# Rule 1: minimum word count
pipeline.add_stage(
    ScoreFilter(
        filter_obj=WordCountFilter(
            min_words=100,
            max_words=100000,
        ),
        text_field="text",
        score_field="word_count",
    )
)

# Rule 2: excessive non-alphanumeric content
pipeline.add_stage(
    ScoreFilter(
        filter_obj=NonAlphaNumericFilter(
            max_non_alpha_numeric_to_text_ratio=0.25
        ),
        text_field="text",
        score_field="non_alphanumeric_ratio",
    )
)

# Rule 3: OUR CUSTOM RBI-SPECIFIC RULE
pipeline.add_stage(
    ScoreFilter(
        filter_obj=RBICustomQualityFilter(),
        text_field="text",
        score_field="rbi_custom_score",
    )
)

# Write result
pipeline.add_stage(
    JsonlWriter(
        path=OUTPUT_DIR
    )
)

print("==============================================")
print("NeMo Curator RBI Quality Filtering")
print("==============================================")
print(f"Input : {INPUT}")
print(f"Output: {OUTPUT_DIR}")
print()
print("Rules:")
print("1. Minimum words >= 100")
print("2. Non-alphanumeric ratio <= 25%")
print("3. RBI custom appendix detection")
print()
print("Starting NeMo Curator pipeline...")

results = pipeline.run()

print()
print("NeMo Curator pipeline completed.")
print(f"Results: {results}")
