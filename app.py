import os

import pandas as pd
import streamlit as st

from upload_database import create_upload_database
from sql_agent import generate_sql, execute_query


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DataQuery AI",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f8fc;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    section[data-testid="stSidebar"] {
        background: #111827;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: white;
    }

    section[data-testid="stSidebar"]
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
    }

    section[data-testid="stSidebar"]
    [data-testid="stFileUploader"] * {
        color: #111827 !important;
    }

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "uploaded_engine" not in st.session_state:
    st.session_state.uploaded_engine = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔎 DataQuery AI")

    st.write(
        "Ask questions about your CSV or Excel data "
        "using natural language."
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx"],
        help="Upload a CSV or Excel file."
    )

    st.divider()

    st.caption("Supported formats")

    st.write("📄 CSV")
    st.write("📊 Excel (.xlsx)")


# ============================================================
# PROCESS UPLOADED FILE
# ============================================================

if uploaded_file is not None:

    # Process only when a new file is uploaded
    if (
        st.session_state.uploaded_filename
        != uploaded_file.name
    ):

        try:

            if uploaded_file.name.lower().endswith(".csv"):

                df = pd.read_csv(uploaded_file)

            else:

                df = pd.read_excel(uploaded_file)

            # Create SQLite database
            engine = create_upload_database(df)

            # Store in session
            st.session_state.uploaded_df = df
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.uploaded_engine = engine

            # Clear previous conversation
            st.session_state.messages = []

            st.success(
                f"Successfully uploaded {uploaded_file.name}"
            )

        except Exception as e:

            st.error(
                f"Error processing file: {str(e)}"
            )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔎 DataQuery AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about your data using natural language'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# NO DATA UPLOADED
# ============================================================

if st.session_state.uploaded_df is None:

    st.info(
        "👋 **Welcome!**\n\n"
        "Upload a CSV or Excel file from the sidebar "
        "and start asking questions about your data."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "**📊 Analytics**\n\n"
            "What is the average value of each category?"
        )

    with col2:

        st.info(
            "**🔢 Aggregation**\n\n"
            "Which category has the highest total sales?"
        )

    with col3:

        st.info(
            "**📈 Trends**\n\n"
            "Show me the monthly sales trend."
        )


# ============================================================
# DATASET INFORMATION
# ============================================================

else:

    df = st.session_state.uploaded_df

    st.success(
        f"🤖 **DataQuery is ready!** "
        f"Dataset: `{st.session_state.uploaded_filename}`"
    )

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Rows",
            f"{df.shape[0]:,}"
        )

    with col2:
        st.metric(
            "Columns",
            f"{df.shape[1]:,}"
        )

    with col3:
        st.metric(
            "Missing Values",
            f"{int(df.isna().sum().sum()):,}"
        )

    # Dataset preview
    with st.expander("👀 Preview Dataset"):

        st.dataframe(
            df.head(100),
            use_container_width=True
        )

    st.divider()


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "user":

            st.write(message["content"])

        else:

            if "sql" in message:

                st.code(
                    message["sql"],
                    language="sql"
                )

            if "columns" in message:

                result_df = pd.DataFrame(
                    message["rows"],
                    columns=message["columns"]
                )

                st.dataframe(
                    result_df,
                    use_container_width=True
                )

            else:

                st.write(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

if st.session_state.uploaded_df is not None:

    question = st.chat_input(
        "Ask a question about your dataset..."
    )

    if question:

        # Display user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):

            st.write(question)

        # Generate response
        with st.chat_message("assistant"):

            try:

                with st.spinner(
                    "🤖 Generating SQL..."
                ):

                    sql = generate_sql(question)

                st.markdown("### Generated SQL")

                st.code(
                    sql,
                    language="sql"
                )

                with st.spinner(
                    "⚡ Executing query..."
                ):

                    columns, rows = execute_query(sql)

                st.markdown("### Results")

                result_df = pd.DataFrame(
                    rows,
                    columns=columns
                )

                st.dataframe(
                    result_df,
                    use_container_width=True
                )

                # Save assistant response
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "sql": sql,
                        "columns": columns,
                        "rows": rows
                    }
                )

            except Exception as e:

                error_message = str(e)

                st.error(
                    f"Something went wrong: {error_message}"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )

else:

    st.chat_input(
        "Upload a dataset first...",
        disabled=True
    )