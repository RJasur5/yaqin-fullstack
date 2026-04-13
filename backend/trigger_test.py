import requests
import json
import time

# Configuration
# Since we updated the IP to 192.168.88.111, we can use localhost if running on the PC
URL = "http://localhost:8005/api/test-notify"

def trigger_test(user_id):
    print(f"Sending test 'mini-window' notification to user {user_id}...")
    try:
        # We can also hit the custom endpoint in main.py
        response = requests.get(f"{URL}/{user_id}")
        if response.status_code == 200:
            print("Successfully sent! Check your phone.")
        else:
            print(f"Failed to send. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Try user ID 26 (mentioned in your previous chats)
    trigger_test(26)
    
    # Also try ID 1 just in case
    # trigger_test(1)
