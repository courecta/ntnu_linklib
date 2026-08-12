# NTNU LinkLib - Codebase Analysis Report

## Overview
This project is a Python library for scraping and parsing course data from NTNU (National Taiwan Normal University) course registration system. It provides tools to extract department information, course details, and syllabus data from the university's web API.

## Project Structure Analysis

### Root Directory Files
- **`main.py`**: Simple entry point with a basic "Hello from ntnu-linklib!" message
- **`test.py`**: API testing script that makes requests to the NTNU course API endpoint
- **`pyproject.toml`**: Project configuration with dependencies (beautifulsoup4, requests)
- **`README.md`**: Minimal project readme
- **Cleaned up**: Removed 5 empty redundant Python files that had duplicates in `course_select/`

### Refactored Implementation in `course_select/` Directory (v2.0)

The codebase has been completely refactored into a clean, simplified API wrapper with the following structure:

#### 1. **`departments.py`** - Department Data API
- **Purpose**: Fetch department listings with language support
- **API Endpoint**: `https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/CofnameCtrl`
- **Function**: `get_departments(language='chinese')`
- **Languages Supported**: 'chinese' (default) or 'english'
- **API Differences**: 
  - Chinese: `year=114` (Taiwan academic year format)
  - English: `year=2025` (Standard year format)
- **Output**: `output/departments_{language}.json`
- **Data**: 810 departments total in both languages
- **Features**:
  - Language-specific API parameter handling
  - Clean error handling (debug logging only on exceptions)
  - Language parameter validation
  - Auto-creates output directory
  - Returns boolean success/failure

#### 2. **`courses.py`** - Course Data API
- **Purpose**: Fetch and parse course listings for specific departments
- **API Endpoint**: `https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/CofopdlCtrl`  
- **Function**: `get_courses(dept_code)`
- **Input**: Department code (e.g., 'SU47', 'SU40')
- **Output**: `output/courses_{DEPT_CODE}.json`
- **Features**:
  - Automatic department code validation
  - Enhanced course data with summary statistics
  - Course type classification (Required/Elective)
  - Teacher and credit statistics
  - Course level determination (Undergraduate/Graduate)
  - Returns boolean success/failure

#### 3. **`syllabus.py`** - Syllabus Data API  
- **Purpose**: Fetch and parse individual course syllabi
- **API Endpoint**: `https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/SyllabusCtrl`
- **Function**: `get_syllabus(course_code, course_group="", dept_code="")`
- **Input**: Course code (required), optional course group and department
- **Output**: `output/syllabus_{COURSE_CODE}_{GROUP}.json`
- **Features**:
  - Automatic department code detection from course patterns
  - Automatic course group discovery
  - Course existence validation
  - Comprehensive syllabus data extraction
  - Metadata tracking (fetch timestamp, status codes)
  - Returns boolean success/failure

#### 4. **`api.py`** - Main API Wrapper
- **Purpose**: Unified interface combining all functions
- **Class**: `NTNUCourseAPI`
- **Methods**:
  - `fetch_departments(language)` - Fetch department data
  - `fetch_courses(dept_code)` - Fetch course data 
  - `fetch_syllabus(course_code, group, dept)` - Fetch syllabus data
  - `get_department_list(language)` - Read cached department data
  - `get_course_list(dept_code)` - Read cached course data
  - `get_syllabus_data(course_code, group)` - Read cached syllabus data
- **Features**:
  - Auto-fetching when cached data doesn't exist
  - Clean separation of fetch vs. read operations
  - Consistent error handling
  - Example usage demonstration

## Refactored API Design Principles

### 1. **Simplified Interface**
- Each script has a single main function with clear parameters
- Functions return boolean success/failure (True/False)
- No terminal output except debug logging on errors
- All outputs go to structured files in the `output/` directory

### 2. **Intelligent Parameter Handling**
- **Departments**: Language parameter ('chinese'/'english') with validation
- **Courses**: Department code validation and error detection
- **Syllabus**: Auto-detection of department codes and course groups from patterns

