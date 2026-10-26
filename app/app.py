import json
import html
import re
import time
import textwrap
from pathlib import Path

import streamlit as st

from pipeline import (
    process_jsonl,
    save_dataset,
    PII_FILTER_SPECS,
    mask_pii,
    mask_pii_detailed,
    mask_preview_string,
)


# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="NeMo Curator — Dataset Quality & Insights",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# Figma-inspired design system
# ---------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg: #f4f6f8;
    --white: #ffffff;
    --border: #d9dee6;
    --text: #111827;
    --muted: #6b7280;
    --blue: #1e3a8a;
    --blue-2: #2563eb;
    --blue-soft: #eef2ff;
    --green-bg: #ecfdf5;
    --green-border: #a7f3d0;
    --green-text: #166534;
    --amber-bg: #fffbeb;
    --amber-border: #fde68a;
    --amber-text: #92400e;
}

html, body, [class*="css"] {
    font-family: "Geist", sans-serif;
}

.stApp {
    background: var(--bg);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1440px;
    padding: 24px 32px 40px 32px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 1px solid var(--border) !important;
    visibility: visible !important;
    display: block !important;
}

section[data-testid="stSidebar"] > div {
    padding: 24px 16px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 24px;
}

.brand-mark {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--blue);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: "Geist Mono";
    font-weight: 700;
}

.brand-title {
    font-weight: 700;
    font-size: 16px;
    color: var(--text);
    line-height: 20px;
}

.brand-subtitle {
    color: var(--blue-2);
    font-family: "Geist Mono";
    font-size: 10px;
    font-weight: 600;
}

.sidebar-label {
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .04em;
    font-size: 11px;
    font-weight: 600;
    margin: 16px 0 8px;
}

.active-dataset {
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
    margin-top: 18px;
    background: white;
}

.dataset-name {
    font-family: "Geist Mono";
    font-size: 12px;
    font-weight: 600;
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.dataset-meta {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    color: var(--muted);
    font-size: 11px;
}

.active-pill {
    background: #dbeafe;
    color: #1d4ed8;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
}

/* Sidebar navigation — stable, readable states */
div[data-testid="stSidebar"] div[data-testid="stButton"] {
    margin: 4px 0 !important;
}

div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    width: 100% !important;
    min-height: 40px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 8px 14px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    opacity: 1 !important;
    cursor: pointer !important;
    transition: background-color 0.15s ease,
                border-color 0.15s ease,
                color 0.15s ease !important;
}

/* Inactive sidebar buttons */
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid="baseButton-secondary"],
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    color: #1f2937 !important;
    -webkit-text-fill-color: #1f2937 !important;
}

/* Hovering an inactive sidebar button - NEVER blank or transparent */
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid="baseButton-secondary"]:hover,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {
    background: #f1f5f9 !important;
    border-color: #2563eb !important;
    color: #1d4ed8 !important;
    -webkit-text-fill-color: #1d4ed8 !important;
}

/* Selected / Active sidebar button */
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
    background: #2563eb !important;
    border: 1px solid #1d4ed8 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Hovering the selected sidebar button */
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover {
    background: #1d4ed8 !important;
    border-color: #1e40af !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Keep nested button text readable and visible under all hover states */
div[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button span,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button div {
    opacity: 1 !important;
    color: inherit !important;
    -webkit-text-fill-color: currentColor !important;
}

/* Header */
.page-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

.page-subtitle {
    color: var(--muted);
    font-size: 14px;
    margin-top: 4px;
}

.status {
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    color: var(--green-text);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 16px 0 24px;
    font-size: 13px;
    font-weight: 500;
}

/* Global Buttons: Always legible with crisp borders and hover */
.stButton > button,
.stDownloadButton > button {
    border-radius: 8px !important;
    min-height: 40px !important;
    font-family: "Geist", sans-serif !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}

/* General Secondary button */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]),
.stDownloadButton > button[kind="secondary"],
.stDownloadButton > button[data-testid="baseButton-secondary"],
.stDownloadButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
    background: #ffffff !important;
    color: #1f2937 !important;
    border: 1px solid #cbd5e1 !important;
    -webkit-text-fill-color: #1f2937 !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover,
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover,
.stDownloadButton > button[kind="secondary"]:hover,
.stDownloadButton > button[data-testid="baseButton-secondary"]:hover,
.stDownloadButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {
    background: #f8fafc !important;
    color: #2563eb !important;
    border-color: #2563eb !important;
    -webkit-text-fill-color: #2563eb !important;
}

/* General Primary button */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
.stDownloadButton > button[kind="primary"],
.stDownloadButton > button[data-testid="baseButton-primary"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #1d4ed8 !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover,
.stDownloadButton > button[data-testid="baseButton-primary"]:hover {
    background: #1d4ed8 !important;
    color: #ffffff !important;
    border-color: #1e40af !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button p,
.stButton > button span,
.stDownloadButton > button p,
.stDownloadButton > button span {
    opacity: 1 !important;
    color: inherit !important;
    -webkit-text-fill-color: currentColor !important;
}

/* Upload */
div[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #cbd5e1;
    border-radius: 10px;
    padding: 8px;
}

/* Metric cards */
.metric-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    min-height: 120px;
}

.metric-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.metric-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 500;
}

.metric-icon {
    width: 32px;
    height: 32px;
    background: var(--bg);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--blue);
    font-weight: 700;
}

.metric-value {
    margin-top: 12px;
    font-family: "Geist Mono";
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
}

.metric-unit {
    font-family: "Geist";
    font-size: 14px;
    color: var(--muted);
    font-weight: 400;
}

.metric-foot {
    margin-top: 7px;
    font-size: 11px;
    color: var(--muted);
}

/* Panels */
.panel {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}

.panel-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: var(--text);
    font-size: 15px;
    font-weight: 600;
}

.panel-line {
    height: 1px;
    background: var(--border);
    margin: 16px 0;
}

.badge {
    background: var(--blue-soft);
    color: var(--blue);
    border-radius: 4px;
    padding: 4px 8px;
    font-family: "Geist Mono";
    font-size: 11px;
    font-weight: 600;
}

.progress-row {
    margin: 14px 0;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: var(--text);
    margin-bottom: 7px;
}

.progress-track {
    height: 6px;
    background: #e5e7eb;
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--blue-2);
    border-radius: 10px;
}

