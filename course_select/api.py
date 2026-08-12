#!/usr/bin/env python3
"""
NTNU Course API Wrapper - Simplified interface for NTNU course system
"""

from departments import get_departments
from courses import get_courses
from syllabus import get_syllabus
import json
from pathlib import Path

class NTNUCourseAPI:
    """Simple API wrapper for NTNU course system"""
    
    def __init__(self):
        self.output_dir = Path('output')
        self.output_dir.mkdir(exist_ok=True)
    
    def fetch_departments(self, language='chinese'):
        """
        Fetch department listings
        
        Args:
            language: 'chinese' or 'english'
            
        Returns:
            bool: True on success, False on failure
        """
        return get_departments(language)
    
    def fetch_courses(self, dept_code):
        """
        Fetch courses for a department
        
        Args:
            dept_code: Department code (e.g., 'SU47')
            
        Returns:
            bool: True on success, False on failure
        """
        return get_courses(dept_code)
    
    def fetch_syllabus(self, course_code, course_group="", dept_code=""):
        """
        Fetch syllabus for a course
        
        Args:
            course_code: Course code (e.g., 'CSU0001')
            course_group: Course group (optional)
            dept_code: Department code (optional)
            
        Returns:
            bool: True on success, False on failure
        """
        return get_syllabus(course_code, course_group, dept_code)
    
    def get_department_list(self, language='chinese'):
        """
        Get list of departments from output file
        
        Args:
            language: 'chinese' or 'english'
            
        Returns:
            list or None: List of departments or None if file doesn't exist
        """
        try:
            filename = f'departments_{language}.json'
            filepath = self.output_dir / filename
            
            if not filepath.exists():
                # Try to fetch if file doesn't exist
                if not self.fetch_departments(language):
                    return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def get_course_list(self, dept_code):
        """
        Get list of courses from output file
        
        Args:
            dept_code: Department code
            
        Returns:
            dict or None: Course data or None if file doesn't exist
        """
        try:
            filename = f'courses_{dept_code.upper()}.json'
            filepath = self.output_dir / filename
            
            if not filepath.exists():
                # Try to fetch if file doesn't exist
                if not self.fetch_courses(dept_code):
                    return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def get_syllabus_data(self, course_code, course_group="A"):
        """
        Get syllabus data from output file
        
        Args:
            course_code: Course code
            course_group: Course group
            
        Returns:
            dict or None: Syllabus data or None if file doesn't exist
        """
        try:
            filename = f'syllabus_{course_code.upper()}_{course_group.upper()}.json'
            filepath = self.output_dir / filename
            
            if not filepath.exists():
                # Try to fetch if file doesn't exist
                if not self.fetch_syllabus(course_code, course_group):
                    return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

def main():
    """Example usage of the API"""
    api = NTNUCourseAPI()
    
    print("NTNU Course API Wrapper")
    print("=" * 30)
    
    # Fetch departments
    print("1. Fetching departments...")
    if api.fetch_departments('chinese'):
        print("   ✓ Chinese departments fetched successfully")
    else:
        print("   ✗ Failed to fetch Chinese departments")
    
    # Fetch courses for Computer Science department
    print("\n2. Fetching courses for Computer Science (SU47)...")
    if api.fetch_courses('SU47'):
        print("   ✓ Courses fetched successfully")
        
        # Get course summary
        course_data = api.get_course_list('SU47')
        if course_data:
            print(f"   → Found {course_data['total_courses']} courses")
            print(f"   → Summary: {course_data['summary']['course_types']}")
    else:
        print("   ✗ Failed to fetch courses")
    
    # Fetch syllabus for a specific course
    print("\n3. Fetching syllabus for CSU0001...")
    if api.fetch_syllabus('CSU0001'):
        print("   ✓ Syllabus fetched successfully")
        
        # Get syllabus summary
        syllabus_data = api.get_syllabus_data('CSU0001')
        if syllabus_data:
            print(f"   → Course: {syllabus_data.get('subject_code', 'N/A')}")
            print(f"   → Title: {syllabus_data.get('english_name', 'N/A')}")
            print(f"   → Instructor: {syllabus_data.get('instructor', 'N/A')}")
    else:
        print("   ✗ Failed to fetch syllabus")
    
    print(f"\n✓ All outputs saved to: {api.output_dir}")

if __name__ == "__main__":
    main()
