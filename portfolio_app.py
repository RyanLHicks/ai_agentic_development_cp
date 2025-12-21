import streamlit as st
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Ryan's Portfolio",
    page_icon="🐾",
    layout="wide"
)

# --- HELPER FUNCTION FOR PROJECT PAGES ---
def show_project_page(project_name, problem_text, solution_text, mock_code, max_width=700):
    st.title(f"✨ {project_name}")
    st.write("---")

    st.subheader("💡 The Problem")
    st.info(problem_text)

    st.subheader("🛠️ The Solution")
    st.success(solution_text)

    st.subheader("🖼️ Project Snapshots: Before & After")
    
    base_image_name = project_name.lower().replace(' ', '_')
    before_image_path = f"images/{base_image_name}_before.png"
    after_image_path = f"images/{base_image_name}.png"

    col_before, col_after = st.columns(2)

    with col_before:
        if os.path.exists(before_image_path):
            st.image(before_image_path, caption=f"{project_name} - Before", width=max_width)
        else:
            st.warning(f"Before image not found for {project_name} at `{before_image_path}`. Using a placeholder.")
            st.image("https://via.placeholder.com/700x400.png?text=Before+Image+Coming+Soon", caption="Placeholder Before Image", width=max_width)

    with col_after:
        if os.path.exists(after_image_path):
            st.image(after_image_path, caption=f"{project_name} - After", width=max_width)
        else:
            st.warning(f"After image not found for {project_name} at `{after_image_path}`. Using a placeholder.")
            st.image("https://via.placeholder.com/700x400.png?text=After+Image+Coming+Soon", caption="Placeholder After Image", width=max_width)

    st.subheader("💻 Code Highlight")
    st.code(mock_code, language="python")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🐾 Ryan's Portfolio")
st.sidebar.markdown("---")
selection = st.sidebar.radio(
    "Go To",
    ["Home", "Retail Pulse", "Data Cleaner", "Price Monitor", "Invoice Bot"]
)
st.sidebar.markdown("---")
st.sidebar.info("Developed with ❤️ by your AI Agentic Developer!")


# --- MAIN PAGE CONTENT ---
if selection == "Home":
    st.image("https://via.placeholder.com/150.png?text=Your+Profile+Pic", width=150)
    st.title("🌟 Ryan - AI Agentic Developer & Supply Chain Analyst")
    st.markdown("### I build automated data solutions using Python, SQL, and AI Agents.")
    st.write("---")

    st.subheader("My Skills 🚀")
    st.markdown("This portfolio website was lovingly crafted with the help of **Code Puppy**! 🐾", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Python 🐍")
        st.write("💪 Data Analysis, Automation, Scripting")
    with col2:
        st.markdown("### Streamlit 📊")
        st.write("✨ Interactive Web Apps, Dashboards")
    with col3:
        st.markdown("### SQL 🗄️")
        st.write("🔍 Database Management, Query Optimization")

    st.markdown("""
        <style>
        .badge {
            display: inline-block;
            padding: 0.25em 0.4em;
            font-size: 75%;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.25rem;
            margin: 0.2em;
        }
        .badge-primary { background-color: #007bff; color: white; }
        .badge-secondary { background-color: #6c757d; color: white; }
        .badge-success { background-color: #28a745; color: white; }
        .badge-danger { background-color: #dc3545; color: white; }
        .badge-warning { background-color: #ffc107; color: black; }
        .badge-info { background-color: #17a2b8; color: white; }
        .badge-light { background-color: #f8f9fa; color: black; border: 1px solid #dee2e6; }
        .badge-dark { background-color: #343a40; color: white; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("""
        <span class="badge badge-primary">Python</span>
        <span class="badge badge-success">Streamlit</span>
        <span class="badge badge-info">SQL</span>
        <span class="badge badge-warning">Pandas</span>
        <span class="badge badge-danger">Regex</span>
        <span class="badge badge-secondary">Web Scraping</span>
        """, unsafe_allow_html=True)

    st.write("---")
    st.write("Connect with me on [LinkedIn](https://www.linkedin.com/in/ryan-hicks-59972639b/) | [GitHub](https://github.com/RyanLHicks/)") # Replace with actual links!


elif selection == "Retail Pulse":
    show_project_page(
        "Retail Pulse",
        "The problem involved analyzing vast amounts of retail sales data to identify trends, optimize inventory, and improve customer experience. Manual analysis was time-consuming and prone to errors.",
        "Developed an AI-powered dashboard using Streamlit and Pandas to provide real-time insights into sales performance, inventory levels, and customer behavior. Implemented anomaly detection to flag unusual patterns.",
        """
import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

st.title("Retail Pulse Dashboard")
data = load_data("retail_sales.csv")
st.line_chart(data.groupby('date')['sales'].sum())
""",
        max_width=700
    )

elif selection == "Data Cleaner":
    show_project_page(
        "Data Cleaner",
        "Dirty, inconsistent, and incomplete datasets are a common headache, leading to flawed analyses and operational inefficiencies. Manual data cleaning is a tedious and error-prone process.",
        "Created an intelligent data cleaning application using Streamlit that leverages Regex and Pandas to automate the identification and correction of data inconsistencies. Features include deduplication, format standardization, and missing value imputation.",
        """
import pandas as pd
import re

def clean_column(df, column_name, pattern, replacement):
    df[column_name] = df[column_name].astype(str).apply(lambda x: re.sub(pattern, replacement, x))
    return df

st.title("Data Cleaner App")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())
""",
        max_width=700
    )

elif selection == "Price Monitor":
    show_project_page(
        "Price Monitor",
        "Businesses struggle to keep track of competitor pricing and market fluctuations, often leading to missed opportunities or uncompetitive pricing strategies.",
        "Built a web scraping agent with Python to continuously monitor product prices across various e-commerce platforms. The Streamlit app visualizes price changes, alerts for drops, and provides competitive intelligence.",
        """
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_product_price(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_element = soup.find('span', class_='price') # Example selector
    return price_element.text if price_element else "N/A"

st.title("Price Monitoring Dashboard")
product_url = st.text_input("Enter Product URL:")
if st.button("Monitor Price"):
    price = get_product_price(product_url)
    st.write(f"Current Price: {price}")
""",
        max_width=700
    )

elif selection == "Invoice Bot":
    show_project_page(
        "Invoice Bot",
        "Manually processing invoices is a labor-intensive and error-prone task, slowing down financial operations and diverting valuable human resources.",
        "Developed an AI-powered Invoice Bot that uses OCR and NLP to automatically extract key information from invoices (e.g., vendor, amount, date) and integrates with accounting systems. The Streamlit interface allows for review and validation.",
        """
from PIL import Image
import pytesseract
import spacy

def extract_invoice_data(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    # Further NLP processing with spaCy
    # nlp = spacy.load("en_core_web_sm")
    # doc = nlp(text)
    return text # Simplified for mock
    
st.title("Invoice Processing Bot")
uploaded_file = st.file_uploader("Upload Invoice Image", type=["png", "jpg", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Invoice", width='stretch')
    extracted_text = extract_invoice_data(uploaded_file)
    st.text_area("Extracted Text", extracted_text, height=300)
""",
        max_width=700
    )
