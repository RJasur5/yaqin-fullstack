import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command('''docker exec findix-backend python3 -c "
import firebase_admin
print('firebase_admin version:', firebase_admin.__version__)

# Test with httpx/requests to see if it's a network issue
import firebase_admin
from firebase_admin import credentials, messaging

# Delete existing app if any
try:
    firebase_admin.delete_app(firebase_admin.get_app())
except:
    pass

cred = credentials.Certificate('/app/serviceAccountKey.json')
app = firebase_admin.initialize_app(cred)
print('App name:', app.name)
print('Project ID:', app.project_id)

# Try sending
token = 'eGRdT3u2YUVfspv07-uva9:APA91bFpoKi0RSDbOBKTvh15aDyHnuIbazJt8xVXQyvlTv6bL_Z-vka8k5G1_aFDC7cJM_dcLEvNzIhCLyvFyukkzttfnGtNBSCdFxGYUyQpKfygBsVawxE'
msg = messaging.Message(
    notification=messaging.Notification(title='Test', body='Test push'),
    token=token,
)
try:
    result = messaging.send(msg)
    print('SEND SUCCESS:', result)
except Exception as e:
    print('SEND ERROR:', type(e).__name__, str(e)[:200])
"
''')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
