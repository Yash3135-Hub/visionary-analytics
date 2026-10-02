# 📊 Visionary Analytics - AI & ML Powered Business Intelligence Dashboard

**Visionary Analytics** is an advanced, end-to-end data analytics and predictive intelligence platform developed using Python and Streamlit. The application integrates modern UI controls, automated machine learning (Linear Regression forecasting), statistical chart rendering, and Large Language Model (LLM) capabilities via the **Google Gemini API** to convert raw business sales data into actionable strategic decisions.

---

## 📑 Table of Contents
- [Project Overview](#-project-overview)
- [System Architecture & Core Modules](#-system-architecture--core-modules)
- [Key Features](#-key-features)
- [Tech Stack & Dependencies](#-tech-stack--dependencies)
- [Folder & File Structure](#-folder--file-structure)
- [Step-by-Step Local Setup & Execution Guide (CMD)](#-step-by-step-local-setup--execution-guide-cmd)
- [Streamlit Cloud Deployment Setup](#-streamlit-cloud-deployment-setup)

---

## 🌐 Project Overview

Modern businesses often struggle to extract actionable insights from raw transactional datasets without technical data analyst intervention. **Visionary Analytics** solves this challenge by providing an interactive, self-service dashboard that handles:
1. **Data Intake & Preprocessing:** Automatic file parsing, metadata extraction, and data cleansers.
2. **Dynamic Visual Analytics:** Real-time visual filtering across multiple dimensions and categories.
3. **Generative AI Insights:** Automated narrative synthesis, trend discovery, and anomaly detection through **Google Gemini**.
4. **Predictive Sales Modeling:** Scikit-Learn regression models for forecasting upcoming sales trajectories.
5. **Report Automation:** One-click PDF report compilation and secure OTP-based password verification via SMTP.

---

## 🏗 System Architecture & Core Modules

The system is structured into four primary functional layers:

1. **Authentication & Access Control Management:**
   - Role-Based Access Control (RBAC) allowing **User** and **Admin** login capabilities.
   - External verification system utilizing SMTP for sending 6-digit verification OTPs for account recovery.

2. **Data Processing & Interactive Analytics Engine:**
   - Support for CSV and XLSX file formats.
   - Interactive UI components (Date pickers, dropdowns, ranges) that slice data dynamically.
   - Chart configuration engine supporting Bar charts, Line graphs, Histograms, Box plots, Scatter graphs, and Pie charts using **Plotly**.

3. **Machine Learning & AI Synthesis Engine:**
   - **Sales Forecasting:** Configurable Machine Learning pipeline using independent features to train models and output regression fit lines.
   - **Gemini AI Integration:** Automated prompt construction that sends dataset metrics to the Gemini LLM for structured executive summaries and strategic action items.

4. **Automated Export & Document Assembly:**
   - Compilation of analytics summaries, statistical tables, and embedded charts into exportable PDF documents.

---

## ✨ Key Features

- 🔑 **Multi-Role Login & Security:** Admin/User role toggle with instant credential validation.
- 📧 **Automated OTP Reset:** Password recovery mechanism integrated with Gmail SMTP (`smtplib`).
- 📁 **Instant Data Upload:** Drag-and-drop CSV/Excel dataset processing with live structure preview.
- 📈 **Interactive Plotly Visuals:** High-resolution charts with cross-filtering and metric aggregation.
- 🧠 **Gemini AI Executive Insights:** Automatic extraction of market anomalies, revenue drivers, and actionable recommendations.
- 🎯 **Predictive ML Sales Models:** Train regression models on uploaded historical sales records to view future targets.
- 📄 **PDF Report Generation:** Auto-format dashboard metrics into a clean PDF summary document.

---

## 🛠 Tech Stack & Dependencies

- **Programming Language:** Python 3.9+
- **Frontend / Application Framework:** Streamlit
- **Data Manipulation:** Pandas, NumPy
- **Data Visualization:** Plotly, Matplotlib, Seaborn
- **Machine Learning:** Scikit-Learn
- **Generative AI:** Google Gemini API (`google-genai`)
- **Document Processing:** PyPDF2, ReportLab / FPDF
- **Security & Mail Services:** `python-dotenv`, `smtplib`

---

## 📂 Folder & File Structure

```text
C:\Users\yashm\Python Project\
│
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Central environment & app configurations
├── auth.py                     # Authentication logic & OTP functions
├── ai_engine.py                # Gemini API integration & prompt builder
├── ml_model.py                 # Sales prediction model setup
├── pdf_generator.py            # PDF document compilation functions
├── requirements.txt            # Python library dependencies
├── .gitignore                  # Git exclude rule list (venv, .env)
└── README.md                   # Project documentation

💻 Step-by-Step Local Setup & Execution Guide (CMD)
Follow these exact steps to set up and execute the project locally on Windows using Command Prompt (cmd):

Step 1: Open Command Prompt
Press Windows Key + R to open the Run dialog box.

Type cmd and press Enter.

Step 2: Navigate to Project Directory
Run the following command to navigate into your project folder:

DOS
cd "C:\Users\yashm\Python Project" (your folder path).

Step 3: Create a Virtual Environment (Recommended)
Create an isolated Python virtual environment named venv:

DOS
python -m venv venv
Activate the virtual environment:

DOS
venv\Scripts\activate
(You will see (venv) prepended to your command prompt path).

Step 4: Install Required Dependencies
Install all required libraries listed in the requirements.txt file:

DOS
pip install -r requirements.txt

run : streamlit run app.py
