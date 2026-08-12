"""
Department API - Fetch department listings from NTNU course system
"""

import requests
import json
from pathlib import Path

def get_departments(language='chinese'):
    """
    Fetch all departments from NTNU course system
    
    Args:
        language: 'chinese' or 'english' (default: 'chinese')
    
    Returns:
        bool: True on success, False on failure
    """
    try:
        # Validate language parameter
        if language not in ['chinese', 'english']:
            raise ValueError("Language must be 'chinese' or 'english'")
        
        # API endpoint
        url = "https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/CofnameCtrl"
        
        # Parameters - English API uses different year format
        if language == 'english':
            params = {
                'action': 'cof',
                'type': 'eng',
                'year': '2025',  # English API uses full year format
                'term': '1',
                '_dc': '1756735461977',
                'page': '1',
                'start': '0',
                'limit': '25'
            }
        else:
            params = {
                'action': 'cof',
                'type': 'chn',
                'year': '114',  # Chinese API uses Taiwan academic year format
                'term': '1',
                '_dc': '1756318906047',
                'page': '1',
                'start': '0',
                'limit': '25'
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
        
        # Parse response
        response_text = response.text.strip()
        
        # Try to parse as JSON-like array
        if response_text.startswith('[') and response_text.endswith(']'):
            import ast
            departments_data = ast.literal_eval(response_text)
            
            # Create output directory if it doesn't exist
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            
            # Save to output file
            filename = f'departments_{language}.json'
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(departments_data, f, ensure_ascii=False, indent=2)
            
            return True
        else:
            raise ValueError("Invalid response format")
            
    except Exception as e:
        # Debug logging only on exception
        print(f"ERROR in get_departments: {e}")
        return False

if __name__ == "__main__":
    # Default behavior - fetch both languages
    get_departments('chinese')
    get_departments('english')
