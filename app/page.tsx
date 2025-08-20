'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, ArrowLeftRight, CheckCircle, XCircle, AlertCircle, HelpCircle, ChevronDown, ChevronUp, Search, Printer, FileDown } from 'lucide-react';
import axios from 'axios';
// Removed unused import

interface BOMPart {
  MPN: string;
  'Ref Des/LOC': string;
  Qty: string;
  Description: string;
  'Line Number': string;
}

interface ModifiedPart {
  MPN: string;
  'File1 Ref Des': string;
  'File2 Ref Des': string;
  'File1 Qty': string;
  'File2 Qty': string;
  'File1 Description': string;
  'File2 Description': string;
  'File1 Line': string;
  'File2 Line': string;
  diffs?: {
    Qty?: boolean;
    Description?: boolean;
    RefDes?: boolean;
    Line?: boolean;
  };
}

interface ComparisonResults {
  new_parts: BOMPart[];
  removed_parts: BOMPart[];
  modified_parts: ModifiedPart[];
  unchanged_parts: BOMPart[];
  unrecognized_parts: BOMPart[];
  summary_stats: {
    total_parts_file1: number;
    total_parts_file2: number;
    new_parts_count: number;
    removed_parts_count: number;
    modified_parts_count: number;
    unchanged_parts_count: number;
    unrecognized_parts_count: number;
  };
}

