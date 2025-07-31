# BOM Side-by-Side Compare Tool

A web-based tool for comparing Bill of Materials (BOM) Excel files to identify differences, new parts, removed parts, and modified quantities.

## Features

- **Automatic Column Detection**: Automatically detects MPN (Manufacturing Part Number), Ref Des/LOC (Reference Designator/Location), Quantity, and Description columns
- **Smart Comparison**: Compares BOMs using MPN + Ref Des as unique identifiers
- **Comprehensive Reports**: Generates detailed reports showing:
  - 🆕 New parts (added in the second file)
  - 🗑️ Removed parts (deleted from the second file)
  - 🔄 Modified parts (quantity or description changes)
  - ✅ Unchanged parts
- **Web Interface**: User-friendly web interface for easy file upload and comparison
- **Excel Output**: Downloads detailed comparison reports in Excel format

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the Web Interface**:
   Open your browser and go to: `http://localhost:5000`

## Usage

### Web Interface

1. **Upload Files**: Upload two Excel files (.xlsx or .xls) containing BOM data
2. **Compare**: Click the "Compare" button to analyze differences
3. **Review Results**: View the comparison results in the web interface
4. **Download Report**: Download a detailed Excel report with all findings

### Command Line Usage

You can also use the core functionality directly:

```python
from excel_tool import compare_boms

# Compare two BOM files
result = compare_boms('file1.xlsx', 'file2.xlsx', 'output.xlsx')
print(f"Found {len(result)} differences")
```

## Supported File Formats

The tool automatically detects common column names:

### MPN (Manufacturing Part Number)
- `mpn`, `manufacturer pn`, `manufacturer part number`, `mfg part number`
- `part number`, `item number`, `pn`, `part #`, `component`

### Reference Designator/Location
- `ref des`, `reference designator`, `location`, `loc`, `refdes`
- `designator`, `ref. des.`, `refdes/loc`

### Quantity
- `qty`, `quantity`, `qnty`, `qty required`, `required qty`

### Description
- `description`, `desc`, `part description`, `notes`, `comment`

## File Requirements

Your Excel files should have:
- Headers in the first few rows (tool scans up to 30 rows)
- At least an MPN column (required)
- Optional: Ref Des, Quantity, and Description columns
- Data starting after the header row

## Example Output

The tool generates comprehensive reports showing:

### Summary Statistics
- Total parts in each file
- Number of new parts
- Number of removed parts  
- Number of modified parts
- Number of unchanged parts

### Detailed Analysis
- **New Parts**: Parts present in File 2 but not in File 1
- **Removed Parts**: Parts present in File 1 but not in File 2
- **Modified Parts**: Parts with different quantities or descriptions
- **Unchanged Parts**: Parts that are identical in both files

## Troubleshooting

### Common Issues

1. **"Missing MPN column" error**:
   - Ensure your Excel file has a column with part numbers
   - Check that headers are in the first few rows
   - Verify column names match supported keywords

2. **"No headers found" warning**:
   - The tool will use the first data row as headers
   - This may not work optimally - consider adding proper headers

3. **Web app not starting**:
   - Check that all dependencies are installed
   - Ensure port 5000 is not in use
   - Try running `python app.py` in the project directory

### Testing

Run the test suite to verify everything works:

```bash
python simple_test.py
```

This will test:
- ✅ All dependencies are available
- ✅ Core BOM comparison functionality
- ✅ Flask web application setup

## Technical Details

### Architecture
- **Backend**: Flask web application with SQLAlchemy database
- **Core Logic**: Pandas-based Excel processing with fuzzy string matching
- **File Processing**: Supports both .xlsx and .xls formats
- **Column Detection**: Uses keyword matching and content analysis

### Key Functions
- `read_bom_with_auto_headers()`: Reads Excel files and detects columns
- `compare_boms()`: Compares two BOM files and returns differences
- `find_header_row_and_map()`: Automatically finds header rows and maps columns

## License

This tool is provided as-is for BOM comparison purposes. 