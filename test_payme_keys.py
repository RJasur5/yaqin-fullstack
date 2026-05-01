import base64
import urllib.request
import urllib.error

merchant_id = "69eef6ba229f5694d6120a73"

params = f"m={merchant_id};a=500000;ac.user_id=123;ac.plan=day"
encoded = base64.b64encode(params.encode()).decode()
url = f"https://checkout.paycom.uz/{encoded}"
print("Testing URL:", url)

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    content = response.read().decode('utf-8')
    title = content.split("<title>")[1].split("</title>")[0] if "<title>" in content else "No title"
    print("Success! Title:", title)
except urllib.error.HTTPError as e:
    print("Error:", e.code)
