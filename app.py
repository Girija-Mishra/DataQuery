import streamlit as st
import pandas as pd

from sql_agent import generate_sql, execute_query
from upload_database import create_upload_database


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="DataQuery AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
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


/* SIDEBAR */

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


/* FILE UPLOADER */

section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: white;
    border-radius: 12px;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: #111827 !important;
}


/* HEADER */

.main-title {
    font-size: 42px;
    font-weight: 750;
    color: #111827;
    margin-bottom: 0;
}

.subtitle {
    font-size: 17px;
    color: #6b7280;
    margin-top: 5px;
    margin-bottom: 30px;
}


/* CARDS */

.info-card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    margin-bottom: 20px;
}

.card-title {
    font-size: 14px;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 5px;
}

.card-value {
    font-size: 25px;
    font-weight: 700;
    color: #111827;
}


/* SECTION TITLES */

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    margin-top: 20px;
    margin-bottom: 10px;
}


/* CHAT */

[data-testid="stChatMessage"] {
    border-radius: 14px;
    margin-bottom: 12px;
}


/* INPUT */

[data-testid="stChatInput"] {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "uploaded_engine" not in st.session_state:
    st.session_state.uploaded_engine = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🔎 DataQuery AI")

    st.caption("Universal Text-to-SQL Assistant")

    st.divider()

    # --------------------------------------------------
    # UPLOAD
    # --------------------------------------------------

    st.markdown("### 📁 Upload your data")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"],
        help="Upload a CSV or Excel file to analyze."
    )

    if uploaded_file:

        try:

            if uploaded_file.name.lower().endswith(".csv"):

                df = pd.read_csv(uploaded_file)

            else:

                df = pd.read_excel(uploaded_file)


            # Store dataframe

            st.session_state.uploaded_df = df

            st.session_state.uploaded_filename = (
                uploaded_file.name
            )


            # Create SQLite database

            st.session_state.uploaded_engine = (
                create_upload_database(df)
            )


            # Clear old conversation

            st.session_state.messages = []


            st.success(
                f"✅ {uploaded_file.name}"
            )

            st.caption(
                f"{len(df):,} rows × "
                f"{len(df.columns)} columns"
            )


        except Exception as e:

            st.error(
                f"Could not read file: {e}"
            )


    st.divider()


    # --------------------------------------------------
    # CAPABILITIES
    # --------------------------------------------------

    st.markdown("### 🚀 Capabilities")

    st.markdown("""
    **💬 Natural Language**

    Ask questions using normal language.

    **🧠 RAG-powered**

    Retrieves relevant database schema.

    **🛡️ SQL Safety**

    Blocks destructive SQL commands.

    **📊 Data Analysis**

    Query your uploaded datasets.

    **⚡ Fast Analytics**

    SQL handles large datasets efficiently.
    """)


    st.divider()


    # --------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


    st.markdown("---")

    st.caption(
        "Built with Gemini + RAG + SQLite"
    )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">'
    'DataQuery AI 🔎'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about your data using natural language.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# UPLOADED FILE PREVIEW
# --------------------------------------------------

if st.session_state.uploaded_df is not None:

    df = st.session_state.uploaded_df


    st.markdown(
        '<div class="info-card">'
        '<div class="card-title">'
        '📁 Uploaded Dataset'
        '</div>'
        f'<div class="card-value">'
        f'{st.session_state.uploaded_filename}'
        f'</div>'
        '</div>',
        unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Rows",
            f"{len(df):,}"
        )


    with col2:

        st.metric(
            "Columns",
            len(df.columns)
        )


    with col3:

        st.metric(
            "Missing Values",
            int(
                df.isna().sum().sum()
            )
        )


    with st.expander(
        "👀 Preview dataset"
    ):

        st.dataframe(
            df.head(10),
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# WELCOME SCREEN
# --------------------------------------------------

if not st.session_state.messages:

    if st.session_state.uploaded_df is None:

        st.info(
            "👋 **Welcome!**\n\n"
            "Upload a CSV or Excel file and ask "
            "questions about it."
        )

    else:

        st.success(
            "🤖 **DataQuery is ready!**\n\n"
            "Ask a natural-language question about your dataset."
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
# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar=(
            "👤"
            if message["role"] == "user"
            else "🤖"
        )
    ):

        st.markdown(
            message["content"]
        )


        if message["role"] == "assistant":


            if "sql" in message:

                st.markdown(
                    '<div class="section-title">'
                    'Generated SQL'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.code(
                    message["sql"],
                    language="sql"
                )


            if "data" in message:

                df_result = pd.DataFrame(
                    message["data"],
                    columns=message["columns"]
                )

                st.markdown(
                    '<div class="section-title">'
                    'Query Result'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.dataframe(
                    df_result,
                    use_container_width=True,
                    hide_index=True
                )


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask anything about your data..."
)


if question:


    # --------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------

    st.session_state.messages.append({

        "role": "user",

        "content": question

    })


    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(question)


    # --------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "🔎 Analyzing your data..."
        ):

            try:


                # Generate SQL

                sql = generate_sql(
                    question
                )


                # Execute SQL

                columns, rows = execute_query(
                    sql
                )


                # --------------------------------------------------
                # GENERATED SQL
                # --------------------------------------------------

                st.markdown(
                    '<div class="section-title">'
                    'Generated SQL'
                    '</div>',
                    unsafe_allow_html=True
                )


                st.code(
                    sql,
                    language="sql"
                )


                # --------------------------------------------------
                # RESULT
                # --------------------------------------------------

                st.markdown(
                    '<div class="section-title">'
                    'Query Result'
                    '</div>',
                    unsafe_allow_html=True
                )


                if rows:

                    result_df = pd.DataFrame(
                        rows,
                        columns=columns
                    )


                    st.dataframe(
                        result_df,
                        use_container_width=True,
                        hide_index=True
                    )


                    st.success(
                        f"Query completed successfully • "
                        f"{len(rows):,} row(s)"
                    )


                else:

                    st.info(
                        "No results found."
                    )


                # --------------------------------------------------
                # SAVE RESPONSE
                # --------------------------------------------------

                st.session_state.messages.append({

                    "role": "assistant",

                    "content":
                        "Query completed successfully.",

                    "sql": sql,

                    "columns": columns,

                    "data": rows

                })


            except Exception as e:

                st.error(
                    f"❌ Error: {e}"
                )


                st.session_state.messages.append({

                    "role": "assistant",

                    "content":
                        f"❌ Error: {e}"

                })