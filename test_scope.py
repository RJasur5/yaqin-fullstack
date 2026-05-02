import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Try sending with legacy FCM API (uses server key, not OAuth)
# First check if there's a server key
script = '''
import json, urllib.request

# Try FCM v1 with explicit project
from google.oauth2 import service_account
import google.auth.transport.requests

sa_creds = service_account.Credentials.from_service_account_file(
    "/app/serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
request = google.auth.transport.requests.Request()
sa_creds.refresh(request)
print("Access token:", sa_creds.token[:30])

# Check what APIs the service account has access to
url = "https://fcm.googleapis.com/v1/projects/yaqin-app-22180/messages:send"
body = json.dumps({
    "message": {
        "token": "dP0nEPp_eE84rlXj2YcYmR:APA91bEWgzEaiYGSGp9ovVgDvnojE3QuXLzUmQyPYJmZiyylZZwT9CZkHp2tyDlN1XrXc4UpQYleuv3n0454oqMX4LL3UnznYXRqd__8WiHTehiIC-xY6TY",
        "notification": {"title": "Test", "body": "Push!"}
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
    if hasattr(e, "read"):
        resp_body = e.read().decode()
        print("Body:", resp_body)
        # Check if it's specifically APNs error or auth error
        import json as j
        try:
            err = j.loads(resp_body)
            details = err.get("error", {}).get("details", [])
            for d in details:
                print("Detail type:", d.get("@type"))
                if "ApnsError" in d.get("@type", ""):
                    print("APNs status:", d.get("statusCode"), d.get("reason"))
        except:
            pass
'''

sftp = ssh.open_sftp()
with sftp.file('/home/yaqingo/test_scope.py', 'w') as f:
    f.write(script)
sftp.close()

ssh.exec_command('docker cp /home/yaqingo/test_scope.py findix-backend:/app/test_scope.py')
time.sleep(1)
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_scope.py')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
