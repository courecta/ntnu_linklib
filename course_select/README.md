# NTNU Course API - Simplified Interface

A clean, simplified API wrapper for NTNU (National Taiwan Normal University) course system.

## Quick Start

```bash
# Fetch all departments
uv run departments.py

# Fetch courses for a specific department
uv run courses.py SU47  # Computer Science
uv run courses.py SU40  # Mathematics

# Fetch syllabus for a specific course  
uv run syllabus.py CSU0001  # Auto-detects department and group
uv run syllabus.py MAU0180  # Math course example

# Use the unified API
uv run api.py  # Demonstrates full workflow
```

## API Functions

### `departments.get_departments(language='chinese')`
- **Input**: Language ('chinese' or 'english')
- **Output**: `output/departments_{language}.json`
- **Returns**: `True` on success, `False` on failure
- **Note**: English and Chinese APIs use different year formats (2025 vs 114)

### `courses.get_courses(dept_code)`
- **Input**: Department code (e.g., 'SU47', 'SU40')
- **Output**: `output/courses_{DEPT_CODE}.json`
- **Returns**: `True` on success, `False` if invalid department

### `syllabus.get_syllabus(course_code, course_group="", dept_code="")`
- **Input**: Course code (required), optional group and department
- **Output**: `output/syllabus_{COURSE_CODE}_{GROUP}.json`  
- **Returns**: `True` on success, `False` if course doesn't exist

## Common Department Codes
- `SU47` - Computer Science
- `SU40` - Mathematics  
- `SU43` - Physics
- `SU44` - Chemistry
- `SU48` - Electrical Engineering

## Course Code Patterns
- `CSU****` - Computer Science Undergraduate
- `CSC****` - Computer Science Graduate
- `MAU****` - Mathematics Undergraduate
- `PHU****` - Physics Undergraduate

## Output Structure
All outputs are saved in the `output/` directory as structured JSON files with:
- Consistent formatting (UTF-8, indented)
- Enhanced metadata and statistics
- Boolean return values for error handling
- Debug logging only on exceptions

## Error Handling
- Invalid department codes: Returns `False`, no courses found
- Invalid course codes: Returns `False`, course doesn't exist
- Network errors: Returns `False`, debug message in console
- All errors: No verbose output, clean boolean responses
