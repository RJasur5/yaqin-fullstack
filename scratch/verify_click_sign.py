import hashlib

def check_click_sign():
    # Data from logs
    click_trans_id = '3644424925'
    service_id = '101893'
    secret_key = 'BifkWPorptsd'
    merchant_trans_id = '40:day:master'
    amount = '5000'
    action = '0'
    sign_time = '2026-04-27 16:43:48'
    received_sign = '059e85f78851b627b6542632bf1ddf60'
    
    # Click signature formula for action 0:
    # md5(click_trans_id + service_id + secret_key + merchant_trans_id + amount + action + sign_time)
    
    sign_str = f"{click_trans_id}{service_id}{secret_key}{merchant_trans_id}{amount}{action}{sign_time}"
    calculated_sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    print(f"String to hash: {sign_str}")
    print(f"Calculated: {calculated_sign}")
    print(f"Received:   {received_sign}")
    print(f"Match:      {calculated_sign == received_sign}")

if __name__ == "__main__":
    check_click_sign()
