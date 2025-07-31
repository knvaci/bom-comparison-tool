from flask import Flask, request, render_template_string, redirect, url_for, session, send_file
import tempfile
import os
from excel_tool import compare_boms
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'

HTML_FORM = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>BOM Side-by-Side Comparison Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {
            background: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow-x: hidden;
        }
        .main-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin: 20px auto;
            max-width: 1400px;
            padding: 40px;
            overflow-x: hidden;
        }
        @media (max-width: 768px) {
            .main-container {
                margin: 10px auto;
                padding: 20px;
                border-radius: 15px;
            }
        }
        .upload-area {
            border: 3px dashed #6c757d;
            border-radius: 15px;
            padding: 40px 20px;
            text-align: center;
            transition: all 0.3s ease;
            background: rgba(108, 117, 125, 0.05);
            cursor: pointer;
        }
        .upload-area:hover {
            border-color: #495057;
            background: rgba(73, 80, 87, 0.1);
            transform: translateY(-2px);
        }
        .upload-area.dragover {
            border-color: #28a745;
            background: rgba(40, 167, 69, 0.1);
            transform: scale(1.02);
        }
        .file-preview {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #28a745;
        }
        .compare-btn {
            background: #6c757d;
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .compare-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(108, 117, 125, 0.3);
        }
        .results-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin: 20px 0;
            overflow: hidden;
        }
        .results-header {
            background: #6c757d;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .stat-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #6c757d;
            transition: all 0.3s ease;
        }
        .stat-card.clickable {
            cursor: pointer;
        }
        .stat-card.clickable:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            background: white;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #6c757d;
        }
        .upload-box {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            padding: 35px;
            margin: 25px 0;
        }
        .file-info {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 10px 0;
        }
        .file-icon {
            font-size: 2rem;
            color: #6c757d;
        }
        .table-responsive {
            overflow-x: auto;
            max-width: 100%;
        }
        .table {
            font-size: 0.9rem;
            min-width: 600px;
        }
        .table th, .table td {
            padding: 8px 6px;
            word-wrap: break-word;
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        @media (max-width: 768px) {
            .table {
                font-size: 0.8rem;
                min-width: 500px;
            }
            .table th, .table td {
                padding: 6px 4px;
                max-width: 120px;
            }
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .side-by-side-container {
            display: flex;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .file-table {
            flex: 1;
            min-width: 300px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        @media (max-width: 768px) {
            .side-by-side-container {
                flex-direction: column;
            }
            .file-table {
                min-width: 100%;
            }
        }
        .file-header {
            padding: 15px;
            text-align: center;
            font-weight: bold;
            color: white;
        }
        .file1-header {
            background: #007bff;
        }
        .file2-header {
            background: #28a745;
        }
        .missing-header {
            background: #dc3545;
        }
        .table th {
            background: #f8f9fa;
            border-top: none;
            font-weight: 600;
        }
        .table td {
            vertical-align: middle;
        }
        .mpn-highlight {
            background-color: #e3f2fd;
            font-weight: bold;
        }
        
        /* Category Sections */
        .category-section {
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .category-header {
            padding: 20px;
            color: white;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .category-header:hover {
            opacity: 0.9;
        }
        
        .category-header h4 {
            margin: 0;
            font-weight: 600;
        }

        .category-total {
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .category-content {
            background: white;
            padding: 20px;
            display: block;
        }
        
        .category-content.collapsed {
            display: none;
        }
        
        .category-summary {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #6c757d;
        }
        
        .category-summary h5 {
            margin: 0;
            color: #495057;
            font-weight: 600;
        }
        
        .category-summary .total-count {
            font-size: 1.5rem;
            font-weight: bold;
            color: #6c757d;
        }
        
        /* Category 1 - All Matches (Green) */
        .category-1 {
            background: #28a745;
        }
        
        /* Category 2 - File Left Only (Blue) */
        .category-2 {
            background: #007bff;
        }
        
        /* Category 3 - File Right Only (Green) */
        .category-3 {
            background: #28a745;
        }
        
                 /* Category 4 - Data Differences (Yellow) */
         .category-4 {
             background: #ffc107;
             color: #212529;
         }
         
         /* Category 5 - Unrecognized (Gray) */
         .category-5 {
             background: #6c757d;
         }
        
        .collapse-icon {
            font-size: 1.2rem;
            transition: transform 0.3s ease;
        }
        
        .collapse-icon.rotated {
            transform: rotate(180deg);
        }
    </style>
</head>
<body>
<div class="container-fluid px-0">
    <div class="main-container">
    <h1 class="text-center mb-4">
      <i class="bi bi-gear-wide-connected"></i>
            BOM Side-by-Side Comparison Tool
    </h1>
    
    <div class="text-center mb-4">
      <form method="post" action="/clear_session" style="display: inline;">
        <button type="submit" class="btn btn-warning btn-md">
          <i class="bi bi-arrow-clockwise"></i> Start Fresh
        </button>
      </form>
    </div>

    <div class="row">
        <div class="col-xl-6 col-lg-6">
          <div class="upload-box">
            <h4><i class="bi bi-file-earmark-spreadsheet"></i> File 1 (Original)</h4>
            <div class="upload-area" id="uploadArea1">
              <i class="bi bi-cloud-upload" style="font-size: 3rem; color: #6c757d;"></i>
              <h5 class="mt-3">Drag & Drop File Here</h5>
              <p class="text-muted">or click to browse</p>
              <input type="file" id="file1" name="file1" accept=".xlsx,.xls" style="display: none;">
            </div>
            <div id="filePreview1">
              {% if file1 %}
                <div class="file-preview">
                  <div class="file-info">
                    <i class="bi bi-file-earmark-spreadsheet file-icon"></i>
                    <div>
                      <strong>{{ file1.filename }}</strong><br>
                      <small class="text-muted">Uploaded</small>
                    </div>
                  </div>
                </div>
              {% endif %}
            </div>
          </div>
        </div>
        <div class="col-xl-6 col-lg-6">
          <div class="upload-box">
            <h4><i class="bi bi-file-earmark-spreadsheet"></i> File 2 (New Version)</h4>
            <div class="upload-area" id="uploadArea2">
              <i class="bi bi-cloud-upload" style="font-size: 3rem; color: #6c757d;"></i>
              <h5 class="mt-3">Drag & Drop File Here</h5>
              <p class="text-muted">or click to browse</p>
              <input type="file" id="file2" name="file2" accept=".xlsx,.xls" style="display: none;">
            </div>
            <div id="filePreview2">
              {% if file2 %}
                <div class="file-preview">
                  <div class="file-info">
                    <i class="bi bi-file-earmark-spreadsheet file-icon"></i>
                    <div>
                      <strong>{{ file2.filename }}</strong><br>
                      <small class="text-muted">Uploaded</small>
                    </div>
                  </div>
                </div>
              {% endif %}
            </div>
          </div>
        </div>
    </div>

    <div class="text-center mt-4" id="compareSection" style="display: none;">
      <button type="button" class="compare-btn" onclick="startComparison()">
        <i class="bi bi-arrow-left-right"></i> Compare Files
      </button>
    </div>

    {% if error %}
        <div class="alert alert-danger mt-4">
            <h5><i class="bi bi-exclamation-triangle"></i> Error:</h5>
      <p>{{ error }}</p>
    </div>
    {% endif %}

    {% if results %}
    <div class="results-card">
      <div class="results-header">
                <h3><i class="bi bi-clipboard-data"></i> Side-by-Side Comparison Results</h3>
            </div>
            <div class="category-summary" style="margin: 20px; background: #e3f2fd; border-left-color: #2196f3;">
                <h5><i class="bi bi-calculator text-info"></i> Total Parts Summary</h5>
                <div class="total-count">
                    <strong>File 1:</strong> {{ results.summary_stats.total_parts_file1 }} parts | 
                    <strong>File 2:</strong> {{ results.summary_stats.total_parts_file2 }} parts | 
                    <strong>Combined Total:</strong> {{ results.summary_stats.total_parts_file1 + results.summary_stats.total_parts_file2 }} parts
                </div>
                                 <div style="margin-top: 10px; font-size: 0.9rem; color: #666;">
                     <strong>Breakdown:</strong> 
                     {{ results.summary_stats.unchanged_parts_count }} matches + 
                     {{ results.summary_stats.removed_parts_count }} missing + 
                     {{ results.summary_stats.new_parts_count }} added + 
                     {{ results.summary_stats.modified_parts_count }} differences + 
                     {{ results.summary_stats.unrecognized_parts_count }} unrecognized
                 </div>
      </div>
      <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number text-info">{{ results.summary_stats.total_parts_file1 + results.summary_stats.total_parts_file2 }}</div>
          <div>Total Parts</div>
                    <small class="text-muted">File 1: {{ results.summary_stats.total_parts_file1 }} | File 2: {{ results.summary_stats.total_parts_file2 }}</small>
        </div>
                <div class="stat-card clickable" onclick="toggleCategory('category-1')">
                    <div class="stat-number text-success">{{ results.summary_stats.unchanged_parts_count }}</div>
                    <div>Category 1: All Matches</div>
                    <small class="text-muted">Click to toggle</small>
        </div>
                <div class="stat-card clickable" onclick="toggleCategory('category-2')">
                    <div class="stat-number text-primary">{{ results.summary_stats.removed_parts_count }}</div>
                    <div>Category 2: File Left Only</div>
                    <small class="text-muted">Click to toggle</small>
        </div>
                <div class="stat-card clickable" onclick="toggleCategory('category-3')">
                    <div class="stat-number text-success">{{ results.summary_stats.new_parts_count }}</div>
                    <div>Category 3: File Right Only</div>
                    <small class="text-muted">Click to toggle</small>
                </div>
                <div class="stat-card clickable" onclick="toggleCategory('category-4')">
          <div class="stat-number text-warning">{{ results.summary_stats.modified_parts_count }}</div>
                    <div>Category 4: Data Differences</div>
                    <small class="text-muted">Click to toggle</small>
        </div>
                <div class="stat-card clickable" onclick="toggleCategory('category-5')">
                    <div class="stat-number text-secondary">{{ results.summary_stats.unrecognized_parts_count }}</div>
                    <div>Category 5: Unrecognized</div>
                    <small class="text-muted">Click to toggle</small>
        </div>
      </div>
      
            <!-- Category 1: All Matches (Green) -->
            {% if results.unchanged_parts %}
            <div class="category-section" id="category-1">
                <div class="category-header category-1" onclick="toggleCategory('category-1')">
                    <h4><i class="bi bi-check-circle"></i> Category 1: All Matches</h4>
                    <div class="category-total">{{ results.summary_stats.unchanged_parts_count }} items</div>
                    <i class="bi bi-chevron-down collapse-icon" id="icon-category-1"></i>
              </div>
                <div class="category-content" id="content-category-1">
                    <div class="category-summary">
                        <h5><i class="bi bi-check-circle text-success"></i> Total Matches Found</h5>
                        <div class="total-count">{{ results.summary_stats.unchanged_parts_count }} parts with identical data in both files</div>
              </div>
                    <div class="side-by-side-container">
                        <div class="file-table">
                            <div class="file-header file1-header">
                                <i class="bi bi-file-earmark-text"></i> {{ file1.filename }}
            </div>
                            <div class="table-responsive">
                                <table class="table table-striped mb-0">
                                    <thead>
                                        <tr>
                                            <th>MPN</th>
                                            <th>Ref Des/LOC</th>
                                            <th>Qty</th>
                                            <th>Description</th>
                                            <th>Line #</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for part in results.unchanged_parts %}
                                        <tr>
                                            <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                                            <td>{{ part['Ref Des/LOC'] }}</td>
                                            <td>{{ part.Qty }}</td>
                                            <td>{{ part.Description }}</td>
                                            <td><span class="badge bg-info">{{ part['Line Number'] }}</span></td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
          </div>
        </div>
                        <div class="file-table">
                            <div class="file-header file2-header">
                                <i class="bi bi-file-earmark-text"></i> {{ file2.filename }}
      </div>
              <div class="table-responsive">
                                <table class="table table-striped mb-0">
                  <thead>
                    <tr>
                      <th>MPN</th>
                      <th>Ref Des/LOC</th>
                      <th>Qty</th>
                      <th>Description</th>
                      <th>Line #</th>
                    </tr>
                  </thead>
                  <tbody>
                                        {% for part in results.unchanged_parts %}
                                        <tr>
                                            <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                      <td>{{ part['Ref Des/LOC'] }}</td>
                      <td>{{ part.Qty }}</td>
                      <td>{{ part.Description }}</td>
                      <td><span class="badge bg-info">{{ part['Line Number'] }}</span></td>
                    </tr>
                    {% endfor %}
                  </tbody>
                </table>
                            </div>
                        </div>
              </div>
            </div>
          </div>
          {% endif %}

            <!-- Category 2: File Left Only (Blue) -->
          {% if results.removed_parts %}
            <div class="category-section" id="category-2">
                <div class="category-header category-2" onclick="toggleCategory('category-2')">
                    <h4><i class="bi bi-dash-circle"></i> Category 2: File Left Only</h4>
                    <div class="category-total">{{ results.summary_stats.removed_parts_count }} items</div>
                    <i class="bi bi-chevron-down collapse-icon" id="icon-category-2"></i>
            </div>
                <div class="category-content" id="content-category-2">
                    <div class="category-summary">
                        <h5><i class="bi bi-dash-circle text-primary"></i> Total Missing Parts</h5>
                        <div class="total-count">{{ results.summary_stats.removed_parts_count }} parts found in File 1 but missing from File 2</div>
                    </div>
                                         <div class="side-by-side-container">
                         <div class="file-table">
                             <div class="file-header file1-header">
                                 <i class="bi bi-file-earmark-text"></i> {{ file1.filename }}
                             </div>
              <div class="table-responsive">
                                 <table class="table table-striped mb-0">
                  <thead>
                    <tr>
                      <th>MPN</th>
                      <th>Ref Des/LOC</th>
                      <th>Qty</th>
                      <th>Description</th>
                      <th>Line #</th>
                    </tr>
                  </thead>
                  <tbody>
                    {% for part in results.removed_parts %}
                                         <tr>
                                             <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                                             <td>{{ part['Ref Des/LOC'] }}</td>
                                             <td>{{ part.Qty }}</td>
                                             <td>{{ part.Description }}</td>
                                             <td><span class="badge bg-info">{{ part['Line Number'] }}</span></td>
                                         </tr>
                          {% endfor %}
                                     </tbody>
                                 </table>
                             </div>
                         </div>
                         <div class="file-table">
                             <div class="file-header missing-header">
                                 <i class="bi bi-x-circle"></i> Not Found in File 2
                             </div>
                             <div class="table-responsive">
                                 <table class="table table-striped mb-0">
                                     <thead>
                                         <tr>
                                             <th>MPN</th>
                                             <th>Ref Des/LOC</th>
                                             <th>Qty</th>
                                             <th>Description</th>
                                             <th>Status</th>
                                         </tr>
                                     </thead>
                                     <tbody>
                                         <!-- Empty table - no data rows -->
                                     </tbody>
                                 </table>
                             </div>
                         </div>
                     </div>
                </div>
            </div>
            {% endif %}

            <!-- Category 3: File Right Only (Green) -->
            {% if results.new_parts %}
            <div class="category-section" id="category-3">
                <div class="category-header category-3" onclick="toggleCategory('category-3')">
                    <h4><i class="bi bi-plus-circle"></i> Category 3: File Right Only</h4>
                    <div class="category-total">{{ results.summary_stats.new_parts_count }} items</div>
                    <i class="bi bi-chevron-down collapse-icon" id="icon-category-3"></i>
                </div>
                <div class="category-content" id="content-category-3">
                    <div class="category-summary">
                        <h5><i class="bi bi-plus-circle text-success"></i> Total Added Parts</h5>
                        <div class="total-count">{{ results.summary_stats.new_parts_count }} parts found in File 2 but missing from File 1</div>
                    </div>
                                         <div class="side-by-side-container">
                         <div class="file-table">
                             <div class="file-header missing-header">
                                 <i class="bi bi-x-circle"></i> Not Found in File 1
                             </div>
                             <div class="table-responsive">
                                 <table class="table table-striped mb-0">
                                     <thead>
                                         <tr>
                                             <th>MPN</th>
                                             <th>Ref Des/LOC</th>
                                             <th>Qty</th>
                                             <th>Description</th>
                                             <th>Status</th>
                                         </tr>
                                     </thead>
                                     <tbody>
                                         <!-- Empty table - no data rows -->
                                     </tbody>
                                 </table>
                             </div>
                         </div>
                         <div class="file-table">
                             <div class="file-header file2-header">
                                 <i class="bi bi-file-earmark-text"></i> {{ file2.filename }}
                             </div>
                             <div class="table-responsive">
                                 <table class="table table-striped mb-0">
                                     <thead>
                                         <tr>
                                             <th>MPN</th>
                                             <th>Ref Des/LOC</th>
                                             <th>Qty</th>
                                             <th>Description</th>
                                             <th>Line #</th>
                                         </tr>
                                     </thead>
                                     <tbody>
                                         {% for part in results.new_parts %}
                                         <tr>
                                             <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                      <td>{{ part['Ref Des/LOC'] }}</td>
                      <td>{{ part.Qty }}</td>
                      <td>{{ part.Description }}</td>
                      <td><span class="badge bg-info">{{ part['Line Number'] }}</span></td>
                    </tr>
                    {% endfor %}
                  </tbody>
                </table>
                             </div>
                         </div>
              </div>
            </div>
          </div>
          {% endif %}

            <!-- Category 4: Data Differences (Yellow) -->
          {% if results.modified_parts %}
            <div class="category-section" id="category-4">
                <div class="category-header category-4" onclick="toggleCategory('category-4')">
                    <h4><i class="bi bi-arrow-left-right"></i> Category 4: Data Differences</h4>
                    <div class="category-total">{{ results.summary_stats.modified_parts_count }} items</div>
                    <i class="bi bi-chevron-down collapse-icon" id="icon-category-4"></i>
            </div>
                <div class="category-content" id="content-category-4">
                    <div class="category-summary">
                        <h5><i class="bi bi-arrow-left-right text-warning"></i> Total Data Differences</h5>
                        <div class="total-count">{{ results.summary_stats.modified_parts_count }} parts with different data between files</div>
                    </div>
                    <div class="side-by-side-container">
                        <div class="file-table">
                            <div class="file-header file1-header">
                                <i class="bi bi-file-earmark-text"></i> {{ file1.filename }}
                            </div>
                  <div class="table-responsive">
                                <table class="table table-striped mb-0">
                      <thead>
                        <tr>
                          <th>MPN</th>
                          <th>Ref Des/LOC</th>
                          <th>Qty</th>
                          <th>Description</th>
                          <th>Line #</th>
                        </tr>
                      </thead>
                      <tbody>
                        {% for part in results.modified_parts %}
                                        <tr>
                                            <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                          <td>{{ part['Ref Des/LOC'] }}</td>
                          <td>{{ part['File1 Qty'] }}</td>
                          <td>{{ part['File1 Description'] }}</td>
                          <td><span class="badge bg-info">{{ part['File1 Line'] }}</span></td>
                        </tr>
                        {% endfor %}
                      </tbody>
                    </table>
                  </div>
                </div>
                        <div class="file-table">
                            <div class="file-header file2-header">
                                <i class="bi bi-file-earmark-text"></i> {{ file2.filename }}
                            </div>
                  <div class="table-responsive">
                                <table class="table table-striped mb-0">
                      <thead>
                        <tr>
                          <th>MPN</th>
                          <th>Ref Des/LOC</th>
                          <th>Qty</th>
                          <th>Description</th>
                          <th>Line #</th>
                        </tr>
                      </thead>
                      <tbody>
                        {% for part in results.modified_parts %}
                                        <tr>
                                            <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                          <td>{{ part['Ref Des/LOC'] }}</td>
                          <td>{{ part['File2 Qty'] }}</td>
                          <td>{{ part['File2 Description'] }}</td>
                          <td><span class="badge bg-info">{{ part['File2 Line'] }}</span></td>
                        </tr>
                        {% endfor %}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
          {% endif %}

             <!-- Category 5: Unrecognized (Gray) -->
             {% if results.unrecognized_parts %}
             <div class="category-section" id="category-5">
                 <div class="category-header category-5" onclick="toggleCategory('category-5')">
                     <h4><i class="bi bi-question-circle"></i> Category 5: Unrecognized</h4>
                     <div class="category-total">{{ results.summary_stats.unrecognized_parts_count }} items</div>
                     <i class="bi bi-chevron-down collapse-icon" id="icon-category-5"></i>
            </div>
                 <div class="category-content" id="content-category-5">
                     <div class="category-summary">
                         <h5><i class="bi bi-question-circle text-secondary"></i> Total Unrecognized Parts</h5>
                         <div class="total-count">{{ results.summary_stats.unrecognized_parts_count }} parts that could not be properly categorized</div>
                     </div>
                     <div class="side-by-side-container">
                         <div class="file-table">
                             <div class="file-header file1-header">
                                 <i class="bi bi-file-earmark-text"></i> {{ file1.filename }}
                             </div>
              <div class="table-responsive">
                                 <table class="table table-striped mb-0">
                  <thead>
                    <tr>
                      <th>MPN</th>
                      <th>Ref Des/LOC</th>
                      <th>Qty</th>
                      <th>Description</th>
                      <th>Line #</th>
                    </tr>
                  </thead>
                  <tbody>
                                         {% for part in results.unrecognized_parts %}
                                         <tr>
                                             <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                      <td>{{ part['Ref Des/LOC'] }}</td>
                      <td>{{ part.Qty }}</td>
                      <td>{{ part.Description }}</td>
                      <td><span class="badge bg-info">{{ part['Line Number'] }}</span></td>
                    </tr>
                    {% endfor %}
                  </tbody>
                </table>
              </div>
            </div>
                         <div class="file-table">
                             <div class="file-header file2-header">
                                 <i class="bi bi-file-earmark-text"></i> {{ file2.filename }}
          </div>
                             <div class="table-responsive">
                                 <table class="table table-striped mb-0">
                                     <thead>
                                         <tr>
                                             <th>MPN</th>
                                             <th>Ref Des/LOC</th>
                                             <th>Qty</th>
                                             <th>Description</th>
                                             <th>Line #</th>
                                         </tr>
                                     </thead>
                                     <tbody>
                                         {% for part in results.unrecognized_parts %}
                                         <tr>
                                             <td class="mpn-highlight"><strong>{{ part.MPN }}</strong></td>
                                             <td>{{ part['Ref Des/LOC'] }}</td>
                                             <td>{{ part.Qty }}</td>
                                             <td>{{ part.Description }}</td>
                                             <td><span class="badge bg-info">{{ part['Line Number'] }}</span></td>
                                         </tr>
                                         {% endfor %}
                                     </tbody>
                                 </table>
        </div>
      </div>
                     </div>
      </div>
             </div>
             {% endif %}
    </div>
    {% endif %}
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    // Drag and Drop functionality
    function setupDragAndDrop(areaId, fileInputId, previewId) {
        const area = document.getElementById(areaId);
        const fileInput = document.getElementById(fileInputId);
        const preview = document.getElementById(previewId);

        area.addEventListener('click', () => fileInput.click());
        
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(fileInput, preview);
            }
        });
        
        fileInput.addEventListener('change', () => {
            handleFileSelect(fileInput, preview);
        });
    }

    function handleFileSelect(fileInput, preview) {
        const file = fileInput.files[0];
        if (file) {
            const fileInfo = `
                <div class="file-preview">
                    <div class="file-info">
                        <i class="bi bi-file-earmark-spreadsheet file-icon"></i>
                        <div>
                            <strong>${file.name}</strong><br>
                            <small class="text-muted">${(file.size / 1024).toFixed(1)} KB</small>
                        </div>
                    </div>
                </div>
            `;
            preview.innerHTML = fileInfo;
            checkBothFilesUploaded();
        }
    }

    function checkBothFilesUploaded() {
        const file1 = document.getElementById('file1').files[0];
        const file2 = document.getElementById('file2').files[0];
        
        if (file1 && file2) {
            document.getElementById('compareSection').style.display = 'block';
        }
    }

    function startComparison() {
        const file1 = document.getElementById('file1').files[0];
        const file2 = document.getElementById('file2').files[0];
        
        if (!file1 || !file2) {
            alert('Please select both files first.');
            return;
        }
        
        const formData = new FormData();
        formData.append('file1', file1);
        formData.append('file2', file2);
        
        fetch('/compare', {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                response.text().then(text => {
                    console.error('Server error:', text);
                    alert('Comparison failed. Please check the console for details.');
                });
            }
        }).catch(error => {
            console.error('Error during comparison:', error);
            alert('Error during comparison. Please check the console for details.');
        });
    }

    // Initialize drag and drop
    setupDragAndDrop('uploadArea1', 'file1', 'filePreview1');
    setupDragAndDrop('uploadArea2', 'file2', 'filePreview2');

    // Category toggle functionality
    function toggleCategory(categoryId) {
        const content = document.getElementById(`content-${categoryId}`);
        const icon = document.getElementById(`icon-${categoryId}`);
        
        if (content.classList.contains('collapsed')) {
            content.classList.remove('collapsed');
            icon.classList.remove('rotated');
          } else {
            content.classList.add('collapsed');
            icon.classList.add('rotated');
        }
    }
    
    // Show all categories by default when results are present
    document.addEventListener('DOMContentLoaded', function() {
        const resultsCard = document.querySelector('.results-card');
        if (resultsCard) {
            // All categories are expanded by default
            console.log('Results found, all categories expanded');
        }
    });
</script>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def index():
    file1 = session.get('file1')
    file2 = session.get('file2')
    error = session.get('error')
    
    # Load results from file if available
    results = None
    results_file = session.get('results_file')
    if results_file and os.path.exists(results_file):
        try:
            import json
            with open(results_file, 'r') as f:
                results = json.load(f)
        except Exception as e:
            print(f"Error loading results: {e}")
            results = None
    
    return render_template_string(HTML_FORM, file1=file1, file2=file2, results=results, error=error)

@app.route("/compare", methods=["POST"])
def compare():
    file1 = request.files.get('file1')
    file2 = request.files.get('file2')
    
    if file1 and file2:
        try:
            # Save uploaded files
            tmp1 = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file1.filename)[1], dir='.')
            file1.save(tmp1.name)
            tmp1.close()
            
            tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file2.filename)[1], dir='.')
            file2.save(tmp2.name)
            tmp2.close()
            
            # Store file info in session (minimal data)
            session['file1'] = {'filename': file1.filename, 'path': tmp1.name}
            session['file2'] = {'filename': file2.filename, 'path': tmp2.name}
            
            # Compare files
            print(f"Starting comparison of {file1.filename} and {file2.filename}")
            results = compare_boms(tmp1.name, tmp2.name)
            print(f"Comparison completed successfully")
            
            # Save results to temporary file instead of session
            import json
            import uuid
            results_id = str(uuid.uuid4())
            results_file = f"results_{results_id}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f)
            
            # Store only the results file path in session
            session['results_file'] = results_file
            session['error'] = None
            
        except Exception as e:
            import traceback
            error_details = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(f"COMPARISON ERROR: {error_details}")
            session['error'] = f"Comparison failed: {str(e)}"
            session['results'] = None
    
        return redirect(url_for('index'))
                
@app.route("/clear_session", methods=["POST"])
def clear_session():
    # Clean up results file if it exists
    results_file = session.get('results_file')
    if results_file and os.path.exists(results_file):
        try:
            os.remove(results_file)
        except Exception as e:
            print(f"Error removing results file: {e}")
    
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
    