.pii-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #eef0f3;
    font-size: 13px;
}

.pii-row:last-child {
    border-bottom: 0;
}

.pii-left {
    display: flex;
    gap: 9px;
    align-items: center;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--blue-2);
}

.big-number {
    font-family: "Geist Mono";
    font-size: 26px;
    font-weight: 700;
    color: var(--text);
}

.small-label {
    color: var(--muted);
    font-size: 12px;
}

.insight {
    padding: 14px 0;
    border-bottom: 1px solid #eef0f3;
}

.insight:last-child {
    border-bottom: 0;
}

.insight-title {
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.insight-text {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.55;
    margin-top: 7px;
}

.quick-action {
    border: 1px solid var(--border);
    background: white;
    border-radius: 8px;
    padding: 11px 14px;
    font-size: 13px;
    color: var(--text);
}

.empty-state {
    background: white;
    border: 1px dashed var(--border);
    border-radius: 12px;
    padding: 60px 30px;
    text-align: center;
    color: var(--muted);
}

.empty-title {
    color: var(--text);
    font-size: 18px;
    font-weight: 600;
}

.mono {
    font-family: "Geist Mono";
}

.mini-card { 
    background: #f8fafc; 
    border: 1px solid #d9dee6; 
    border-radius: 10px; 
    padding: 16px;
    transition: all 0.2s ease;
}
.mini-card:hover {
    background: #ffffff;
    border-color: #93c5fd;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.06);
}

.section-title { font-size: 20px; font-weight: 700; color: #111827; }
.section-subtitle { color: #6b7280; font-size: 13px; margin-top: 4px; margin-bottom: 14px; }

.evidence-grid { display: grid; grid-template-columns: 1fr 36px 1fr; gap: 12px; align-items: stretch; }
.evidence-card { 
    background: #fff; 
    border: 1px solid #d9dee6; 
    border-radius: 10px; 
    padding: 18px; 
    min-height: 150px; 
    transition: all 0.2s ease;
}
.evidence-card:hover {
    border-color: #2563eb;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08);
}
.evidence-label { font-family: "Geist Mono", monospace; font-size: 11px; font-weight: 700; color: #4b5563; letter-spacing: .03em; margin-bottom: 10px; }
.evidence-text { font-family: "Geist Mono", monospace; font-size: 12px; line-height: 1.6; color: #111827; white-space: pre-wrap; word-break: break-word; max-height: 260px; overflow: auto; }
.evidence-arrow { display: flex; align-items: center; justify-content: center; font-size: 24px; color: #2563eb; font-weight: 700; }

/* Filter Spec Deep Dive Cards */
.filter-spec-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin: 16px 0;
}
.filter-spec-card {
    background: #ffffff;
    border: 1px solid #d9dee6;
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.filter-spec-card:hover {
    border-color: #2563eb;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.08);
    transform: translateY(-2px);
}
.filter-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}
.filter-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
}
.filter-card-badge {
    font-family: "Geist Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    background: #eef2ff;
    color: #1d4ed8;
    border: 1px solid #c7d2fe;
    border-radius: 6px;
    padding: 3px 8px;
}
.filter-card-desc {
    font-size: 12.5px;
    color: #4b5563;
    line-height: 1.5;
    margin-bottom: 12px;
}
.filter-meta-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
}
.filter-meta-label {
    color: #6b7280;
    font-weight: 500;
}
.filter-meta-val {
    color: #111827;
    font-weight: 600;
    text-align: right;
}
.filter-code-box {
    background: #0f172a;
    color: #38bdf8;
    border-radius: 6px;
    padding: 8px 10px;
    font-family: "Geist Mono", monospace;
    font-size: 11px;
    word-break: break-all;
    margin: 10px 0;
}
.filter-action-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.5px;
    line-height: 1.4;
    margin-top: 8px;
}

/* Stepper Workflow */
.pipeline-stepper {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 16px 0 24px;
}
.step-item {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    position: relative;
    transition: all 0.2s ease;
}
.step-item:hover {
    border-color: #2563eb;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.06);
}
.step-num {
    font-family: "Geist Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    color: #2563eb;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.step-name {
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
}
.step-detail {
    font-size: 11px;
    color: #64748b;
    line-height: 1.4;
}

/* Diff styling */
.diff-highlight-bad {
    background: #fee2e2;
    color: #991b1b;
    padding: 1px 4px;
    border-radius: 4px;
    font-weight: 600;
    text-decoration: line-through;
}
.diff-highlight-good {
    background: #dbeafe;
    color: #1e40af;
    padding: 1px 4px;
    border-radius: 4px;
    font-weight: 600;
}

/* Container safety */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #d9dee6 !important;
    padding: 4px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #cbd5e1 !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04) !important;
}

/* Quick action buttons */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] > button {
    min-height: 42px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def pick(mapping, *keys, default=0):
    """Read a value from a dict while tolerating naming differences."""
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def normalize_result(result):
    """Normalize the existing pipeline result into UI-friendly metrics."""
    quality = pick(result, "quality", "quality_analysis", default={})
    pii = pick(result, "pii", "pii_analysis", default={})
    dedup = pick(result, "dedup", "deduplication", default={})

    input_records = int(
        pick(result, "input_records", "total_records", default=0)
    )

    quality_passed = int(
        pick(quality, "passed", "passed_records", default=input_records)
    )
    quality_failed = int(
        pick(quality, "failed", "failed_records", default=max(0, input_records - quality_passed))
    )

    pass_rate = float(
        pick(
            quality,
            "pass_rate",
            "pass_rate_percent",
            default=(quality_passed / input_records * 100 if input_records else 0),
        )
    )

    pii_records = int(
        pick(
            pii,
            "records_with_pii",
            "records_with_PII",
            "pii_records",
            default=0,
        )
    )

    email = int(pick(pii, "email", "emails", "email_detected", default=0))
    phone = int(pick(pii, "phone", "phones", "phone_detected", default=0))
    pan = int(pick(pii, "pan", "PAN", "pan_detected", default=0))
    aadhaar = int(
        pick(pii, "aadhaar", "AADHAAR", "aadhaar_detected", default=0)
    )

    before = int(
        pick(
            dedup,
            "before",
            "original_records",
            "records_after_intentional_duplication",
            default=input_records,
        )
    )
    duplicates = int(
        pick(
            dedup,
            "duplicates",
            "duplicates_removed",
            "intentional_duplicates",
            default=0,
        )
    )
    final_records = int(
        pick(
            dedup,
            "final",
            "final_unique_records",
            default=max(0, before - duplicates),
        )
    )

    total_pii = int(
        pick(pii, "total_instances", default=(email + phone + pan + aadhaar))
    )
    pii_filters = pii.get("filters", {})
    pii_findings = pii.get("findings", [])

    return {
        "input": input_records,
        "passed": quality_passed,
        "failed": quality_failed,
        "pass_rate": pass_rate,
        "pii_records": pii_records,
        "total_pii": total_pii,
        "email": email,
        "phone": phone,
        "pan": pan,
        "aadhaar": aadhaar,
        "filters": pii_filters,
        "findings": pii_findings,
        "before": before,
        "duplicates": duplicates,
        "final": final_records,
        "raw": result,
    }


def build_clean_bytes(result):
    """Use the existing save_dataset API if available, then read its output."""
    output_dir = Path("data/app_processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "cleaned_dataset.jsonl"

    cleaned = result.get("cleaned_records") or result.get("records")

    try:
        save_dataset(cleaned, output_path)
    except TypeError:
        try:
            save_dataset(cleaned, str(output_path))
        except Exception:
            pass
    except Exception:
        pass

    if output_path.exists():
        return output_path.read_bytes()

    # Fallback for pipelines that return JSON-serializable records.
    if cleaned is not None:
        if isinstance(cleaned, str):
            return cleaned.encode("utf-8")
        return (
            "\n".join(
                json.dumps(row, ensure_ascii=False)
                for row in cleaned
            )
            + "\n"
        ).encode("utf-8")

    return b""


def render_sidebar(filename=None, records=0):
    st.sidebar.markdown(
        """
        <div class="brand">
            <div class="brand-mark">N</div>
            <div>
                <div class="brand-title">NeMo Curator</div>
                <div class="brand-subtitle">NVIDIA AI FOUNDRY</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<div class="sidebar-label">Core Tools</div>', unsafe_allow_html=True)

    # Use real Streamlit buttons instead of st.radio for the Figma-style
    # sidebar navigation. This avoids Streamlit's radio-label opacity/theme
    # behavior that was making the navigation names nearly invisible.
    nav_items = [
        "Dataset Insights",
        "Quality Filters",
        "PII Protection",
        "De-Duplication",
        "Job History",
    ]

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "Dataset Insights"

    for item in nav_items:
        active = st.session_state.nav_page == item
        if st.sidebar.button(
            item,
            key=f"nav_{item.lower().replace(' ', '_').replace('-', '_')}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.nav_page = item
            st.rerun()

    page = st.session_state.nav_page

    if filename:
        st.sidebar.markdown(
            f"""
            <div class="active-dataset">
                <div class="sidebar-label" style="margin:0 0 10px;">Active Dataset</div>
                <div class="dataset-name">▣ {filename}</div>
                <div class="dataset-meta">
                    <span>{records:,} Records</span>
                    <span class="active-pill">Active</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        """
        <div style="position:fixed; bottom:22px; width:225px;">
            <div style="display:flex; gap:10px; align-items:center;">
                <div style="width:32px;height:32px;border-radius:50%;background:#dbeafe;
                            display:flex;align-items:center;justify-content:center;
                            color:#1e3a8a;font-weight:700;">N</div>
                <div>
                    <div style="font-size:13px;font-weight:500;color:#111827;">NVIDIA Operator</div>
                    <div style="font-family:'Geist Mono';font-size:11px;color:#6b7280;">
                        admin@nvidia.local
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return page


# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------

# mask_pii and mask_pii_detailed imported from pipeline.py


if "result" not in st.session_state:
    st.session_state.result = None

if "filename" not in st.session_state:
    st.session_state.filename = None

if "elapsed" not in st.session_state:
    st.session_state.elapsed = None
if "input_path" not in st.session_state:
    st.session_state.input_path = None

if "min_words" not in st.session_state:
    st.session_state.min_words = 100
if "max_words" not in st.session_state:
    st.session_state.max_words = 100000
if "max_non_alpha_ratio" not in st.session_state:
    st.session_state.max_non_alpha_ratio = 0.25
if "threshold_draft" not in st.session_state:
    st.session_state.threshold_draft = False
if "show_pii_export" not in st.session_state:
    st.session_state.show_pii_export = False

metrics = (
    normalize_result(st.session_state.result)
    if st.session_state.result is not None
    else None
)

page = render_sidebar(
    st.session_state.filename,
    metrics["input"] if metrics else 0,
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
left, right = st.columns([1.65, 1], vertical_alignment="center")

with left:
    st.markdown(
        """
        <div class="page-title">Dataset Quality &amp; Insights</div>
        <div class="page-subtitle">
            Analyze, sanitize, and curate text datasets for Large Language Model (LLM) training.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    c1, c2 = st.columns(2)
    with c1:
        uploaded = st.file_uploader(
            "Upload JSONL",
            type=["jsonl", "json"],
            label_visibility="collapsed",
            key="dataset_upload",
        )
    with c2:
        if st.session_state.result is not None:
            clean_bytes = build_clean_bytes(st.session_state.result)
            st.download_button(
                "Redact & Export",
                data=clean_bytes,
                file_name="cleaned_dataset.jsonl",
                mime="application/jsonl",
                use_container_width=True,
                type="primary",
            )


# ---------------------------------------------------------------------
# Upload + processing
# ---------------------------------------------------------------------
if uploaded is not None:
    if st.session_state.filename != uploaded.name:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_name = Path(uploaded.name).name
        input_path = upload_dir / safe_name
        input_path.write_bytes(uploaded.getvalue())

        with st.spinner("Running NeMo Curator pipeline..."):
            start = time.perf_counter()
            result = process_jsonl(
                input_path,
                min_words=st.session_state.min_words,
                max_words=st.session_state.max_words,
                max_non_alpha_ratio=st.session_state.max_non_alpha_ratio,
            )
            elapsed = time.perf_counter() - start

        st.session_state.result = result
        st.session_state.filename = safe_name
        st.session_state.elapsed = elapsed
        st.session_state.input_path = str(input_path)

        st.rerun()


# ---------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------
if metrics is None:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-title">Upload a JSONL dataset to begin</div>
            <div style="margin-top:8px;">
                Your file will be processed for quality, PII, and duplicate analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


elapsed = st.session_state.elapsed or 0
filename = st.session_state.filename or "dataset.jsonl"

st.markdown(
    f"""
    <div class="status">
        ✓ &nbsp;Success: Dataset imported successfully.
        Pipeline finished execution in {elapsed:.1f} seconds.
        <span style="float:right;font-family:'Geist Mono';font-size:12px;">
            ● {filename}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Focused navigation views
# ---------------------------------------------------------------------
if page == "Quality Filters":
    st.markdown(
        '<div class="page-title">Quality Filters</div>'
        '<div class="page-subtitle">Configure the quality thresholds used by the NeMo Curator filtering stage.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="panel-title">Quality Filter Rules</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-line"></div>', unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        with r1:
            min_words = st.number_input(
                "Minimum words",
                min_value=0,
                max_value=1000000,
                value=int(st.session_state.min_words),
                step=10,
                key="edit_min_words",
                help="Documents below this word count are filtered.",
            )
        with r2:
            max_words = st.number_input(
                "Maximum words",
                min_value=1,
                max_value=1000000,
                value=int(st.session_state.max_words),
                step=100,
                key="edit_max_words",
                help="Documents above this word count are filtered.",
            )
        with r3:
            max_ratio_pct = st.number_input(
                "Max special-character ratio (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.max_non_alpha_ratio * 100),
                step=1.0,
                key="edit_non_alpha_pct",
                help="Maximum allowed non-alphanumeric-to-text ratio.",
            )

        if min_words >= max_words:
            st.error("Minimum words must be smaller than maximum words.")
        else:
            if st.button("Apply Rules & Re-run Dataset", type="primary", use_container_width=True):
                st.session_state.min_words = int(min_words)
                st.session_state.max_words = int(max_words)
                st.session_state.max_non_alpha_ratio = float(max_ratio_pct / 100.0)

                current_path = st.session_state.input_path
                if current_path and Path(current_path).exists():
                    with st.spinner("Re-running NeMo Curator with the updated rules..."):
                        start = time.perf_counter()
                        result = process_jsonl(
                            current_path,
                            min_words=st.session_state.min_words,
                            max_words=st.session_state.max_words,
                            max_non_alpha_ratio=st.session_state.max_non_alpha_ratio,
                        )
                        st.session_state.result = result
                        st.session_state.elapsed = time.perf_counter() - start
                    st.toast("Quality rules applied and dataset re-processed.")
                    st.rerun()
                else:
                    st.warning("Upload a JSONL dataset before applying quality rules.")

        st.caption(
            f"Active rules: {st.session_state.min_words:,}–{st.session_state.max_words:,} words "
            f"and ≤ {st.session_state.max_non_alpha_ratio * 100:.0f}% non-alphanumeric ratio."
        )

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">
                <span>◌ &nbsp; Quality Filtering Performance</span>
                <span class="badge">{metrics['pass_rate']:.1f}% Passed</span>
            </div>
            <div class="panel-line"></div>
            <div class="progress-row">
                <div class="progress-label">
                    <span>Passed Documents</span>
                    <span>{metrics['passed']:,} / {metrics['input']:,}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{min(100, max(0, metrics['pass_rate']))}%;"></div>
                </div>
            </div>
            <div class="progress-row">
                <div class="progress-label">
                    <span>Low-Quality Outliers Filtered</span>
                    <span>{metrics['failed']:,}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{min(100, metrics['failed']/max(metrics['input'],1)*100)}%;"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-title" style="margin-top:20px;">Active Individual Quality Rules</div>
        <div class="section-subtitle">NeMo Curator runs these three specialized heuristic DocumentFilters sequentially on every ingested record:</div>
        <div class="filter-spec-grid">
            <div class="filter-spec-card">
                <div>
                    <div class="filter-card-header">
                        <div class="filter-card-title">1. WordCountFilter</div>
                        <span class="filter-card-badge">Length Check</span>
                    </div>
                    <div class="filter-card-desc">Filters out sentence fragments or runaway long documents that disrupt LLM context windows.</div>
                    <div class="filter-meta-row">
                        <span class="filter-meta-label">What is done:</span>
                        <span class="filter-meta-val">Counts whitespace-delimited tokens per record.</span>
                    </div>
                    <div class="filter-meta-row">
                        <span class="filter-meta-label">Rule:</span>
                        <span class="filter-meta-val">min_words ≤ token_count ≤ max_words</span>
                    </div>
                </div>
                <div class="filter-action-box">Keeps documents with substantial context while discarding empty or clipped lines.</div>
            </div>
            <div class="filter-spec-card">
                <div>
                    <div class="filter-card-header">
                        <div class="filter-card-title">2. NonAlphaNumericFilter</div>
                        <span class="filter-card-badge">OCR / Noise Filter</span>
                    </div>
                    <div class="filter-card-desc">Measures the proportion of special symbols, escape characters, or binary noise in the text.</div>
                    <div class="filter-meta-row">
                        <span class="filter-meta-label">What is done:</span>
                        <span class="filter-meta-val">Calculates (non_alphanumeric_chars / total_chars).</span>
                    </div>
                    <div class="filter-meta-row">
                        <span class="filter-meta-label">Rule:</span>
                        <span class="filter-meta-val">ratio ≤ max_non_alpha_ratio</span>
                    </div>
                </div>
                <div class="filter-action-box">Eliminates corrupted OCR scans, markdown gibberish, and formatting garbage.</div>
            </div>
            <div class="filter-spec-card">
                <div>
                    <div class="filter-card-header">
                        <div class="filter-card-title">3. RBICustomQualityFilter</div>
                        <span class="filter-card-badge">Domain Quality</span>
                    </div>
                    <div class="filter-card-desc">Identifies and filters legacy repeal lists, circular cancellation indexes, and administrative boilerplate.</div>
                    <div class="filter-meta-row">
                        <span class="filter-meta-label">What is done:</span>
                        <span class="filter-meta-val">Scores density of obsolete regulatory indicators.</span>
                    </div>
                    <div class="filter-meta-row">
                        <span class="filter-meta-label">Rule:</span>
                        <span class="filter-meta-val">score &lt; 3 (repeal indicator threshold)</span>
                    </div>
                </div>
                <div class="filter-action-box">Retains active substantive regulatory directions while discarding repealed circular indexes.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

if page == "PII Protection":
    st.markdown(
        """
        <div class="page-title">PII Protection &amp; Redaction Engine</div>
        <div class="page-subtitle">
            Detect, analyze, and neutralize Personally Identifiable Information (PII) before model training with individual filter inspection and verification.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------
    # 1. Pipeline Architecture Stepper
    # -----------------------------------------------------------------
    st.markdown(
        """
        <div class="pipeline-stepper">
            <div class="step-item">
                <div class="step-num">Step 01 · Scanning</div>
                <div class="step-name">Pattern Tokenization</div>
                <div class="step-detail">Regex scanners evaluate RFC 5322 emails, Indian telecom +91, IT Dept PAN, and UIDAI Aadhaar syntax.</div>
            </div>
            <div class="step-item">
                <div class="step-num">Step 02 · Classification</div>
                <div class="step-name">Entity Risk Scoring</div>
                <div class="step-detail">Classifies matched substrings into Contact PII vs. Government &amp; Financial regulatory identifiers.</div>
            </div>
            <div class="step-item">
                <div class="step-num">Step 03 · Redaction</div>
                <div class="step-name">Placeholder Masking</div>
                <div class="step-detail">Substitutes raw sensitive data with context-preserving tags: [EMAIL], [PHONE], [PAN], and [AADHAAR].</div>
            </div>
            <div class="step-item">
                <div class="step-num">Step 04 · Verification</div>
                <div class="step-name">Audit Trail Logging</div>
                <div class="step-detail">Records character offsets, structural previews, and sanitized outputs for regulatory compliance.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------
    # 2. Executive Metrics Summary
    # -----------------------------------------------------------------
    pii_total = metrics["email"] + metrics["phone"] + metrics["pan"] + metrics["aadhaar"]
    pii_records = metrics["pii_records"]
    clean_records = metrics["passed"] - pii_records
    pii_pct = (pii_records / max(metrics["passed"], 1)) * 100

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="mini-card">
                <div class="small-label">Total Documents Scanned</div>
                <div class="big-number">{metrics['passed']:,}</div>
                <div style="font-size:11px;color:#6b7280;margin-top:4px;">Passed quality stage</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="mini-card" style="border-left: 3px solid #ef4444;">
                <div class="small-label">Documents with PII</div>
                <div class="big-number" style="color:#b91c1c;">{pii_records:,}</div>
                <div style="font-size:11px;color:#dc2626;margin-top:4px;">{pii_pct:.1f}% exposure rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="mini-card" style="border-left: 3px solid #10b981;">
                <div class="small-label">Clean Documents Preserved</div>
                <div class="big-number" style="color:#047857;">{clean_records:,}</div>
                <div style="font-size:11px;color:#059669;margin-top:4px;">Zero PII detected</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="mini-card" style="border-left: 3px solid #2563eb;">
                <div class="small-label">PII Entities Neutralized</div>
                <div class="big-number" style="color:#1d4ed8;">{pii_total:,}</div>
                <div style="font-size:11px;color:#2563eb;margin-top:4px;">100% redacted &amp; audited</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 3. Individual Filter Deep Dive Cards ("Each and every individual filter")
    # -----------------------------------------------------------------
    st.markdown(
        """
        <div class="section-title">Individual Filter Specifications &amp; Actions</div>
        <div class="section-subtitle">Detailed breakdown of each individual filter: what is detected, why it is removed, the regex rule applied, and the sanitization mechanism.</div>
        """,
        unsafe_allow_html=True,
    )

    filter_keys = ["EMAIL", "PHONE", "PAN", "AADHAAR"]
    filter_counts = {
        "EMAIL": metrics["email"],
        "PHONE": metrics["phone"],
        "PAN": metrics["pan"],
        "AADHAAR": metrics["aadhaar"],
    }

    # Render 2x2 grid of rich filter cards
    f_col1, f_col2 = st.columns(2)
    for idx, f_key in enumerate(filter_keys):
        spec = PII_FILTER_SPECS.get(f_key, {})
        target_col = f_col1 if idx % 2 == 0 else f_col2
        count = filter_counts.get(f_key, 0)
        status_color = "#15803d" if count > 0 else "#64748b"
        status_text = f"{count:,} Removed" if count > 0 else "0 Found"

        with target_col:
            st.markdown(
                f"""
                <div class="filter-spec-card">
                    <div>
                        <div class="filter-card-header">
                            <div>
                                <div class="filter-card-title">{spec.get('name', f_key)}</div>
                                <div style="font-size:11px;color:#6b7280;margin-top:2px;">Category: <b>{spec.get('category', 'PII')}</b></div>
                            </div>
                            <span class="filter-card-badge">{spec.get('placeholder', f'[{f_key}]')}</span>
                        </div>
                        <div class="filter-card-desc">{spec.get('description', '')}</div>
                        <div class="filter-meta-row">
                            <span class="filter-meta-label">What is done &amp; removed:</span>
                            <span class="filter-meta-val" style="max-width:65%;">{spec.get('action_taken', '')}</span>
                        </div>
                        <div class="filter-meta-row">
                            <span class="filter-meta-label">How it works:</span>
                            <span class="filter-meta-val" style="max-width:65%;">{spec.get('how_it_works', '')}</span>
                        </div>
                        <div class="filter-meta-row">
                            <span class="filter-meta-label">Compliance standard:</span>
                            <span class="filter-meta-val" style="max-width:65%;color:#1d4ed8;">{spec.get('compliance', '')}</span>
                        </div>
                        <div class="filter-code-box">Pattern: {spec.get('pattern_str', '')}</div>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;padding-top:10px;border-top:1px solid #e2e8f0;">
                        <span style="font-size:12px;color:#64748b;">Example: <code style="color:#0f172a;">{spec.get('example_input', '')}</code> → <b style="color:#2563eb;">{spec.get('example_output', '')}</b></span>
                        <span style="font-family:'Geist Mono';font-size:12px;font-weight:700;color:{status_color};background:#f8fafc;padding:3px 8px;border-radius:6px;border:1px solid #e2e8f0;">{status_text}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 4. Interactive Removed Entities Audit Trail
    # -----------------------------------------------------------------
    st.markdown(
        """
        <div class="section-title">Granular PII Detection Audit Trail</div>
        <div class="section-subtitle">Examine all instances flagged and redacted across the current dataset. Filter by individual rule or inspect full audit tokens.</div>
        """,
        unsafe_allow_html=True,
    )

    # Retrieve all findings from pipeline result or generate dynamically from current input
    findings = metrics.get("findings", [])
    source_path = Path(st.session_state.input_path) if st.session_state.input_path else None

    # If findings weren't pre-populated, build them dynamically
    if not findings and source_path and source_path.exists():
        findings = []
        try:
            with source_path.open("r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    raw_text = str(row.get("text", ""))
                    rec_id = row.get("id") or f"doc_{line_idx:03d}"
                    det = mask_pii_detailed(raw_text)
                    for m in det["matches"]:
                        findings.append({
                            "record_id": rec_id,
                            "type": m["type"],
                            "filter_name": m["filter_name"],
                            "category": m["category"],
                            "raw": m["raw"],
                            "preview": m["preview"],
                            "replacement": m["replacement"],
                            "action": m["action"],
                            "how_it_works": m["how_it_works"],
                            "compliance": m["compliance"],
                        })
        except Exception:
            findings = []

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.2, 1])
    with ctrl_col1:
        filter_choice = st.selectbox(
            "Filter by PII Rule",
            options=["All Filters", "EMAIL (Email Address)", "PHONE (Phone Number)", "PAN (Permanent Account No.)", "AADHAAR (UIDAI Identity)"],
            index=0,
            key="audit_filter_choice",
        )
    with ctrl_col2:
        search_query = st.text_input(
            "Search Record ID or Value",
            placeholder="Search e.g. rahul, kyc_001, 9876...",
            key="audit_search_query",
        )
    with ctrl_col3:
        reveal_raw = st.toggle("Reveal Unmasked Values", value=False, help="Toggle between privacy-preserving structure preview and raw extracted value.")

    # Filter findings based on user selection
    selected_type = None
    if "EMAIL" in filter_choice:
        selected_type = "EMAIL"
    elif "PHONE" in filter_choice:
        selected_type = "PHONE"
    elif "PAN" in filter_choice:
        selected_type = "PAN"
    elif "AADHAAR" in filter_choice:
        selected_type = "AADHAAR"

    filtered_findings = findings
    if selected_type:
        filtered_findings = [f for f in filtered_findings if f["type"] == selected_type]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_findings = [
            f for f in filtered_findings
            if q in str(f.get("record_id", "")).lower()
            or q in str(f.get("raw", "")).lower()
            or q in str(f.get("preview", "")).lower()
        ]

    if filtered_findings:
        table_rows = []
        for f in filtered_findings:
            shown_val = f["raw"] if reveal_raw else f["preview"]
            table_rows.append({
                "Record ID": f["record_id"],
                "Filter": f["type"],
                "Category": f["category"],
                "Detected Sensitive Value": shown_val,
                "Replacement Token": f["replacement"],
                "Action Taken": f["action"],
                "Compliance Standard": f["compliance"],
            })
        st.dataframe(table_rows, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(table_rows):,} detected PII occurrences matching current view filters.")
    else:
        st.info("No PII entries match the selected filter criteria.")

    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 5. Record-by-Record Visual Diff Inspector
    # -----------------------------------------------------------------
    st.markdown(
        """
        <div class="section-title">Before / After Document Masking Evidence</div>
        <div class="section-subtitle">Inspect any document with detected PII side-by-side to verify how each sensitive token was removed and replaced.</div>
        """,
        unsafe_allow_html=True,
    )

    # Collect all records that have PII
    pii_candidate_records = []
    if source_path and source_path.exists():
        try:
            with source_path.open("r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    raw_text = str(row.get("text", ""))
                    det = mask_pii_detailed(raw_text)
                    if det["total_count"] > 0:
                        rec_id = row.get("id") or f"doc_{line_idx:03d}"
                        pii_candidate_records.append({
                            "id": rec_id,
                            "original": raw_text,
                            "masked": det["masked_text"],
                            "counts": det["counts"],
                            "matches": det["matches"],
                        })
        except Exception:
            pii_candidate_records = []

    if pii_candidate_records:
        rec_options = [
            f"{r['id']} ({sum(r['counts'].values())} PII item{'s' if sum(r['counts'].values())>1 else ''}: "
            f"{', '.join(k for k, v in r['counts'].items() if v)})"
            for r in pii_candidate_records
        ]
        chosen_rec_label = st.selectbox(
            "Select Record to Compare",
            options=rec_options,
            index=0,
            key="diff_record_selector",
        )
        chosen_idx = rec_options.index(chosen_rec_label)
        selected_record = pii_candidate_records[chosen_idx]

        # Build visually highlighted versions
        orig_html = html.escape(selected_record["original"])
        masked_html = html.escape(selected_record["masked"])

        # Highlight detected items in original
        for m in selected_record["matches"]:
            raw_esc = html.escape(m["raw"])
            if raw_esc in orig_html:
                orig_html = orig_html.replace(
                    raw_esc,
                    f'<span class="diff-highlight-bad">{raw_esc}</span>',
                    1
                )

        # Highlight replacement badges in masked
        for f_key, spec in PII_FILTER_SPECS.items():
            tag = spec["placeholder"]
            tag_esc = html.escape(tag)
            if tag_esc in masked_html:
                masked_html = masked_html.replace(
                    tag_esc,
                    f'<span class="diff-highlight-good">{tag_esc}</span>'
                )

        st.html(
            f"""
            <div class="evidence-grid">
                <div class="evidence-card">
                    <div class="evidence-label" style="color:#b91c1c;">BEFORE MASKING (RAW INPUT) · {html.escape(selected_record['id'])}</div>
                    <div class="evidence-text">{orig_html}</div>
                </div>
                <div class="evidence-arrow">→</div>
                <div class="evidence-card">
                    <div class="evidence-label" style="color:#1d4ed8;">AFTER MASKING (CLEANED) · {html.escape(selected_record['id'])}</div>
                    <div class="evidence-text">{masked_html}</div>
                </div>
            </div>
            """
        )

        # Summary tags for the selected record
        tag_items = []
        for k, v in selected_record["counts"].items():
            if v > 0:
                tag_items.append(f"<b>{k}</b>: {v} occurrence{'s' if v > 1 else ''}")
        st.markdown(
            f"<div style='margin-top:8px;font-size:12.5px;color:#475569;'>Filtered on this record: {' · '.join(tag_items)}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No PII-containing records found in current dataset to demonstrate before/after masking.")

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 6. Live Interactive PII Testing Sandbox
    # -----------------------------------------------------------------
    st.markdown(
        """
        <div class="section-title">Live PII Filter Testing Sandbox</div>
        <div class="section-subtitle">Type or paste any custom customer text or document fragment below to test all individual PII filters in real-time.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        default_sandbox_text = "Please send KYC verification to rahul.verma@axisbank.com or call +91-9876543210. PAN is ABCDE1234F and Aadhaar number is 1234 5678 9012."
        user_test_input = st.text_area(
            "Sandbox Input Text",
            value=default_sandbox_text,
            height=90,
            key="pii_sandbox_text",
            help="Enter text containing names, emails, phone numbers, PAN, or Aadhaar numbers.",
        )

        if user_test_input.strip():
            sandbox_res = mask_pii_detailed(user_test_input)
            s1, s2 = st.columns([1, 1.2])

            with s1:
                st.markdown("<b>Filter Triggers Detected:</b>", unsafe_allow_html=True)
                if sandbox_res["total_count"] > 0:
                    for m in sandbox_res["matches"]:
                        st.markdown(
                            f"""
                            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:8px 12px;margin-bottom:6px;font-size:12px;">
                                <span style="font-weight:700;color:#2563eb;">{m['filter_name']}</span>
                                <span style="font-family:'Geist Mono';float:right;background:#eef2ff;color:#1e40af;padding:1px 6px;border-radius:4px;">{m['replacement']}</span>
                                <div style="color:#64748b;margin-top:4px;">Matched: <code style="color:#b91c1c;">{html.escape(m['raw'])}</code></div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.success("✓ No PII detected. Document conforms to all clean text checks.")

            with s2:
                st.markdown("<b>Sanitized Output:</b>", unsafe_allow_html=True)
                st.text_area(
                    "Sanitized Result",
                    value=sandbox_res["masked_text"],
                    height=130,
                    disabled=True,
                    key="sandbox_output_box",
                    label_visibility="collapsed",
                )

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 7. Export Masked Dataset & Audit Trail
    # -----------------------------------------------------------------
    st.markdown(
        """
        <div class="section-title">Dataset Redaction &amp; Compliance Export</div>
        <div class="section-subtitle">Download the fully sanitized dataset or the machine-readable PII audit report.</div>
        """,
        unsafe_allow_html=True,
    )

    down_c1, down_c2 = st.columns(2)
    cleaned_records = st.session_state.result.get("cleaned_records", []) if st.session_state.result else []
    masked_jsonl_content = "\n".join(json.dumps(row, ensure_ascii=False) for row in cleaned_records) + "\n"

    with down_c1:
        st.download_button(
            "Download Fully Masked JSONL Dataset",
            data=masked_jsonl_content.encode("utf-8"),
            file_name=f"{Path(filename).stem}_pii_sanitized.jsonl",
            mime="application/jsonl",
            use_container_width=True,
            type="primary",
            key="dl_masked_jsonl_main",
        )

    with down_c2:
        audit_report = {
            "dataset_filename": filename,
            "total_documents_analyzed": metrics["passed"],
            "documents_with_pii": metrics["pii_records"],
            "total_pii_entities_removed": pii_total,
            "per_filter_breakdown": {
                "email_addresses": metrics["email"],
                "phone_numbers": metrics["phone"],
                "pan_numbers": metrics["pan"],
                "aadhaar_numbers": metrics["aadhaar"],
            },
            "findings_audit_trail": findings,
        }
        st.download_button(
            "Download PII Audit Trail Report (JSON)",
            data=json.dumps(audit_report, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name=f"{Path(filename).stem}_pii_audit_report.json",
            mime="application/json",
            use_container_width=True,
            key="dl_pii_audit_json",
        )

    st.stop()

if page == "De-Duplication":
    unique_pct = metrics["final"] / max(metrics["before"], 1) * 100
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">
                <span>De-Duplication</span>
                <span class="badge">{unique_pct:.1f}% Unique</span>
            </div>
            <div class="panel-line"></div>
            <div style="display:flex;gap:40px;">
                <div style="flex:1;">
                    <div class="small-label">Identified Duplicates</div>
                    <div class="big-number">{metrics['duplicates']:,}</div>
                </div>
                <div style="width:1px;background:#d9dee6;"></div>
                <div style="flex:1;">
                    <div class="small-label">Final Purged Dataset Size</div>
                    <div class="big-number">{metrics['final']:,} records</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

if page == "Job History":
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">Current Job</div>
            <div class="panel-line"></div>
            <div style="font-family:'Geist Mono';font-size:13px;">{filename}</div>
            <div style="margin-top:10px;color:#6b7280;font-size:13px;">
                {metrics['input']:,} input records · {elapsed:.1f}s execution time
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ---------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

cards = [
    ("Total Raw Records", metrics["input"], "documents", "▤", ""),
    ("Quality Filtered", metrics["passed"], f"passed ({metrics['pass_rate']:.0f}%)", "✦",
     f"{metrics['failed']:+,} records cleaned" if metrics["failed"] else "No records removed"),
    ("PII Items Flagged",
     metrics["email"] + metrics["phone"] + metrics["pan"] + metrics["aadhaar"],
     "instances", "◉",
     f"{metrics['pii_records']:,} records contain PII" if metrics["pii_records"] else "No PII detected"),
    ("Duplicates Removed", metrics["duplicates"], "records", "◫",
     f"{metrics['final']/max(metrics['before'],1)*100:.1f}% Unique"),
]

for col, (label, value, unit, icon, foot) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-top">
                    <div class="metric-label">{label}</div>
                    <div class="metric-icon">{icon}</div>
                </div>
                <div class="metric-value">
                    {value:,}
                    <span class="metric-unit">{unit}</span>
                </div>
                <div class="metric-foot">{foot}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")


# ---------------------------------------------------------------------
# Main analysis grid
# ---------------------------------------------------------------------
main_col, insight_col = st.columns([1.62, 1], gap="medium")

with main_col:
    # Quality
    st.html(
        textwrap.dedent(f"""
        <div class="panel">
            <div class="panel-title">
                <span>◌ &nbsp; Quality Filtering Performance</span>
                <span class="badge">{metrics['pass_rate']:.1f}% Passed</span>
            </div>
            <div class="panel-line"></div>

            <div class="progress-row">
                <div class="progress-label">
                    <span>Passed Documents</span>
                    <span>{metrics['passed']:,} / {metrics['input']:,}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{min(100, max(0, metrics['pass_rate']))}%;"></div>
                </div>
            </div>

            <div class="progress-row">
                <div class="progress-label">
                    <span>Low-Quality Outliers Filtered</span>
                    <span>{metrics['failed']:,}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{min(100, metrics['failed']/max(metrics['input'],1)*100)}%;"></div>
                </div>
            </div>
        </div>
        """)
    )

    # PII Analysis on Main Dashboard
    st.html(
        textwrap.dedent(f"""
        <div class="panel">
            <div class="panel-title">
                <span>◉ &nbsp; Personally Identifiable Information (PII) Analysis</span>
                <span class="badge" style="background:#dbeafe;color:#1e40af;">{metrics['pii_records']} Records Flagged · {metrics.get('total_pii', metrics['email']+metrics['phone']+metrics['pan']+metrics['aadhaar'])} Entities</span>
            </div>
            <div class="panel-line"></div>

            <div class="pii-row">
                <div class="pii-left"><span class="dot" style="background:#2563eb;"></span>Email Address Filter <code style="font-size:10.5px;color:#2563eb;margin-left:4px;">[EMAIL]</code></div>
                <div><b>{metrics['email']}</b> <span style="font-size:11px;color:#15803d;margin-left:6px;">{'● Redacted' if metrics['email'] else '○ Clean'}</span></div>
            </div>
            <div class="pii-row">
                <div class="pii-left"><span class="dot" style="background:#2563eb;"></span>Phone Number Filter <code style="font-size:10.5px;color:#2563eb;margin-left:4px;">[PHONE]</code></div>
                <div><b>{metrics['phone']}</b> <span style="font-size:11px;color:#15803d;margin-left:6px;">{'● Redacted' if metrics['phone'] else '○ Clean'}</span></div>
            </div>
            <div class="pii-row">
                <div class="pii-left"><span class="dot" style="background:#2563eb;"></span>Income Tax PAN Filter <code style="font-size:10.5px;color:#2563eb;margin-left:4px;">[PAN]</code></div>
                <div><b>{metrics['pan']}</b> <span style="font-size:11px;color:#15803d;margin-left:6px;">{'● Redacted' if metrics['pan'] else '○ Clean'}</span></div>
            </div>
            <div class="pii-row">
                <div class="pii-left"><span class="dot" style="background:#2563eb;"></span>UIDAI Aadhaar Filter <code style="font-size:10.5px;color:#2563eb;margin-left:4px;">[AADHAAR]</code></div>
                <div><b>{metrics['aadhaar']}</b> <span style="font-size:11px;color:#15803d;margin-left:6px;">{'● Redacted' if metrics['aadhaar'] else '○ Clean'}</span></div>
            </div>
        </div>
        """)
    )

    # Dedup
    unique_pct = metrics["final"] / max(metrics["before"], 1) * 100
    st.html(
        textwrap.dedent(f"""
        <div class="panel">
            <div class="panel-title">
                <span>◫ &nbsp; Exact De-Duplication (SHA-256)</span>
                <span class="badge">{unique_pct:.1f}% Unique</span>
            </div>
            <div class="panel-line"></div>

            <div style="display:flex;gap:40px;">
                <div style="flex:1;">
                    <div class="small-label">Identified Duplicates</div>
                    <div class="big-number">{metrics['duplicates']:,}</div>
                </div>
                <div style="width:1px;background:#d9dee6;"></div>
                <div style="flex:1;">
                    <div class="small-label">Final Purged Dataset Size</div>
                    <div class="big-number">{metrics['final']:,} records</div>
                </div>
            </div>
        </div>
        """)
    )

with insight_col:
    pii_total = metrics["email"] + metrics["phone"] + metrics["pan"] + metrics["aadhaar"]
    pii_pct = metrics["pii_records"] / max(metrics["input"], 1) * 100
    failed_pct = metrics["failed"] / max(metrics["input"], 1) * 100

    if metrics["pii_records"]:
        pii_message = (
            f"System detected {pii_total:,} PII instance(s) across "
            f"{metrics['pii_records']:,} record(s) ({pii_pct:.1f}% of the input). "
            "Redaction is recommended before downstream model training."
        )
    else:
        pii_message = "No PII records were detected by the configured protection rules."

    if metrics["failed"]:
        quality_message = (
            f"{metrics['passed']:,} of {metrics['input']:,} records passed the "
            f"configured quality checks. {metrics['failed']:,} record(s) "
            f"({failed_pct:.1f}%) were filtered."
        )
    else:
        quality_message = (
            f"All {metrics['input']:,} imported records passed the configured "
            "quality checks."
        )

    if metrics["duplicates"]:
        dedup_message = (
            f"{metrics['duplicates']:,} redundant record(s) were removed, "
            f"leaving {metrics['final']:,} unique records."
        )
    else:
        dedup_message = (
            f"No redundant records were found. The dataset contains "
            f"{metrics['final']:,} unique records."
        )

    st.html(
        textwrap.dedent(f"""
        <div class="panel">
            <div class="panel-title">💡 &nbsp; Automatic AI Insights</div>
            <div class="panel-line"></div>

            <div class="insight">
                <div class="insight-title">● &nbsp; PII Detection</div>
                <div class="insight-text">{pii_message}</div>
            </div>

            <div class="insight">
                <div class="insight-title">● &nbsp; Clean Record Integrity</div>
                <div class="insight-text">{quality_message}</div>
            </div>

            <div class="insight">
                <div class="insight-title">● &nbsp; Duplication Analysis</div>
                <div class="insight-text">{dedup_message}</div>
            </div>
        </div>
        """)
    )

    with st.container(border=True):
        st.markdown(
            '<div class="panel-title">Quick Actions</div><div class="panel-line"></div>',
            unsafe_allow_html=True,
        )

        q1, q2 = st.columns(2)
        with q1:
            if st.button("Anonymize & Redact Emails", key="quick_redact", use_container_width=True):
                st.session_state.nav_page = "PII Protection"
                st.session_state.show_pii_export = True
                st.rerun()

        with q2:
            if st.button("Edit Filter Threshold Rules", key="quick_rules", use_container_width=True):
                st.session_state.nav_page = "Quality Filters"
                st.rerun()
