import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# 1. Get current FCM token from DB
stdin, stdout, stderr = ssh.exec_command('''docker exec findix-backend python3 -c "
from database import SessionLocal
from models import User
db = SessionLocal()
u = db.query(User).filter(User.id == 26).first()
print('FCM token:', u.fcm_token if u else 'NOT FOUND')
db.close()
"''')
token_output = stdout.read().decode().strip()
print(token_output)

# Extract token
fcm_token = token_output.split('FCM token: ')[1] if 'FCM token: ' in token_output else None
print(f"Token: {fcm_token[:40]}..." if fcm_token else "NO TOKEN!")

if fcm_token and fcm_token != 'None':
    # 2. Send test push
    script = f'''import json, urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests

sa_creds = service_account.Credentials.from_service_account_file(
    "/app/serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)
request = google.auth.transport.requests.Request()
sa_creds.refresh(request)

token = "{fcm_token}"
url = "https://fcm.googleapis.com/v1/projects/yaqin-app-22180/messages:send"
body = json.dumps({{
    "message": {{
        "token": token,
        "notification": {{"title": "Yaqin Test!", "body": "Push notification works!"}},
        "apns": {{
            "headers": {{"apns-push-type": "alert", "apns-priority": "10"}},
            "payload": {{"aps": {{"alert": {{"title": "Yaqin Test!", "body": "Push notification works!"}}, "sound": "default"}}}}
        }}
    }}
}}).encode("utf-8")

req = urllib.request.Request(url, data=body, method="POST")
req.add_header("Authorization", "Bearer " + sa_creds.token)
req.add_header("Content-Type", "application/json")

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS:", response.read().decode())
except Exception as e:
    print("ERROR:", e)
    if hasattr(e, "read"):
        print("Body:", e.read().decode())
'''
    sftp = ssh.open_sftp()
    with sftp.file('/home/yaqingo/test_new.py', 'w') as f:
        f.write(script)
    sftp.close()
    
    ssh.exec_command('docker cp /home/yaqingo/test_new.py findix-backend:/app/test_new.py')
    time.sleep(1)
    stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_new.py')
    print("\nPush result:")
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())

# 3. Check latest server logs
print("\n=== Latest server logs ===")
stdin, stdout, stderr = ssh.exec_command('docker logs --tail 20 findix-backend 2>&1 | grep -i "FCM\|NOTIFY\|ERROR\|push\|token"')
print(stdout.read().decode())

ssh.close()
