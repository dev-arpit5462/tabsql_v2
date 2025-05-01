import streamlit as st
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from db_utils import extract_schema, execute_query, validate_query, is_valid_db_file
from llm import generate_sql_query, correct_sql_query

# Page configuration
st.set_page_config(
    page_title="SQL Query Generator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db_path' not in st.session_state:
    st.session_state.db_path = None
if 'schema' not in st.session_state:
    st.session_state.schema = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'mode' not in st.session_state:
    st.session_state.mode = "safe"  # "safe" or "fast"
if 'current_query' not in st.session_state:
    st.session_state.current_query = None

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to a temporary location and return the path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def display_schema_info(schema: Dict[str, List[Dict[str, str]]]):
    """Display database schema information in the sidebar."""
    st.sidebar.subheader("Database Schema")
    for table_name, columns in schema.items():
        with st.sidebar.expander(f"Table: {table_name}"):
            for col in columns:
                st.write(f"• {col['name']} ({col['type']})")
                if col['pk']:
                    st.write("  Primary Key")
                if col['notnull']:
                    st.write("  Not Null")

def display_query_history():
    """Display query history in the sidebar."""
    if st.session_state.query_history:
        st.sidebar.subheader("Query History")
        for i, (nl_query, sql_query) in enumerate(st.session_state.query_history):
            with st.sidebar.expander(f"Query {i+1}"):
                st.write("Natural Language:")
                st.code(nl_query)
                st.write("SQL:")
                st.code(sql_query)

def main():
    st.title("🔍 SQL Query Generator")
    st.markdown("""
    Convert natural language to SQL queries using Google's Gemini Pro AI.
    Upload a SQLite database file and type your query in natural language.
    
    Made with ❤️ by Arpit Singh
    """)

    # File upload
    uploaded_file = st.file_uploader("Upload SQLite Database", type=['db', 'sqlite'])
    
    if uploaded_file is not None:
        # Save uploaded file
        db_path = save_uploaded_file(uploaded_file)
        st.session_state.db_path = db_path
        
        # Extract and store schema
        try:
            schema = extract_schema(db_path)
            st.session_state.schema = schema
            st.success("Database loaded successfully!")
            
            # Display schema in sidebar
            display_schema_info(schema)
            
        except Exception as e:
            st.error(f"Error loading database: {str(e)}")
            return
    
    # Mode selection
    st.session_state.mode = st.radio(
        "Generation Mode",
        ["safe", "fast"],
        format_func=lambda x: "Safe Mode (with schema validation)" if x == "safe" else "Fast Mode (no schema validation)",
        horizontal=True
    )
    
    # Query input
    natural_language_query = st.text_area(
        "Enter your query in natural language:",
        placeholder="e.g., Show all orders placed in the last 7 days by customer ID"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        generate_button = st.button("Generate SQL")
    
    if generate_button:
        if not st.session_state.db_path:
            st.error("Please upload a database file first.")
            return
        
        if not natural_language_query:
            st.error("Please enter a query.")
            return
        
        # Generate SQL query
        with st.spinner("Generating SQL query..."):
            schema = st.session_state.schema if st.session_state.mode == "safe" else None
            generated_query, error = generate_sql_query(natural_language_query, schema)
            
            if error:
                st.error(error)
                st.session_state.current_query = None
                return
            
            # Store the generated query in session state
            st.session_state.current_query = generated_query
            
            # Display generated query
            st.subheader("Generated SQL Query")
            st.code(generated_query, language="sql")
            
            # Add to query history
            st.session_state.query_history.append((natural_language_query, generated_query))
    
    # Execute query button (outside the generate button's if block)
    with col2:
        execute_button = st.button("Execute Query")
    
    if execute_button:
        if not st.session_state.current_query:
            st.error("Please generate a SQL query first.")
            return
            
        with st.spinner("Executing query..."):
            # Validate query
            is_valid, error = validate_query(st.session_state.db_path, st.session_state.current_query)
            if not is_valid:
                st.error(f"Invalid query: {error}")
                
                # Attempt to correct the query
                with st.spinner("Attempting to correct the query..."):
                    schema = st.session_state.schema if st.session_state.mode == "safe" else None
                    corrected_query, error = correct_sql_query(error, st.session_state.current_query, schema)
                    if error:
                        st.error(error)
                        return
                    
                    st.info("Query corrected automatically:")
                    st.code(corrected_query, language="sql")
                    st.session_state.current_query = corrected_query
            
            # Execute query
            results, error = execute_query(st.session_state.db_path, st.session_state.current_query)
            if error:
                st.error(f"Error executing query: {error}")
                return
            
            # Display results
            st.subheader("Query Results")
            st.dataframe(results)
            
            # Download results as CSV
            if not results.empty:
                csv = results.to_csv(index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
    
    # Display query history
    display_query_history()

if __name__ == "__main__":
    main() 