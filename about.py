import streamlit as st
from utils import render_feature_cards

def render_about_page():
    st.title("📖 About This Project")
    st.markdown("""
    **Visionary Analytics** is an AI-powered web application that helps
    businesses analyze sales data, visualize trends, and forecast future sales —
    without writing a single formula manually.
    """)

    st.subheader("✨ Key Features")
    render_feature_cards([
        ("bi-shield-lock", "Secure Authentication", "Login & registration backed by SQLite with SHA-256 hashed passwords."),
        ("bi-bar-chart-line", "Interactive Analytics", "Dynamic KPIs, filters, and Plotly charts (Bar, Line, Pie, Scatter, Area)."),
        ("bi-grid-3x3-gap", "Correlation Heatmap", "Instant correlation analysis across all numeric columns."),
        ("bi-robot", "AI Sales Insights", "Google Gemini AI analyzes your dataset and generates business recommendations."),
        ("bi-graph-up-arrow", "ML Sales Prediction", "Linear Regression model forecasts future values from any two numeric columns."),
        ("bi-file-earmark-pdf", "PDF Report Export", "Download a complete, shareable PDF summary of KPIs, heatmap, and AI insights."),
    ])

    st.subheader("🛠 Technology Stack")
    st.markdown("""
    | Layer | Technology |
    |---|---|
    | Frontend / UI | Streamlit, HTML/CSS |
    | Backend | Python |
    | Database | SQLite |
    | Data Processing | Pandas |
    | Visualization | Plotly, Matplotlib |
    | Machine Learning | Scikit-learn (Linear Regression) |
    | AI Integration | Google Gemini API (`gemini-2.5-flash`) |
    | Report Export | FPDF2 |
    """)

    st.subheader("🎓 Academic Information")
    st.markdown("""
    This project was developed as part of **System Development Project – I (P13A6SDP1)**
    for **M.C.A. Semester-III**, under **Acharya Motibhai Patel Institute of Computer
    Studies (AMPICS), Ganpat University**.
    """)