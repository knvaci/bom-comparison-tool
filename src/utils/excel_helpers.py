"""
Utility functions for Excel file handling
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Tuple

def validate_excel_file(file_path: str) -> bool:
    """Validate if file is a valid Excel file"""
    try:
        if not os.path.exists(file_path):
            return False
        
        # Try to read the file
        pd.read_excel(file_path, nrows=1)
        return True
    except Exception:
        return False

def get_file_info(file_path: str) -> Dict:
    """Get information about an Excel file"""
    try:
        df = pd.read_excel(file_path)
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'file_size': os.path.getsize(file_path),
            'file_name': os.path.basename(file_path)
        }
    except Exception as e:
        return {'error': str(e)}

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names by removing whitespace and special characters"""
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
    return df

def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove completely empty rows"""
    return df.dropna(how='all')

def normalize_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize data types for comparison"""
    # Convert numeric columns to string for consistent comparison
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].astype(str)
    return df

def extract_sample_data(df: pd.DataFrame, n_samples: int = 5) -> Dict:
    """Extract sample data from DataFrame for debugging"""
    samples = {}
    for col in df.columns:
        non_null_values = df[col].dropna()
        if len(non_null_values) > 0:
            samples[col] = non_null_values.head(n_samples).tolist()
        else:
            samples[col] = []
    return samples 