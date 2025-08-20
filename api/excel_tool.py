import pandas as pd
import re
import os
import sys

def safe_print(text):
    """Safe printing function that handles Unicode characters on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic Unicode characters with ASCII equivalents
        safe_text = str(text).encode('ascii', 'replace').decode('ascii')
        print(safe_text)

# Column mapping keywords
HEADER_KEYWORDS = {
    'mpn': [
        # Acronyms
        'mpn', 'pn', 'part #', 'part no', 'part number', 'item no', 'item number', 'component number',
        # Full names and variations
        'manufacturer part number', 'manufacturer pn', 'manufacturer part no', 'manufacturer part #',
        'manufacturer 1 pn', 'manufacturer 1 p/n', 'manufacturer 1 part number', 'manufacturer 1 part no',
        'mfg part number', 'mfg pn', 'mfg part no', 'mfg part #',
        'mfr part number', 'mfr pn', 'mfr part no', 'mfr part #',
        'manufacturing part number', 'manufacturing pn', 'manufacturing part no',
        'part', 'component', 'component part number', 'component pn',
        'item', 'item part number', 'item pn', 'item part no',
        'stock number', 'stock no', 'stock #', 'catalog number', 'catalog no',
        'model number', 'model no', 'model #', 'product number', 'product no',
        'sku', 'stock keeping unit', 'vendor part number', 'vendor pn',
        'supplier part number', 'supplier pn', 'supplier part no'
    ],
    'refdes': [
        # Acronyms
        'refdes', 'ref des', 'ref', 'loc', 'designator',
        # Full names and variations
        'reference designator', 'reference des', 'reference designation',
        'location', 'loc', 'position', 'pos', 'placement',
        'refdes/loc', 'ref des/loc', 'reference/location', 'ref/loc',
        'ref. des.', 'ref. des', 'reference designator/location',
        'component location', 'component position', 'component placement',
        'part location', 'part position', 'part placement',
        'designation', 'designator', 'reference', 'ref designation'
    ],
    'qty': [
        # Acronyms
        'qty', 'qnty', "q'ty", 'qnt', 'qty.', 'qty req', 'qty required',
        # Full names and variations
        'quantity', 'quantities', 'qty required', 'required qty', 'required quantity',
        'amount', 'count', 'number', 'count required', 'amount required',
        'quantity needed', 'qty needed', 'quantity per', 'qty per',
        'quantity per assembly', 'qty per assembly', 'quantity per unit',
        'qty per unit', 'quantity per board', 'qty per board',
        'total quantity', 'total qty', 'sum quantity', 'sum qty',
        'quantity total', 'qty total', 'quantity count', 'qty count'
    ],
    'description': [
        # Acronyms
        'desc', 'description',
        # Full names and variations
        'part description', 'component description', 'item description',
        'notes', 'note', 'comment', 'comments', 'remarks', 'remark',
        'part name', 'component name', 'item name', 'part title',
        'component title', 'item title', 'part details', 'component details',
        'item details', 'part info', 'component info', 'item info',
        'part specification', 'component specification', 'item specification',
        'part spec', 'component spec', 'item spec', 'specification',
        'part summary', 'component summary', 'item summary',
        'part notes', 'component notes', 'item notes',
        'description text', 'desc text', 'part text', 'component text',
        # Additional variations
        'description text', 'desc text', 'part text', 'component text',
        'part description text', 'component description text',
        'item description text', 'part details text',
        'component details text', 'item details text',
        'part info text', 'component info text', 'item info text',
        'part specification text', 'component specification text',
        'item specification text', 'part spec text', 'component spec text',
        'item spec text', 'specification text', 'part summary text',
        'component summary text', 'item summary text', 'part notes text',
        'component notes text', 'item notes text',
        # More specific keywords
        'component', 'part', 'item', 'material', 'materials',
        'component description', 'part description', 'item description',
        'material description', 'component name', 'part name', 'item name',
        'material name', 'component type', 'part type', 'item type',
        'material type', 'component info', 'part info', 'item info',
        'material info', 'component details', 'part details', 'item details',
        'material details', 'component notes', 'part notes', 'item notes',
        'material notes', 'component specification', 'part specification',
        'item specification', 'material specification', 'component spec',
        'part spec', 'item spec', 'material spec', 'component summary',
        'part summary', 'item summary', 'material summary'
    ]
}

def find_header_row_and_map(file_path):
    """Find the header row and map columns to standard names."""
    safe_print(f"\nFinding headers for: {os.path.basename(file_path)}")
    
    # Read the file without headers first
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.xls':
        df_raw = pd.read_excel(file_path, header=None, engine='xlrd')
    else:
        df_raw = pd.read_excel(file_path, header=None)
    
    print(f"Raw file shape: {df_raw.shape}")
    
    # Debug: Show first 15 rows to understand the file structure
    print(f"\nFirst 15 rows for debugging:")
    for i in range(min(15, len(df_raw))):
        row_data = df_raw.iloc[i].tolist()
        # Show only first 10 columns to avoid overwhelming output
        row_display = row_data[:10] if len(row_data) > 10 else row_data
        safe_print(f"Row {i}: {row_display}")
    
    # Look for the header row by checking each row
    header_row = None
    best_header_score = 0
    best_header_row = 0
    
    for row_idx in range(min(30, len(df_raw))):  # Check first 30 rows
        row = df_raw.iloc[row_idx]
        header_like_count = 0
        header_score = 0
        
        for cell in row:
            if pd.notna(cell) and isinstance(cell, str):
                cell_lower = str(cell).lower().strip()
                # Check for header-like keywords with different weights
                if any(kw in cell_lower for kw in ['mpn', 'part', 'qty', 'desc', 'ref', 'loc', 'item', 'mfr', 'package', 'manufacturer', 'designator', 'quantity']):
                    header_like_count += 1
                    # Give higher weight to specific MPN-related keywords
                    if any(kw in cell_lower for kw in ['manufacturer', 'mpn', 'part number', 'pn']):
                        header_score += 3
                    elif any(kw in cell_lower for kw in ['qty', 'quantity']):
                        header_score += 2
                    elif any(kw in cell_lower for kw in ['desc', 'description']):
                        header_score += 2
                    elif any(kw in cell_lower for kw in ['ref', 'designator']):
                        header_score += 2
                    else:
                        header_score += 1
        
        print(f"Row {row_idx}: {list(row)} -> Header-like count: {header_like_count}, Score: {header_score}")
        
        # Use a more flexible scoring system
        if header_like_count >= 2 and header_score >= 4:  # Lower threshold but require good score
            header_row = row_idx
            print(f"  -> FOUND HEADER ROW at index {row_idx} (score: {header_score})")
            break
        elif header_score > best_header_score:
            best_header_score = header_score
            best_header_row = row_idx
    
    if header_row is None:
        if best_header_score >= 2:  # Use best candidate if we found something reasonable
            header_row = best_header_row
            print(f"  -> USING BEST CANDIDATE HEADER ROW at index {header_row} (score: {best_header_score})")
        else:
            print("WARNING: No header row found, using row 0")
            header_row = 0 
    
    # Now read the file with the correct header row
    if ext == '.xls':
        df = pd.read_excel(file_path, header=header_row, engine='xlrd')
    else:
        df = pd.read_excel(file_path, header=header_row)
    
    print(f"Columns after header detection: {list(df.columns)}")
    
    # Debug: Show all column names with their indices
    print(f"\nDetailed column analysis:")
    for idx, col_name in enumerate(df.columns):
        col_lower = str(col_name).lower().strip()
        print(f"  Column {idx}: '{col_name}' (lowercase: '{col_lower}')")
    
    # Map columns to standard names
    col_map = {}
    
    # MPN detection with priority
    mpn_candidates = []
    for idx, col_name in enumerate(df.columns):
        cell_lower = str(col_name).lower().strip()
        
        # Skip very long descriptions that might contain part-related words
        if len(cell_lower) > 50:  # Skip very long descriptions
            continue
            
        # Priority 1: Exact "MPN"
        if cell_lower == 'mpn':
            mpn_candidates.append((idx, 10, 'Exact MPN'))
        # Priority 2: Manufacturer Part Number variations
        elif 'manufacturer part' in cell_lower and ('no' in cell_lower or 'number' in cell_lower):
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'manufacturer p/n' in cell_lower or 'manufacturer pn' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'manufacturer 1 pn' in cell_lower or 'manufacturer 1 p/n' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'manufacturer 1' in cell_lower and 'pn' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'mfg p/n' in cell_lower or 'mfg pn' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'mfg. p/n' in cell_lower or 'mfg. pn' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'manufacturer part no' in cell_lower or 'manufacturer part number' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'mfg part no' in cell_lower or 'mfg part number' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'manufacturer part#' in cell_lower or 'mfg part#' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'manufacturer part no.' in cell_lower or 'mfg part no.' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        elif 'manufacturer part number' in cell_lower or 'mfg part number' in cell_lower:
            mpn_candidates.append((idx, 8, 'Manufacturer Part Number'))
        # Priority 3: Vendor Part Number variations  
        elif 'vendor part' in cell_lower and ('no' in cell_lower or 'number' in cell_lower):
            mpn_candidates.append((idx, 6, 'Vendor Part Number'))
        elif 'vendor p/n' in cell_lower or 'vendor pn' in cell_lower:
            mpn_candidates.append((idx, 6, 'Vendor Part Number'))
        elif 'vendor part no' in cell_lower or 'vendor part number' in cell_lower:
            mpn_candidates.append((idx, 6, 'Vendor Part Number'))
        # Priority 4: Other part number variations
        elif len(cell_lower) <= 30 and any(kw in cell_lower for kw in ['part number', 'part no', 'part #', 'pn', 'item#', 'item #']):
            mpn_candidates.append((idx, 4, 'Other Part Number'))
    
    # Select the highest priority MPN column
    if mpn_candidates:
        mpn_candidates.sort(key=lambda x: x[1], reverse=True)
        selected_mpn = mpn_candidates[0]
        col_map['mpn'] = selected_mpn[0]
        print(f"Selected MPN column: {df.columns[selected_mpn[0]]} ({selected_mpn[2]})")
    else:
        print("WARNING: No MPN column found!")
    
    # Quantity detection
    qty_candidates = []
    for idx, col_name in enumerate(df.columns):
        cell_lower = str(col_name).lower().strip()
        if any(kw in cell_lower for kw in ['qty', 'quantity', 'qty.', 'qty:']):
            qty_candidates.append((idx, cell_lower))
    
    if qty_candidates:
        col_map['qty'] = qty_candidates[0][0]
        print(f"Selected Qty column: {df.columns[qty_candidates[0][0]]}")
    else:
        print("WARNING: No Qty column found!")
    
    # Ref Des/LOC detection
    refdes_candidates = []
    for idx, col_name in enumerate(df.columns):
        cell_lower = str(col_name).lower().strip()
        if any(kw in cell_lower for kw in ['ref', 'reference', 'designator', 'designation', 'loc', 'location']):
            refdes_candidates.append((idx, cell_lower))
    
    if refdes_candidates:
        col_map['refdes'] = refdes_candidates[0][0]
        print(f"Selected Ref Des/LOC column: {df.columns[refdes_candidates[0][0]]}")
    else:
        print("WARNING: No Ref Des/LOC column found!")
    
    # Description detection
    desc_candidates = []
    for idx, col_name in enumerate(df.columns):
        cell_lower = str(col_name).lower().strip()
        if any(kw in cell_lower for kw in ['desc', 'description', 'note', 'comment', 'remark']):
            desc_candidates.append((idx, cell_lower))
    
    if desc_candidates:
        col_map['description'] = desc_candidates[0][0]
        print(f"Selected Description column: {df.columns[desc_candidates[0][0]]}")
    else:
        print("WARNING: No Description column found!")
    
    print(f"Final column map: {col_map}")
    return header_row, col_map

def read_bom_with_auto_headers(file_path):
    """Read BOM file with auto-detected headers."""
    print(f"Reading: {file_path}")
    
    header_row, col_map = find_header_row_and_map(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    # First, read without headers to get the actual data
    if ext == '.xls':
        df_raw = pd.read_excel(file_path, header=None, engine='xlrd')
    else:
        df_raw = pd.read_excel(file_path, header=None)
    
    # Get the MPN column data before pandas converts it
    if 'mpn' in col_map and col_map['mpn'] < len(df_raw.columns):
        mpn_col_idx = col_map['mpn']
        # Get the original MPN values as strings
        original_mpn_values = df_raw.iloc[header_row+1:, mpn_col_idx].astype(str).tolist()
        print(f"Original MPN values (first 5): {original_mpn_values[:5]}")
    
    # Now read with headers
    if ext == '.xls':
        df = pd.read_excel(file_path, header=header_row, engine='xlrd')
    else:
        df = pd.read_excel(file_path, header=header_row)
    
    # Convert MPN column to string to preserve original formatting
    if 'mpn' in col_map and col_map['mpn'] < len(df.columns):
        mpn_col = df.columns[col_map['mpn']]
        df[mpn_col] = df[mpn_col].astype(str)
        print(f"Converted MPN column '{mpn_col}' to string type")
        
        # Replace with original values if we have them
        if 'original_mpn_values' in locals() and len(original_mpn_values) == len(df):
            df[mpn_col] = original_mpn_values
            print(f"Restored original MPN values")
    
    print(f"Detected columns: {col_map}")
    print(f"Available columns: {list(df.columns)}")
    print(f"Header row: {header_row}")
    print(f"Header row content: {df.iloc[header_row].tolist()}")
    print(f"Column mapping details:")
    for key, idx in col_map.items():
        if idx < len(df.columns):
            print(f"  {key} -> {df.columns[idx]} (index {idx})")
        else:
            print(f"  {key} -> INVALID INDEX {idx}")
    
    # Additional debugging: Show all columns and their sample values
    print(f"\nAll columns with sample values:")
    for idx, col_name in enumerate(df.columns):
        sample_values = df[col_name].dropna().head(3).tolist()
        print(f"  Column {idx}: '{col_name}' -> Sample values: {sample_values}")
    
    # Check if description column was found and has data
    if 'description' in col_map:
        desc_col_idx = col_map['description']
        if desc_col_idx < len(df.columns):
            desc_col_name = df.columns[desc_col_idx]
            desc_sample_values = df[desc_col_name].dropna().head(5).tolist()
            print(f"\nDescription column '{desc_col_name}' (index {desc_col_idx}) sample values:")
            print(f"  {desc_sample_values}")
            print(f"  Total non-null values: {len(df[desc_col_name].dropna())}")
            
            # Validate that the description column has meaningful data
            non_null_count = len(df[desc_col_name].dropna())
            if non_null_count == 0:
                print(f"  WARNING: Description column '{desc_col_name}' has no data!")
                # Remove this column from the map and try to find another
                del col_map['description']
            elif non_null_count < 3:
                print(f"  WARNING: Description column '{desc_col_name}' has very little data ({non_null_count} values)")
                # Check if the values are meaningful
                meaningful_values = [v for v in desc_sample_values if str(v).strip() and str(v).lower() not in ['nan', 'n/a', 'none', '']]
                if len(meaningful_values) == 0:
                    print(f"  WARNING: No meaningful values found in description column!")
                    del col_map['description']
        else:
            print(f"\nWARNING: Description column index {desc_col_idx} is invalid!")
            del col_map['description']
    else:
        print(f"\nWARNING: No description column found!")
        print(f"Available columns: {list(df.columns)}")
        # Try to find a description-like column
        for idx, col_name in enumerate(df.columns):
            col_lower = str(col_name).lower()
            if any(kw in col_lower for kw in ['desc', 'note', 'comment', 'remark', 'component', 'part', 'item', 'material']):
                print(f"  Potential description column: '{col_name}' (index {idx})")
                sample_values = df[col_name].dropna().head(3).tolist()
                print(f"    Sample values: {sample_values}")
                # Check if this column has meaningful data
                meaningful_values = [v for v in sample_values if str(v).strip() and str(v).lower() not in ['nan', 'n/a', 'none', '']]
                if len(meaningful_values) > 0:
                    print(f"    Found meaningful values: {meaningful_values}")
                    col_map['description'] = idx
                    break
    
    # Map columns to standard names
    mapped_cols = {}
    for key, idx in col_map.items():
        if idx < len(df.columns):
            mapped_cols[key] = df.columns[idx]
    
    return df, mapped_cols

def compare_boms(file1, file2):
    """Compare two BOM files and return differences."""
    print("Starting BOM comparison...")
    
    # Read both files
    df1, map1 = read_bom_with_auto_headers(file1)
    df2, map2 = read_bom_with_auto_headers(file2)
    
    # Check for required MPN column
    if 'mpn' not in map1 or 'mpn' not in map2:
        raise ValueError("MPN column not found in one or both files")
    
    # Normalize values
    def norm(val):
        """Normalize values while preserving original MPN formatting."""
        if pd.isna(val) or val == '' or str(val).lower() in ['nan', 'none', 'null', '']:
            return ''
        
        # Convert to string and strip whitespace
        val_str = str(val).strip()
        
        # Skip empty strings after stripping
        if not val_str or val_str.lower() in ['nan', 'none', 'null']:
            return ''
        
        # For MPN values, preserve original case and formatting
        # Only convert to uppercase for comparison purposes
        return val_str.upper()
    
    # Create comparison keys
    mpn_col1 = df1.columns[map1['mpn']] if isinstance(map1['mpn'], int) else map1['mpn']
    mpn_col2 = df2.columns[map2['mpn']] if isinstance(map2['mpn'], int) else map2['mpn']
    
    # Use only MPN for comparison (not Ref Des) to find modified parts
    key1 = df1[mpn_col1].apply(lambda x: norm(x))
    key2 = df2[mpn_col2].apply(lambda x: norm(x))
    
    # Filter out empty/nan keys but keep original indices
    # Create masks for valid entries
    mask1 = key1 != ''
    mask2 = key2 != ''
    
    # Filter dataframes to only include rows with valid MPNs
    df1_filtered = df1[mask1].copy()
    df2_filtered = df2[mask2].copy()
    
    # Recalculate keys for filtered dataframes
    key1_filtered = df1_filtered[mpn_col1].apply(lambda x: norm(x))
    key2_filtered = df2_filtered[mpn_col2].apply(lambda x: norm(x))
    
    set1 = set(key1_filtered)
    set2 = set(key2_filtered)
    
    # Use filtered data for comparison
    df1 = df1_filtered
    df2 = df2_filtered
    key1 = key1_filtered
    key2 = key2_filtered
    
    # Helper function to get values safely
    def safe_get_value(df, key_series, key, column_map, column_name):
        if column_name not in column_map:
            return 'N/A'
        
        col_name = column_map[column_name]
        if isinstance(col_name, int):
            col_name = df.columns[col_name]
        
        filtered = df.loc[key_series == key, col_name]
        if filtered.empty:
            return 'N/A'
        return filtered.iloc[0]
    
    # Helper function to get original MPN value (not normalized)
    def get_original_mpn(df, key_series, key, column_map):
        if 'mpn' not in column_map:
            return 'N/A'
        
        col_name = column_map['mpn']
        if isinstance(col_name, int):
            col_name = df.columns[col_name]
        
        filtered = df.loc[key_series == key, col_name]
        if filtered.empty:
            return 'N/A'
        
        # Get the original value and format it properly
        original_val = filtered.iloc[0]
        if pd.isna(original_val):
            return 'N/A'
        
        # Format as integer if it's a whole number, otherwise as string
        if isinstance(original_val, (int, float)) and original_val == int(original_val):
            return str(int(original_val))
        else:
            return str(original_val).strip()
    
    # Helper function to get Ref Des/LOC value
    def get_refdes_value(df, key_series, key, column_map):
        print(f"DEBUG get_refdes_value: key={key}, column_map={column_map}")
        if 'refdes' not in column_map:
            print(f"  No 'refdes' in column_map, returning N/A")
            return 'N/A'
        
        col_name = column_map['refdes']
        if isinstance(col_name, int):
            col_name = df.columns[col_name]
        print(f"  Using refdes column: {col_name}")
        
        filtered = df.loc[key_series == key, col_name]
        print(f"  Filtered data: {filtered}")
        if filtered.empty:
            print(f"  Filtered is empty, returning N/A")
            return 'N/A'
        
        refdes_val = filtered.iloc[0]
        print(f"  Raw refdes_val: {refdes_val} (type: {type(refdes_val)})")
        if pd.isna(refdes_val):
            print(f"  refdes_val is NaN, returning N/A")
            return 'N/A'
        
        result = str(refdes_val).strip()
        print(f"  Final result: '{result}'")
        return result
    
    # Find differences
    new_parts = []
    removed_parts = []
    modified_parts = []
    unchanged_parts = []
    unrecognized_parts = []
    
    # New parts (in File 2, not in File 1)
    for k in set2 - set1:
        # Get original MPN value for display
        original_mpn = get_original_mpn(df2, key2, k, map2)
        refdes = get_refdes_value(df2, key2, k, map2)
        line_idx = key2[key2 == k].index[0]
        line_number = line_idx + 2  # +2 because Excel is 1-indexed and we have header row
        
        new_parts.append({
            'MPN': original_mpn,
            'Ref Des/LOC': refdes,
            'Qty': safe_get_value(df2, key2, k, map2, 'qty'),
            'Description': safe_get_value(df2, key2, k, map2, 'description'),
            'Line Number': line_number
        })
    
    # Removed parts (in File 1, not in File 2)
    for k in set1 - set2:
        # Get original MPN value for display
        original_mpn = get_original_mpn(df1, key1, k, map1)
        refdes = get_refdes_value(df1, key1, k, map1)
        line_idx = key1[key1 == k].index[0]
        line_number = line_idx + 2  # +2 because Excel is 1-indexed and we have header row
        
        removed_parts.append({
            'MPN': original_mpn,
            'Ref Des/LOC': refdes,
            'Qty': safe_get_value(df1, key1, k, map1, 'qty'),
            'Description': safe_get_value(df1, key1, k, map1, 'description'),
            'Line Number': line_number
        })
    
    # Modified parts (same part, different qty/description)
    for k in set1 & set2:
        # Get values from both files
        qty1 = safe_get_value(df1, key1, k, map1, 'qty')
        qty2 = safe_get_value(df2, key2, k, map2, 'qty')
        desc1 = safe_get_value(df1, key1, k, map1, 'description')
        desc2 = safe_get_value(df2, key2, k, map2, 'description')
        
        # Normalize quantities for comparison (handle numeric vs string)
        def normalize_qty(qty_str):
            if pd.isna(qty_str) or qty_str == '' or str(qty_str).lower() == 'nan':
                return ''
            try:
                # Convert to float first, then to int if it's a whole number
                qty_float = float(str(qty_str))
                if qty_float == int(qty_float):
                    return str(int(qty_float))
                else:
                    return str(qty_float)
            except:
                return str(qty_str).strip()
        
        qty1_norm = normalize_qty(qty1)
        qty2_norm = normalize_qty(qty2)
        
        # Normalize descriptions
        desc1_norm = norm(desc1)
        desc2_norm = norm(desc2)
        
        # Check for differences
        qty_changed = qty1_norm != qty2_norm
        desc_changed = desc1_norm != desc2_norm
        
        print(f"Comparing part {k}:")
        print(f"  Qty1: '{qty1}' -> '{qty1_norm}'")
        print(f"  Qty2: '{qty2}' -> '{qty2_norm}'")
        print(f"  Qty changed: {qty_changed}")
        print(f"  Desc1: '{desc1}' -> '{desc1_norm}'")
        print(f"  Desc2: '{desc2}' -> '{desc2_norm}'")
        print(f"  Desc changed: {desc_changed}")
        
        if qty_changed or desc_changed:
            print(f"  -> Adding to modified parts")
            # Get original MPN values from both files
            original_mpn1 = get_original_mpn(df1, key1, k, map1)
            original_mpn2 = get_original_mpn(df2, key2, k, map2)
            refdes1 = get_refdes_value(df1, key1, k, map1)
            refdes2 = get_refdes_value(df2, key2, k, map2)
            line1_idx = key1[key1 == k].index[0]
            line2_idx = key2[key2 == k].index[0]
            line1_number = line1_idx + 2  # +2 because Excel is 1-indexed and we have header row
            line2_number = line2_idx + 2  # +2 because Excel is 1-indexed and we have header row
            
            # Debug: Log the ref des values being added
            print(f"DEBUG: Adding modified part {original_mpn1}")
            print(f"  refdes1 (File1): '{refdes1}' (type: {type(refdes1)})")
            print(f"  refdes2 (File2): '{refdes2}' (type: {type(refdes2)})")
            
            modified_part = {
                'MPN': original_mpn1,  # Use File1 MPN for display
                'Ref Des/LOC': refdes1,  # Use File1 Ref Des for display
                'File1 Ref Des': refdes1,  # Add File1 Ref Des
                'File2 Ref Des': refdes2,  # Add File2 Ref Des
                'File1 Qty': qty1,
                'File2 Qty': qty2,
                'File1 Description': desc1,
                'File2 Description': desc2,
                'File1 Line': line1_number,
                'File2 Line': line2_number
            }
            print(f"  Final modified_part: {modified_part}")
            modified_parts.append(modified_part)
        else:
            print(f"  -> Adding to unchanged parts")
            # Get original MPN value for display
            original_mpn = get_original_mpn(df1, key1, k, map1)
            refdes = get_refdes_value(df1, key1, k, map1)
            line_idx = key1[key1 == k].index[0]
            line_number = line_idx + 2  # +2 because Excel is 1-indexed and we have header row
            
            unchanged_parts.append({
                'MPN': original_mpn,
                'Ref Des/LOC': refdes,
                'Qty': qty1,
                'Description': desc1,
                'Line Number': line_number
            })
    
    # Summary statistics
    summary_stats = {
        'total_parts_file1': len(set1),
        'total_parts_file2': len(set2),
        'new_parts_count': len(new_parts),
        'removed_parts_count': len(removed_parts),
        'modified_parts_count': len(modified_parts),
        'unchanged_parts_count': len(unchanged_parts),
        'unrecognized_parts_count': len(unrecognized_parts)
    }
    
    # Convert all values to strings for web display
    def to_str_dict_list(lst):
        def clean_value(v):
            if pd.isna(v) or v == '' or str(v).lower() in ['nan', 'none', 'null']:
                return 'N/A'
            # Format numbers properly
            if isinstance(v, (int, float)) and not pd.isna(v):
                if v == int(v):
                    return str(int(v))
                else:
                    return str(v)
            val_str = str(v).strip()
            if not val_str or val_str.lower() in ['nan', 'none', 'null']:
                return 'N/A'
            return val_str
        
        return [{k: clean_value(v) for k, v in row.items()} for row in lst]
    
    return {
        'new_parts': to_str_dict_list(new_parts),
        'removed_parts': to_str_dict_list(removed_parts),
        'modified_parts': to_str_dict_list(modified_parts),
        'unchanged_parts': to_str_dict_list(unchanged_parts),
        'unrecognized_parts': to_str_dict_list(unrecognized_parts),
        'summary_stats': summary_stats
    } 