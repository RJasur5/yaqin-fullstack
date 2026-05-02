import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

script = '''
import firebase_admin
print("firebase_admin:", firebase_admin.__version__)

try:
    import httpx
    print("httpx:", httpx.__version__)
except:
    print("httpx: not installed")

try:
    import requests
    print("requests:", requests.__version__)
except:
    print("requests: not installed")

try:
    import google.auth
    print("google-auth:", google.auth.__version__)
except:
    print("google-auth: not installed")

# Try with explicit httpOptions
from firebase_admin import credentials, messaging
try:
    firebase_admin.delete_app(firebase_admin.get_app())
except:
    pass

cred = credentials.Certificate("/app/serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)

token = "eGRdT3u2YUVfspv07-uva9:APA91bFpoKi0RSDbOBKTvh15aDyHnuIbazJt8xVXQyvlTv6bL_Z-vka8k5G1_aFDC7cJM_dcLEvNzIhCLyvFyukkzttfnGtNBSCdFxGYUyQpKfygBsVawxE"

# Try using the low-level API
import google.auth.transport.requests
from google.oauth2 import service_account
import json

sa_creds = service_account.Credentials.from_service_account_file(
    "/app/serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)
request = google.auth.transport.requests.Request()
sa_creds.refresh(request)

import urllib.request
url = "https://fcm.googleapis.com/v1/projects/yaqin-app-22180/messages:send"
body = json.dumps({
    "message": {
        "token": token,
        "notification": {
            "title": "Test Yaqin",
            "body": "Push works!"
        }
    }
}).encode("utf-8")

req = urllib.request.Request(url, data=body, method="POST")
req.add_header("Authorization", f"Bearer {sa_creds.token}")
req.add_header("Content-Type", "application/json")

try:
    response = urllib.request.urlopen(req)
    print("DIRECT API SUCCESS:", response.read().decode())
except Exception as e:
    print("DIRECT API ERROR:", e)
    if hasattr(e, 'read'):
        print("Response body:", e.read().decode())
'''

sftp = ssh.open_sftp()
with sftp.file('/home/yaqingo/test_push3.py', 'w') as f:
    f.write(script)
sftp.close()

ssh.exec_command('docker cp /home/yaqingo/test_push3.py findix-backend:/app/test_push3.py')
time.sleep(1)
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_push3.py')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
