# DataForge User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [First Steps](#first-steps)
4. [Features Overview](#features-overview)
5. [Detailed Workflows](#detailed-workflows)
6. [Tips & Tricks](#tips--tricks)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

Welcome to DataForge! This guide will walk you through all the features and best practices for using the application efficiently.

### System Requirements

- **Operating System**: Windows 7 or later
- **RAM**: Minimum 2GB (4GB+ recommended for large datasets)
- **Storage**: 500MB free disk space
- **Display**: 1024x768 minimum resolution (1920x1080 recommended)

### First Login

1. Launch the DataForge application
2. Enter your credentials on the login screen
3. Click **Login** to access the main workspace
4. Your session will be securely authenticated

---

## Installation

### Option 1: Using the Executable (Recommended)

1. Download the `dataForge.exe` file
2. Double-click to launch the installer or run directly
3. No additional installation required
4. Launch from your Start Menu or desktop shortcut

### Option 2: Running from Source

```bash
# Clone or download the project
cd DATA\ FORGE

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## First Steps

### Step 1: Load Your Data

1. Click **Load File** in the main toolbar
2. Select a CSV file from your computer
3. DataForge will automatically detect:
   - Data types for each column
   - Missing values
   - Basic statistics

4. Review the preview and confirm loading

*Note: Large files (>100MB) are automatically loaded in chunks for optimal performance*

### Step 2: Explore the Data

The main window displays:

- **Left Panel**: Dataset switcher and operations menu
- **Center Panel**: Data table with sorted/filtered results
- **Right Panel**: Column information and statistics
- **Toolbar**: Quick access to main operations

### Step 3: Perform Your First Operation

Try one of these simple operations:

- **Filter**: Select Tools > Filter Data to find specific records
- **Sort**: Right-click column header to sort ascending/descending
- **Summary**: Click Tools > Data Summary for quick statistics

---

## Features Overview

### 1. Data Loading & Management

**Load Multiple Files**
- Open File > Open Dataset
- Load multiple CSV files simultaneously
- Each dataset appears in the left sidebar
- Switch between datasets by clicking on them

**Dataset Operations**
- Rename datasets for better organization
- Remove datasets no longer needed
- View dataset statistics and metadata

### 2. Data Cleaning

The Data Cleaning tool helps prepare your data for analysis:

**Access**: Tools > Clean Data

**Available Options**:
- **Remove Duplicates**: Eliminate duplicate rows based on selected columns
- **Handle Missing Values**:
  - Fill with mean (numerical columns)
  - Fill with median (numerical columns)
  - Fill with mode (categorical columns)
  - Delete rows with missing values
  - Forward fill or back fill (for time series)
- **Format Standardization**: Convert data types and standardize formats

**Best Practice**: Always review cleaned data before saving

### 3. Data Filtering

Create complex filter conditions to focus on subsets of your data:

**Access**: Tools > Filter Data

**Filter Types**:
- **Exact Match**: Column = "Value"
- **Range**: Column between value1 and value2
- **Text Pattern**: Column contains "pattern"
- **Date Range**: Select data within specific date range
- **Numerical Conditions**: >, <, >=, <=, !=

**Combining Filters**:
- Apply multiple filters simultaneously
- Filters use AND logic by default
- Filtered view is non-destructive (original data unchanged)

### 4. Data Sorting

Organize data by one or multiple columns:

**Access**: Right-click column header > Sort

**Sort Options**:
- Ascending (A to Z, smallest to largest)
- Descending (Z to A, largest to smallest)
- Multi-column sorting (primary, secondary, tertiary)

### 5. Data Merging

Combine data from multiple datasets using various join strategies:

**Access**: Tools > Merge Datasets

**Merge Steps**:
1. Select first dataset
2. Select second dataset
3. Choose join type:
   - **Inner Join**: Only matching records
   - **Outer Join**: All records from both datasets
   - **Left Join**: All records from first dataset
   - **Right Join**: All records from second dataset
4. Select join columns (often "ID" or "Key")
5. Name your result and confirm

**Example**: Merge customer data with purchase history using Customer ID

### 6. Data Comparison

Analyze differences between two datasets:

**Access**: Tools > Compare Datasets

**Comparison Shows**:
- Rows unique to Dataset A
- Rows unique to Dataset B
- Matching rows
- Column differences
- Data type mismatches

**Use Case**: Verify data consistency between two versions of your dataset

### 7. Data Visualization

Create professional charts and visualizations:

**Access**: Tools > Create Chart

**Available Chart Types**:

| Chart Type | Best For | Example |
|-----------|----------|---------|
| **Line Chart** | Trends over time | Sales by month |
| **Bar Chart** | Category comparison | Revenue by region |
| **Scatter Plot** | Relationship analysis | Correlation between variables |
| **Histogram** | Distribution analysis | Age distribution |

**Creating a Chart**:
1. Select chart type
2. Choose X-axis column
3. Choose Y-axis column
4. Optional: Configure colors and labels
5. Click Generate to view
6. Save as image if needed

### 8. Data Summary & Profiling

Get instant statistics about your dataset:

**Access**: Tools > Data Summary

**Information Provided**:
- **Basic Stats**: Count, mean, median, std deviation
- **Data Types**: Column types and conversion info
- **Missing Data**: Number and percentage of nulls
- **Value Ranges**: Min, max, and quartile information
- **Unique Values**: Cardinality of each column

---

## Detailed Workflows

### Workflow 1: Clean and Analyze Sales Data

1. **Load** sales data (CSV file)
2. **Remove** duplicate transactions
3. **Filter** for Q4 sales only
4. **Sort** by revenue (descending)
5. **Create Chart** showing top products
6. **Generate Summary** for management report

### Workflow 2: Compare Two Data Exports

1. **Load** first version of dataset
2. **Load** second version of dataset
3. **Compare Datasets** to identify changes
4. **Merge** if consolidation needed
5. **Export** unified dataset

### Workflow 3: Prepare Data for External Analysis

1. **Load** raw data
2. **Clean** missing values and duplicates
3. **Filter** to relevant date range
4. **Merge** with supplementary data
5. **Export** clean dataset for downstream analysis

---

## Tips & Tricks

### Performance Tips

- **For Large Files**: DataForge automatically chunks files >100MB
- **Optimize Memory**: Close unused datasets to free resources
- **Faster Sorting**: Sort on indexed columns when possible
- **Reduce Display**: The table shows max 1000 rows; use filters to work with subsets

### Data Quality Checks

- Always check **Data Summary** before processing
- Verify **data types** are correct after loading
- Look for **missing values** and address them early
- Check **value ranges** to identify outliers

### Workflow Optimization

- **Use Named Datasets**: Name datasets clearly (e.g., "Q4_Sales_Raw")
- **Document Steps**: Keep notes of transformations applied
- **Save Intermediate Results**: Save cleaned data before complex analysis
- **Verify Results**: Always spot-check results against raw data

### Keyboard Shortcuts

- `Ctrl+O`: Open file
- `Ctrl+S`: Save active dataset
- `Ctrl+F`: Filter data
- `Ctrl+Q`: Exit application
- `F1`: Help documentation

---

## Troubleshooting

### Issue: "File is too large to load into memory"

**Solution**: 
- DataForge will automatically handle this by chunking
- If still problematic, pre-filter your CSV in another tool first
- Break into smaller date ranges or categories

### Issue: "Missing values not displaying correctly"

**Solution**:
- Click Tools > Clean Data
- Select the problematic column
- Choose appropriate handling method
- Verify in Data Summary after cleaning

### Issue: "Charts not displaying"

**Solution**:
- Verify columns contain numeric data
- Check for missing values in selected columns
- Ensure you have selected valid X and Y axes
- Try selecting different columns

### Issue: "Merged dataset looks incorrect"

**Solution**:
- Verify join columns are exactlyagreed matches
- Check data types of join columns match
- Review comparison view of the two datasets first
- Try alternative join type (Inner vs Outer)

### Issue: "Application runs slowly with large datasets"

**Solution**:
- Reduce number of rows displayed (use filters)
- Close other memory-intensive applications
- Increase system RAM if possible
- Process data in smaller chunks
- Use Data Summary instead of viewing all rows

### Issue: "Login fails or credentials not working"

**Solution**:
- Verify CAPS LOCK is off
- Check credentials with administrator
- Reset password if forgotten
- Ensure you have valid user account

---

## Need More Help?

For additional support:
- Check application Help menu for context-sensitive assistance
- Review the ABOUT.md file for project information
- Contact your system administrator
- Check the technical documentation in the project repository

---

**DataForge Version 1.0 - Professional Data Analysis Made Simple**
