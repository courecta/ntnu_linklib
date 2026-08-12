"""
Syllabus API - Fetch and parse syllabus data for specific courses from NTNU course system
"""

import requests
import json
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup, Tag

def get_syllabus(course_code, course_group="", dept_code=""):
    """
    Fetch and parse syllabus data for a specific course
    
    Args:
        course_code: Course code (e.g., 'CSU0001')
        course_group: Course group (e.g., 'A') - optional, will try to find automatically
        dept_code: Department code (e.g., 'SU47') - optional, will try to determine from course code
    
    Returns:
        bool: True on success, False on failure (invalid course_code or course not found)
    """
    try:
        if not course_code or not isinstance(course_code, str):
            raise ValueError("Course code must be a non-empty string")
        
        course_code = course_code.upper()
        
        # Auto-determine department code if not provided
        if not dept_code:
            dept_code = _determine_dept_code(course_code)
            if not dept_code:
                return False
        
        # Auto-determine course group if not provided  
        if not course_group:
            course_group = _determine_course_group(course_code, dept_code)
            if not course_group:
                return False
        
        # API endpoint for syllabus data
        url = "https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/SyllabusCtrl"
        
        # Form data parameters
        form_data = {
            'year': '114',
            'term': '1',
            'courseCode': course_code,
            'courseGroup': course_group.upper(),
            'formS': '',
            'classes1': '',
            'deptCode': dept_code.upper(),
            'deptGroup': '',
            'language2': 'chinese'
        }
        
        # Headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://courseap2.itc.ntnu.edu.tw',
            'Referer': 'https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/CofopdlCtrl?language=chinese',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Make POST request
        response = requests.post(url, data=form_data, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if response is valid HTML
        if 'text/html' not in response.headers.get('content-type', ''):
            return False
        
        # Parse the HTML response
        syllabus_data = _parse_syllabus_html(response.text)
        
        if not syllabus_data:
            return False
        
        # Add request metadata
        syllabus_data['_metadata'] = {
            'course_code': course_code,
            'course_group': course_group,
            'dept_code': dept_code,
            'fetch_timestamp': time.time(),
            'status_code': response.status_code
        }
        
        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Save to output file
        filename = f'syllabus_{course_code}_{course_group}.json'
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(syllabus_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        # Debug logging only on exception
        print(f"ERROR in get_syllabus for course {course_code}: {e}")
        return False

def _determine_dept_code(course_code):
    """Determine department code from course code pattern"""
    # Common mappings based on course code patterns
    if course_code.startswith('CSU') or course_code.startswith('CSC'):
        return 'SU47'  # Computer Science
    elif course_code.startswith('MAU') or course_code.startswith('MAC'):
        return 'SU40'  # Mathematics
    elif course_code.startswith('PHU') or course_code.startswith('PHC'):
        return 'SU43'  # Physics
    elif course_code.startswith('CHU') or course_code.startswith('CHC'):
        return 'SU44'  # Chemistry
    elif course_code.startswith('EEU') or course_code.startswith('EEC'):
        return 'SU48'  # Electrical Engineering
    # Add more mappings as needed
    return None

def _determine_course_group(course_code, dept_code):
    """Determine course group by checking available courses in department"""
    try:
        # First try common groups
        common_groups = ['A', 'B', 'C', '1', '2', '3']
        
        for group in common_groups:
            if _check_course_exists(course_code, group, dept_code):
                return group
        
        # If no common group works, return None (course doesn't exist)
        return None
        
    except:
        return None

def _check_course_exists(course_code, course_group, dept_code):
    """Quick check if a course exists with given parameters"""
    try:
        url = "https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/SyllabusCtrl"
        form_data = {
            'year': '114',
            'term': '1',
            'courseCode': course_code,
            'courseGroup': course_group,
            'formS': '',
            'classes1': '',
            'deptCode': dept_code,
            'deptGroup': '',
            'language2': 'chinese'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(url, data=form_data, headers=headers, timeout=5)
        
        # If we get a successful response with reasonable length, course likely exists
        return response.status_code == 200 and len(response.text) > 1000
        
    except:
        return False

def _parse_syllabus_html(html_content):
    """Parse syllabus HTML and extract structured data"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        syllabus_data = {}
        
        # Extract data from table rows
        tables = soup.find_all('table')
        if not tables:
            return None
        
        all_rows = []
        for table in tables:
            # Check if table is a proper Tag element
            if isinstance(table, Tag):
                rows = table.find_all('tr')
                all_rows.extend(rows)
        
        # Extract syllabus sections
        for row in all_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                first_cell = cells[0]
                
                # Check if first cell is a header
                if (first_cell.get('bgcolor') == '#DFEFFF' or 
                    first_cell.find('b') is not None):
                    
                    header_text = first_cell.get_text(strip=True)
                    content_cell = cells[1] if len(cells) > 1 else None
                    
                    if content_cell:
                        content_text = content_cell.get_text(strip=True)
                        content_text = re.sub(r'\s+', ' ', content_text)
                        
                        # Map headers to standardized keys
                        key = _normalize_header_key(header_text)
                        if key:
                            syllabus_data[key] = content_text
        
        # Extract basic course info from JavaScript variables
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_text = script.get_text()
            
            # Extract variables
            patterns = {
                'course_code': r"var course_code = '([^']+)'",
                'teacher': r"var teacher = '([^']+)'",
                'department_code': r"var dept_code = '([^']+)'"
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, script_text)
                if match and key not in syllabus_data:
                    syllabus_data[key] = match.group(1)
        
        return syllabus_data if syllabus_data else None
        
    except Exception as e:
        return None

def _normalize_header_key(header_text):
    """Normalize header text to standardized key names"""
    header_lower = header_text.lower()
    
    # Mapping of common headers to standard keys
    mappings = {
        'required and recommended texts': 'required_texts',
        '參考書目': 'required_texts',
        'course description': 'course_description',
        '課程概述': 'course_description',
        '課程簡介': 'course_description',
        'learning objectives': 'learning_objectives',
        '學習目標': 'learning_objectives',
        '課程目標': 'learning_objectives',
        'teaching methods': 'teaching_methods',
        '教學方式': 'teaching_methods',
        'evaluation': 'evaluation_methods',
        '評量方式': 'evaluation_methods',
        'office hours': 'office_hours',
        '課業諮詢': 'office_hours',
        'prerequisites': 'prerequisites',
        '先修課程': 'prerequisites',
        '開課序號': 'course_serial',
        '科目代碼': 'subject_code',
        '英文名稱': 'english_name',
        '全_半年': 'duration',
        '學分數': 'credits',
        '開課系級': 'department_level',
        '授課教師': 'instructor'
    }
    
    # Check for exact matches first
    if header_lower in mappings:
        return mappings[header_lower]
    
    # Check for partial matches
    for pattern, key in mappings.items():
        if pattern in header_lower:
            return key
    
    # Create a safe key from the header text
    key = re.sub(r'[^\w\u4e00-\u9fff]', '_', header_text.lower()).strip('_')
    return key if key else None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        course_code = sys.argv[1]
        course_group = sys.argv[2] if len(sys.argv) > 2 else ""
        dept_code = sys.argv[3] if len(sys.argv) > 3 else ""
        
        success = get_syllabus(course_code, course_group, dept_code)
        if not success:
            print(f"ERROR: Failed to fetch syllabus for course '{course_code}'. Check if course code is valid and exists.")
    else:
        # Default test
        get_syllabus('CSU0001', 'A', 'SU47')
