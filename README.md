# 🚀 InsightEngine AI | Sales & Business Analytics Hub

**"Turning raw data into a strategic roadmap with Agentic AI."**

InsightEngine AI is a professional, multi-page analytics suite built to help retail businesses understand their customers. It moves beyond simple charts by integrating **Gemini AI** to act as a virtual consultant and **Scikit-Learn** to project future sales.

---

## ✨ Features that set this apart

### 🧠 1. AI Business Strategist (Executive Dashboard)
Don't just look at numbers. The integrated **Gemini 1.5/2.0 Flash Agent** analyzes your specific `basket_details.csv` and narrates:
* **CEO Summaries**: Two-sentence executive overviews.
* **Growth Hacks**: Actionable strategies like cross-selling or loyalty shifts.
* **Risk Auditing**: Identifying potential inventory or retention issues.

### 🔍 2. Dynamic Deep Dive
Designed for the data auditor. Filter through thousands of rows of customer and product data dynamically and export the cleaned results as a fresh CSV for external reporting.

### 🔮 3. Predictive Forecasting
Utilizes **Linear Regression** to map historical transaction velocity. It provides a 30-day look-ahead trend, allowing business owners to anticipate demand and plan inventory effectively.

### 🎨 4. Enterprise-Grade UI
Custom-built with a **Dark Mode SaaS aesthetic**:
* **Inter Typography**: Clean, modern professional font.
* **Interactive KPIs**: Glassmorphism tiles with hover-state animations.
* **Responsive Layout**: Optimized for both widescreen monitors and tablets.

---

## 🛠️ Tech Stack
* **Language**: Python 3.10+
* **Framework**: Streamlit (Multi-page Architecture)
* **AI/LLM**: Google Gemini API (Agentic Workflows)
* **ML**: Scikit-Learn (Time-Series Regression)
* **Data**: Pandas & NumPy
* **Visuals**: Plotly (Interactive Charts)

---

## 📂 Project Structure
```text
├── app.py                  # Main Entry Point & File Upload Agent
├── utils.py                # Backend Logic (Cleaning, AI, Forecasting)
├── styles.css              # Custom SaaS UI Styling
├── requirements.txt        # Dependency Manifest
├── pages/                  # Specialized Dashboard Modules
│   ├── 1_Executive_Dashboard.py
│   ├── 2_Deep_Dive.py
│   └── 3_Predictions.py
└── basket_details.csv      # Sample Training Dataset
