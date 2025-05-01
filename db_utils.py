import sqlite3
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
from pathlib import Path

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

def extract_schema(db_path: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Extract the complete schema from a SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary containing table names as keys and lists of column info as values
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema = {}
        for (table_name,) in tables:
            # Get column info for each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Format column info
            column_info = []
            for col in columns:
                column_info.append({
                    'name': col[1],
                    'type': col[2],
                    'notnull': col[3],
                    'dflt_value': col[4],
                    'pk': col[5]
                })
            
            schema[table_name] = column_info
        
        return schema
    
    except sqlite3.Error as e:
        raise DatabaseError(f"Error extracting schema: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def execute_query(db_path: str, query: str) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    
    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute
        
    Returns:
        Tuple of (DataFrame with results, error message if any)
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        return df, None
    
    except sqlite3.Error as e:
        return pd.DataFrame(), str(e)
    except pd.errors.DatabaseError as e:
        return pd.DataFrame(), str(e)
    finally:
        if 'conn' in locals():
            conn.close()

def validate_query(db_path: str, query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a SQL query without executing it.
    
    Args:
        db_path: Path to the SQLite database file
        query: SQL query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        return True, None
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        if 'conn' in locals():
            conn.close()

def is_valid_db_file(file_path: str) -> bool:
    """
    Check if a file is a valid SQLite database.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is a valid SQLite database, False otherwise
    """
    if not Path(file_path).exists():
        return False
    
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False
    finally:
        if 'conn' in locals():
            conn.close() 