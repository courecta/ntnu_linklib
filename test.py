import requests

# API endpoint
url = "https://courseap2.itc.ntnu.edu.tw/acadmOpenCourse/CofnameCtrl"

# Parameters (payload)
params = {
    'action': 'cof',
    'type': 'chn',
    'year': '114',
    'term': '1',
    '_dc': '1756318906047',
    'page': '1',
    'start': '0',
    'limit': '25'
}

try:
    # Make the GET request
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Print the response
    print("Status Code:", response.status_code)
    print("Content Type:", response.headers.get('content-type', 'Unknown'))
    print("Raw Response:")
    print(response.text)
    
    # Try to parse as JSON if possible
    try:
        json_data = response.json()
        print("\nParsed JSON:")
        print(json_data)
    except ValueError:
        print("\nResponse is not valid JSON")
    
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")

