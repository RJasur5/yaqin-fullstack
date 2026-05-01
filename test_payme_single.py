import base64
import urllib.request
import re

merchant_id = "69eef6070ba8aa967a862f8c" # Their Prod ID from .env

def test_params(params_str):
    encoded = base64.b64encode(params_str.encode()).decode()
    url = f"https://checkout.paycom.uz/{encoded}"
    print(f"Testing URL: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')
        title = content.split("<title>")[1].split("</title>")[0] if "<title>" in content else "No title"
        print("Success! Title:", title)
    except Exception as e:
        print("Error:", e)

# Test only user_id
test_params(f"m={merchant_id};a=500000;ac.user_id=123")
