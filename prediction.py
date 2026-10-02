import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression

def render_prediction_page():
    st.title("🤖 Sales Prediction")
    uploaded_file = st.file_uploader("Upload Excel File for Prediction", type=["xlsx"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

            if len(numeric_cols) >= 2:
                x_col = st.selectbox("Select Independent Variable", numeric_cols)
                y_col = st.selectbox("Select Dependent Variable", numeric_cols)

                X = df[[x_col]]
                y = df[y_col]

                model = LinearRegression()
                model.fit(X, y)

                future_value = st.number_input("Enter Future " + x_col)
                prediction = model.predict([[future_value]])

                st.success(f"Predicted {y_col}: {prediction[0]:.2f}")

                fig = px.scatter(df, x=x_col, y=y_col, trendline="ols", title="Prediction Graph")
                st.plotly_chart(fig, width='stretch')
            else:
                st.warning("Dataset must contain at least 2 numeric columns.")
        except Exception as e:
            st.error(f"Error: {e}")