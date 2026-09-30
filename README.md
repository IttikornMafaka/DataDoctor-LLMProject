<div align="center">

🩺 Data Doctor

AI-Powered Data Quality & Cleaning Assistant

<p>
  <strong>Upload → Analyze → Understand → Clean → Review</strong>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Gradio-UI-FF7C00?style=for-the-badge&logo=gradio&logoColor=white" alt="Gradio">
  <img src="https://img.shields.io/badge/Hugging%20Face-LLM-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="Hugging Face">
</p>

<p>
  <a href="https://github.com/IttikornMafaka/DataDoctor-LLMProject">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Project-AI%20%2F%20LLM%20Engineering-blue?style=flat-square" alt="Project Type">
</p>

</div>

📌 Overview

Data Doctor is an AI-powered application for data quality analysis, validation, and controlled data cleaning.

Instead of simply cleaning a dataset automatically, Data Doctor follows a safer workflow:

Detect the problem → Explain the problem → Recommend an action → Validate the action → Apply the cleaning

Users can upload CSV or Excel files, inspect the dataset, detect common data-quality issues, receive LLM-powered explanations, apply supported cleaning operations, correct data types, and review the cleaned result.

The project is designed as a practical AI / LLM Engineering portfolio project, combining data processing, rule-based validation, LLM integration, and an interactive web UI.

✨ What Can Data Doctor Do?

Feature

Description

📂 Data Ingestion

Load CSV, XLSX, and XLS files

🔍 Dataset Analysis

Analyze shape, types, missing values, duplicates, statistics, and distributions

🏥 Data Health Check

Identify common data-quality problems

🧠 LLM Analysis

Explain dataset problems using an LLM

🛡️ Rule-Based Validation

Validate values using explicit data-quality rules

🔄 Type Detection

Detect columns that may have incorrect data types

🛠️ Type Correction

Convert numeric, integer, boolean, datetime, and string columns

🧹 Missing Value Cleaning

Mean, median, mode, or drop rows

♻️ Duplicate Removal

Detect and remove duplicate records

🤖 LLM Cleaning Advisor

Suggest supported cleaning strategies

🔐 Controlled Pipeline

Validate AI recommendations before executing them

📋 Cleaning Logs

Record important changes made during processing

🌐 Gradio UI

Interactive browser-based interface

🧠 Core Concept

Data Doctor separates AI recommendation from data modification.

                         DATA DOCTOR
                              │
                              ▼
                    ┌──────────────────┐
                    │   Upload Dataset │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Dataset Analysis │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Detect Problems  │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │ Rule-Based      │       │ LLM Analysis    │
       │ Validation      │       │ & Recommendation│
       └────────┬────────┘       └────────┬────────┘
                │                         │
                └────────────┬────────────┘
                             ▼
                    ┌──────────────────┐
                    │ Validate Plan    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Cleaning Pipeline│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Review Result    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Download Dataset │
                    └──────────────────┘

Why this design?

The LLM does not directly modify the dataset.

Instead:

LLM
 │
 │ recommendation
 ▼
Validation
 │
 │ approved strategy
 ▼
Cleaning Pipeline
 │
 ▼
Pandas DataFrame

This makes the system more predictable and easier to audit.

🔍 Data Quality Analysis

Data Doctor generates a structured report before asking the LLM for an explanation.

The report can contain:

Dataset-level information

Number of rows

Number of columns

Duplicate count

Missing-value count

Missing-value percentage

Column-level information

Column name

Data type

Missing values

Unique values

Numerical statistics

Value distribution

Potential issues

Missing values

Duplicate rows

Incorrect data types

Invalid values

Inconsistent values

Suspicious numerical values

Potential outliers

⚠️ A potential outlier is treated as an observation, not automatically as an error.

🛡️ Rule-Based Validation

Data Doctor uses explicit rules to detect values that may not be reasonable for certain types of columns.

Example: Age

Age
├── Must be an integer
├── Minimum: 0
└── Maximum: 120

Example: Percentage

Percentage
├── Minimum: 0
└── Maximum: 100

Example: Quality Score

Quality
└── Must be an integer

This creates a clear separation between:

Type Detection
      +
Invalid Value Detection
      +
Value Sanity Rules

🔄 Automatic Type Detection

Data Doctor can identify columns that appear to have an incorrect type.

For example:

age
----------------
"21"
"35"
"42"
"18"

The values may be stored as:

object

but Data Doctor can detect:

