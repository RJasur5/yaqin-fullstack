import base64
import urllib.request

merchant_id = "69eef6070ba8aa967a862f8c"
params = f"m={merchant_id};a=500000;ac.user_id=123"
encoded = base64.b64encode(params.encode()).decode()
url = f"https://checkout.paycom.uz/{encoded}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
content = response.read().decode('utf-8')
print("Content snippets:")
import re
texts = re.findall(r'<p[^>]*>(.*?)</p>', content)
for t in texts:
    print(t)
texts = re.findall(r'<div class="error[^>]*>(.*?)</div>', content)
for t in texts:
    print(t)
    
if "vue" in content.lower():
    print("It's a Vue app, getting initial data...")
    match = re.search(r'window\.INITIAL_STATE\s*=\s*({.*?});', content)
    if match:
        print(match.group(1))
