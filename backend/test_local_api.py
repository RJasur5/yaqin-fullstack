import requests

try:
    response = requests.get('http://127.0.0.1:8005/api/categories', timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
