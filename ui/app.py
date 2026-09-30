import sys
import tempfile
import html
import re
from pathlib import Path
from typing import Optional

import gradio as gr
import pandas as pd



# Project Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from ingestion import load_document
from ai.analyzer import generate_analysis
from cleaning.standarization import detect_category_variant
from cleaning.type_correcter import detect_type_issue, correct_types
from cleaning.value_validator import detect_value_violations, build_rule_summary, strip_units
from cleaning.value_normalizer import (
    normalize_values,
    normalize_dates,
    fill_missing_prices,
    is_price_column,
)
from cleaning.rule import match_rules


def _has_word(name, word: str) -> bool:
    """True if `word` appears as a whole word, so 'age' matches 'age' / 'customer_age' but not 'message'."""
    return re.search(rf"(?<![a-z]){word}(?![a-z])", str(name).lower()) is not None


# Custom CSS


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ==========================================
   Design tokens
   ========================================== */

:root {
    --dd-bg: #070b12;
    --dd-surface: #0e1420;
    --dd-surface-2: #131b2b;
    --dd-surface-3: #182236;
    --dd-border: #1f2a3d;
    --dd-border-strong: #2b3a54;
    --dd-text: #e8edf5;
    --dd-muted: #8a97ad;
    --dd-faint: #5b6880;
    --dd-accent: #34d399;
    --dd-accent-strong: #10b981;
    --dd-accent-2: #22d3ee;
    --dd-warn: #fbbf24;
    --dd-danger: #fb7185;
    --dd-radius: 16px;
}

body,
.gradio-container {
    background:
        radial-gradient(1100px 500px at 12% -10%, rgba(52, 211, 153, 0.07), transparent 60%),
        radial-gradient(900px 480px at 100% 0%, rgba(34, 211, 238, 0.06), transparent 55%),
        var(--dd-bg) !important;
    color: var(--dd-text) !important;
    font-family: "Inter", "Segoe UI", system-ui, sans-serif !important;
}

.gradio-container {
    max-width: 1280px !important;
    margin: 0 auto !important;
    padding: 28px 28px 16px !important;
}

footer {
    display: none !important;
}

/* ==========================================
   Header
   ========================================== */

#app-header {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(135deg, rgba(52, 211, 153, 0.10), rgba(34, 211, 238, 0.05) 55%, transparent),
        var(--dd-surface);
    border: 1px solid var(--dd-border);
    border-radius: 22px;
    padding: 30px 34px 26px;
    margin-bottom: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
}

#app-header::after {
    content: "";
    position: absolute;
    right: -80px;
    top: -80px;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(52, 211, 153, 0.16), transparent 65%);
    pointer-events: none;
}

#app-header .hero-top {
    display: flex;
    align-items: center;
    gap: 18px;
}

#app-header .logo {
    width: 58px;
    height: 58px;
    flex: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    border-radius: 16px;
    background: linear-gradient(135deg, #10b981, #22d3ee);
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.35);
}

#app-header .brand {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.8px;
    color: var(--dd-text);
    line-height: 1.1;
}

#app-header .subtitle {
    margin-top: 6px;
    font-size: 14px;
    color: var(--dd-muted);
    line-height: 1.6;
    max-width: 640px;
}

#app-header .steps {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 22px;
    position: relative;
    z-index: 1;
}

#app-header .step {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px 6px 6px;
    border: 1px solid var(--dd-border-strong);
    border-radius: 999px;
    background: rgba(7, 11, 18, 0.55);
    color: #c5d0e2;
    font-size: 12.5px;
    font-weight: 600;
}

#app-header .step b {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: rgba(52, 211, 153, 0.16);
    color: var(--dd-accent);
    font-size: 11px;
    font-weight: 700;
}

/* ==========================================
   Cards / dashboard
   ========================================== */

.dashboard-row {
    align-items: stretch !important;
    gap: 18px !important;
    margin-bottom: 18px !important;
}

.section-card {
    background: var(--dd-surface) !important;
    border: 1px solid var(--dd-border) !important;
    border-radius: var(--dd-radius) !important;
    padding: 22px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.22);
    gap: 14px !important;
}

.card-title {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: -0.2px;
    color: var(--dd-text);
}

.card-sub {
    margin-top: 3px;
    font-size: 12.5px;
    color: var(--dd-muted);
    line-height: 1.5;
}

.panel-right {
    justify-content: flex-start !important;
}

.stats-row {
    gap: 14px !important;
}

.stats-row > * {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* ==========================================
   Stat cards
   ========================================== */

.stat-card {
    position: relative;
    overflow: hidden;
    background: var(--dd-surface-2);
    border: 1px solid var(--dd-border);
    border-radius: 14px;
    padding: 18px 16px 16px;
    min-height: 108px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: border-color 0.15s ease, transform 0.15s ease;
    --tone: var(--dd-accent);
}

.stat-card:hover {
    border-color: var(--dd-border-strong);
    transform: translateY(-1px);
}

.stat-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--tone);
    opacity: 0.9;
}

.stat-card.tone-teal { --tone: #34d399; }
.stat-card.tone-cyan { --tone: #22d3ee; }
.stat-card.tone-amber { --tone: #fbbf24; }
.stat-card.tone-rose { --tone: #fb7185; }

.stat-card .stat-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.stat-card .stat-label {
    color: var(--dd-muted);
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}

.stat-card .stat-icon {
    color: var(--tone);
    font-size: 17px;
    opacity: 0.9;
}

.stat-card .stat-value {
    color: var(--dd-text);
    font-size: 30px;
    font-weight: 750;
    letter-spacing: -1px;
    line-height: 1.15;
    font-variant-numeric: tabular-nums;
    word-break: break-word;
}

/* ==========================================
   Status pill
   ========================================== */

#status-box {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    border-radius: 12px;
    padding: 11px 14px;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.5;
    border: 1px solid transparent;
    word-break: break-word;
}

#status-box .status-icon {
    flex: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 800;
    margin-top: 1px;
}

#status-box.status-idle {
    background: var(--dd-surface-2);
    border-color: var(--dd-border);
    color: var(--dd-muted);
}
#status-box.status-idle .status-icon { background: var(--dd-surface-3); color: var(--dd-muted); }

#status-box.status-ok {
    background: rgba(16, 185, 129, 0.10);
    border-color: rgba(52, 211, 153, 0.35);
    color: #a7f3d0;
}
#status-box.status-ok .status-icon { background: rgba(52, 211, 153, 0.22); color: #34d399; }

