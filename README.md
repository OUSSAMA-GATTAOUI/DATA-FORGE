# DataForge - Professional Data Analysis Platform

<div align="center">

![DataForge Logo](icon.ico)

**A powerful, user-friendly desktop application for data analysis, cleaning, transformation, and visualization.**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![Pandas](https://img.shields.io/badge/Data-Pandas-orange)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red)]()

[Quick Start](#quick-start) • [Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation)

</div>

---

## Overview

DataForge is a comprehensive data analysis and manipulation platform designed for data professionals, analysts, researchers, and business users. With an intuitive graphical interface built on PyQt5, DataForge abstracts away the complexity of data processing while maintaining professional-grade capabilities.

Whether you're cleaning customer datasets, analyzing sales trends, comparing data versions, or creating professional visualizations, DataForge provides tools to accomplish your goals efficiently.

### Key Highlights

✅ **Load & Manage** multiple CSV datasets simultaneously  
✅ **Clean & Transform** data with intelligent missing value handling  
✅ **Filter & Sort** complex datasets with advanced criteria  
✅ **Merge & Compare** datasets using multiple join strategies  
✅ **Visualize** data with interactive charts and graphics  
✅ **Analyze** with comprehensive statistical summaries  
✅ **Optimize** memory handling for large files (100MB+)  
✅ **Secure** user authentication and session management  

---

## Quick Start

### For Users (Using Executable)

```bash
# 1. Download dataForge.exe
# 2. Double-click to run
# 3. Login with your credentials
# 4. Load a CSV file and start analyzing!
```

### For Developers (From Source)

```bash
# 1. Clone the repository
git clone <repository-url>
cd "DATA FORGE"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

---

## Features

### 📊 Data Loading & Management
- Load multiple CSV files with automatic type detection
- Manage multiple datasets in a single workspace
- Large file support with optimized chunked loading (handles 100MB+ files)
- Non-destructive operations preserve original data
- Dataset renaming and organization

### 🧹 Data Cleaning
- Remove duplicate records
- Intelligent missing value handling (mean, median, mode, forward fill)
- Data type conversion and standardization
- Format normalization
- Automated data validation

### 🔍 Data Filtering
- Advanced multi-criteria filtering
- Pattern matching and text search
- Numerical comparisons and ranges
- Date-based filtering
- Conditional logic with AND operators

### 📈 Data Sorting
- Single and multi-column sorting
- Ascending and descending order
- Efficient sorting for large datasets
- Custom column ordering

### 🔗 Data Merging
- Inner, Outer, Left, and Right joins
- Multi-column join support
- Intelligent key column detection
- Automatic result naming

### ⚖️ Data Comparison
- Side-by-side dataset analysis
- Identify unique rows in each dataset
- Detect matching records
- Column-level difference detection
- Data type mismatch identification

### 📉 Data Visualization
- Line charts for trend analysis
- Bar charts for category comparison
- Scatter plots for relationship analysis
- Histograms for distribution analysis
- Customizable colors and labels
- Export visualizations as images

### 📊 Data Analysis & Profiling
- Comprehensive statistical summaries
- Distribution analysis
- Descriptive statistics (mean, median, std dev, quartiles)
- Missing value identification
- Cardinality and value range analysis
- Column-level profiling

---

## Installation

### System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 7 or later |
| **Python** | 3.8 or higher |
| **RAM** | 2GB minimum (4GB+ recommended) |
| **Storage** | 500MB available space |
| **Display** | 1024x768 minimum (1920x1080 recommended) |

### Method 1: Executable (Recommended for End Users)

1. Download `dataForge.exe` from the releases page
2. Double-click the executable
3. Application launches immediately - no installation required
4. Create a shortcut to the executable or pin to Start Menu

### Method 2: From Source Code

```bash
# Install Python 3.8 or later if needed

# Navigate to project directory
cd "DATA FORGE"

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Method 3: Building Your Own Executable

```bash
# Ensure PyInstaller is installed
pip install pyinstaller

# Build executable from spec file
pyinstaller build.spec

# Executable created in dist/dataForge/dataForge.exe
```

---

## Usage

### Basic Workflow

#### 1. Login
```
Launch DataForge → Enter credentials → Click Login
```

#### 2. Load Data
```
File > Open Dataset → Select CSV file → Review preview → Confirm Load
```

#### 3. Explore
```
View data table → Check Data Summary → Identify columns and types
```

#### 4. Process
```
Apply cleaning, filtering, sorting, or merging operations as needed
```

#### 5. Visualize
```
Tools > Create Chart → Select chart type and columns → Generate visualization
```

#### 6. Export/Save
```
File > Export → Choose format and location
```

### Common Tasks

**Task: Clean mismatched data types**
```
1. Load dataset
2. Tools → Clean Data
3. Select columns with issues
4. Choose standardization method
5. Apply changes
```

**Task: Compare two versions of a dataset**
```
1. Load Dataset A
2. Load Dataset B
3. Tools → Compare Datasets
4. Select both datasets
5. Review detailed differences report
```

**Task: Merge customer and transaction data**
```
1. Load customer_data.csv
2. Load transactions.csv
3. Tools → Merge Datasets
4. Select join columns (Customer ID)
5. Choose Inner Join
6. Name result and confirm
```

**Task: Create trending sales visualization**
```
1. Load sales_data.csv
2. Filter for current year: date >= '2024-01-01'
3. Tools → Create Chart
4. Select Line Chart
5. X-axis: Month, Y-axis: Revenue
6. Generate and customize
```

---

## Project Structure

```
DATA FORGE/
├── main.py                 # Application entry point
├── build.spec             # PyInstaller configuration
├── requirements.txt       # Python dependencies
├── icon.ico              # Application icon
├── README.md             # This file
├── ABOUT.md              # Project information
├── GUIDE.md              # User guide
│
├── src/
│   ├── login.py          # Authentication interface
│   ├── main_window.py    # Main application window
│   │
│   ├── core/
│   │   └── auth.py       # Authentication logic
│   │
│   ├── data/
│   │   ├── data_manager.py      # Dataset management
│   │   ├── compare_engine.py    # Dataset comparison
│   │   └── merge_engine.py      # Merge operations
│   │
│   ├── dialogs/
│   │   ├── chart_dialog.py      # Visualization module
│   │   ├── clean_dialog.py      # Data cleaning
│   │   ├── compare_dialog.py    # Comparison UI
│   │   ├── filter_dialog.py     # Filtering interface
│   │   ├── merge_dialog.py      # Merge interface
│   │   ├── sort_dialog.py       # Sorting interface
│   │   └── summary_dialog.py    # Statistics display
│   │
│   └── utils/
│       └── styles.py            # Application styling
│
├── scripts/
│   └── create_icon.py           # Icon generation tool
│
└── build/                        # Build artifacts (generated)
```

---

## Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.8+ | Core language |
| **PyQt5** | 5.15.9 | GUI framework |
| **Pandas** | 2.0.3 | Data manipulation |
| **NumPy** | 1.24.3 | Numerical computing |
| **Matplotlib** | 3.7.2 | Data visualization |
| **python-dateutil** | 2.8.2 | Date parsing |
| **PyInstaller** | 5.13.2 | Executable creation |

---

## Advanced Features

### Memory-Efficient Large File Handling

DataForge automatically detects file size and applies chunked loading for files exceeding 100MB:

```python
# Automatic behavior - no user configuration needed
if file_size > 100MB:
    data = pd.read_csv(file, chunksize=50000)
    # Process chunks efficiently
```

This allows analysis of datasets significantly larger than available RAM.

### Intelligent Data Type Detection

Automatic detection and classification of:
- Numerical (int, float)
- Categorical/String
- Date/Time
- Mixed types with warnings

### Multi-Dataset Workspace

Work with multiple datasets simultaneously:
- Load unlimited datasets
- Switch between them instantly
- Perform cross-dataset operations (merge, compare)
- Isolated modifications per dataset

---

## Configuration

### Application Settings

Settings are stored in `pitcha.db` and include:
- User credentials and session info
- Recent datasets
- User preferences
- Operation history

### Customization

Styling can be modified in `src/utils/styles.py`:
```python
SIDEBAR_WIDTH = 250        # Sidebar width in pixels
SPACING_LG = 16           # Large spacing units
SPACING_MD = 8            # Medium spacing units
```

---

## Performance Optimization

### Tips for Best Performance

1. **Filter Before Analysis**: Reduce dataset size before processing
2. **Close Unused Datasets**: Free memory by removing unnecessary datasets
3. **Use Summary Statistics**: Instead of manual scanning of large tables
4. **Batch Operations**: Perform multiple operations in sequence, not iteratively
5. **Monitor Memory**: Check system resources for very large datasets (>1GB)

### Expected Performance

| Dataset Size | Load Time | Filter | Sort | Merge |
|-------------|-----------|--------|------|-------|
| < 1MB | < 1 sec | < 1 sec | 1-2 sec | 1-2 sec |
| 1-10MB | 1-2 sec | 1-2 sec | 2-3 sec | 2-4 sec |
| 10-100MB | 2-5 sec | 3-5 sec | 5-10 sec | 5-15 sec |
| 100MB+ | 5-30 sec | 5-10 sec | 10-30 sec | 15-45 sec |

*Times vary by hardware specifications*

---

## Troubleshooting

### Common Issues

**Application crashes on startup**
```
Solution: Check requirements.txt installed
pip install -r requirements.txt --force-reinstall
```

**Cannot login**
```
Solution: Verify credentials with administrator
- Check CAPS LOCK is off
- Reset password if forgotten
```

**Charts not rendering**
```
Solution: Ensure selected columns have numeric data
- Check Data Summary for column types
- Select different columns
```

**Large file loading fails**
```
Solution: File was not loaded due to memory constraints
- Close other applications
- Try pre-filtering data
- Increase system RAM
```

**Merge shows unexpected results**
```
Solution: Verify join configuration
- Check join column names match exactly
- Review data types of join columns
- Use Compare Datasets first to verify compatibility
```

---

## Contributing

To contribute improvements to DataForge:

1. Report issues with detailed reproduction steps
2. Suggest features with clear use cases
3. Submit improvements following the existing code style
4. Test thoroughly before submitting

---

## Roadmap

### Planned Features (Future Releases)

- 📡 **Real-time Data Streaming**: Live data input support
- 🤖 **Machine Learning Integration**: Built-in ML model training
- 🗄️ **Database Connectivity**: Direct SQL database access
- ☁️ **Cloud Collaboration**: Multi-user workspace sharing
- 📊 **Extended Export Formats**: Excel, JSON, Parquet support
- 🧮 **Custom Formula Builder**: User-defined calculations
- ⏰ **Scheduled Processing**: Automated data processing jobs
- 🔌 **API Integration**: REST API for programmatic access

---

## Support & Documentation

### Documentation Files

- **[README.md](README.md)** - Project overview and setup (this file)
- **[ABOUT.md](ABOUT.md)** - Project vision and features
- **[GUIDE.md](GUIDE.md)** - Comprehensive user guide with workflows

### Getting Help

1. Check the **GUIDE.md** for detailed feature documentation
2. Review **ABOUT.md** for project information
3. Check the in-application Help menu
4. Review application logs in the build directory

---

## License

DataForge is proprietary software. Unauthorized copying, modification, or distribution is prohibited.

For licensing inquiries, contact the development team.

---

## Acknowledgments

DataForge is built upon these excellent open-source projects:

- **PyQt5** - Cross-platform GUI toolkit
- **Pandas** - Data analysis and manipulation
- **Matplotlib** - Data visualization
- **NumPy** - Numerical computing
- **Python** - General-purpose programming language

---

<div align="center">

### Made with ❤️ for data professionals

**DataForge v1.0** - Professional Data Analysis Made Simple

[Report Issues](../../issues) • [Request Features](../../issues) • [Documentation](GUIDE.md) • [About](ABOUT.md)

</div>
