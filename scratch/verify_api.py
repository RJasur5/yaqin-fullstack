import paramiko
import time

def verify():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e')
    
    # This is a robust test script that will run INSIDE the backend container
    # It uses its own internal libraries to avoid networking issues
    test_code = """
import requests
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'findix-secret-key-2026-change-in-production'
ALGORITHM = 'HS256'

def run_test(i):
    payload = {'sub': '26', 'role': 'admin', 'exp': datetime.utcnow() + timedelta(days=1)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'subcategory_id': 1,
        'description': f'AUTO-TEST-PROD-{i}',
        'city': 'Toshkent',
        'district': 'Chilonzor',
        'price': 100,
        'include_lunch': False,
        'include_taxi': False
    }
    
    # Internal docker connection to localhost:8000 (where uvicorn runs inside the container)
    try:
        res = requests.post('http://localhost:8000/api/orders', json=data, headers=headers)
        print(f'RUN {i}: STATUS {res.status_code} | RESP: {res.text[:50]}...')
    except Exception as e:
        print(f'RUN {i}: FAILED | {e}')

if __name__ == '__main__':
    for i in range(1, 4):
        run_test(i)
"""

    print("EXECUTING 3-STEP VERIFICATION ON SERVER...")
    # Escape properly for the shell
    # Actually, we can just write the file to /tmp/verify.py first to be 100% safe
    sftp = client.open_sftp()
    with sftp.file('/tmp/verify_api_internal.py', 'w') as f:
        f.write(test_code)
    sftp.close()
    
    cmd = 'docker exec -i findix-backend python -c \"$(cat /tmp/verify_api_internal.py)\"'
    stdin, stdout, stderr = client.exec_command(cmd)
    
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    print("RESULTS:")
    print(output)
    if error:
        print("ERRORS:")
        print(error)
    
    client.close()

if __name__ == '__main__':
    verify()
