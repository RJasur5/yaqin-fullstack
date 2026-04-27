import requests

def test_login():
    url = "http://95.182.118.245/api/auth/login"
    payload = {
        "phone": "+998998426574",
        "password": "789789"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
