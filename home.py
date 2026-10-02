import streamlit as st
from utils import render_kpi_cards, render_feature_cards

def render_home_page():
    st.title("📊 Visionary Analytics")
    st.markdown('<div class="tagline">Analyze • Visualize • Predict</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#8FA7B6; max-width:700px; line-height:1.6;">'
        'Upload any sales Excel file and instantly get KPI metrics, interactive charts, '
        'AI-generated business insights, and machine learning based sales predictions '
        '— no formulas required.</p>',
        unsafe_allow_html=True
    )

    if st.button("🚀 Get Started — Go to Dashboard"):
        st.session_state.jump_to_dashboard = True
        st.rerun()

    st.write("")
    render_kpi_cards([
        ("5+", "Chart Types"),
        ("AI", "Powered Insights"),
        ("ML", "Sales Prediction"),
        ("PDF", "Report Export"),
    ])

    st.subheader("✨ What You Can Do")
    render_feature_cards([
        ("bi-file-earmark-spreadsheet", "Excel Upload", "Upload any structured sales dataset in seconds."),
        ("bi-speedometer2", "KPI Metrics", "Instant totals, averages, and highest values."),
        ("bi-sliders", "Interactive Filters", "Slice your data by any category column."),
        ("bi-bar-chart-line", "Plotly Charts", "Bar, Line, Pie, Scatter, and Area charts."),
        ("bi-grid-3x3-gap", "Correlation Heatmap", "Spot relationships across numeric columns."),
        ("bi-robot", "AI & ML Prediction", "Gemini insights plus Linear Regression forecasts."),
    ])