#status-box.status-error {
    background: rgba(251, 113, 133, 0.10);
    border-color: rgba(251, 113, 133, 0.35);
    color: #fecdd3;
}
#status-box.status-error .status-icon { background: rgba(251, 113, 133, 0.22); color: #fb7185; }

/* ==========================================
   Upload area
   ========================================== */

#upload-box {
    border: 1.5px dashed var(--dd-border-strong) !important;
    border-radius: 14px !important;
    background: var(--dd-surface-2) !important;
    transition: border-color 0.15s ease, background 0.15s ease;
}

#upload-box:hover {
    border-color: var(--dd-accent) !important;
    background: var(--dd-surface-3) !important;
}

/* ==========================================
   Buttons
   ========================================== */

button.primary,
#analyze-button {
    background: linear-gradient(135deg, #10b981, #0ea5b7) !important;
    color: #04130e !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1px;
    min-height: 46px !important;
    box-shadow: 0 6px 18px rgba(16, 185, 129, 0.25);
    transition: filter 0.15s ease, transform 0.1s ease;
}

button.primary:hover,
#analyze-button:hover {
    filter: brightness(1.08);
}

button.primary:active,
#analyze-button:active {
    transform: translateY(1px);
}

button.secondary {
    background: var(--dd-surface-2) !important;
    color: var(--dd-text) !important;
    border: 1px solid var(--dd-border-strong) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    min-height: 46px !important;
}

button.secondary:hover {
    background: var(--dd-surface-3) !important;
    border-color: var(--dd-accent) !important;
}

/* ==========================================
   Tabs
   ========================================== */

#main-tabs {
    background: var(--dd-surface) !important;
    border: 1px solid var(--dd-border) !important;
    border-radius: var(--dd-radius) !important;
    padding: 6px 18px 18px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.22);
}

#main-tabs button[role="tab"] {
    color: var(--dd-muted) !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 12px 16px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}

#main-tabs button[role="tab"]:hover {
    color: var(--dd-text) !important;
}

#main-tabs button[role="tab"].selected,
#main-tabs button[role="tab"][aria-selected="true"] {
    color: var(--dd-accent) !important;
    border-bottom: 2px solid var(--dd-accent) !important;
}

#main-tabs .tab-nav,
#main-tabs [role="tablist"] {
    border-bottom: 1px solid var(--dd-border) !important;
    margin-bottom: 14px;
}

#main-tabs .tabitem,
#main-tabs [role="tabpanel"] {
    background: transparent !important;
    border: none !important;
    padding-top: 6px !important;
}

/* ==========================================
   Markdown content
   ========================================== */

.markdown-text,
.prose {
    color: #c5d0e2 !important;
    line-height: 1.65;
}

.prose h1, .prose h2, .prose h3, .prose h4,
.markdown-text h1, .markdown-text h2, .markdown-text h3, .markdown-text h4 {
    color: var(--dd-text) !important;
    letter-spacing: -0.3px;
}

.prose h2, .markdown-text h2 {
    font-size: 17px;
    margin-top: 26px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--dd-border);
}

.prose h3, .markdown-text h3 { font-size: 15px; }
.prose h4, .markdown-text h4 { font-size: 13.5px; color: var(--dd-accent) !important; }

.prose table,
.markdown-text table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid var(--dd-border) !important;
    border-radius: 12px;
    overflow: hidden;
    font-size: 13px;
    margin: 12px 0 18px;
}

.prose th,
.markdown-text th {
    background: var(--dd-surface-2) !important;
    color: var(--dd-muted) !important;
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding: 10px 14px !important;
    border-color: var(--dd-border) !important;
}

.prose td,
.markdown-text td {
    padding: 9px 14px !important;
    border-color: var(--dd-border) !important;
    color: #cbd5e6 !important;
    font-variant-numeric: tabular-nums;
}

.prose tbody tr:nth-child(even) td,
.markdown-text tbody tr:nth-child(even) td {
    background: rgba(255, 255, 255, 0.015);
}

.prose tbody tr:hover td,
.markdown-text tbody tr:hover td {
    background: rgba(52, 211, 153, 0.05);
}

.prose code,
.markdown-text code {
    font-family: "JetBrains Mono", ui-monospace, monospace !important;
    font-size: 12px;
    background: var(--dd-surface-3) !important;
    color: #7dd3fc !important;
    border: 1px solid var(--dd-border);
    border-radius: 6px;
    padding: 1px 6px;
}

.prose pre,
.markdown-text pre {
    background: #0a101b !important;
    border: 1px solid var(--dd-border) !important;
    border-radius: 12px !important;
}

.prose pre code,
.markdown-text pre code {
    background: transparent !important;
    border: none;
    color: #b6c4dc !important;
    padding: 0;
}

.prose blockquote,
.markdown-text blockquote {
    border-left: 3px solid var(--dd-accent) !important;
    background: rgba(52, 211, 153, 0.06);
    color: var(--dd-muted) !important;
    border-radius: 0 10px 10px 0;
    padding: 8px 14px;
}

/* ==========================================
   Data tables / accordions / inputs
   ========================================== */

#preview-table,
.gradio-container .table-wrap {
    border: 1px solid var(--dd-border) !important;
    border-radius: 14px !important;
    overflow: hidden;
}

