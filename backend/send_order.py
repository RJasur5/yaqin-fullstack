import requests
import json

BASE_URL = "http://localhost:8005/api"

def run_test():
    # 1. Login
    print("Logging in...")
    login_data = {
        "phone": "+998901234567",
        "password": "123456"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    print("Login successful. Token obtained.")

    # 2. Create Order
    print("Creating order for Yakkasaroy...")
    order_data = {
        "subcategory_id": 1,
        "description": "СРОЧНО: Тестовый заказ для проверки уведомлений в Яккасарае!",
        "city": "Toshkent",
        "district": "Yakkasaroy",
        "price": 45000.0
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/orders", headers=headers, json=order_data)
    if response.status_code == 200:
        print("ORDER CREATED SUCCESSFULLY!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Failed to create order: {response.status_code} - {response.text}")

if __name__ == "__main__":
    run_test()
