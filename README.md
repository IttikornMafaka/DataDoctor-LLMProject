🩺 Data Doctor — AI Data Quality & Cleaning Assistant

Data Doctor is an AI-powered data quality and data cleaning application designed to help users understand, validate, and improve the quality of tabular datasets.

Users can upload CSV or Excel files, inspect dataset statistics, detect data-quality issues, receive LLM-powered analysis and recommendations, apply controlled cleaning operations, correct data types, and download the cleaned dataset.

The project combines Data Engineering, Data Quality, Rule-Based Validation, LLM Engineering, and an Interactive Gradio UI into one practical application.

✨ Features

📂 1. Data Ingestion

Data Doctor supports common tabular data formats:

CSV

Excel .xlsx

Excel .xls

Automatic file-type detection

Dataset loading

Dataset preview

📊 2. Dataset Analysis

Data Doctor analyzes uploaded datasets and generates a structured dataset-quality report.

The analysis includes:

Number of rows

Number of columns

Column names

Data types

Missing values

Missing-value percentage

Duplicate rows

Numerical statistics

Unique values

Value distributions

Potential outliers

Column-level information

🏥 3. Dataset Health Analysis

Data Doctor looks for common data-quality problems such as:

Missing values

Duplicate records

Incorrect data types

Invalid values

Inconsistent values

Suspicious numerical values

Potential outliers

The system does not automatically assume that every unusual value is an error. Potential outliers are treated as observations that should be reviewed.

🔎 4. Data Validation

Data Doctor includes rule-based validation for identifying values that may not make sense for a specific type of column.

Examples include:

Age

Age should be:
- An integer
- Greater than or equal to 0
- Less than or equal to 120

Percentage

Percentage should be between 0 and 100.

Quality Score

Quality score should be an integer.

The validation system separates:

Type detection

Invalid-value detection

Value sanity rules

This helps avoid treating every unusual value as a data error.

🔄 5. Data Type Detection

Data Doctor can detect columns that may have an incorrect data type.

For example:

"20"
"35"
"42"
"18"

may currently be stored as:

object / string

but the system can detect that the values are likely numeric.

Supported type suggestions include:

text → numeric
text → integer
text → boolean
text → datetime
values → string

The system calculates a confidence value based on the proportion of values that can be successfully interpreted as the target type.

Example:

Column: age
Current Type: object
Suggested Type: integer
Confidence: 100%

🛠️ 6. Data Type Correction

After detecting potential type problems, Data Doctor can apply controlled type conversions.

Supported conversions include:

Numeric

pd.to_numeric(..., errors="coerce")

Integer

Values are converted into Pandas nullable integer format:

Int64

This allows missing values to remain representable.

Boolean

Supported values include:

true
false
yes
no

Datetime

Datetime values are converted using Pandas datetime parsing.

Mixed datetime formats can be handled using:

format="mixed"

String

Columns can be explicitly converted into Pandas string type.

🧹 7. Missing Value Cleaning

Data Doctor provides several strategies for handling missing values.

Strategy

Description

mean

Fill missing numerical values using the mean

median

Fill missing numerical values using the median

mode

Fill missing values using the most frequent value

drop_rows

Remove rows containing missing values

The cleaning system validates the requested strategy before applying it.

Unsupported strategies are rejected instead of being executed automatically.

🧹 8. Duplicate Removal

Data Doctor can detect duplicate records and remove duplicate rows during the cleaning process.

Example:

Before:
100 rows
10 duplicate rows

After:
90 rows

The operation is performed on the cleaned copy of the dataset.

🤖 9. LLM-Powered Data Analysis

Data Doctor integrates an LLM to provide natural-language explanations of dataset-quality problems.

The LLM receives a structured dataset analysis report rather than blindly receiving the entire raw dataset.

The AI can provide:

Dataset quality overview

Important detected problems

Explanations of why problems matter

Suggested cleaning actions

Discussion of potential outliers

Practical recommendations

The LLM is instructed to use only information available in the provided report. If information is not available, it should state that the information is not present rather than inventing an answer.

🧠 10. LLM Data Quality Advisor

The LLM can explain detected problems in a way that is easier for non-technical users to understand.

Example:

Problem:
The age column contains missing values.

Explanation:
Some records do not contain an age value. This may affect
analysis that depends on age.

Recommendation:
Consider using the median value if the distribution is skewed,
or review the records before removing them.

The LLM provides recommendations, while cleaning operations remain controlled by the application's cleaning pipeline.

🧹 11. LLM-Assisted Cleaning Advisor

The project includes an LLM-assisted cleaning advisor that can suggest supported cleaning strategies.

Example:

{
  "age": "median",
  "income": "mean",
  "category": "mode"
}

Only allowed strategies are accepted:

mean
median
mode
drop_rows

This prevents the LLM from directly executing arbitrary operations on the dataset.

🔐 12. Controlled Cleaning Pipeline

The cleaning system separates recommendation from execution.

Dataset
   ↓
Analysis
   ↓
Detect Problems
   ↓
LLM Recommendation
   ↓
Validate Cleaning Plan
   ↓
Cleaning Pipeline
   ↓
Cleaned Dataset

The LLM does not directly modify the DataFrame.

Instead:

LLM
 ↓
Recommendation
 ↓
Validation
 ↓
Cleaning Pipeline
 ↓
Pandas

📋 13. Cleaning Logs

The cleaning system can record operations performed on the dataset.

For type correction, logs can contain:

Column
Old Type
New Type

Example:

age
object → Int64

price
object → float64

created_at
object → datetime64[ns]

This helps users understand what changed during the cleaning process.

🧪 14. Before / After Dataset Processing

