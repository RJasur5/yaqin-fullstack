import base64

merchant_id = "69eef6070ba8aa967a862f8c"
amount_tiyin = 500000
account = {'user_id': 123, 'plan': 'day', 'role': 'master'}

params = f"m={merchant_id};a={amount_tiyin}"
for k, v in account.items():
    params += f";ac.{k}={v}"

encoded_params = base64.b64encode(params.encode()).decode()
print(f"URL: https://checkout.paycom.uz/{encoded_params}")
