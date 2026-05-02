import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

fcm_token = "eGRdT3u2YUVfspv07-uva9:APA91bFpoKi0RSDbOBKTvh15aDyHnuIbazJt8xVXQyvlTv6bL_Z-vka8k5G1_aFDC7cJM_dcLEvNzIhCLyvFyukkzttfnGtNBSCdFxGYUyQpKfygBsVawxE"

# Write the test script to the container first
test_script = f'''
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("/app/serviceAccountKey.json")
try:
    app = firebase_admin.get_app()
except ValueError:
    app = firebase_admin.initialize_app(cred)

token = "{fcm_token}"
message = messaging.Message(
    notification=messaging.Notification(title="Test Yaqin", body="Push works!"),
    token=token,
)
try:
    response = messaging.send(message)
    print("SUCCESS:", response)
except Exception as e:
    print("ERROR:", e)
'''

# Write script to container
sftp = ssh.open_sftp()
with sftp.file('/home/yaqingo/test_push.py', 'w') as f:
    f.write(test_script)
sftp.close()

# Copy into container and run
ssh.exec_command('docker cp /home/yaqingo/test_push.py findix-backend:/app/test_push.py')
import time
time.sleep(1)
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_push.py')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
