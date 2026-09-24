# 🩺 Data Doctor AI Data Quality Assistant

Data Doctor is an AI-powered data quality assistant that helps users inspect, understand, and identify potential problems in datasets.

The application allows users to upload CSV or Excel files, analyze dataset quality, and receive AI-generated explanations and recommendations in an easy-to-understand format.

## ✨ Features

* 📂 Upload CSV and Excel files
* 📊 Inspect dataset dimensions (rows and columns)
* 🔍 Detect missing values
* ♻️ Identify duplicate records
* 📋 Preview dataset contents
* 🧪 Generate a dataset analysis report
* 🤖 Use an LLM to explain data quality issues
* 💡 Receive practical data-cleaning recommendations
* 🌐 Interactive web interface powered by Gradio

## 🏗️ Project Structure

```text
DataDoctor-LLMProject/
│
├── ai/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── client.py
│   └── test_llm.py
│
├── ingestion/
│   ├── __init__.py
│   └── loader.py
│
├── ui/
│   └── app.py
│
├── .gitignore
├── .gitattributes
├── .python-version
├── README.md
├── pyproject.toml
└── uv.lock
```

## 🔄 Application Workflow

```text
Upload CSV / Excel File
          ↓
Load Dataset
          ↓
Analyze Dataset
          ↓
Generate Data Quality Report
          ↓
Send Report to LLM
          ↓
Generate AI Explanation
          ↓
Display Results in Gradio UI
```

## 🛠️ Technologies

* **Python** — Main programming language
* **Pandas** — Dataset loading and analysis
* **Gradio** — Interactive web interface
* **Hugging Face Inference API** — LLM access
* **Qwen/Qwen3-8B** — Language model
* **uv** — Python project and dependency management
* **Git & GitHub** — Version control

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/IttikornMafaka/DataDoctor-LLMProject.git
cd DataDoctor-LLMProject
```

### 2. Install Dependencies

This project uses `uv` for Python dependency management.

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
HF_TOKEN=your_huggingface_token
```

Replace `your_huggingface_token` with your Hugging Face API token.

**Important:** Never upload your `.env` file or expose your API token publicly.

### 4. Run the Application

```bash
uv run python ui/app.py
```

The Gradio application will start locally. Open the URL shown in the terminal.

## 🧠 AI Analysis

Data Doctor uses a language model to analyze the dataset report and provide:

1. An overview of dataset quality
2. Important data quality problems
3. Explanations of why problems matter
4. Suggested data-cleaning actions
5. Careful discussion of potential outliers

The AI should not be treated as a replacement for manual data validation. Its recommendations should be reviewed before making changes to the original dataset.

## 📌 Current Scope

The current version focuses on:

* Dataset inspection
* Basic data quality analysis
* AI-generated explanations
* CSV and Excel file ingestion
* A simple Gradio-based user interface

More advanced data-cleaning and automated correction features may be added in future versions.

## 🚀 Future Improvements

* [ ] Automatic data-cleaning suggestions
* [ ] Interactive missing-value handling
* [ ] Outlier visualization
* [ ] Data type validation
* [ ] Data quality scoring
* [ ] Downloadable analysis reports
* [ ] Support for additional file formats
* [ ] Improved AI recommendations
* [ ] Production deployment

## 👨‍💻 Author

**Ittikorn Supsomboon (William)**

Artificial Intelligence Engineering Student

GitHub: [@IttikornMafaka](https://github.com/IttikornMafaka)

---

⭐ This project is developed as an AI and data engineering learning project.
