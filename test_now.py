import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

script = '''import json, urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests

sa_creds = service_account.Credentials.from_service_account_file(
    "/app/serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)
request = google.auth.transport.requests.Request()
sa_creds.refresh(request)

token = "d2V5Wssd5U8RqWMREp9_yE:APA91bE4T_QPEeSPPiIm7cXd6hf6Mu1JHvOSTrib-6Zp0k7rFBa063ASfjsZSSfLs1fnycVYHxux2Db6I7nutoqKPQCcjVMfqMaFxqD_ebsHwVI_BCeIX-s"
url = "https://fcm.googleapis.com/v1/projects/yaqin-app-22180/messages:send"
body = json.dumps({
    "message": {
        "token": token,
        "notification": {"title": "Yaqin!", "body": "Push notifications work!"},
        "apns": {
            "headers": {"apns-push-type": "alert", "apns-priority": "10"},
            "payload": {"aps": {"alert": {"title": "Yaqin!", "body": "Push notifications work!"}, "sound": "default"}}
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
    if hasattr(e, "read"):
        print("Body:", e.read().decode())
'''

sftp = ssh.open_sftp()
with sftp.file('/home/yaqingo/test_now.py', 'w') as f:
    f.write(script)
sftp.close()

ssh.exec_command('docker cp /home/yaqingo/test_now.py findix-backend:/app/test_now.py')
time.sleep(1)
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_now.py')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
