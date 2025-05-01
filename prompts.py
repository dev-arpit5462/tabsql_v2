from typing import Dict, List, Optional

def build_schema_prompt(schema: Dict[str, List[Dict[str, str]]]) -> str:
    """Build a formatted schema description for the prompt."""
    schema_desc = []
    for table_name, columns in schema.items():
        schema_desc.append(f"Table: {table_name}")
        for col in columns:
            constraints = []
            if col['pk']:
                constraints.append("PRIMARY KEY")
            if col['notnull']:
                constraints.append("NOT NULL")
            constraint_str = f" ({', '.join(constraints)})" if constraints else ""
            schema_desc.append(f"  - {col['name']} {col['type']}{constraint_str}")
        schema_desc.append("")
    return "\n".join(schema_desc)

def get_base_prompt(schema: Optional[Dict[str, List[Dict[str, str]]]] = None) -> str:
    """Get the base prompt for SQL generation."""
    if not schema:
        return """You are a SQL expert. Your task is to generate SQLite queries ONLY for database-related questions.

CRITICAL INSTRUCTIONS:
1. If the user's question is not about querying a database (e.g., general knowledge questions, non-database questions), respond with EXACTLY:
   "NOT_DB_QUERY: This question is not related to database querying."
2. Only generate SQL for questions that are clearly asking to retrieve or analyze data from a database.
3. If unsure about the schema, respond with EXACTLY:
   "SCHEMA_NEEDED: Please provide the database schema to generate an accurate query."

Format SQL responses as a single query without any explanations or markdown.

Now, process the following request:
"""
    
    schema_prompt = build_schema_prompt(schema)
    return f"""You are a SQL expert. Your task is to generate SQLite queries ONLY for questions about the provided database.

CRITICAL INSTRUCTIONS:
1. If the user's question cannot be answered using the tables and columns below, respond with EXACTLY:
   "NOT_DB_QUERY: This question cannot be answered with the available database schema."
2. Only use the tables and columns listed in this schema - DO NOT reference any tables or columns not listed here.
3. Do not make assumptions about additional tables or columns.

Database Schema:
{schema_prompt}

Format SQL responses as a single query without any explanations or markdown.

Now, process the following request:
"""

def get_error_correction_prompt(error_message: str, query: str, schema: Optional[Dict[str, List[Dict[str, str]]]] = None) -> str:
    """Get a prompt for correcting SQL errors."""
    base_prompt = f"""The following SQL query generated an error:
{error_message}

Original query:
{query}

Please correct the query to fix the error. The corrected query should be valid SQLite syntax.
IMPORTANT: Only use tables and columns that exist in the database schema.
If the query cannot be corrected using the available schema, respond with EXACTLY:
"NOT_DB_QUERY: This query cannot be corrected with the available database schema."
"""
    
    if schema:
        schema_prompt = build_schema_prompt(schema)
        base_prompt += f"\nDatabase Schema:\n{schema_prompt}\n"
    
    base_prompt += "\nProvide only the corrected SQL query without any explanations."
    return base_prompt 