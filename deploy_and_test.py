import paramiko, time, os
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
sftp = ssh.open_sftp()

# Upload updated fcm_service.py
sftp.put(os.path.join(os.getcwd(), 'backend', 'services', 'fcm_service.py'), '/home/yaqingo/yaqin-production/backend/services/fcm_service.py')
# Upload updated orders.py
sftp.put(os.path.join(os.getcwd(), 'backend', 'routers', 'orders.py'), '/home/yaqingo/yaqin-production/backend/routers/orders.py')
sftp.close()
print("Files uploaded")

# Rebuild
print("Rebuilding...")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose up -d --build backend')
print(stdout.read().decode())
print(stderr.read().decode())

time.sleep(5)

# Test with sandbox flag
test_code = """
import firebase_admin
from firebase_admin import credentials, messaging
import json, urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests

# Get access token
sa_creds = service_account.Credentials.from_service_account_file(
    "/app/serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)
request = google.auth.transport.requests.Request()
sa_creds.refresh(request)

token = "eGRdT3u2YUVfspv07-uva9:APA91bFpoKi0RSDbOBKTvh15aDyHnuIbazJt8xVXQyvlTv6bL_Z-vka8k5G1_aFDC7cJM_dcLEvNzIhCLyvFyukkzttfnGtNBSCdFxGYUyQpKfygBsVawxE"
url = "https://fcm.googleapis.com/v1/projects/yaqin-app-22180/messages:send"
body = json.dumps({
    "message": {
        "token": token,
        "notification": {"title": "Test Yaqin", "body": "Push test!"},
        "apns": {
            "headers": {"apns-push-type": "alert", "apns-priority": "10"},
            "payload": {
                "aps": {"alert": {"title": "Test Yaqin", "body": "Push test!"}, "sound": "default", "badge": 1}
            }
        }
    }
}).encode("utf-8")

req = urllib.request.Request(url, data=body, method="POST")
req.add_header("Authorization", "Bearer " + sa_creds.token)
req.add_header("Content-Type", "application/json")

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS:", response.read().decode())
except Exception as e:
    print("ERROR:", e)
    if hasattr(e, 'read'):
        print("Body:", e.read().decode())
"""

sftp2 = ssh.open_sftp()
with sftp2.file('/home/yaqingo/test_sandbox.py', 'w') as f:
    f.write(test_code)
sftp2.close()
ssh.exec_command('docker cp /home/yaqingo/test_sandbox.py findix-backend:/app/test_sandbox.py')
time.sleep(1)
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_sandbox.py')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
print("Done!")