Suggested Type: integer
Confidence: 100%

Supported suggestions

text ──────────► numeric
text ──────────► integer
text ──────────► boolean
text ──────────► datetime
values ────────► string

Confidence is based on how many non-null values can be successfully interpreted as the suggested type.

🛠️ Type Correction

After reviewing a detected issue, Data Doctor can apply controlled type conversion.

Numeric

pd.to_numeric(..., errors="coerce")

Integer

Uses Pandas nullable integer:

Int64

This allows missing values to remain represented.

Boolean

Supports values such as:

true
false
yes
no

Datetime

Datetime values are converted using Pandas datetime parsing, including mixed-format values.

String

Columns can be explicitly converted to Pandas string type.

🧹 Missing Value Cleaning

Data Doctor currently supports four controlled strategies:

Strategy

Use

mean

Fill numerical missing values with the mean

median

Fill numerical missing values with the median

mode

Fill missing values with the most frequent value

drop_rows

Remove rows containing missing values

The cleaning advisor is restricted to these supported strategies.

Example recommendation:

{
  "age": "median",
  "income": "mean",
  "category": "mode"
}

The recommendation is validated before execution.

♻️ Duplicate Cleaning

Duplicate rows can be detected and removed through the cleaning pipeline.

Example:

Before
──────
100 rows
 10 duplicate rows

After
─────
 90 rows

The original DataFrame is kept unchanged while cleaning is performed on a copy.

🤖 LLM-Powered Analysis

Data Doctor integrates an LLM through the Hugging Face Inference API.

The project is designed to work with:

Qwen/Qwen3-8B

The LLM receives a structured analysis report and provides natural-language explanations.

The LLM can help answer:

What problems were detected?

Which issues should be reviewed?

Why might an issue matter?

What cleaning approach could be considered?

Which observations may require manual review?

Anti-hallucination principle

The LLM is instructed to:

Use only information contained in the report.
Do not invent missing information.
If the report does not contain the information,
say that it is not available.

🔐 Controlled AI Cleaning

One of the main design principles is:

AI recommends. The application validates and executes.

┌──────────────┐
│     LLM      │
└──────┬───────┘
       │
       │ JSON recommendation
       ▼
┌──────────────┐
│   Validator  │
└──────┬───────┘
       │
       │ approved strategy
       ▼
┌──────────────┐
│   Cleaner    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Pandas    │
└──────────────┘

This prevents the LLM from directly executing arbitrary Python or Pandas operations.

📋 Cleaning Logs

Important cleaning operations can be recorded for transparency.

Example:

Column      Old Type        New Type
────────────────────────────────────────
age         object          Int64
price       object          float64
created_at  object          datetime64[ns]

This provides a simple audit trail of type corrections.

🌐 User Interface

Data Doctor uses Gradio for the interactive web application.

The intended user flow is:

┌───────────────┐
│ Upload File   │
└───────┬───────┘
        ▼
┌───────────────┐
│ Preview Data  │
└───────┬───────┘
        ▼
┌───────────────┐
│ Analyze       │
└───────┬───────┘
        ▼
┌───────────────┐
│ Review Issues │
└───────┬───────┘
        ▼
┌───────────────┐
│ AI Advice     │
└───────┬───────┘
        ▼
┌───────────────┐
│ Clean Data    │
└───────┬───────┘
        ▼
┌───────────────┐
│ Review Result │
└───────┬───────┘
        ▼
┌───────────────┐
│ Export        │
└───────────────┘

🏗️ Project Structure

DataDoctor-LLMProject/
│
├── 📁 ai/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── client.py
│   └── test_llm.py
│
├── 📁 cleaning/
│   ├── __init__.py
│   ├── cleaner.py
│   ├── clean_advisor.py
│   ├── pipeline.py
│   ├── type_correcter.py
│   └── ...
│
├── 📁 ingestion/
│   ├── __init__.py
│   └── loader.py
│
├── 📁 ui/
│   └── app.py
│
├── 📁 data/
│   └── ...
│
├── 📄 .gitignore
├── 📄 .gitattributes
├── 📄 .python-version
├── 📄 README.md
├── 📄 pyproject.toml
└── 📄 uv.lock

🧩 Architecture

Layer

Responsibility

ingestion/

Load and prepare datasets

ai/

LLM communication and analysis

cleaning/

Validation, type correction, and cleaning

ui/

Gradio interface

data/

Test/sample datasets

🛠️ Tech Stack

