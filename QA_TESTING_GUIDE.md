# 🧪 QA Testing Guide for BOM Comparison Tool

## ✅ **Setup Complete!**

Your environment is now ready for QA testing:
- ✅ **PostgreSQL Database**: Created and configured
- ✅ **All Dependencies**: Installed and working
- ✅ **Test Files**: Organized in `test_files/` directory
- ✅ **Flask App**: Running on `http://localhost:5000`

---

## 📋 **QA Testing Checklist**

### **1. Basic Functionality Tests**

#### **File Upload Testing**
- [ ] **Drag & Drop**: Test dragging files from `test_files/` to upload areas
- [ ] **File Selection**: Test clicking "Choose Files" button
- [ ] **File Validation**: Test uploading non-Excel files (should show error)
- [ ] **File Size**: Test uploading files larger than 16MB (should show error)

#### **Column Detection Testing**
- [ ] **MPN Detection**: Verify all file formats detect MPN columns correctly
- [ ] **Quantity Detection**: Verify Qty columns are detected
- [ ] **Ref Des Detection**: Verify Ref Des/LOC columns are detected
- [ ] **Description Detection**: Verify Description columns are detected

### **2. Comparison Logic Tests**

#### **Category Testing**
- [ ] **Category 1 (Green)**: Parts present in both files
- [ ] **Category 2 (Blue)**: Parts only in file 1
- [ ] **Category 3 (Green)**: Parts only in file 2
- [ ] **Category 4 (Yellow)**: Parts with data differences
- [ ] **Category 5 (Gray)**: Unrecognized parts

#### **Data Accuracy Testing**
- [ ] **MPN Formatting**: Verify MPN numbers display correctly (no ".0" suffixes)
- [ ] **Quantity Comparison**: Verify quantities are compared correctly
- [ ] **Description Comparison**: Verify descriptions are compared correctly
- [ ] **Line Numbers**: Verify line numbers are calculated correctly

### **3. UI/UX Testing**

#### **Responsive Design**
- [ ] **Desktop**: Test on desktop browser
- [ ] **Mobile**: Test on mobile browser
- [ ] **Tablet**: Test on tablet browser
- [ ] **Different Browsers**: Test on Chrome, Firefox, Edge

#### **Interactive Features**
- [ ] **Collapsible Sections**: Test expanding/collapsing each category
- [ ] **Side-by-Side Layout**: Verify tables display correctly
- [ ] **Empty Columns**: Verify missing data shows red empty columns
- [ ] **Totals Display**: Verify category totals are shown correctly

### **4. File Format Testing**

#### **Test All File Combinations**
Use these file pairs for comprehensive testing:

**Pair 1:**
- `8520L MEDSHIFT MS MOAG REV4 BOM QUOTE 03-01-23.xlsx`
- `Bill of Materials-MS_MOAG-4(updated).xlsx`

**Pair 2:**
- `COPY 6588L HARSCO 4028626 BOM FOR ASSEMBLY.xlsx`
- `HARSCO 4028626 Rev C BOM.xlsx`

**Pair 3:**
- `COPY Schneider NVE87475 BOM QUOTE.xlsx`
- `NVE87475 Power Board BOM for American Circuits 1_27_17.xlsx`

**Pair 4:**
- `HARSCO 4028741 BOM_ACI.xlsx`
- `HD32R2 parts list module 11_15_11.xls`

**Pair 5:**
- `edited 301-0679-01 (new 06-23-25).xlsx`
- `320-0037C_01 DO NOT USE.xlsx`

### **5. Error Handling Testing**

#### **Edge Cases**
- [ ] **Empty Files**: Test uploading empty Excel files
- [ ] **Corrupted Files**: Test uploading corrupted files
- [ ] **Missing Columns**: Test files with missing MPN columns
- [ ] **Large Files**: Test files with many rows/columns
- [ ] **Special Characters**: Test files with special characters in data

### **6. Performance Testing**

#### **Speed Tests**
- [ ] **Small Files**: Test with files < 100 rows
- [ ] **Medium Files**: Test with files 100-1000 rows
- [ ] **Large Files**: Test with files > 1000 rows
- [ ] **Memory Usage**: Monitor memory usage during comparisons

---

## 🚀 **How to Run QA Tests**

### **1. Automated Testing**
```bash
python scripts/run_tests.py
```

### **2. Manual Testing Steps**

1. **Start the Application**:
   ```bash
   python run.py
   ```

2. **Open Browser**: Go to `http://localhost:5000`

3. **Test Each File Pair**: Upload files and verify results

4. **Document Issues**: Note any problems or unexpected behavior

---

## 📊 **Expected Results**

### **File Pair 1** (8520L vs Bill of Materials):
- **Category 1**: Should show common parts
- **Category 2**: Should show parts only in 8520L file
- **Category 3**: Should show parts only in Bill of Materials file
- **Category 4**: Should show parts with differences

### **File Pair 2** (COPY 6588L vs HARSCO 4028626):
- **Category 1**: Should show common parts
- **Category 2**: Should show parts only in COPY file
- **Category 3**: Should show parts only in HARSCO file
- **Category 4**: Should show parts with differences

---

## 🐛 **Common Issues to Watch For**

1. **MPN Formatting**: Numbers showing as "145.0" instead of "145"
2. **Missing Categories**: Categories showing 0 when they should have data
3. **Column Detection**: Wrong columns being selected
4. **Responsive Issues**: Tables not fitting on mobile screens
5. **Performance**: Slow loading with large files

---

## 📝 **Reporting Issues**

When you find issues, document:
1. **File Names**: Which files were being compared
2. **Expected Result**: What you expected to see
3. **Actual Result**: What you actually saw
4. **Steps to Reproduce**: How to recreate the issue
5. **Browser/Device**: What you were using

---

## ✅ **Success Criteria**

QA testing is successful when:
- ✅ All file combinations work correctly
- ✅ All 5 categories display properly
- ✅ UI is responsive on all devices
- ✅ No data formatting issues
- ✅ Performance is acceptable
- ✅ Error handling works correctly

---

**Ready to start testing! 🎉** 