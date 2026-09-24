import sys
from pathlib import Path

import gradio as gr
import pandas as pd



# Project Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from ingestion import load_document
from ai.analyzer import generate_analysis


# Custom CSS


CUSTOM_CSS = """
/* ==========================================
   Global Dark Theme
   ========================================== */

:root {
    --primary: #818cf8;
    --primary-hover: #a5b4fc;
    --bg-main: #0b0f19;
    --bg-card: #111827;
    --bg-card-hover: #172033;
    --border: #273449;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
}

body {
    background: #0b0f19 !important;
}

.gradio-container {
    max-width: 1380px !important;
    margin: 0 auto !important;
    padding: 24px 32px !important;
    background: #0b0f19 !important;
    color: #f8fafc !important;
    font-family: "Inter", "Segoe UI", sans-serif !important;
}

/* ==========================================
   Header
   ========================================== */

#app-header {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #1e1b4b 55%,
        #172554 100%
    );

    border: 1px solid #3730a3;
    border-radius: 24px;
    padding: 32px 36px;
    margin-bottom: 24px;
    color: white;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
}

#app-header .brand {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.8px;
    color: #f8fafc;
}

#app-header .subtitle {
    margin-top: 8px;
    font-size: 15px;
    color: #c7d2fe;
    line-height: 1.7;
}

#app-header .badge {
    display: inline-block;
    margin-top: 18px;
    padding: 5px 12px;
    border: 1px solid #4f46e5;
    border-radius: 999px;
    color: #c7d2fe;
    font-size: 12px;
}

/* ==========================================
   Dashboard Row (Left / Right balance)
   ========================================== */

.dashboard-row {
    align-items: stretch !important;
    gap: 20px !important;
}

.section-card {
    background: #111827 !important;
    border: 1px solid #273449 !important;
    border-radius: 18px;
    padding: 22px !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.15);
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}

/* ฝั่งซ้าย: จัดองค์ประกอบให้ชิดบน เว้นระยะเท่ากัน */
.panel-left {
    justify-content: flex-start !important;
    gap: 4px;
}

.panel-left > * {
    margin-bottom: 6px;
}

/* ฝั่งขวา: จัดการ์ดสถิติให้อยู่กึ่งกลางแนวตั้ง เทียบความสูงกับฝั่งซ้าย */
.panel-right {
    justify-content: flex-start !important;
}

.stats-grid-wrap {
    flex: 1 1 auto;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    gap: 16px;
}

.stats-row {
    gap: 16px !important;
}

.stats-row > * {
    flex: 1 1 0 !important;
}

/* แท็กรูปแบบไฟล์ที่รองรับ (แทน markdown ยาว) */
.format-tags {
    margin-top: 10px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.format-tags .tag {
    background: #0f172a;
    border: 1px solid #374151;
    color: #c7d2fe;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.stage-note {
    margin-top: auto;
    padding-top: 14px;
    color: #64748b;
    font-size: 12px;
    border-top: 1px dashed #273449;
}

/* ==========================================
   Upload Area
   ========================================== */

#upload-box {
    border: 2px dashed #374151 !important;
    border-radius: 16px !important;
    background: #0f172a !important;
    color: #e2e8f0 !important;
}

#upload-box:hover {
    border-color: #818cf8 !important;
}

/* ==========================================
   Statistics Cards
   ========================================== */

.stat-card {
    background: #0f172a;
    border: 1px solid #273449;
    border-radius: 16px;
    padding: 18px 12px;
    min-height: 106px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.stat-card .stat-icon {
    font-size: 18px;
    margin-bottom: 5px;
}

.stat-card .stat-value {
    color: #a5b4fc;
    font-size: 25px;
    font-weight: 750;
    line-height: 1.3;
    word-break: break-word;
}

.stat-card .stat-label {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 500;
    margin-top: 5px;
}

/* ==========================================
   Status
   ========================================== */

#status-box {
    border-radius: 12px;
    padding: 13px 16px;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.6;
}

/* ==========================================
   Buttons
   ========================================== */

#analyze-button {
    border-radius: 12px !important;
    font-weight: 650 !important;
    min-height: 46px !important;
    background: #4f46e5 !important;
    color: white !important;
    border: none !important;
}

#analyze-button:hover {
    background: #6366f1 !important;
}

/* ==========================================
   Text and Markdown
   ========================================== */

h1, h2, h3, h4, label {
    color: #f8fafc !important;
}

p, span {
    color: inherit;
}

.markdown-text {
    color: #cbd5e1 !important;
}

.prose {
    color: #cbd5e1 !important;
}

.prose h1,
.prose h2,
.prose h3 {
    color: #f8fafc !important;
}

.prose table {
    color: #cbd5e1 !important;
    border-color: #273449 !important;
}

.prose th {
    background: #1e293b !important;
    color: #f8fafc !important;
}

.prose td {
    border-color: #273449 !important;
}

/* ==========================================
   Data Preview
   ========================================== */

#preview-table {
    border: 1px solid #273449 !important;
    border-radius: 16px;
    overflow: hidden;
}

/* Dataframe table */
#preview-table table {
    background: #111827 !important;
    color: #e2e8f0 !important;
}

#preview-table th {
    background: #1e293b !important;
    color: #f8fafc !important;
}

#preview-table td {
    background: #111827 !important;
    color: #cbd5e1 !important;
    border-color: #273449 !important;
}

/* ==========================================
   Inputs
   ========================================== */

input,
textarea,
select {
    background: #0f172a !important;
    color: #f8fafc !important;
    border-color: #374151 !important;
}

/* ==========================================
   Footer
   ========================================== */

#app-footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 24px 0 8px 0;
}

footer {
    display: none !important;
}
"""

