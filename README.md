# NeMo Curator — Dataset Quality & Insights Pipeline

A comprehensive dataset curation and quality analysis pipeline built with **NVIDIA NeMo Curator** and **Streamlit**. Designed for auditing, cleaning, and validating enterprise text datasets (with a specialized showcase for RBI KYC regulatory documents).

---

## 🌟 Key Features

1. **NeMo Curator Quality Filtering**:
   - Heuristic rules: `WordCountFilter` and `NonAlphaNumericFilter`.
   - Domain-specific rules: Custom `RBICustomQualityFilter` for filtering regulatory appendix noise and repealed circulars.
   - Batch-mode execution optimized for resource-constrained environments.

2. **PII Detection & Masking**:
   - High-precision detection for sensitive Indian identifiers: Aadhaar numbers, Permanent Account Numbers (PAN), Indian phone numbers, and email addresses.
   - Safe redaction/masking with detailed stage metrics and preview diffs.

3. **Exact & Semantic Deduplication**:
   - MD5 document hash matching to remove exact repeated text records.
   - Metrics reporting deduplication ratios, unique documents retained, and duplicate clusters.

4. **Interactive Streamlit Dashboard**:
   - Upload custom `.jsonl` or `.json` datasets for real-time curation.
   - Live stage toggles, slider-driven threshold customization, and downloadable curated outputs.
   - Visual KPI cards, quality score distributions, and inspection tables.

---

## 🏗️ Project Architecture

```
nemo-curator-project/
├── app/
│   ├── app.py              # Streamlit dashboard application
│   └── pipeline.py         # NeMo Curator runtime processing stages & filters
├── dashboard/              # Stored pipeline report metrics & KPI summaries
│   ├── final_project_report.json
│   ├── quality_report.json
│   └── stats.json
├── data/
│   ├── raw/                # Original raw documents & samples
│   ├── processed/          # Intermediate curated & deduplicated datasets
│   └── final/              # Final high-quality dataset outputs
├── scripts/                # Standalone step-by-step pipeline scripts (01-09)
│   ├── 01_extract.py
│   ├── 02_chunk.py
│   ├── 03_nemo_quality_filter.py
│   ├── 04_nemo_pii_masking.py
│   ├── 05_nemo_exact_dedup.py
│   └── ...
├── pyrightconfig.json      # Python language server configuration
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Docker (recommended for running NeMo Curator on macOS/Linux) or a Linux environment with Python 3.10–3.12.
- NVIDIA NeMo Curator (`pip install nemo-curator`).

### 2. Running with Docker
```bash
docker run -it -p 8501:8501 -v $(pwd):/workspace ubuntu:24.04 bash
```
Inside the container:
```bash
source .venv/bin/activate
streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0
```

### 3. Running Locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit nemo-curator
streamlit run app/app.py
```

Open your browser at `http://localhost:8501` to view the dashboard.

---

## 📊 Pipeline Stages

| Stage | Rule / Filter | Description |
|---|---|---|
| **Quality** | `WordCountFilter(100..100000)` | Removes short stubs and fragments |
| **Quality** | `NonAlphaNumericFilter(<=0.25)` | Filters out corrupted or non-text content |
| **Quality** | `RBICustomQualityFilter` | Flags repeated legal boilerplate & repealed appendices |
| **Privacy** | `PII Masker` | Redacts Aadhaar (`XXXX-XXXX-1234`), PAN, phone, and email |
| **Deduplication** | Exact Dedup | Eliminates verbatim duplicates across document collections |

---

## 📄 License
This project is open-source under the MIT License.
