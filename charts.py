import io
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from config import client, GEMINI_API_KEY

plt.style.use('ggplot')


def explain_chart_with_ai(chart_type, x_axis, y_axis, chart_data):
    """Generates a concise 3-bullet point AI explanation for a specific chart."""
    if not GEMINI_API_KEY or not client:
        return "⚠️ Gemini API key missing in .env file."
    
    try:
        summary_str = chart_data.to_string(index=False)
        prompt = f"""
        You are a Data Analyst. Explain this {chart_type} in 3 short, high-impact bullet points.
        X-axis: {x_axis}
        Y-axis: {y_axis}
        
        Summary Data:
        {summary_str}

        Keep it brief, easy to understand, and mention the highest and lowest performers.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error explaining chart: {e}"


def render_interactive_chart(df, x_axis, y_axis, chart_type):
    chart_data = df.groupby(x_axis)[y_axis].sum().reset_index()

    # Layout: Chart Title & ✨ AI Button side-by-side
    col_title, col_ai_btn = st.columns([0.9, 0.1])
    
    with col_title:
        st.markdown(f"##### 📊 {chart_type}: {y_axis} by {x_axis}")
    
    with col_ai_btn:
        # Subtle ✨ Icon Button
        ai_clicked = st.button("✨", key=f"ai_btn_{x_axis}_{y_axis}_{chart_type}", help="Explain this chart with AI")

    # Plotly Chart
    if chart_type == "Bar Chart":
        fig = px.bar(chart_data, x=x_axis, y=y_axis, color=x_axis, title="")
    elif chart_type == "Line Chart":
        fig = px.line(chart_data, x=x_axis, y=y_axis, markers=True, title="")
    elif chart_type == "Pie Chart":
        fig = px.pie(chart_data, names=x_axis, values=y_axis, title="")
    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_axis, y=y_axis, color=x_axis, size=y_axis, title="")
    elif chart_type == "Area Chart":
        fig = px.area(chart_data, x=x_axis, y=y_axis, title="")

    st.plotly_chart(fig, use_container_width=True)

    # Triggered on ✨ Button Click
    if ai_clicked:
        with st.spinner("✨ Gemini is analyzing this chart..."):
            explanation = explain_chart_with_ai(chart_type, x_axis, y_axis, chart_data)
            st.info(explanation, icon="🤖")


def render_correlation_heatmap(df, numeric_cols):
    if len(numeric_cols) > 1:
        correlation = df[numeric_cols].corr()

        col_l, col_c, col_r = st.columns([1, 2, 1])

        with col_c:
            fig, ax = plt.subplots(figsize=(5, 3.6))
            im = ax.imshow(correlation, cmap="Oranges")

            ax.set_xticks(range(len(numeric_cols)))
            ax.set_yticks(range(len(numeric_cols)))
            ax.set_xticklabels(numeric_cols, fontsize=7, rotation=30, ha="right")
            ax.set_yticklabels(numeric_cols, fontsize=7)

            for i in range(len(numeric_cols)):
                for j in range(len(numeric_cols)):
                    ax.text(j, i, f"{correlation.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color="black")

            fig.colorbar(im, fraction=0.046, pad=0.04)
            fig.tight_layout()
            st.pyplot(fig, width='content')

        heatmap_buf = io.BytesIO()
        fig.savefig(heatmap_buf, format="png", bbox_inches="tight", dpi=150)
        return heatmap_buf.getvalue()
    return None


def render_correlation_table(df, numeric_cols):
    """Show the exact correlation coefficients below the heatmap."""
    if len(numeric_cols) > 1:
        correlation = df[numeric_cols].corr().round(2)
        st.dataframe(correlation, width='stretch')


def render_summary_statistics(df, numeric_cols):
    """Show mean, median, std dev, min, max for all numeric columns."""
    if len(numeric_cols) > 0:
        stats = df[numeric_cols].describe().T[["mean", "50%", "std", "min", "max"]]
        stats.columns = ["Mean", "Median", "Std Dev", "Min", "Max"]
        st.dataframe(stats.round(2), width='stretch')


def render_distribution_analysis(df, numeric_cols):
    """Histogram + Box Plot for a user-selected numeric column."""
    if len(numeric_cols) > 0:
        dist_col = st.selectbox("Select Column for Distribution", numeric_cols, key="dist_col_select")

        col1, col2 = st.columns(2)

        with col1:
            fig_hist, ax_hist = plt.subplots(figsize=(4.4, 3.2))
            ax_hist.hist(df[dist_col], bins=20, color="#FF7A45", edgecolor="black")
            ax_hist.set_title(f"Histogram of {dist_col}", fontsize=9)
            ax_hist.set_xlabel(dist_col, fontsize=8)
            ax_hist.set_ylabel("Frequency", fontsize=8)
            ax_hist.tick_params(labelsize=7)
            fig_hist.tight_layout()
            st.pyplot(fig_hist, width='content')

        with col2:
            fig_box, ax_box = plt.subplots(figsize=(4.4, 3.2))
            ax_box.boxplot(df[dist_col].dropna(), vert=True, patch_artist=True,
                            boxprops=dict(facecolor="#FF7A45"))
            ax_box.set_title(f"Box Plot of {dist_col}", fontsize=9)
            ax_box.set_ylabel(dist_col, fontsize=8)
            ax_box.tick_params(labelsize=7)
            fig_box.tight_layout()
            st.pyplot(fig_box, width='content')


def render_top_n_chart(df, category_col, value_col, n=5):
    """Horizontal bar chart of the top-N categories by summed value."""
    if category_col and value_col:
        top_n = df.groupby(category_col)[value_col].sum().sort_values(ascending=False).head(n).reset_index()
        fig = px.bar(
            top_n, x=value_col, y=category_col, orientation="h",
            color=value_col, title=f"Top {n} {category_col} by {value_col}",
            color_continuous_scale=["#FF7A45", "#FF4B4B"],
            height=320
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, width='stretch')