# UI Helper Functions

def format_status(
    success: bool,
    message: str,
) -> str:
    """
    Create a status message in HTML format.
    """

    if success:
        color = "#166534"
        background = "#dcfce7"
        icon = "✓"

    else:
        color = "#991b1b"
        background = "#fee2e2"
        icon = "!"

    return f"""
    <div
        id="status-box"
        style="
            background: {background};
            color: {color};
        "
    >
        <span style="margin-right: 8px;">{icon}</span>
        {message}
    </div>
    """


def format_stat_card(
    value: str,
    label: str,
    icon: str,
) -> str:
    """
    Create a statistics card in HTML format.
    """

    return f"""
    <div class="stat-card">

        <div class="stat-icon">
            {icon}
        </div>

        <div class="stat-value">
            {value}
        </div>

        <div class="stat-label">
            {label}
        </div>

    </div>
    """


def empty_outputs(message: str = "Waiting for a dataset"):
    """
    Return default values for all output components.
    """

    empty_df = pd.DataFrame()

    return (
        format_status(False, message),

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


# Dataset Processing


def process_file(file):
    """
    Load and inspect a CSV or Excel file.

    Returns:
        - Status message
        - Total rows card
        - Total columns card
        - Missing values card
        - Duplicate rows card
        - Dataset summary
        - Data preview
    """

    if file is None:
        return empty_outputs(
            "Please upload a dataset first."
        )

    try:
        # Gradio filepath
        file_path = str(file)

        # Load as Pandas DataFrame
        df = load_document(file_path)

        # Basic statistics
        row_count = len(df)
        column_count = len(df.columns)

        missing_count = int(
            df.isna().sum().sum()
        )

        duplicate_count = int(
            df.duplicated().sum()
        )

        file_name = Path(file_path).name
        file_type = Path(file_path).suffix.upper().replace(
            ".",
            "",
        )

        # Status
        status = format_status(
            True,
            f"Successfully loaded: {file_name}",
        )

        # Statistic cards
        rows_card = format_stat_card(
            f"{row_count:,}",
            "Total Rows",
            "▤",
        )

        columns_card = format_stat_card(
            f"{column_count:,}",
            "Total Columns",
            "▥",
        )

        missing_card = format_stat_card(
            f"{missing_count:,}",
            "Missing Values",
            "◌",
        )

        duplicate_card = format_stat_card(
            f"{duplicate_count:,}",
            "Duplicate Rows",
            "⧉",
        )

        # Column information
        column_rows = []

        for column, dtype in df.dtypes.items():

            missing = int(df[column].isna().sum())

            column_rows.append(
                f"| `{column}` | `{dtype}` | {missing:,} |"
            )

        column_table = "\n".join(column_rows)

        # Dataset summary
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
{column_table}
"""

        # Advanced analysis
        advanced_analysis = build_advanced_analysis(df)
        summary = summary + "\n\n" + advanced_analysis

        # Generate AI analysis
        ai_analysis = generate_analysis(summary)

        # Preview
        preview = df.head(20)

        return (
            status,
            rows_card,
            columns_card,
            missing_card,
            duplicate_card,
            summary,
            ai_analysis,
            preview,
        )

    except Exception as error:

        return (
            format_status(
                False,
                f"Failed to process file: {error}",
            ),

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

            f"""
## Processing Error

```text
{error}
```
""",

            "AI analysis could not be generated because dataset processing failed.",

            pd.DataFrame(),
        )


# ==========================================
# Gradio Application
# ==========================================

with gr.Blocks(
    css=CUSTOM_CSS,
    theme=gr.themes.Base(
        primary_hue="indigo",
        secondary_hue="slate",
        neutral_hue="slate",
    ),
    title="DataDoctor",
) as demo:

    # --------------------------------------
    # Header
    # --------------------------------------

    gr.HTML(
        """
        <div id="app-header">

            <div class="brand">
                🩺 DataDoctor
            </div>

            <div class="subtitle">
                Dataset Health & Quality Platform
                <br>
                Upload, inspect, and understand your data
                before building machine learning models.
            </div>

            <div class="badge">
                ● Data Inspection · CSV · Excel
            </div>

        </div>
        """
    )

    # --------------------------------------
    # Main Dashboard (Left / Right — สัดส่วนเท่ากัน 1:1)
    # --------------------------------------

    with gr.Row(elem_classes="dashboard-row"):

        # ---------- ฝั่งซ้าย: Upload Panel ----------
        with gr.Column(
            scale=1,
            elem_classes="section-card panel-left",
        ):

            gr.Markdown("### Upload Dataset")

            gr.Markdown(
                "Select a CSV or Excel file to begin your dataset inspection.",
                elem_classes="markdown-text",
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
                )
            )

            # แท็กรูปแบบไฟล์ที่รองรับ — กระชับกว่า markdown เดิม
            gr.HTML(
                """
                <div class="format-tags">
                    <span class="tag">CSV</span>
                    <span class="tag">XLSX</span>
                    <span class="tag">XLS</span>
                </div>
                """
            )

            gr.HTML(
                """
                <div class="stage-note">
                    Current stage: file ingestion &amp; initial inspection.
                </div>
                """
            )

        # ---------- ฝั่งขวา: Statistics Panel ----------
        with gr.Column(
            scale=1,
            elem_classes="section-card panel-right",
        ):

            gr.Markdown("### Dataset Health Snapshot")

            with gr.Column(elem_classes="stats-grid-wrap"):

                with gr.Row(elem_classes="stats-row"):

                    rows_output = gr.HTML(
                        format_stat_card(
                            "-",
                            "Total Rows",
                            "▤",
                        )
                    )

                    columns_output = gr.HTML(
                        format_stat_card(
                            "-",
                            "Total Columns",
                            "▥",
                        )
                    )

                with gr.Row(elem_classes="stats-row"):

                    missing_output = gr.HTML(
                        format_stat_card(
                            "-",
                            "Missing Values",
                            "◌",
                        )
                    )

                    duplicate_output = gr.HTML(
                        format_stat_card(
                            "-",
                            "Duplicate Rows",
                            "⧉",
                        )
                    )

    # --------------------------------------
    # Dataset Summary
    # --------------------------------------

    gr.Markdown("### Dataset Information")

    summary_output = gr.Markdown(
        "Upload a dataset to view its summary.",
        elem_classes="markdown-text",
    )

    # --------------------------------------
    # AI Data Quality Analysis
    # --------------------------------------

    gr.Markdown("### AI Data Quality Analysis")

    ai_analysis_output = gr.Markdown(
        "AI analysis will appear here after dataset processing.",
        elem_classes="markdown-text",
    )

    # --------------------------------------
    # Data Preview
    # --------------------------------------

    gr.Markdown("### Data Preview")

    gr.Markdown(
        "The first 20 rows of your dataset are displayed below."
    )

    preview_output = gr.Dataframe(
        headers=None,
        interactive=False,
        wrap=True,
        elem_id="preview-table",
    )

    # --------------------------------------
    # Events
    # --------------------------------------

    outputs = [
        status_output,
        rows_output,
        columns_output,
        missing_output,
        duplicate_output,
        summary_output,
        ai_analysis_output,
        preview_output,
    ]

    # เลือกไฟล์ใหม่ -> ล้างผลลัพธ์เก่า ยังไม่ประมวลผลจนกว่าจะกดปุ่ม
    def reset_on_upload():
        return empty_outputs('File ready. Click "Analyze Dataset" to process.')

    file_input.upload(
        fn=reset_on_upload,
        inputs=None,
        outputs=outputs,
    )

    # ลบไฟล์ -> ล้างผลลัพธ์กลับเป็นค่าเริ่มต้น
    file_input.clear(
        fn=lambda: empty_outputs("Waiting for a dataset"),
        inputs=None,
        outputs=outputs,
    )

    # Process only when clicking the button (upload alone ไม่ประมวลผล)
    analyze_button.click(
        fn=process_file,
        inputs=file_input,
        outputs=outputs,
        show_progress="full",
    )

    # --------------------------------------
    # Footer
    # --------------------------------------

    gr.HTML(
        """
        <div id="app-footer">
            DataDoctor · Built with Python, Pandas & Gradio
        </div>
        """
    )


# ==========================================
# Launch Application
# ==========================================

if __name__ == "__main__":

    demo.launch(
        share=False,
        inbrowser=True,
    )