import urllib.request
import re

url = "https://payme.uz/fallback/merchant/?id=69eef6ba229f5694d6120a73"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    # Print all input tags and their names
    inputs = re.findall(r'<input[^>]+name=["\'](.*?)["\'][^>]*>', html)
    print("Found inputs:", inputs)
    
    # Also check vue state
    match = re.search(r'window\.INITIAL_STATE\s*=\s*({.*?});', html)
    if match:
        print("INITIAL_STATE length:", len(match.group(1)))
        import json
        state = json.loads(match.group(1))
        # state -> api -> checkout -> merchant 
        # try to find the fields array
        for key, val in state.items():
            if 'merchant' in str(val).lower():
                print("Possible merchant data in:", key)
except Exception as e:
    print("Error:", e)
