import os
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import get_base_prompt, get_error_correction_prompt

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

class QueryGenerationError(Exception):
    """Custom exception for query generation errors."""
    pass

def generate_sql_query(
    natural_language_query: str,
    schema: Optional[Dict[str, List[Dict[str, str]]]] = None,
    max_retries: int = 2
) -> Tuple[str, Optional[str]]:
    """
    Generate a SQL query from natural language using Gemini.
    
    Args:
        natural_language_query: The natural language query to convert
        schema: Optional database schema for context
        max_retries: Maximum number of retries for error correction
        
    Returns:
        Tuple of (generated SQL query or error message, error type if any)
    """
    try:
        # Build the prompt
        prompt = get_base_prompt(schema) + natural_language_query
        
        # Generate initial query
        response = model.generate_content(prompt)
        generated_query = response.text.strip()
        
        # Check for special responses
        if generated_query.startswith("NOT_DB_QUERY:"):
            return "", "Sorry, this information is not available in the current database."
        
        if generated_query.startswith("SCHEMA_NEEDED:"):
            return "", "Unable to generate query without database schema information."
        
        # Remove any markdown formatting if present
        if generated_query.startswith("```sql"):
            generated_query = generated_query[6:]
        if generated_query.endswith("```"):
            generated_query = generated_query[:-3]
        generated_query = generated_query.strip()
        
        return generated_query, None
    
    except Exception as e:
        return "", f"Error generating SQL query: {str(e)}"

def correct_sql_query(
    error_message: str,
    original_query: str,
    schema: Optional[Dict[str, List[Dict[str, str]]]] = None
) -> Tuple[str, Optional[str]]:
    """
    Attempt to correct a SQL query that generated an error.
    
    Args:
        error_message: The error message from the failed query
        original_query: The original SQL query that failed
        schema: Optional database schema for context
        
    Returns:
        Tuple of (corrected SQL query or error message, error type if any)
    """
    try:
        # Build the correction prompt
        prompt = get_error_correction_prompt(error_message, original_query, schema)
        
        # Generate corrected query
        response = model.generate_content(prompt)
        corrected_query = response.text.strip()
        
        # Check for special responses
        if corrected_query.startswith("NOT_DB_QUERY:"):
            return "", "Sorry, this query cannot be corrected with the available database schema."
        
        # Remove any markdown formatting if present
        if corrected_query.startswith("```sql"):
            corrected_query = corrected_query[6:]
        if corrected_query.endswith("```"):
            corrected_query = corrected_query[:-3]
        corrected_query = corrected_query.strip()
        
        return corrected_query, None
    
    except Exception as e:
        return "", f"Error correcting SQL query: {str(e)}" 