.gradio-container .accordion,
.gradio-container .block.accordion,
.gradio-container details {
    background: var(--dd-surface-2) !important;
    border: 1px solid var(--dd-border) !important;
    border-radius: 12px !important;
}

input, textarea, select {
    background: var(--dd-surface-2) !important;
    color: var(--dd-text) !important;
    border-color: var(--dd-border-strong) !important;
    border-radius: 10px !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--dd-accent) !important;
    box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.18) !important;
}

/* ==========================================
   Footer
   ========================================== */

#app-footer {
    text-align: center;
    color: var(--dd-faint);
    font-size: 12px;
    padding: 26px 0 10px;
}

#app-footer span {
    color: var(--dd-accent);
}

/* ==========================================
   Small screens
   ========================================== */

@media (max-width: 768px) {
    .gradio-container { padding: 16px 12px !important; }
    #app-header { padding: 22px 18px; }
    #app-header .brand { font-size: 24px; }
    .stat-card .stat-value { font-size: 24px; }
}
"""

# UI Helper Functions

def describe_error(error: Exception) -> str:
    """Error text plus the file, line and code where it was raised."""
    import os
    import traceback

    frames = traceback.extract_tb(error.__traceback__)
    if not frames:
        return str(error)

    last = frames[-1]
    code = (last.line or "").strip()
    return (
        f"{error}  [{os.path.basename(last.filename)}, line {last.lineno}, "
        f"in {last.name}(): {code}]"
    )


STAT_TONES = {
    "Total Rows": "teal",
    "Total Columns": "cyan",
    "Missing Values": "amber",
    "Duplicate Rows": "rose",
}


def format_status(
    success: bool,
    message: str,
    level: Optional[str] = None,
) -> str:
    """
    Create a status pill in HTML format.

    level: "ok", "error" or "idle". When omitted it is derived from `success`.
    """

    if level is None:
        level = "ok" if success else "error"

    icon = {"ok": "✓", "error": "!", "idle": "…"}.get(level, "•")

    return (
        f'<div id="status-box" class="status-{level}">'
        f'<span class="status-icon">{icon}</span>'
        f"<span>{html.escape(str(message))}</span>"
        f"</div>"
    )


def format_stat_card(
    value: str,
    label: str,
    icon: str,
) -> str:
    """
    Create a statistics card in HTML format.
    """

    tone = STAT_TONES.get(label, "teal")

    return f"""
    <div class="stat-card tone-{tone}">
        <div class="stat-top">
            <div class="stat-label">{label}</div>
            <div class="stat-icon">{icon}</div>
        </div>
        <div class="stat-value">{value}</div>
    </div>
    """


def empty_outputs(message: str = "Waiting for a dataset"):
    """
    Return default values for all output components.
    """

    empty_df = pd.DataFrame()

    return (
        format_status(False, message, level="idle"),

        format_stat_card(
            "-",
            "Total Rows",
            "▤",
        ),

        format_stat_card(
            "-",
            "Total Columns",
            "▥",
        ),

        format_stat_card(
            "-",
            "Missing Values",
            "◌",
        ),

        format_stat_card(
            "-",
            "Duplicate Rows",
            "⧉",
        ),

        "Upload a dataset to view its information.",

        "AI analysis will appear here after dataset processing.",

        "Cleaning recommendations will appear here after dataset processing.",

        empty_df,

        {},
        "No cleaned dataset yet.",
        empty_df,
        None,
        empty_df,
        empty_df,
    )



def build_advanced_analysis(df: pd.DataFrame) -> str:
    """
    Build additional dataset analysis:
    - Numerical statistics
    - Categorical/text distribution
    - IQR-based outlier detection
    """

    sections = []

    # Numerical statistics
    numeric_df = df.select_dtypes(include="number")

    if not numeric_df.empty:
        stats = numeric_df.describe().T
        stats_table = [
            "| Column | Mean | Median | Min | Max | Std |",
            "|---|---:|---:|---:|---:|---:|",
        ]

        for column, row in stats.iterrows():
            stats_table.append(
                f"| `{column}` | "
                f"{row['mean']:.2f} | "
                f"{row['50%']:.2f} | "
                f"{row['min']:.2f} | "
                f"{row['max']:.2f} | "
                f"{row['std']:.2f} |"
            )

        sections.append(
            "## Numerical Statistics\n\n"
            + "\n".join(stats_table)
        )
    else:
        sections.append(
            "## Numerical Statistics\n\n"
            "No numerical columns were found."
        )

    # Categorical and text distribution
    distribution_table = [
        "| Column | Unique Values | Top Value | Top Count |",
        "|---|---:|---|---:|",
    ]

    for column in df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns:
        non_null = df[column].dropna()

        if non_null.empty:
            top_value = "-"
            top_count = 0
        else:
            value_counts = non_null.astype(str).value_counts()
            top_value = str(value_counts.index[0]).replace("|", "\\|")
            top_count = int(value_counts.iloc[0])

        unique_count = int(non_null.nunique())

        distribution_table.append(
            f"| `{column}` | {unique_count:,} | "
            f"`{top_value}` | {top_count:,} |"
        )

    if len(distribution_table) > 2:
        sections.append(
            "## Categorical / Text Distribution\n\n"
            + "\n".join(distribution_table)
        )
    else:
        sections.append(
            "## Categorical / Text Distribution\n\n"
            "No categorical or text columns were found."
        )

    # IQR-based outlier detection
    outlier_table = [
        "| Column | Lower Bound | Upper Bound | Outliers |",
        "|---|---:|---:|---:|",
    ]

    for column in numeric_df.columns:
        series = numeric_df[column].dropna()

        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outlier_count = int(
            ((series < lower_bound) | (series > upper_bound)).sum()
        )

        outlier_table.append(
            f"| `{column}` | {lower_bound:.2f} | "
            f"{upper_bound:.2f} | {outlier_count:,} |"
        )

    if len(outlier_table) > 2:
        sections.append(
            "## Outlier Detection (IQR)\n\n"
            + "\n".join(outlier_table)
            + "\n\n"
            "> Outliers are potential anomalies, not automatically incorrect data."
        )
    else:
        sections.append(
            "## Outlier Detection (IQR)\n\n"
            "No numerical columns were found."
        )

    return "\n\n".join(sections)


def build_cleaning_report(df: pd.DataFrame) -> str:
    """
    Detect possible data cleaning issues.

    Detects:
    - Category variants
    - Data type issues

    This function does NOT modify the original DataFrame.
    """

    sections = []

    # ==========================================
    # Category Variants
    # ==========================================

    category_issues = detect_category_variant(df)

    sections.append("## Category Consistency")

    if category_issues.empty:
        sections.append(
            "No category formatting inconsistencies were detected."
        )
    else:
        table = [
            "| Column | Variant | Suggested Value | Count |",
            "|---|---|---|---:|",
        ]

        for _, row in category_issues.iterrows():
            table.append(
                f"| `{row['column']}` "
                f"| `{row['variant']}` "
                f"| `{row['canonical']}` "
                f"| {row['count']:,} |"
            )

        sections.append("\n".join(table))

    # ==========================================
    # Data Type Issues
    # ==========================================

    type_issues = detect_type_issue(df)

    sections.append("## Data Type Consistency")

    if type_issues.empty:
        sections.append(
            "No obvious data type issues were detected."
        )
    else:
        table = [
            "| Column | Current Type | Suggested Type | Confidence |",
            "|---|---|---|---:|",
        ]

        for _, row in type_issues.iterrows():
            confidence = row.get("confidence_percent", "-")

            table.append(
                f"| `{row['column']}` "
                f"| `{row['current_type']}` "
                f"| `{row['suggested_type']}` "
                f"| {confidence}% |"
            )

        sections.append("\n".join(table))

    return "\n\n".join(sections)


def build_missing_strategies(df: pd.DataFrame) -> dict:
    """Choose deterministic missing-value strategies without an LLM advisor."""
    strategies = {}

    for column in df.columns:
        if df[column].isna().sum() == 0:
            continue

        series = df[column]
        missing_percent = (series.isna().sum() / len(df)) * 100 if len(df) else 0

        if missing_percent < 2:
            strategies[column] = "drop_rows"
        elif pd.api.types.is_numeric_dtype(series):
            # Median is safer than mean when the distribution may contain outliers.
            strategies[column] = "median"
        else:
            strategies[column] = "mode"

    return strategies


def format_cleaning_recommendations(df: pd.DataFrame, cleaning_state: dict) -> str:
    """Show all detected cleaning actions."""
    lines = ["### Cleaning Recommendations", ""]

    missing = cleaning_state.get("missing", {})
    category = cleaning_state.get("category")
    types = cleaning_state.get("types")
    duplicate_count = int(df.duplicated().sum())

    lines.append("#### Missing Values")
    if missing:
        lines.extend([
            "| Column | Missing | Action |",
            "|---|---:|---|",
        ])
        for column, strategy in missing.items():
            lines.append(
                f"| `{column}` | {int(df[column].isna().sum()):,} | `{strategy}` |"
            )
    else:
        lines.append("No missing values detected.")

    lines.extend(["", "#### Category Consistency"])
    if category is None or category.empty:
        lines.append("No category variants detected.")
    else:
        lines.extend([
            "| Column | Variant | Replace With | Count |",
            "|---|---|---|---:|",
        ])
        for _, row in category.iterrows():
            lines.append(
                f"| `{row['column']}` | `{row['variant']}` | "
                f"`{row['canonical']}` | {int(row['count']):,} |"
            )

    lines.extend(["", "#### Data Types"])
    if types is None or types.empty:
        lines.append("No obvious type issues detected.")
    else:
        lines.extend([
            "| Column | Current | Suggested | Confidence |",
            "|---|---|---|---:|",
        ])
        for _, row in types.iterrows():
            confidence = row.get("confidence_percent", "-")
            lines.append(
                f"| `{row['column']}` | `{row['current_type']}` | "
                f"`{row['suggested_type']}` | {confidence}% |"
            )

    lines.extend(["", "#### Duplicate Rows"])
    lines.append(f"{duplicate_count:,} duplicate rows will be removed.")

    return "\n".join(lines)


def apply_missing_strategies(df: pd.DataFrame, strategies: dict) -> pd.DataFrame:
    result = df.copy()

    for column, strategy in (strategies or {}).items():
        if column not in result.columns:
            continue

        if strategy == "mean" and pd.api.types.is_numeric_dtype(result[column]):
            result[column] = result[column].fillna(result[column].mean())
        elif strategy == "median" and pd.api.types.is_numeric_dtype(result[column]):
            result[column] = result[column].fillna(result[column].median())
        elif strategy == "mode":
            mode = result[column].mode(dropna=True)
            if not mode.empty:
                result[column] = result[column].fillna(mode.iloc[0])
        elif strategy == "drop_rows":
            result = result.dropna(subset=[column])

    return result


def apply_category_corrections(df: pd.DataFrame, issues: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if issues is None or issues.empty:
        return result

    for _, row in issues.iterrows():
        column = row["column"]
        variant = row["variant"]
        canonical = row["canonical"]
        if column in result.columns:
            mask = result[column].astype("string") == str(variant)
            result.loc[mask, column] = canonical

    return result


def apply_value_sanity_in_app(df: pd.DataFrame):
    """Apply deterministic Value Sanity rules directly in app.py."""
    result = df.copy()
    logs = []
    corrections = 0

    # ------------------------------------------
    # QUALITY: remove units/text, then enforce integer >= 0
    # ------------------------------------------
    for column in result.columns:
        column_name = str(column).strip().lower()

        if "quality" in column_name:
            original = result[column].copy()

            # Examples: "80 kg", "75.5 kg", "$80" -> 80, 75.5, 80
            text = (
                result[column]
                .astype("string")
                .str.strip()
                .str.replace(",", "", regex=False)
            )
            extracted = text.str.extract(
                r"([+\-]?\d+(?:\.\d+)?)",
                expand=False,
            )
            numeric = pd.to_numeric(extracted, errors="coerce")

            changed_unit = (
                original.notna()
                & numeric.notna()
                & (original.astype("string").str.strip() != numeric.astype("string"))
            )

            if changed_unit.any():
                count = int(changed_unit.sum())
                corrections += count
                logs.append(
                    f"{column} [quality]: removed units/text from {count:,} value(s)"
                )

            result[column] = numeric

            # quality: non-negative integer
            negative = result[column].notna() & (result[column] < 0)
            if negative.any():
                count = int(negative.sum())
                result.loc[negative, column] = 0
                corrections += count
                logs.append(
                    f"{column} [below_min]: changed {count:,} negative value(s) to 0"
                )

            decimal = (
                result[column].notna()
                & ((result[column] - result[column].round()).abs() > 1e-9)
            )
            if decimal.any():
                count = int(decimal.sum())
                result.loc[decimal, column] = result.loc[decimal, column].round()
                corrections += count
                logs.append(
                    f"{column} [not_integer]: rounded {count:,} value(s)"
                )

            # Keep quality as nullable integer when possible.
            result[column] = result[column].round().astype("Int64")

    # ------------------------------------------
    # AGE: numeric, integer, 0 <= age <= 120
    # ------------------------------------------
    for column in result.columns:
        if not _has_word(column, "age"):
            continue

        original = result[column].copy()
        numeric = pd.to_numeric(result[column], errors="coerce")

        invalid_number = original.notna() & numeric.isna()
        if invalid_number.any():
            count = int(invalid_number.sum())
            corrections += count
            logs.append(
                f"{column} [not_number]: converted {count:,} invalid value(s) to NaN"
            )

        below_min = numeric.notna() & (numeric < 0)
        if below_min.any():
            count = int(below_min.sum())
            numeric.loc[below_min] = 0
            corrections += count
            logs.append(
                f"{column} [below_min]: clipped {count:,} value(s) to 0"
            )

        above_max = numeric.notna() & (numeric > 120)
        if above_max.any():
            count = int(above_max.sum())
            numeric.loc[above_max] = 120
            corrections += count
            logs.append(
                f"{column} [above_max]: clipped {count:,} value(s) to 120"
            )

        decimal = numeric.notna() & ((numeric - numeric.round()).abs() > 1e-9)
        if decimal.any():
            count = int(decimal.sum())
            numeric.loc[decimal] = numeric.loc[decimal].round()
            corrections += count
            logs.append(
                f"{column} [not_integer]: rounded {count:,} value(s)"
            )

        result[column] = numeric.round().astype("Int64")

    # ------------------------------------------
    # ALL OTHER NUMERIC COLUMNS: strip units such as "5 pcs", "$120", "1,200 kg"
    # ------------------------------------------
    try:
        rule_columns = {
            column
            for column, rule in match_rules(result.columns).items()
            if rule.dtype in ("integer", "number") or rule.min_value is not None
        }
    except Exception:
        rule_columns = set()

    result, unit_count, unit_log = strip_units(result, rule_columns=rule_columns)
    if unit_count:
        corrections += unit_count
        logs.append(unit_log)

    return result, corrections, "\n".join(logs) if logs else "No value sanity corrections were required."


def apply_all_cleaning(df: pd.DataFrame, cleaning_state: dict):
    """
    Run all cleaning functions in a fixed, deterministic order.

    Cleaning order:
    1. Missing values
    2. Category consistency
    3. Value sanity
    4. Data type correction
    5. Remove duplicates

    Value Sanity handles special columns such as:
    - quality
    - age

    These columns are skipped by the generic Type Corrector
    to prevent their cleaned values from being overwritten.
    """

    original = df.copy()
    result = original.copy()

    before = {
        "rows": len(result),
        "missing": int(result.isna().sum().sum()),
        "duplicates": int(result.duplicated().sum()),
    }

    # =========================================================
    # 1. Missing Values
    # =========================================================

    # Price columns are filled later (step 3b), after units are stripped,
    # so they get a numeric median instead of a text "mode".
    result = apply_missing_strategies(
        result,
        {
            column: strategy
            for column, strategy in cleaning_state.get("missing", {}).items()
            if not is_price_column(column)
        },
    )

    # =========================================================
    # 2. Category Consistency
    # =========================================================

    result = apply_category_corrections(
        result,
        cleaning_state.get("category")
    )

    # =========================================================
    # 3. Value Sanity
    #
    # Must happen BEFORE generic type correction.
    #
    # Examples:
    # "80 kg"   -> 80
    # "75.5 kg" -> 76
    # -10       -> 0
    # =========================================================

    result, value_corrections, value_log = (
        apply_value_sanity_in_app(result)
    )

    # =========================================================
    # 3b. Missing prices -> median (after units are stripped)
    # =========================================================

    result, price_log = fill_missing_prices(result)

    # =========================================================
    # 4. Data Type Correction
    #
    # IMPORTANT:
    # Do NOT allow Type Corrector to modify columns that are
    # already handled by Value Sanity.
    # =========================================================

    type_issues = cleaning_state.get("types")

    type_corrections = {}

    SANITY_COLUMNS = {
        "quality",
        "age",
    }

    if type_issues is not None and not type_issues.empty:

        for _, row in type_issues.iterrows():

            column = str(row["column"])
            column_lower = column.strip().lower()

            # Value Sanity already handles these columns.
            # Skip them to prevent overwriting cleaned values.
            if "quality" in column_lower or _has_word(column, "age"):
                continue

            type_corrections[column] = str(
                row["suggested_type"]
            )

    type_log = "No type corrections were required."

    # Apply generic type corrections only to
    # columns that are NOT handled by Value Sanity.
    if type_corrections:

        result , type_log = correct_types(result,type_corrections)

    # =========================================================
    # 4b. Date Normalization  (2020-10-02 -> 2020/10/2)
    # =========================================================

    result, date_log = normalize_dates(result)

    # =========================================================
    # 5. Remove Duplicates
    # =========================================================

    duplicate_before = int(
        result.duplicated().sum()
    )

    result = (
        result
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # =========================================================
    # AFTER
    # =========================================================

    after = {
        "rows": len(result),
        "missing": int(result.isna().sum().sum()),
        "duplicates": int(result.duplicated().sum()),
    }

    # =========================================================
    # Cleaning Statistics
    # =========================================================

    stats = {
        "rows_before": before["rows"],
        "rows_after": after["rows"],
        "rows_removed": (
            before["rows"] - after["rows"]
        ),

        "missing_before": before["missing"],
        "missing_after": after["missing"],

        "duplicates_removed": duplicate_before,

        "type_corrections": len(
            type_corrections
        ),

        "type_log": type_log,

        "value_corrections": value_corrections,

        "value_log": value_log,

        "date_log": date_log,

        "price_log": price_log,
    }

    return result, stats


def preview_cleaning(
    df: pd.DataFrame,
    cleaning_state: dict
):
    if df is None or df.empty:
        return (
            pd.DataFrame(),
            "Please analyze a dataset first."
        )

    try:

        cleaned_df, stats = apply_all_cleaning(
            df,
            cleaning_state or {}
        )

        message = (
            "### Cleaning Preview\n\n"

            f"- Rows: "
            f"**{stats['rows_before']:,} "
            f"→ {stats['rows_after']:,}**\n"

            f"- Missing values: "
            f"**{stats['missing_before']:,} "
            f"→ {stats['missing_after']:,}**\n"

            f"- Duplicate rows removed: "
            f"**{stats['duplicates_removed']:,}**\n"

            f"- Type corrections applied: "
            f"**{stats['type_corrections']:,}**\n"

            f"- Value corrections applied: "
            f"**{stats['value_corrections']:,}**\n\n"

            "#### Value Sanity Log\n"

            f"```text\n"
            f"{stats['value_log']}\n"
            f"```\n\n"

            "#### Date Log\n"

            f"```text\n"
            f"{stats['date_log']}\n"
            f"```\n\n"

            "#### Price Log\n"

            f"```text\n"
            f"{stats['price_log']}\n"
            f"```"
        )

        return (
            cleaned_df.head(20),
            message
        )

    except Exception as error:

        return (
            pd.DataFrame(),
            f"### Cleaning Preview Failed\n\n"
            f"`{describe_error(error)}`"
        )

def apply_cleaning(
    file,
    cleaning_state: dict
):

    if file is None:
        return (
            "Please upload and analyze a dataset first.",
            pd.DataFrame(),
            None
        )

    try:

        original_df = load_document(
            str(file)
        )

        cleaned_df, stats = apply_all_cleaning(
            original_df,
            cleaning_state or {}
        )

        output_path = (
            Path(tempfile.gettempdir())
            / "datadoctor_cleaned_dataset.csv"
        )

        cleaned_df.to_csv(
            output_path,
            index=False
        )

        status = (
            "### Cleaning Completed ✓\n\n"

            f"- Rows: "
            f"**{stats['rows_before']:,} "
            f"→ {stats['rows_after']:,}**\n"

            f"- Missing values: "
            f"**{stats['missing_before']:,} "
            f"→ {stats['missing_after']:,}**\n"

            f"- Duplicate rows removed: "
            f"**{stats['duplicates_removed']:,}**\n"

            f"- Type corrections applied: "
            f"**{stats['type_corrections']:,}**\n"

            f"- Value corrections applied: "
            f"**{stats['value_corrections']:,}**\n\n"

            "#### Type Corrector Log\n"

            f"```text\n"
            f"{stats['type_log']}\n"
            f"```\n\n"

            "#### Value Sanity Log\n"

            f"```text\n"
            f"{stats['value_log']}\n"
            f"```\n\n"

            "#### Date Log\n"

            f"```text\n"
            f"{stats['date_log']}\n"
            f"```\n\n"

            "#### Price Log\n"

            f"```text\n"
            f"{stats['price_log']}\n"
            f"```\n\n"

            "The cleaned dataset is ready to download."
        )

        return (
            status,
            cleaned_df.head(20),
            str(output_path)
        )

    except Exception as error:

        return (
            f"### Cleaning Failed\n\n"
            f"`{describe_error(error)}`",
            pd.DataFrame(),
            None
        )


# Value Normalization


def apply_value_corrections(file, choices_json: str):
    """
    Apply only the value corrections explicitly selected by the user.

    Example:
    [
      {"column": "age", "violation": "above_max", "action": "clip"},
      {"column": "quality", "violation": "not_integer", "action": "round_int"}
    ]
    """
    if file is None:
        return "Please upload and analyze a dataset first.", pd.DataFrame()

    try:
        import json

        data = json.loads(choices_json or "[]")
        if not isinstance(data, list):
            raise ValueError("Choices must be a JSON list.")

        choices = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("Each choice must be an object.")
            choices.append((
                item["column"],
                item["violation"],
                item["action"],
            ))

        df = load_document(str(file))
        cleaned_df, log_text = normalize_values(df, choices)

        return (
            "### Value Corrections Applied ✓\n\n"
            + (log_text or "No corrections were applied."),
            cleaned_df.head(20),
        )

    except Exception as error:
        return f"### Value Correction Failed\n\n`{error}`", pd.DataFrame()


# Dataset Processing

def process_file(file):
    if file is None:
        return empty_outputs("Please upload a dataset first.")

    try:
        file_path = str(file)
        df = load_document(file_path)

        row_count = len(df)
        column_count = len(df.columns)
        missing_count = int(df.isna().sum().sum())
        duplicate_count = int(df.duplicated().sum())
        file_name = Path(file_path).name
        file_type = Path(file_path).suffix.upper().replace(".", "")

        status = format_status(True, f"Successfully loaded: {file_name}")
        rows_card = format_stat_card(f"{row_count:,}", "Total Rows", "▤")
        columns_card = format_stat_card(f"{column_count:,}", "Total Columns", "▥")
        missing_card = format_stat_card(f"{missing_count:,}", "Missing Values", "◌")
        duplicate_card = format_stat_card(f"{duplicate_count:,}", "Duplicate Rows", "⧉")

        column_rows = []
        for column, dtype in df.dtypes.items():
            column_rows.append(
                f"| `{column}` | `{dtype}` | {int(df[column].isna().sum()):,} |"
            )

        summary = f"""
