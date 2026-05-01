import base64
import urllib.request

merchant_id = "69eef6070ba8aa967a862f8c" # PROD
merchant_id2 = "69eef6ba229f5694d6120a73" # FALLBACK LINK

def test(m_id, account_dict):
    params = f"m={m_id};a=500000"
    for k, v in account_dict.items():
        params += f";ac.{k}={v}"
    encoded = base64.b64encode(params.encode()).decode()
    url = f"https://checkout.paycom.uz/{encoded}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')
        title = content.split("<title>")[1].split("</title>")[0] if "<title>" in content else "No title"
        print(f"[{m_id}] {account_dict} -> {title}")
    except Exception as e:
        print(f"[{m_id}] {account_dict} -> Error")

combos = [
    {"user_id": 123},
    {"user_id": 123, "plan": "day"},
    {"user_id": 123, "tarif": "day"},
    {"user_id": 123, "plan_name": "day"},
    {"user_id": 123, "plan": "day", "role": "master"},
    {"order_id": 123},
]

for c in combos:
    test(merchant_id, c)
    test(merchant_id2, c)
