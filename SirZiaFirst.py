import streamlit as st
import pandas as pd
import os
import plotly.express as px
from io import BytesIO

# 🌟 Set Page Configuration
st.set_page_config(page_title="Data Sweeper App", page_icon="📊", layout="wide")

# 🎨 Custom CSS Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .title {
        font-size: 32px;
        font-weight: bold;
        color: #00e6e6;
        text-align: center;
    }
    .stButton>button {
        background-color: #00e6e6;
        color: black;
        font-weight: bold;
        border-radius: 10px;
        padding: 8px 16px;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #007f7f;
        color: white;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 230, 230, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# 🌟 App Title
st.markdown("<h1 class='title'>🚀 Data Sweeper App</h1>", unsafe_allow_html=True)
st.write("📂 Transform your data into CSV and Excel formats with built-in Data Cleaning & Visualization.")

# 📂 File Upload
uploaded_file = st.file_uploader("Upload your file (CSV, Excel, or PDF)", type=['csv', 'xlsx', 'pdf'], accept_multiple_files=True)

# 📊 Processing Uploaded Files
if uploaded_file:
    for file in uploaded_file:
        file_ext = os.path.splitext(file.name)[-1].lower()
        df = None  # Initialize DataFrame

        with st.spinner(f"Processing {file.name}..."):
            # 🟢 Load CSV
            if file_ext == '.csv':
                df = pd.read_csv(file)

            # 🟢 Load Excel
            elif file_ext == '.xlsx':
                df = pd.read_excel(file)

            # 🟢 Convert PDF to DataFrame
            elif file_ext == '.pdf':
                pdf_tables = []
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        tables = page.extract_table()
                        if tables:
                            pdf_tables.extend(tables)

                if pdf_tables:
                    df = pd.DataFrame(pdf_tables[1:], columns=pdf_tables[0])
                    st.success(f"✅ Extracted {len(df)} rows from {file.name}")
                else:
                    st.error("⚠ No tabular data found in this PDF.")
                    continue

            else:
                st.error(f"⚠ Unsupported File Format: {file_ext}")
                continue

        # 📄 Display File Info
        st.markdown("### 📄 File Details")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**File Name:** {file.name}")
            st.info(f"**File Size:** {file.size / 1024:.2f} KB")
        with col2:
            st.info(f"**File Type:** {file_ext.upper()}")
            st.info(f"**Rows:** {len(df)}")

        # 📊 Show Data Preview
        st.markdown("### 📊 Data Preview")
        st.dataframe(df.head())

        # 🛠 Data Cleaning
        st.markdown("## 🛠 Data Cleaning")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑 Remove Duplicates", key=file.name + "_dup"):
                df.drop_duplicates(inplace=True)
                st.success("✅ Duplicates Removed!")

        with col2:
            if st.button("🛠 Fill Missing Values", key=file.name + "_fill"):
                num_cols = df.select_dtypes(include=['number']).columns
                df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
                st.success("✅ Missing Values Filled!")

        # 🎯 Column Selection
        st.markdown("## 🎯 Select Columns")
        selected_columns = st.multiselect("Choose Columns:", df.columns, default=df.columns)
        df = df[selected_columns]

        # 📊 Data Visualization
        st.markdown("## 📈 Data Visualization")
        chart_type = st.selectbox("Choose a chart type:", ["Bar Chart", "Line Chart", "Pie Chart"])

        if chart_type == "Bar Chart":
            st.bar_chart(df.select_dtypes(include=['number']).iloc[:, :2])
        elif chart_type == "Line Chart":
            st.line_chart(df.select_dtypes(include=['number']).iloc[:, :2])
        elif chart_type == "Pie Chart":
            col = st.selectbox("Select column for Pie Chart:", df.columns, key=file.name + "_pie")
            pie_chart = px.pie(df, names=col, title=f"Distribution of {col}")
            st.plotly_chart(pie_chart)

        # 🔄 Convert & Download
        st.markdown("## 💾 Convert & Download")
        conversion_type = st.radio("Convert to:", ["CSV", "Excel"], key=file.name + "_convert")

        if st.button("🚀 Convert & Download", key=file.name + "_download"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine='openpyxl')
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)
            st.download_button(
                label=f"📥 Download {file_name}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
            )
            st.success("✅ File Ready for Download!")

