# 📊 Financial Analysis Automation System (AI-Assisted)

## 🧩 Overview
This project automates **financial data analysis and report generation** for Vietnamese listed companies.  
It combines **Python, Pandas, Matplotlib, Streamlit, and Gemini AI** to produce full PDF reports comparing company metrics with industry benchmarks.

The system allows users to:
- Select a company from a dropdown menu (Streamlit UI)
- Automatically generate charts and financial tables
- Compare company KPIs (ROA, ROE, Liquidity, Efficiency) vs. industry averages
- Create AI-generated **financial narratives** for each company
- Export everything into a **professional multi-page PDF**

---

## ⚙️ Tech Stack
- **Python 3.x**
- **Libraries:** Pandas, Matplotlib, FPDF, Streamlit, Google Generative AI (Gemini)
- **Data Sources:** Local CSV & Excel files (Balance Sheet, Income Statement, Industry Data)
- **Output:** PDF report with visual charts and AI-written financial story

---

## 🧠 Key Features
✅ Data loading and cleaning from multiple CSV files  
✅ Financial metric comparison (company vs. industry)  
✅ Visualization of ROA/ROE, liquidity, and efficiency indicators  
✅ Integration with **Gemini AI** for automatic financial commentary  
✅ Streamlit web interface for interactive report generation  
✅ Export full analysis as **PDF report** with visuals and AI-generated content  

---

## 🏗️ Project Structure
Auto_Financial_Report/
│
├── data/ # 📊 Raw financial datasets
│ ├── BCTCKH.csv
│ ├── BCDKT.csv
│ ├── KQKD.csv
│ ├── LCTT.csv
│ ├── Average_by_Code.csv
│ ├── Average_by_Sector.csv
│ ├── price.csv
│ ├── TBN.csv
│ └── Cleaned_Vietnam_Price.xlsx
│
├── fonts/ # 🔤 Fonts used for PDF generation
│ └── DejaVuSans.ttf
│
├── G1.py # 🧠 Main Python script (Streamlit + PDF generator)
├── README.md # 📘 Project documentation
├── requirements.txt # ⚙️ Python dependencies
└── .gitignore # 🚫 Ignored files