export default function Home() {
  const [file1, setFile1] = useState<File | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const [fileName1, setFileName1] = useState<string>('');
  const [fileName2, setFileName2] = useState<string>('');
  const [results, setResults] = useState<ComparisonResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['category-1', 'category-2', 'category-3']));
  const [prePrintExpanded, setPrePrintExpanded] = useState<Set<string> | null>(null);
  const onDrop1 = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile1(acceptedFiles[0]);
      setFileName1(acceptedFiles[0].name); 
    }
  }, []);

  const onDrop2 = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile2(acceptedFiles[0]);
      setFileName2(acceptedFiles[0].name);
      setError(null);
    }
  }, []);

  const { getRootProps: getRootProps1, getInputProps: getInputProps1, isDragActive: isDragActive1 } = useDropzone({
    onDrop: onDrop1,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  });

  const { getRootProps: getRootProps2, getInputProps: getInputProps2, isDragActive: isDragActive2 } = useDropzone({
    onDrop: onDrop2,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  });

  const handleCompare = async () => {
    if (!file1 || !file2) {
      setError('Please select both files first.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file1', file1); 
      formData.append('file2', file2);

      // Use relative URL to work with ngrok and any domain
      const apiUrl = '/api/compare';
      const response = await axios.post(apiUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'ngrok-skip-browser-warning': 'true', // Skip ngrok warning page
        },
        timeout: 120000, // 120 second timeout
        withCredentials: false, // Don't send credentials for CORS
      });

      console.log('API Response:', response.data);
      
      // Debug: Check what's in modified_parts
      if (response.data.modified_parts && response.data.modified_parts.length > 0) {
        console.log('First modified part:', response.data.modified_parts[0]);
        console.log('Modified parts keys:', Object.keys(response.data.modified_parts[0]));
      }
      
      setResults(response.data);
    } catch (err: any) {
      console.error('Comparison error:', err);
      console.error('Error response:', err.response);
      
      let errorMessage = 'Comparison failed. Please try again.';
      
      if (err.response) {
        // Server responded with error status
        if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response.data?.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.status === 500) {
          errorMessage = 'Server error occurred. Please try again.';
        } else if (err.response.status === 400) {
          errorMessage = 'Invalid file format. Please upload Excel files only.';
        }
      } else if (err.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something else happened
        errorMessage = err.message || 'An unexpected error occurred.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const clearFiles = () => {
    setFile1(null);
    setFile2(null);
    setFileName1('');
    setFileName2('');
    setResults(null);
    setError(null);
    setSearchTerm('');
  };

  const handlePrint = () => {
    if (typeof window === 'undefined') return;
    // Ensure categories are expanded for print
    setPrePrintExpanded(new Set(expandedCategories));
    setExpandedCategories(new Set(['category-1', 'category-2', 'category-3']));
    setTimeout(() => window.print(), 300);
  };

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const restore = () => {
      if (prePrintExpanded) {
        setExpandedCategories(prePrintExpanded);
      }
    };
    window.addEventListener('afterprint', restore);
    return () => window.removeEventListener('afterprint', restore);
  }, [prePrintExpanded]);

  const exportToExcel = () => {
    if (!results) return;
    try {
      // Use exceljs for styled export that mirrors UI
      // @ts-ignore - exceljs types may not be available in the runtime image
      import('exceljs').then(async (ExcelJSImport) => {
        const ExcelJS: any = (ExcelJSImport as any).default || ExcelJSImport;
        const workbook = new ExcelJS.Workbook();

        const addStyledSheet = (name: string, headerLeft: string, headerRight: string, rows: Array<any[]>) => {
          const sheet = workbook.addWorksheet(name);
          sheet.views = [{ state: 'frozen', ySplit: 2 }];

          // Column widths to reflect UI
          sheet.columns = [
            { width: 28 }, // MPN
            { width: 24 }, // RefDes F1
            { width: 10 }, // Qty F1
            { width: 24 }, // RefDes F2
            { width: 10 }, // Qty F2
          ];

          const headerRow1 = sheet.addRow(['MPN', headerLeft, null, headerRight, null]);
          headerRow1.font = { bold: true };
          headerRow1.getCell(2).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'DBEAFE' } }; // blue-100
          headerRow1.getCell(4).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'DCFCE7' } }; // green-100
          sheet.mergeCells(1, 2, 1, 3);
          sheet.mergeCells(1, 4, 1, 5);

          const headerRow2 = sheet.addRow(['MPN', 'Ref Des (F1)', 'Qty (F1)', 'Ref Des (F2)', 'Qty (F2)']);
          headerRow2.font = { bold: true };

          // Borders for header rows
          [headerRow1, headerRow2].forEach((r: any) => r.eachCell((c: any) => {
            c.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
          }));

          // Data rows mirroring UI
          rows.forEach((a: any[]) => {
            const row: any = sheet.addRow(a);
            row.eachCell((c: any) => {
              c.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
              c.alignment = { wrapText: true };
            });
          });
        };

        // Build rows for each section from current UI state
        const changeRows = results.modified_parts
          .sort((a, b) => a.MPN.localeCompare(b.MPN))
          .map(p => [p.MPN, p['File1 Ref Des'], p['File1 Qty'], p['File2 Ref Des'], p['File2 Qty']]);
        addStyledSheet('Change', `File 1: ${fileName1 || 'File 1'}`, `File 2: ${fileName2 || 'File 2'}`, changeRows);

        const deleteRows = results.removed_parts.map(p => [p.MPN, p['Ref Des/LOC'], p.Qty, '', '']);
        addStyledSheet('Delete (File1 only)', `File 1: ${fileName1 || 'File 1'}`, `File 2: ${fileName2 || 'File 2'}`, deleteRows);

        const addRows = results.new_parts.map(p => [p.MPN, '', '', p['Ref Des/LOC'], p.Qty]);
        addStyledSheet('Add (File2 only)', `File 1: ${fileName1 || 'File 1'}`, `File 2: ${fileName2 || 'File 2'}`, addRows);

        const fileNameSafe1 = (fileName1 || 'File1').replace(/[^\w\-\.]+/g, '_');
        const fileNameSafe2 = (fileName2 || 'File2').replace(/[^\w\-\.]+/g, '_');
        const outName = `bom_comparison_${fileNameSafe1}_vs_${fileNameSafe2}.xlsx`;

        const buf = await workbook.xlsx.writeBuffer();
        const blob = new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = outName;
        link.click();
        URL.revokeObjectURL(link.href);
      });
    } catch (e) {
      console.error('Excel export failed', e);
    }
  };

  // Filter results based on search term
  const filterResults = (results: ComparisonResults, searchTerm: string) => {
    if (!searchTerm.trim()) return results;
    
    const searchLower = searchTerm.toLowerCase();
    
    const filterParts = (parts: BOMPart[]) => 
      parts.filter(part => 
        part.MPN.toLowerCase().includes(searchLower) ||
        part['Ref Des/LOC'].toLowerCase().includes(searchLower)
      );
    
    const filterModifiedParts = (parts: ModifiedPart[]) =>
      parts.filter(part =>
        part.MPN.toLowerCase().includes(searchLower) ||
        part['File1 Ref Des'].toLowerCase().includes(searchLower)
      );
    
    return {
      ...results,
      new_parts: filterParts(results.new_parts),
      removed_parts: filterParts(results.removed_parts),
      modified_parts: filterModifiedParts(results.modified_parts),
      unchanged_parts: filterParts(results.unchanged_parts),
      unrecognized_parts: filterParts(results.unrecognized_parts),
      summary_stats: {
        ...results.summary_stats,
        new_parts_count: filterParts(results.new_parts).length,
        removed_parts_count: filterParts(results.removed_parts).length,
        modified_parts_count: filterModifiedParts(results.modified_parts).length,
        unchanged_parts_count: filterParts(results.unchanged_parts).length,
        unrecognized_parts_count: filterParts(results.unrecognized_parts).length,
      }
    };
  };

  const renderPartTable = (parts: BOMPart[] | ModifiedPart[], isModified = false) => (
    <div className="overflow-x-auto">
          <table className="w-full bg-white border-2 border-gray-600 rounded-lg text-sm min-w-full border-collapse">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-2 py-2 text-left font-semibold text-sm min-w-40 border border-gray-600">MPN</th>
            <th className="px-2 py-2 text-left font-semibold text-sm min-w-24 border border-gray-600">{isModified ? 'File1 Ref Des' : 'Ref Des/LOC'}</th>
            <th className="px-2 py-2 text-left font-semibold text-sm min-w-16 border border-gray-600">{isModified ? 'File1 Qty' : 'Qty'}</th>
          </tr>
        </thead>
        <tbody>
          {parts.map((part, index) => (
            <tr key={index}>
              <td className="px-2 py-2 font-medium text-primary-600 text-sm break-all min-w-40 border border-gray-600">{part.MPN}</td>
              <td className="px-2 py-2 text-sm break-all min-w-24 border border-gray-600">{isModified ? (part as ModifiedPart)['File1 Ref Des'] : (part as BOMPart)['Ref Des/LOC']}</td>
              <td className="px-2 py-2 text-sm min-w-16 border border-gray-600">{isModified ? (part as ModifiedPart)['File1 Qty'] : (part as BOMPart).Qty}</td>
                {/* Description and Line removed */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderEmptyTable = (message: string) => (
    <div className="overflow-x-auto">
      <table className="w-full bg-white border-2 border-gray-600 rounded-lg text-sm min-w-full border-collapse">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-2 py-2 text-left font-semibold text-sm min-w-40 border border-gray-600">MPN</th>
            <th className="px-2 py-2 text-left font-semibold text-sm min-w-24 border border-gray-600">Ref Des/LOC</th>
            <th className="px-2 py-2 text-left font-semibold text-sm min-w-16 border border-gray-600">Qty</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colSpan={3} className="px-2 py-8 text-center text-gray-500 border border-gray-600">
              {message}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );

  const FileHeader = ({ fileName, color, position }: { fileName: string; color: string; position: 'left' | 'right' }) => (
    <div className={`flex items-center gap-2 mb-3 ${position === 'right' ? 'justify-end' : ''}`}>
      <div className={`px-3 py-1 rounded-t-lg ${color} text-white text-sm font-medium`}>
        {fileName || `File ${position === 'left' ? '1' : '2'}`}
      </div>
    </div>
  );

  const renderPartComparisonView = (results: ComparisonResults) => (
    <div className="space-y-6 category-section">
      {/* Category 1: Delete (was removed before; now redefined) */}
      {results.removed_parts.length > 0 && (
      <CategorySection
          id="category-1"
          title="Category 1: Delete (Parts only in File 1)"
          icon={XCircle}
          color="primary"
          count={results.summary_stats.removed_parts_count}
          isExpanded={expandedCategories.has('category-1')}
          onToggle={() => toggleCategory('category-1')}
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <FileHeader fileName={fileName1} color="bg-blue-600" position="left" />
            {results.removed_parts.length > 0 ? (
              renderPartTable(results.removed_parts)
            ) : (
              renderEmptyTable("No parts found in File 1 only")
            )}
          </div>
          <div className={'print:hidden'}>
            <FileHeader fileName={fileName2} color="bg-red-600" position="right" />
            {renderEmptyTable("Not Found in File 2")}
          </div>
          </div>
        </CategorySection>
      )}

      {/* Category 2: Add (Parts Only in File 2) */}
      <CategorySection
        id="category-2"
        title="Category 2: Add (Parts Only in File 2)"
        icon={CheckCircle}
        color="success"
        count={results.summary_stats.new_parts_count}
        isExpanded={expandedCategories.has('category-2')}
        onToggle={() => toggleCategory('category-2')}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className={'print:hidden'}>
            <FileHeader fileName={fileName1} color="bg-blue-600" position="left" />
            {renderEmptyTable("Not Found in File 1")}
          </div>
          <div>
            <FileHeader fileName={fileName2} color="bg-green-600" position="right" />
            {results.new_parts.length > 0 ? (
              renderPartTable(results.new_parts)
            ) : (
              renderEmptyTable("No parts found in File 2 only")
            )}
          </div>
        </div>
      </CategorySection>

      {/* Category 3: Change (Data Differences) */}
      <CategorySection
        id="category-3"
        title="Category 3: Change (Parts with Data Differences)"
        icon={AlertCircle}
        color="warning"
        count={results.summary_stats.modified_parts_count}
        isExpanded={expandedCategories.has('category-3')}
        onToggle={() => toggleCategory('category-3')}
      >
        {/* Category 3 content */}
        {results.modified_parts.length > 0 && (
        <>
          <div className="overflow-x-auto">
            <div className="text-xs text-gray-600 mb-2">Yellow highlight indicates differences between File 1 and File 2.</div>
            <table className="w-full bg-white border-2 border-gray-600 rounded-lg text-sm min-w-full border-collapse">
              <thead>
                <tr>
                  <th rowSpan={2} className="px-2 py-2 text-left font-semibold text-sm min-w-40 sticky left-0 z-20 bg-gray-50">MPN</th>
                  <th colSpan={2} className="px-2 py-2 text-center font-semibold text-sm bg-blue-100 text-blue-900">File 1: {fileName1 || 'File 1'}</th>
                  <th colSpan={2} className="px-2 py-2 text-center font-semibold text-sm bg-green-100 text-green-900 border-l-4 border-gray-300">File 2: {fileName2 || 'File 2'}</th>
                </tr>
                <tr className="bg-gray-50">
                  <th className="px-2 py-2 text-left font-medium text-sm min-w-24 border border-gray-600">Ref Des (F1)</th>
                  <th className="px-2 py-2 text-left font-medium text-sm min-w-16 border border-gray-600">Qty (F1)</th>
                  <th className="px-2 py-2 text-left font-medium text-sm min-w-24 border-l-4 border-gray-800 border-t border-b border-r border-gray-700">Ref Des (F2)</th>
                  <th className="px-2 py-2 text-left font-medium text-sm min-w-16 border border-gray-600">Qty (F2)</th>
                </tr>
              </thead>
              <tbody>
                {[...results.modified_parts].sort((a, b) => a.MPN.localeCompare(b.MPN)).map((part, index) => {
                  // Helpers to ignore formatting-only differences
                  const normalizeQty = (v: any) => {
                    if (v === undefined || v === null) return '';
                    const s = String(v).trim();
                    if (!s || ['na', 'n/a', 'none'].includes(s.toLowerCase())) return '';
                    const n = Number(s);
                    if (!isNaN(n)) {
                      if (Number.isInteger(n)) return String(n);
                      const t = String(n);
                      return t.includes('.') ? t.replace(/\.0+$/, '').replace(/(\..*?)0+$/, '$1').replace(/\.$/, '') : t;
                    }
                    return s;
                  };
                  const parseRefSet = (s: any) => {
                    if (s === undefined || s === null) return new Set<string>();
                    const text = String(s).toUpperCase();
                    if (!text || ['NA', 'N/A', 'NONE', 'NULL', 'UNDEFINED'].includes(text)) return new Set<string>();
                    return new Set(text.split(/[,;\s]+/).filter(x => x.length > 0));
                  };
                  const setsEqual = (a: Set<string>, b: Set<string>) => {
                    if (a.size !== b.size) return false;
                    const arr = Array.from(a);
                    for (let i = 0; i < arr.length; i++) {
                      if (!b.has(arr[i])) return false;
                    }
                    return true;
                  };

                  const qtyDiff = normalizeQty(part['File1 Qty']) !== normalizeQty(part['File2 Qty']);
                  const refDesDiff = !setsEqual(parseRefSet(part['File1 Ref Des']), parseRefSet(part['File2 Ref Des']));
                  
                  return (
                    <tr key={index}>
                      <td className="px-2 py-2 font-medium text-primary-600 text-sm break-all min-w-40 sticky left-0 z-10 bg-white border border-gray-700">{part.MPN}</td>
                      <td className={`px-2 py-2 text-sm break-all min-w-24 border border-gray-700 ${refDesDiff ? 'bg-yellow-300 font-semibold' : 'bg-blue-50'}`}>{part['File1 Ref Des']}</td>
                      <td className={`px-2 py-2 text-sm min-w-16 border border-gray-700 ${qtyDiff ? 'bg-yellow-300 font-semibold' : 'bg-blue-50'}`}>{part['File1 Qty']}</td>
                      <td className={`px-2 py-2 text-sm break-all min-w-24 border-l-4 border-gray-800 border-t border-b border-r border-gray-700 ${refDesDiff ? 'bg-yellow-300 font-semibold' : 'bg-green-50'}`}>{part['File2 Ref Des']}</td>
                      <td className={`px-2 py-2 text-sm min-w-16 border border-gray-700 ${qtyDiff ? 'bg-yellow-300 font-semibold' : 'bg-green-50'}`}>{part['File2 Qty']}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
        )}
      </CategorySection>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="text-center mb-8 print:hidden">
        <h1 className="text-4xl font-bold text-gray-900 mb-4 flex items-center justify-center gap-3">
          <FileSpreadsheet className="w-8 h-8 text-primary-600" />
          BOM Comparison Tool
        </h1>
        <p className="text-gray-600 text-lg">
          Compare Bill of Materials Excel files with intelligent column detection
        </p>
      </div>

      <div className="controls w-full flex items-center justify-between mb-6 gap-4 print:hidden">
        <div className="w-1/3" />
        <div className="flex-1 flex justify-center">
          <button onClick={clearFiles} className="btn-warning px-5">Start Fresh</button>
        </div>
        <div className="w-1/3 flex justify-end gap-3">
          <button onClick={handlePrint} className="btn-primary flex items-center gap-2 px-4">
            <Printer className="w-4 h-4" /> Print
          </button>
          <button onClick={exportToExcel} className="btn-primary flex items-center gap-2 px-4">
            <FileDown className="w-4 h-4" /> Export Excel
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 print:hidden">
        {/* File 1 Upload */}
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-primary-600" />
            File 1 (Original)
          </h3>
          <div
            {...getRootProps1()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
              isDragActive1
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps1()} />
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-700 mb-2">
              {isDragActive1 ? 'Drop the file here' : 'Drag & drop file here'}
            </p>
            <p className="text-gray-500">or click to browse</p>
            {file1 && (
              <div className="mt-4 p-3 bg-success-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <FileSpreadsheet className="w-5 h-5 text-success-600" />
                  <div>
                    <p className="font-medium text-success-800">{fileName1}</p>
                    <p className="text-sm text-success-600">
                      {(file1.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* File 2 Upload */}
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-primary-600" />
            File 2 (New Version)
          </h3>
          <div
            {...getRootProps2()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
              isDragActive2
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps2()} />
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-700 mb-2">
              {isDragActive2 ? 'Drop the file here' : 'Drag & drop file here'}
            </p>
            <p className="text-gray-500">or click to browse</p>
            {file2 && (
              <div className="mt-4 p-3 bg-success-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <FileSpreadsheet className="w-5 h-5 text-success-600" />
                  <div>
                    <p className="font-medium text-success-800">{fileName2}</p>
                    <p className="text-sm text-success-600">
                      {(file2.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Compare Button */}
      <div className="text-center mb-8">
        <button
          onClick={handleCompare}
          disabled={!file1 || !file2 || loading}
          className={`btn-primary flex items-center gap-2 mx-auto ${
            (!file1 || !file2 || loading) ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Comparing...
            </>
          ) : (
            <>
              <ArrowLeftRight className="w-5 h-5" /> 
              Compare Files
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-danger-50 border border-danger-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-danger-600" />
            <span className="text-danger-800 font-medium">{error}</span>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6 print-area">

          {/* Stats removed per client request */}

          {/* Search Bar */}
          <div className="relative mb-6 search-bar print:hidden">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search parts by MPN or Ref Des..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-5 w-5" />
              </button>
            )}
          </div>

          {/* Summary cards for new 3-category model: Delete, Add, Change */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 summary-cards">
            <CategoryCard
              title="Delete (in File 1 only)"
              count={filterResults(results, searchTerm).summary_stats.removed_parts_count}
              icon={XCircle}
              color="primary"
              onClick={() => toggleCategory('category-1')}
            />
            <CategoryCard
              title="Add (in File 2 only)"
              count={filterResults(results, searchTerm).summary_stats.new_parts_count}
              icon={CheckCircle}
              color="success"
              onClick={() => toggleCategory('category-2')}
            />
            <CategoryCard
              title="Change (data differences)"
              count={filterResults(results, searchTerm).summary_stats.modified_parts_count}
              icon={AlertCircle}
              color="warning"
              onClick={() => toggleCategory('category-3')}
            />
          </div>

          {/* Detailed Results */}
          {renderPartComparisonView(filterResults(results, searchTerm))}
        </div>
      )}
    </div>
  );
}

interface CategoryCardProps {
  title: string;
  count: number;
  icon: React.ComponentType<{ className?: string }>;
  color: 'success' | 'danger' | 'warning' | 'gray' | 'primary';
  onClick: () => void;
}

function CategoryCard({ title, count, icon: Icon, color, onClick }: CategoryCardProps) {
  const colorClasses = {
    success: 'bg-success-600 hover:bg-success-700',
    danger: 'bg-danger-600 hover:bg-danger-700',
    warning: 'bg-warning-600 hover:bg-warning-700',
    gray: 'bg-gray-600 hover:bg-gray-700',
    primary: 'bg-primary-600 hover:bg-primary-700',
  };

  return (
    <div
      className={`${colorClasses[color]} text-white p-4 rounded-lg cursor-pointer transition-colors duration-200`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5" />
          <span className="font-medium">{title}</span>
        </div>
        <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-bold">
          {count}
        </span>
      </div>
    </div>
  );
}

interface CategoryDetailsProps {
  results: ComparisonResults;
  expandedCategories: Set<string>;
  toggleCategory: (categoryId: string) => void;
  fileName1: string;
  fileName2: string;
}

function CategoryDetails({ results, expandedCategories, toggleCategory, fileName1, fileName2 }: CategoryDetailsProps) {
  const renderPartTable = (parts: BOMPart[] | ModifiedPart[], isModified = false) => (
    <div className="overflow-x-auto">
          <table className="w-full bg-white border-2 border-gray-600 rounded-lg text-sm min-w-full border-collapse">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-2 py-2 text-left font-medium text-sm min-w-40 border border-gray-600">MPN</th>
            <th className="px-2 py-2 text-left font-medium text-sm min-w-24 border border-gray-600">Ref Des</th>
            <th className="px-2 py-2 text-left font-medium text-sm min-w-16 border border-gray-600">Qty</th>
              {/* Description and Line removed */}
          </tr>
        </thead>
        <tbody>
          {parts.map((part, index) => (
            <tr key={index}>
              <td className="px-2 py-2 font-medium text-primary-600 text-sm break-all min-w-40 border border-gray-600">{part.MPN}</td>
              <td className="px-2 py-2 text-sm break-all min-w-24 border border-gray-600">{isModified ? (part as ModifiedPart)['File1 Ref Des'] : (part as BOMPart)['Ref Des/LOC']}</td>
              <td className="px-2 py-2 text-sm min-w-16 border border-gray-600">{isModified ? (part as ModifiedPart)['File1 Qty'] : (part as BOMPart).Qty}</td>
                {/* Description and Line removed */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderEmptyTable = (message: string) => (
    <div className="overflow-hidden">
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <XCircle className="w-5 h-5 text-red-600" />
          <h4 className="font-semibold text-red-600 text-sm">{message}</h4>
        </div>
        <table className="w-full bg-white border border-gray-300 rounded-lg text-sm border-collapse">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-2 py-2 text-left font-medium text-sm min-w-40 border border-gray-200">MPN</th>
              <th className="px-2 py-2 text-left font-medium text-sm min-w-24 border border-gray-200">Ref Des</th>
              <th className="px-2 py-2 text-left font-medium text-sm min-w-16 border border-gray-200">Qty</th>
              <th className="px-2 py-2 text-left font-medium text-sm min-w-48 border border-gray-200">Description</th>
              <th className="px-2 py-2 text-left font-medium text-sm min-w-16 border border-gray-200">Line</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={5} className="px-2 py-8 text-center text-gray-400 text-sm border border-gray-200">
                No data available
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );

  const FileHeader = ({ fileName, color, position }: { fileName: string; color: string; position: 'left' | 'right' }) => (
    <div className={`flex items-center gap-2 mb-3 ${position === 'right' ? 'justify-end' : ''}`}>
      <div className={`px-3 py-1 rounded-t-lg ${color} text-white text-sm font-medium`}>
        {fileName || `File ${position === 'left' ? '1' : '2'}`}
      </div>
    </div>
  );
}

interface CategorySectionProps {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  color: 'success' | 'danger' | 'warning' | 'gray' | 'primary';
  count: number;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function CategorySection({ id, title, icon: Icon, color, count, isExpanded, onToggle, children }: CategorySectionProps) {
  const colorClasses = {
    primary: 'bg-primary-600',
    success: 'bg-success-600', 
    danger: 'bg-danger-600',
    warning: 'bg-warning-600',
    gray: 'bg-gray-600'
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div
        className={`${colorClasses[color]} text-white p-4 cursor-pointer flex items-center justify-between`}
        onClick={onToggle}
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5" />
          <h3 className="font-semibold">{title}</h3>
          <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-medium">
            {count} items
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5" />
        ) : (
          <ChevronDown className="w-5 h-5" />
        )}
      </div>
      {isExpanded && (
        <div className="p-4 bg-gray-50">
          {children}
        </div>
      )}
    </div>
  );
}
