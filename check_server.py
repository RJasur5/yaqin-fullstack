import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e', timeout=30)

# Test API
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST https://yaqingo.uz/api/auth/register '
    '-H "Content-Type: application/json" '
    '-d \'{"phone":"+998868686868","password":"test123","role":"client"}\' '
    '| head -c 500'
)
print("Register test:", stdout.read().decode())
print("ERR:", stderr.read().decode()[:300])

# Check nginx logs
stdin, stdout, stderr = ssh.exec_command('docker logs findix-nginx --tail=10 2>&1')
print("\nNginx logs:", stdout.read().decode())

ssh.close()
