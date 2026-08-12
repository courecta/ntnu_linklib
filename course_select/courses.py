"""
Courses API - Fetch and parse course listings for specific departments from NTNU course system
"""

import requests
import json
import time
from pathlib import Path

def get_courses(dept_code):
    """
    Fetch and parse course listings for a specific department
    
    Args:
        dept_code: Department code (e.g., 'SU47' for Computer Science)
    
    Returns:
        bool: True on success, False on failure (invalid dept_code or API error)
    """
    try:
        if not dept_code or not isinstance(dept_code, str):
            raise ValueError("Department code must be a non-empty string")
        
        # API endpoint for course data
        url = "https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/CofopdlCtrl"
        
        # Query parameters
        params = {
            '_dc': str(int(time.time() * 1000)),
            'acadmYear': '114',
            'acadmTerm': '1',
            'chn': '',
            'engTeach': 'N',
            'clang': 'N',
            'moocs': 'N',
            'remoteCourse': 'N',
            'digital': 'N',
            'adsl': 'N',
            'deptCode': dept_code.upper(),
            'zuDept': '',
            'classCode': '',
            'kind': '',
            'generalCore': '',
            'teacher': '',
            'serial_number': '',
            'course_code': '',
            'language': 'chinese',
            'action': 'showGrid',
            'start': '0',
            'limit': '99999',
            'page': '1'
        }
        
        # Headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Referer': 'https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/CofopdlCtrl?language=chinese',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Make request
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse response based on content type
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            data = response.json()
        else:
            # Try to parse as JSON even if content-type is different
            try:
                data = response.json()
            except:
                # If the response is not JSON, it might be an error or invalid dept_code
                return False
        
        # Validate response structure
        if not isinstance(data, dict) or 'List' not in data:
            return False
        
        # Check if department has any courses
        if data.get('Count', 0) == 0:
            return False
        
        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Process and save course data
        courses = data['List']
        
        # Create enhanced course data with summary
        processed_data = {
            'department_code': dept_code.upper(),
            'total_courses': data['Count'],
            'courses_returned': len(courses),
            'courses': courses,
            'summary': _generate_course_summary(courses)
        }
        
        # Save to output file
        filename = f'courses_{dept_code.upper()}.json'
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        # Debug logging only on exception
        print(f"ERROR in get_courses for dept {dept_code}: {e}")
        return False

def _generate_course_summary(courses):
    """Generate summary statistics for courses"""
    summary = {
        'course_types': {},
        'course_levels': {},
        'total_teachers': 0,
        'total_credits': 0,
        'teachers': []
    }
    
    teachers = set()
    total_credits = 0
    
    for course in courses:
        # Count course types (Required vs Elective)
        course_type = 'Required' if course.get('option_code') == '必' else 'Elective'
        summary['course_types'][course_type] = summary['course_types'].get(course_type, 0) + 1
        
        # Collect teachers
        teacher = course.get('teacher', '').strip()
        if teacher:
            teachers.add(teacher)
        
        # Count credits
        try:
            credits = float(course.get('credit', 0))
            total_credits += credits
        except (ValueError, TypeError):
            pass
        
        # Determine course level
        course_code = course.get('course_code', '')
        if course_code:
            if 'U' in course_code:  # Undergraduate
                level = 'Undergraduate'
            elif 'C' in course_code:  # Graduate/Advanced
                level = 'Graduate'
            else:
                level = 'Other'
            summary['course_levels'][level] = summary['course_levels'].get(level, 0) + 1
    
    summary['teachers'] = sorted(list(teachers))
    summary['total_teachers'] = len(teachers)
    summary['total_credits'] = total_credits
    
    return summary

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        dept_code = sys.argv[1]
        success = get_courses(dept_code)
        if not success:
            print(f"ERROR: Failed to fetch courses for department '{dept_code}'. Check if department code is valid.")
    else:
        # Default to Computer Science department
        get_courses('SU47')