<div align="center">

Technology

Role

🐍 Python 3.11

Application development

🐼 Pandas

Data processing

🎨 Gradio

Web UI

🤗 Hugging Face

LLM inference

🧠 Qwen/Qwen3-8B

Language model

🔗 LangChain

LLM application components

📊 OpenPyXL

Excel processing

⚡ uv

Python environment & dependencies

🔧 Git

Version control

🌐 GitHub

Repository hosting

</div>

⚙️ Installation

1. Clone the repository

git clone https://github.com/IttikornMafaka/DataDoctor-LLMProject.git
cd DataDoctor-LLMProject

2. Install dependencies

uv sync

3. Configure Hugging Face

Create a .env file in the project root:

HF_TOKEN=your_huggingface_token

🔒 Never commit .env or expose your API token publicly.

▶️ Run

uv run python ui/app.py

Then open the local Gradio URL shown in the terminal.

🧪 Example Dataset

A simple dataset for testing:

name,age,price,category,date
Alice,21,100.5,A,2026-01-10
Bob,,200.0,A,2026-01-11
Charlie,25,,B,2026-01-12
David,abc,300.0,B,invalid-date
Alice,21,100.5,A,2026-01-10

This dataset intentionally contains:

❌ Missing values

❌ Duplicate records

❌ Invalid numeric values

❌ Potential type problems

❌ Invalid datetime values

🔒 Data Safety Principles

01 — Preserve the original

Cleaning is performed on a copy of the DataFrame.

02 — Restrict AI actions

The LLM can only recommend supported cleaning strategies.

03 — Validate before execution

AI-generated cleaning plans are validated before being passed to the cleaning pipeline.

04 — Do not assume outliers are errors

Potential outliers are observations that may require review.

05 — Avoid hallucination

The LLM should only use information available in the supplied analysis report.

06 — Keep humans in the loop

Important data modifications should be reviewed before being used in real workflows.

📈 Project Status

✅ Implemented

CSV ingestion

Excel ingestion

Dataset preview

Dataset statistics

Missing-value detection

Duplicate detection

Numerical analysis

Distribution analysis

Potential outlier analysis

LLM dataset analysis

Missing-value cleaning

Duplicate removal

Cleaning pipeline

Cleaning strategy validation

Data type issue detection

Numeric type correction

Integer type correction

Boolean type correction

Datetime type correction

String type correction

Type correction logging

Gradio interface

Git/GitHub project management

🚧 Planned

Better dataset health scoring

Interactive before/after comparison

More advanced categorical standardization

More invalid-value rules

More robust datetime detection

Improved outlier visualization

Cleaning history

Detailed audit logs

Downloadable quality reports

More file formats

Automated tests

Unit test coverage

Production deployment

Performance optimization for large datasets

🎯 Why I Built This

Data cleaning is often one of the first steps in a real machine-learning or analytics workflow, but messy data can make downstream analysis unreliable.

I built Data Doctor to explore how LLMs can assist with data-quality workflows without giving the model unrestricted control over the data.

The project focuses on combining:

          Data Engineering
                 │
                 ▼
           Data Quality
                 │
                 ▼
        Rule-Based Validation
                 │
                 ▼
          LLM Engineering
                 │
                 ▼
           Data Cleaning
                 │
                 ▼
           Interactive UI

The goal is to build a practical application that demonstrates both software engineering and AI/LLM engineering skills.

🚀 Roadmap

Phase 1
───────
Dataset Ingestion
       ↓
Dataset Analysis
       ↓
Issue Detection

Phase 2
───────
Rule-Based Validation
       ↓
Type Detection
       ↓
Cleaning Pipeline

Phase 3
───────
LLM Analysis
       ↓
LLM Cleaning Advisor
       ↓
Controlled AI Workflow

Phase 4
───────
Before / After Comparison
       ↓
Cleaning History
       ↓
Audit Logs
       ↓
Production Deployment

👨‍💻 Author

<div align="center">

Ittikorn Supsomboon (William)

Artificial Intelligence Engineering Student

<a href="https://github.com/IttikornMafaka">
  <img src="https://img.shields.io/badge/GitHub-IttikornMafaka-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</a>

</div>

📄 License

This project is currently developed as a personal AI / LLM Engineering portfolio and learning project.

<div align="center">

🩺 Data Doctor

Make your data healthier before it reaches your model.

⭐ If you find the project interesting, feel free to explore the repository.

</div>
