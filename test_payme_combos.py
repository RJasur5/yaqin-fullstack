import base64
import urllib.request
import re

merchant_id = "69eef6ba229f5694d6120a73"

def test_params(params_str):
    encoded = base64.b64encode(params_str.encode()).decode()
    url = f"https://checkout.paycom.uz/{encoded}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')
        match = re.search(r'window\.INITIAL_STATE\s*=\s*({.*?});', content)
        if match:
            print("Response:", match.group(1)[:150]) # Print beginning of JSON state
        else:
            print("No state found")
    except Exception as e:
        print("Error:", e)

# Let's test combinations!
print("Testing user_id and plan")
test_params(f"m={merchant_id};a=500000;ac.user_id=123;ac.plan=day")

print("Testing only user_id")
test_params(f"m={merchant_id};a=500000;ac.user_id=123")

print("Testing only plan")
test_params(f"m={merchant_id};a=500000;ac.plan=day")

print("Testing user_id, plan, and role")
test_params(f"m={merchant_id};a=500000;ac.user_id=123;ac.plan=day;ac.role=master")
