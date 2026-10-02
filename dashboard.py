import streamlit as st
import pandas as pd
from utils import render_kpi_cards
from charts import (
    render_interactive_chart, render_correlation_heatmap,
    render_correlation_table, render_summary_statistics,
    render_distribution_analysis, render_top_n_chart
)
from ai_assistant import analyze_sales_data
from pdf_report import generate_pdf_report
from database import record_upload

def render_dashboard_page():
    st.title("📊 Sales Dashboard")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="dashboard_file_uploader")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            st.success("File Uploaded Successfully!")

            # Log this upload once per unique file selection (avoid duplicate logs on every rerun)
            upload_log_key = f"logged_{uploaded_file.file_id}"
            if not st.session_state.get(upload_log_key):
                record_upload(st.session_state.username, uploaded_file.name, len(df))
                st.session_state[upload_log_key] = True

            st.subheader("🤖 AI Sales Insights")
            if st.button("📊 Analyze with AI"):
                analysis = analyze_sales_data(df)
                if analysis:
                    st.session_state["ai_analysis"] = analysis
                    st.subheader("🤖 AI Analysis")
                    st.write(analysis)

            st.subheader("📋 Dataset Preview")
            st.dataframe(df)

            csv = df.to_csv(index=False)
            st.download_button("⬇ Download CSV", data=csv, file_name="sales_data.csv", mime="text/csv")

            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            category_cols = df.select_dtypes(include=['object', 'str']).columns.tolist()

            st.sidebar.subheader("🔍 Filters")
            if len(category_cols) > 0:
                selected_category = st.sidebar.selectbox("Select Category Column", category_cols)
                selected_values = st.sidebar.multiselect("Select " + selected_category, df[selected_category].unique())
                if selected_values:
                    df = df[df[selected_category].isin(selected_values)]

            st.subheader("📌 KPI Metrics")
            total_sales, average_sales, max_sales, total_records = 0, 0, 0, len(df)
            if len(numeric_cols) > 0:
                metric_col = numeric_cols[0]
                total_sales = df[metric_col].sum()
                average_sales = df[metric_col].mean()
                max_sales = df[metric_col].max()

                render_kpi_cards([
                    ("{:,.0f}".format(total_sales), "Total Sales"),
                    ("{:,.2f}".format(average_sales), "Average Sales"),
                    ("{:,.0f}".format(max_sales), "Highest Value"),
                    ("{:,}".format(total_records), "Total Records"),
                ])

            st.subheader("📈 Interactive Charts")
            x_axis, y_axis = None, None
            if len(numeric_cols) > 0 and len(category_cols) > 0:
                x_axis = st.selectbox("Select X-axis", category_cols)
                y_axis = st.selectbox("Select Y-axis", numeric_cols)
                chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Area Chart"])
                render_interactive_chart(df, x_axis, y_axis, chart_type)

                st.subheader("🏆 Top 5 Ranking")
                render_top_n_chart(df, x_axis, y_axis, n=5)

            st.subheader("🔥 Correlation Heatmap")
            heatmap_bytes = render_correlation_heatmap(df, numeric_cols)
            if heatmap_bytes:
                st.session_state["heatmap_img"] = heatmap_bytes
                render_correlation_table(df, numeric_cols)

            st.subheader("📐 Summary Statistics")
            render_summary_statistics(df, numeric_cols)

            st.subheader("📊 Distribution Analysis")
            render_distribution_analysis(df, numeric_cols)

            st.subheader("📌 Automatic Insights")
            top_category, top_value = None, None
            if x_axis and y_axis:
                top_category = df.groupby(x_axis)[y_axis].sum().idxmax()
                top_value = df.groupby(x_axis)[y_axis].sum().max()
                st.success(f"Top Performing {x_axis}: {top_category} ({top_value})")

            st.subheader("📄 PDF Report")
            if st.button("⬇ Generate PDF Report"):
                with st.spinner("Building PDF report..."):
                    pdf_bytes = generate_pdf_report(
                        filename=uploaded_file.name,
                        total_sales=total_sales,
                        average_sales=average_sales,
                        max_sales=max_sales,
                        total_records=total_records,
                        top_category_col=x_axis,
                        top_category=top_category,
                        top_value=top_value,
                        heatmap_img=st.session_state.get("heatmap_img"),
                        ai_analysis=st.session_state.get("ai_analysis"),
                    )
                st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name="sales_report.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Please upload an Excel file.")