### 3. **Robust Error Handling**
- Invalid department codes return False (no courses found)
- Invalid course codes return False (course doesn't exist)
- Network errors are handled gracefully
- Debug information only shown on exceptions

### 4. **Consistent Output Structure**
```
output/
├── departments_chinese.json     # All departments in Chinese
├── departments_english.json     # All departments in English  
├── courses_{DEPT_CODE}.json     # Courses for specific department
└── syllabus_{COURSE}_{GROUP}.json # Individual course syllabus
```

### 5. **Enhanced Data Structure**
- **Courses**: Include summary statistics (types, levels, teachers, credits)
- **Syllabus**: Standardized field names with metadata tracking
- **All files**: Structured JSON with consistent formatting

## Usage Examples

### Command Line Usage
```bash
# Fetch departments in both languages
uv run departments.py

# Fetch courses for Computer Science department
uv run courses.py SU47

# Fetch syllabus for specific course (auto-detects group and department)
uv run syllabus.py CSU0001

# Use the unified API wrapper
uv run api.py
```

### Programmatic Usage
```python
from api import NTNUCourseAPI

api = NTNUCourseAPI()

# Fetch data
success = api.fetch_courses('SU47')
if success:
    course_data = api.get_course_list('SU47')
    print(f"Found {course_data['total_courses']} courses")

# Fetch syllabus
success = api.fetch_syllabus('CSU0001')  # Auto-detects department and group
if success:
    syllabus = api.get_syllabus_data('CSU0001')
    print(f"Instructor: {syllabus['instructor']}")
```

## API Integration Details

### Base URL
`https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/`

### Key Endpoints
1. **CofnameCtrl**: Department listing
2. **CofopdlCtrl**: Course listings by department

### Authentication & Headers
- Uses session cookies and complete browser header simulation
- CSRF protection with dynamic timestamps (`_dc` parameter)
- User-Agent spoofing to avoid bot detection

### Parameters
- **Academic Year**: 114 (2025)
- **Academic Term**: 1 (First semester)
- **Language**: Chinese/English support
- **Pagination**: Configurable limits (up to 99999 records)

## Technical Implementation Notes

### Dependencies
- **requests**: HTTP client for API calls
- **beautifulsoup4**: HTML parsing for syllabus extraction
- **json**: Data serialization
- **re**: Regex pattern matching for text extraction

### Error Handling
- Network timeout handling (10 seconds)
- Multiple parsing fallback methods
- Content-type detection and appropriate processing
- Raw data preservation for debugging

### Data Processing Pipeline
1. **Fetch** → Raw API responses saved to `.txt` files
2. **Parse** → Extract structured data to `.json` files  
3. **Analyze** → Generate summaries and statistics
4. **Store** → Multiple output formats for different use cases

## Current State & Functionality (v2.0 - Refactored)
- ✅ **Department API** - Supports both Chinese and English (`departments.py`)
- ✅ **Course API** - Works with any valid department code (`courses.py`)
- ✅ **Syllabus API** - Auto-detects parameters, works with any course (`syllabus.py`)
- ✅ **Unified API Wrapper** - Clean programmatic interface (`api.py`)
- ✅ **Intelligent Error Handling** - Returns boolean status, debug logging only
- ✅ **Structured Output** - All data saved to `output/` directory in consistent JSON format
- ✅ **Auto-Detection** - Department codes and course groups determined automatically
- ✅ **Enhanced Data** - Course summaries and metadata included
- 🧹 **Simplified Codebase** - Removed 6+ old files, combined functionality

## Complete Refactored Pipeline
1. **Fetch Departments** → `departments.py` → `output/departments_{language}.json`
2. **Fetch Courses** → `courses.py {DEPT_CODE}` → `output/courses_{DEPT}.json` 
3. **Fetch Syllabus** → `syllabus.py {COURSE_CODE}` → `output/syllabus_{COURSE}_{GROUP}.json`
4. **API Wrapper** → `api.py` → Unified interface with caching and auto-fetch

## Key Improvements Made
- **Simplified Interface**: Single function per script with clear parameters
- **Better Error Handling**: Invalid codes return False, no verbose output
- **Auto-Detection**: Department and group codes detected from course patterns
- **Consistent Output**: All files in structured `output/` directory
- **Enhanced Data**: Course statistics and metadata included
- **Clean Code**: Combined parsing with fetching, removed redundant files

## Final Project Structure (Post-Refactoring)

```
course_select/
├── departments.py              # Fetch departments (Chinese/English)
├── courses.py                  # Fetch courses by department code  
├── syllabus.py                 # Fetch syllabus by course code (auto-detect)
├── api.py                      # Unified API wrapper class
├── README.md                   # API documentation
└── output/                     # All structured output files
    ├── departments_chinese.json
    ├── departments_english.json
    ├── courses_{DEPT_CODE}.json
    └── syllabus_{COURSE}_{GROUP}.json
```

## Future Enhancements Suggested
- Add command-line interface with argparse for better UX
- Implement caching with expiration dates
- Add batch processing for multiple departments/courses
- Create web interface for course search and filtering
- Add data validation and integrity checks
- Implement rate limiting for respectful API usage

---

## ✅ **REFACTORING COMPLETE - ALL TESTS PASSED!**

### **Final Test Results**
- ✅ **Departments API**: Both Chinese (11KB) and English (15KB) working correctly with proper year formats
- ✅ **Courses API**: Successfully tested with SU47 (Computer Science, 25 courses) and SU40 (Mathematics, larger dataset)  
- ✅ **Syllabus API**: Successfully fetched CSU0001 syllabus with auto-detection
- ✅ **API Wrapper**: Unified interface working with all components
- ✅ **Error Handling**: Invalid department/course codes properly handled
- ✅ **Output Structure**: All files consistently formatted in `output/` directory

### **Major Improvements Delivered**
- 🔧 **Fixed English Departments API**: Corrected year parameter (2025 vs 114)
- 🗑️ **Cleaned Codebase**: Removed 6+ redundant empty files 
- 🔄 **Combined Functionality**: Merged parsing with fetching in each module
- 📁 **Organized Outputs**: Structured `output/` directory with consistent JSON formatting
- 🎯 **Simplified Interface**: Boolean returns, clean error handling, auto-detection
- 📚 **Enhanced Documentation**: Complete API documentation and usage examples

**The NTNU Course API wrapper is now production-ready with a clean, intuitive interface!**