## Dataset Overview

| Metric | Value |
|---|---|
| File Name | `{file_name}` |
| File Type | `{file_type}` |
| Total Rows | {row_count:,} |
| Total Columns | {column_count:,} |
| Missing Values | {missing_count:,} |
| Duplicate Rows | {duplicate_count:,} |

## Column Information

| Column | Data Type | Missing Values |
|---|---|---:|
{chr(10).join(column_rows)}
"""

        summary += "\n\n" + build_advanced_analysis(df)

        category_issues = detect_category_variant(df)
        type_issues = detect_type_issue(df)
        missing_strategies = build_missing_strategies(df)

        # Value Sanity Validation
        value_report = detect_value_violations(df)
        rule_summary = build_rule_summary(df)

        cleaning_state = {
            "missing": missing_strategies,
            "category": category_issues,
            "types": type_issues,
            "value_report": value_report,
            "value_rules": rule_summary,
            "value_choices": [],
        }

        cleaning_report = format_cleaning_recommendations(df, cleaning_state)
        summary += "\n\n" + cleaning_report

        if not value_report.empty:
            summary += "\n\n## Value Sanity Validation\n\n" + value_report.to_markdown(index=False)
        else:
            summary += "\n\n## Value Sanity Validation\n\nNo violations were detected by the configured value rules."

        try:
            ai_analysis = generate_analysis(summary)
        except Exception as ai_error:
            ai_analysis = (
                "AI analysis unavailable. Local dataset analysis is still available.\n\n"
                f"`{ai_error}`"
            )

        return (
            status,
            rows_card,
            columns_card,
            missing_card,
            duplicate_card,
            summary,
            ai_analysis,
            cleaning_report,
            df.head(20),
            cleaning_state,
            "No cleaned dataset yet.",
            pd.DataFrame(),
            None,
            value_report,
            rule_summary,
        )

    except Exception as error:
        import traceback

        error_trace = traceback.format_exc()
        print(error_trace)  # also shows in the terminal that runs the app

        return (
            format_status(False, f"Failed to process file: {describe_error(error)}"),
            format_stat_card("-", "Total Rows", "▤"),
            format_stat_card("-", "Total Columns", "▥"),
            format_stat_card("-", "Missing Values", "◌"),
            format_stat_card("-", "Duplicate Rows", "⧉"),
            f"## Processing Error\n\n```text\n{error_trace}\n```",
            "AI analysis could not be generated because dataset processing failed.",
            "Cleaning analysis could not be generated.",
            pd.DataFrame(),
            {},
            "No cleaned dataset yet.",
            pd.DataFrame(),
            None,
            pd.DataFrame(),
            pd.DataFrame(),
        )


# Gradio Application

THEME = gr.themes.Base(
    primary_hue="emerald",
    secondary_hue="cyan",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "Segoe UI", "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
).set(
    # Same dark values for light and dark mode, so the app always looks the same.
    body_background_fill="#070b12",
    body_background_fill_dark="#070b12",
    body_text_color="#e8edf5",
    body_text_color_dark="#e8edf5",
    body_text_color_subdued="#8a97ad",
    body_text_color_subdued_dark="#8a97ad",
    background_fill_primary="#0e1420",
    background_fill_primary_dark="#0e1420",
    background_fill_secondary="#131b2b",
    background_fill_secondary_dark="#131b2b",
    block_background_fill="#0e1420",
    block_background_fill_dark="#0e1420",
    block_border_color="#1f2a3d",
    block_border_color_dark="#1f2a3d",
    block_label_background_fill="#131b2b",
    block_label_background_fill_dark="#131b2b",
    block_label_text_color="#8a97ad",
    block_label_text_color_dark="#8a97ad",
    block_title_text_color="#e8edf5",
    block_title_text_color_dark="#e8edf5",
    border_color_primary="#1f2a3d",
    border_color_primary_dark="#1f2a3d",
    input_background_fill="#131b2b",
    input_background_fill_dark="#131b2b",
    table_even_background_fill="#0e1420",
    table_even_background_fill_dark="#0e1420",
    table_odd_background_fill="#111a2a",
    table_odd_background_fill_dark="#111a2a",
    table_border_color="#1f2a3d",
    table_border_color_dark="#1f2a3d",
    button_primary_background_fill="#10b981",
    button_primary_background_fill_dark="#10b981",
    button_primary_text_color="#04130e",
    button_primary_text_color_dark="#04130e",
    button_secondary_background_fill="#131b2b",
    button_secondary_background_fill_dark="#131b2b",
    button_secondary_text_color="#e8edf5",
    button_secondary_text_color_dark="#e8edf5",
)

with gr.Blocks(
    css=CUSTOM_CSS,
    theme=THEME,
    title="DataDoctor",
) as demo:

    # Header


    gr.HTML(
        """
        <div id="app-header">

            <div class="hero-top">
                <div class="logo">🩺</div>
                <div>
                    <div class="brand">DataDoctor</div>
                    <div class="subtitle">
                        Dataset health &amp; quality platform. Inspect, diagnose and
                        clean your data before it reaches a machine learning model.
                    </div>
                </div>
            </div>

            <div class="steps">
                <div class="step"><b>1</b> Upload</div>
                <div class="step"><b>2</b> Analyze</div>
                <div class="step"><b>3</b> Review issues</div>
                <div class="step"><b>4</b> Clean &amp; export</div>
            </div>

        </div>
        """
    )

    # Upload + health snapshot


    with gr.Row(elem_classes="dashboard-row"):

        with gr.Column(
            scale=5,
            elem_classes="section-card panel-left",
        ):

            gr.HTML(
                """
                <div>
                    <div class="card-title">Upload dataset</div>
                    <div class="card-sub">
                        CSV or Excel (.csv, .xlsx, .xls).
                        Nothing is processed until you press Analyze.
                    </div>
                </div>
                """
            )

            file_input = gr.File(
                label="Dataset File",
                file_types=[
                    ".csv",
                    ".xlsx",
                    ".xls",
                ],
                type="filepath",
                elem_id="upload-box",
            )

            analyze_button = gr.Button(
                "Analyze Dataset",
                variant="primary",
                elem_id="analyze-button",
            )

            status_output = gr.HTML(
                format_status(
                    False,
                    "Waiting for a dataset",
                    level="idle",
                )
            )

        with gr.Column(
            scale=7,
            elem_classes="section-card panel-right",
        ):

            gr.HTML(
                """
                <div>
                    <div class="card-title">Dataset health snapshot</div>
                    <div class="card-sub">
                        A quick read on size, gaps and duplicates.
                    </div>
                </div>
                """
            )

            with gr.Row(elem_classes="stats-row"):

                rows_output = gr.HTML(
                    format_stat_card("-", "Total Rows", "▤")
                )

                columns_output = gr.HTML(
                    format_stat_card("-", "Total Columns", "▥")
                )

            with gr.Row(elem_classes="stats-row"):

                missing_output = gr.HTML(
                    format_stat_card("-", "Missing Values", "◌")
                )

                duplicate_output = gr.HTML(
                    format_stat_card("-", "Duplicate Rows", "⧉")
                )

    # Results (tabs)

    with gr.Tabs(elem_id="main-tabs"):

        with gr.Tab("Overview"):

            summary_output = gr.Markdown(
                "Upload a dataset to view its summary.",
                elem_classes="markdown-text",
            )

        with gr.Tab("AI analysis"):

            ai_analysis_output = gr.Markdown(
                "AI analysis will appear here after dataset processing.",
                elem_classes="markdown-text",
            )

        with gr.Tab("Data quality"):

            cleaning_output = gr.Markdown(
                "Cleaning recommendations will appear here after dataset processing.",
                elem_classes="markdown-text",
            )

            advisor_state = gr.State({})

            gr.Markdown("### Value sanity validation")

            gr.Markdown(
                "Checks values against explicit sanity rules. "
                "Review violations before cleaning.",
                elem_classes="markdown-text",
            )

            value_report_output = gr.Dataframe(
                headers=None,
                interactive=False,
                wrap=True,
            )

            with gr.Accordion("Matched value rules", open=False):

                value_rule_output = gr.Dataframe(
                    headers=None,
                    interactive=False,
                    wrap=True,
                )

        with gr.Tab("Data preview"):

            gr.Markdown(
                "The first 20 rows of your dataset.",
                elem_classes="markdown-text",
            )

            preview_output = gr.Dataframe(
                headers=None,
                interactive=False,
                wrap=True,
                elem_id="preview-table",
            )

        with gr.Tab("Clean & export"):

            gr.Markdown(
                "Preview the recommended cleaning first, then apply it "
                "and download the cleaned dataset.",
                elem_classes="markdown-text",
            )

            with gr.Row():
                preview_clean_button = gr.Button("Preview Cleaning")
                apply_clean_button = gr.Button(
                    "Clean Dataset",
                    variant="primary",
                )

            cleaning_status = gr.Markdown(
                "No cleaned dataset yet.",
                elem_classes="markdown-text",
            )

            cleaned_preview = gr.Dataframe(
                headers=None,
                interactive=False,
                wrap=True,
            )

            download_output = gr.File(
                label="Download Cleaned Dataset"
            )

    # Events

    outputs = [
        status_output,
        rows_output,
        columns_output,
        missing_output,
        duplicate_output,
        summary_output,
        ai_analysis_output,
        cleaning_output,
        preview_output,
        advisor_state,
        cleaning_status,
        cleaned_preview,
        download_output,
        value_report_output,
        value_rule_output,
    ]

    # Selecting a new file -> clear old results; nothing is processed until the button is clicked
    def reset_on_upload():
        return empty_outputs('File ready. Click "Analyze Dataset" to process.')

    file_input.upload(
        fn=reset_on_upload,
        inputs=None,
        outputs=outputs,
    )

    # Removing the file -> reset results to defaults
    file_input.clear(
        fn=lambda: empty_outputs("Waiting for a dataset"),
        inputs=None,
        outputs=outputs,
    )

    # Process only when clicking the button (upload alone does not process)
    analyze_button.click(
        fn=process_file,
        inputs=file_input,
        outputs=outputs,
        show_progress="full",
    )

    preview_clean_button.click(fn=lambda cleaning_state, file: preview_cleaning(load_document(str(file)) if file else pd.DataFrame(),cleaning_state,),
        inputs=[advisor_state, file_input],
        outputs=[cleaned_preview, cleaning_status],
        show_progress="full",
    )

    apply_clean_button.click(
        fn=apply_cleaning,
        inputs=[file_input, advisor_state],
        outputs=[cleaning_status, cleaned_preview, download_output],
        show_progress="full",
    )

    # Footer


    gr.HTML(
        """
        <div id="app-footer">
            DataDoctor · Built with Python, Pandas & Gradio
        </div>
        """
    )


# Launch Application

if __name__ == "__main__":
    demo.launch(share=False,inbrowser=True,)