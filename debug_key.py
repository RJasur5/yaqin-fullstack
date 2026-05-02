import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Check the key file content (just project_id and client_email, not the private key)
stdin, stdout, stderr = ssh.exec_command('''docker exec findix-backend python3 -c "
import json
with open('/app/serviceAccountKey.json') as f:
    data = json.load(f)
print('type:', data.get('type'))
print('project_id:', data.get('project_id'))
print('client_email:', data.get('client_email'))
print('private_key_id:', data.get('private_key_id'))
print('private_key starts with:', data.get('private_key', '')[:50])
print('private_key ends with:', data.get('private_key', '')[-50:])
print('token_uri:', data.get('token_uri'))

# Try to get access token manually
from google.oauth2 import service_account
import google.auth.transport.requests

creds = service_account.Credentials.from_service_account_file(
    '/app/serviceAccountKey.json',
    scopes=['https://www.googleapis.com/auth/firebase.messaging']
)
try:
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    print('ACCESS TOKEN obtained:', creds.token[:30] if creds.token else 'None')
except Exception as e:
    print('AUTH ERROR:', e)
"''')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
