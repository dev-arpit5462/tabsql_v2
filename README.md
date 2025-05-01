# SQL Query Generator

A Streamlit web application that converts natural language to SQL queries using Google's Gemini Pro AI. The application allows users to upload SQLite databases and generate SQL queries through natural language input.

## Features

- Upload and analyze SQLite databases
- Convert natural language to SQL queries
- Two generation modes:
  - Safe Mode: Uses database schema for accurate query generation
  - Fast Mode: Quick generation without schema validation
- Query history tracking
- Schema visualization in sidebar
- Automatic query correction
- Results export to CSV
- Modern, user-friendly interface

## Prerequisites

- Python 3.10 or higher
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dev-arpit5462/tabsql_v2.git
cd sql-query-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Add your Gemini API key to the `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run main.py
```

2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

3. Upload a SQLite database file (.db or .sqlite)

4. Enter your query in natural language

5. Choose between Safe Mode (with schema validation) or Fast Mode

6. Click "Generate SQL" to generate the query

7. Review the generated SQL and click "Execute Query" to run it

8. View the results and download them as CSV if needed

## Project Structure

- `main.py` - Streamlit UI and main application logic
- `llm.py` - Gemini API integration and query generation
- `db_utils.py` - SQLite database utilities
- `prompts.py` - Prompt templates for Gemini
- `requirements.txt` - Python dependencies

## Error Handling

The application includes comprehensive error handling for:
- Invalid database files
- Query generation failures
- SQL syntax errors
- Query execution errors

Automatic query correction is attempted when possible.



## License

This project is licensed under the MIT License - see the LICENSE file for details. 
