import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import tempfile
import os

# === Function to generate NLP Summary ===
def generate_summary(df: pd.DataFrame) -> str:
    summary_lines = []
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            col_mean = df[column].mean()
            col_min = df[column].min()
            col_max = df[column].max()
            trend = "increasing " if df[column].iloc[-1] > df[column].iloc[0] else "decreasing "
            summary_lines.append(
                f"- **{column}** has a mean of **{col_mean:.2f}**, ranging from **{col_min}** to **{col_max}**, and appears to be **{trend}**."
            )
    return "\n".join(summary_lines) or "No numeric data available to summarize."

# === Function to plot chart ===
def plot_chart(df, x_col, y_col, chart_type):
    fig, ax = plt.subplots(figsize=(8, 5))
    if chart_type == "Line":
        ax.plot(df[x_col], df[y_col], marker='o', linestyle='-', color='blue')
    elif chart_type == "Bar":
        ax.bar(df[x_col], df[y_col], color='green')
    elif chart_type == "Scatter":
        ax.scatter(df[x_col], df[y_col], color='red')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f'{chart_type} Chart: {y_col} vs {x_col}')
    return fig

# === Function to generate PDF ===
def generate_pdf(df, logo_file, summary_text, chart_fig):
    pdf = FPDF()
    pdf.add_page()

    # Handle logo
    if logo_file is not None:
        tmp_logo_path = os.path.join(tempfile.gettempdir(), "logo.png")
        with open(tmp_logo_path, "wb") as f:
            f.write(logo_file.read())
        pdf.image(tmp_logo_path, x=10, y=8, w=30)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI-Based Business Report", ln=True, align='C')
    pdf.ln(20)

    # Add summary
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=summary_text or "No summary available.")
    pdf.ln(10)

    # Save chart
    chart_path = os.path.join(tempfile.gettempdir(), "chart.png")
    chart_fig.savefig(chart_path)
    pdf.image(chart_path, x=30, w=150)

    # Save PDF
    pdf_path = os.path.join(tempfile.gettempdir(), "business_report.pdf")
    pdf.output(pdf_path)
    return pdf_path

# === Streamlit App ===
st.set_page_config(page_title="AI Business Report", layout="wide")
st.title(" AI-Based Business Report Web App")

# Sidebar for logo
logo_file = st.sidebar.file_uploader("Upload Company Logo (Optional)", type=["png", "jpg", "jpeg"])

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(" File uploaded successfully.")
    st.dataframe(df)

    tab1, tab2, tab3 = st.tabs([" Charts", " Summary", " Generate Report"])

    with tab1:
        x_col = st.selectbox("X-axis", df.columns)
        y_col = st.selectbox("Y-axis", df.columns)
        chart_type = st.radio("Chart Type", ["Line", "Bar", "Scatter"])
        fig = plot_chart(df, x_col, y_col, chart_type)
        st.pyplot(fig)

    with tab2:
        summary = generate_summary(df)
        st.markdown(summary)

    with tab3:
        st.markdown("Click below to generate and download the report as a PDF.")
        if st.button(" Generate PDF Report"):
            pdf_path = generate_pdf(df, logo_file, summary, fig)
            with open(pdf_path, "rb") as f:
                st.download_button(" Download Report", f, file_name="AI_Business_Report.pdf")
else:
    st.info(" Please upload a CSV file to begin.")
