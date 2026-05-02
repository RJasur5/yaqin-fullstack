import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Try sending to an Android token (to check if FCM itself works)
# Also try sending a data-only message (no APNs needed)
script = '''import json, urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests

sa_creds = service_account.Credentials.from_service_account_file(
    "/app/serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)
request = google.auth.transport.requests.Request()
sa_creds.refresh(request)

# Send data-only message (no notification) to test FCM without APNs
token = "dP0nEPp_eE84rlXj2YcYmR:APA91bEWgzEaiYGSGp9ovVgDvnojE3QuXLzUmQyPYJmZiyylZZwT9CZkHp2tyDlN1XrXc4UpQYleuv3n0454oqMX4LL3UnznYXRqd__8WiHTehiIC-xY6TY"
url = "https://fcm.googleapis.com/v1/projects/yaqin-app-22180/messages:send"

# Test 1: Data-only (no APNs notification)
body = json.dumps({
    "message": {
        "token": token,
        "data": {"type": "test", "message": "hello"}
    }
}).encode("utf-8")

req = urllib.request.Request(url, data=body, method="POST")
req.add_header("Authorization", "Bearer " + sa_creds.token)
req.add_header("Content-Type", "application/json")

try:
    response = urllib.request.urlopen(req)
    print("DATA-ONLY SUCCESS:", response.read().decode())
except Exception as e:
    print("DATA-ONLY ERROR:", e)
    if hasattr(e, "read"):
        print("Body:", e.read().decode())

# Test 2: Validate-only (dry run)
body2 = json.dumps({
    "validate_only": True,
    "message": {
        "token": token,
        "notification": {"title": "Test", "body": "Test"}
    }
}).encode("utf-8")

req2 = urllib.request.Request(url, data=body2, method="POST")
req2.add_header("Authorization", "Bearer " + sa_creds.token)
req2.add_header("Content-Type", "application/json")

try:
    response2 = urllib.request.urlopen(req2)
    print("VALIDATE SUCCESS:", response2.read().decode())
except Exception as e:
    print("VALIDATE ERROR:", e)
    if hasattr(e, "read"):
        print("Body:", e.read().decode())
'''

sftp = ssh.open_sftp()
with sftp.file('/home/yaqingo/test_data.py', 'w') as f:
    f.write(script)
sftp.close()

ssh.exec_command('docker cp /home/yaqingo/test_data.py findix-backend:/app/test_data.py')
time.sleep(1)
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_data.py')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