Data Doctor processes cleaning operations using a copy of the original DataFrame.

Original Dataset
       │
       ├───────────────┐
       │               │
       ↓               ↓
Keep Original       Clean Copy
                       │
                       ↓
                 Cleaning Pipeline
                       │
                       ↓
                Cleaned Dataset

The original uploaded dataset is not directly modified during cleaning.

🌐 15. Gradio Web Interface

The application uses Gradio to provide an interactive web interface.

The interface allows users to:

Upload a dataset

Preview the dataset

Analyze data quality

View detected issues

Request LLM analysis

Review cleaning recommendations

Apply supported cleaning operations

Review the cleaned dataset

Download the cleaned file

🔄 Application Workflow

Upload CSV / Excel
        ↓
Load Dataset
        ↓
Dataset Preview
        ↓
Analyze Dataset
        ↓
Generate Data Quality Report
        ↓
Detect Data Issues
        ↓
LLM Analysis & Recommendations
        ↓
Create Cleaning Plan
        ↓
Apply Cleaning Operations
        ↓
Review Cleaning Results
        ↓
Download Cleaned Dataset

🏗️ Project Architecture

DataDoctor-LLMProject/
│
├── ai/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── client.py
│   └── test_llm.py
│
├── cleaning/
│   ├── __init__.py
│   ├── cleaner.py
│   ├── clean_advisor.py
│   ├── pipeline.py
│   ├── type_correcter.py
│   └── ...
│
├── ingestion/
│   ├── __init__.py
│   └── loader.py
│
├── ui/
│   └── app.py
│
├── data/
│   └── ...
│
├── .gitignore
├── .gitattributes
├── .python-version
├── README.md
├── pyproject.toml
└── uv.lock

🧩 Main Components

ingestion/

Responsible for loading user datasets.

File
 ↓
Loader
 ↓
Pandas DataFrame

ai/

Responsible for LLM interaction and AI-powered dataset analysis.

Main responsibilities:

LLM client

Dataset analysis prompt

LLM response generation

AI analysis

cleaning/

Responsible for data cleaning and preprocessing.

Main responsibilities:

Missing-value handling

Duplicate removal

Cleaning strategy validation

Cleaning pipeline

Data type detection

Data type correction

ui/

Contains the Gradio application.

Main responsibilities:

User interface

File upload

Dataset preview

Analysis results

Cleaning controls

LLM interaction

Download functionality

🛠️ Technology Stack

Technology

Purpose

Python 3.11

Main programming language

Pandas

Data processing and analysis

Gradio

Web interface

Hugging Face Inference API

LLM inference

Qwen/Qwen3-8B

Language model

LangChain

LLM application components

OpenPyXL

Excel processing

uv

Dependency management

Git

Version control

GitHub

Source code hosting

⚙️ Installation

1. Clone the repository

git clone https://github.com/IttikornMafaka/DataDoctor-LLMProject.git
cd DataDoctor-LLMProject

2. Install dependencies

This project uses uv.

uv sync

3. Configure Hugging Face

Create a .env file in the project root:

HF_TOKEN=your_huggingface_token

Replace your_huggingface_token with your Hugging Face API token.

Never commit .env or expose your API token publicly.

▶️ Run the Application

uv run python ui/app.py

Gradio will start the local web application.

Open the local URL shown in the terminal.

📦 Python Environment

The project targets:

Python >= 3.11

The project uses uv for dependency and environment management.

Recommended workflow:

uv sync
uv run python ui/app.py

🧪 Example Dataset

Data Doctor can be tested with datasets containing common data-quality problems.

Example:

name,age,price,category,date
Alice,21,100.5,A,2026-01-10
Bob,,200.0,A,2026-01-11
Charlie,25,,B,2026-01-12
David,abc,300.0,B,invalid-date
Alice,21,100.5,A,2026-01-10

This dataset contains examples of:

Missing values

Duplicate records

Invalid numeric values

Potential type problems

Invalid datetime values

🔐 Data Safety Principles

Data Doctor follows several design principles.

1. Do not blindly modify source data

Cleaning operations are performed on a copy of the DataFrame.

2. Controlled cleaning strategies

Only supported cleaning strategies are accepted.

3. LLM recommendations are validated

The LLM does not directly execute arbitrary Python or Pandas operations.

4. Outliers are observations

An outlier is not automatically treated as an error.

5. Do not invent information

The LLM should only use information provided in the analysis report.

6. Review before important data modification

AI-generated recommendations should be reviewed before applying them to important datasets.

📈 Current Project Status

Implemented

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

🚀 Future Improvements

Better data quality scoring

Interactive before/after comparison

More advanced categorical standardization

More invalid-value rules

More robust datetime detection

Improved outlier visualization

Cleaning history

Detailed audit logs

Downloadable quality reports

More file formats

Automated testing

Unit test coverage

Production deployment

Performance optimization for large datasets

🎯 Project Goal

The goal of Data Doctor is to build a practical AI-powered data-quality application rather than a simple notebook experiment.

The project combines:

Data Engineering
      +
Data Quality
      +
Rule-Based Validation
      +
LLM Engineering
      +
Data Cleaning
      +
Interactive UI

into a single practical application.

The final goal is to provide users with an assistant that can help them:

Understand their data
        ↓
Find potential problems
        ↓
Understand why they matter
        ↓
Receive cleaning recommendations
        ↓
Apply controlled cleaning
        ↓
Review the results
        ↓
Export the cleaned dataset

👨‍💻 Author

Ittikorn Supsomboon (William)

Artificial Intelligence Engineering Student

GitHub:

https://github.com/IttikornMafaka
