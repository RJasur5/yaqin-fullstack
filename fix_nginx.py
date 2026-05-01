import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e', timeout=30)

print("Restarting nginx to refresh backend IP...")
stdin, stdout, stderr = ssh.exec_command(
    'cd /home/yaqingo/yaqin-production && docker compose restart nginx'
)
print(stdout.read().decode())
print("ERR:", stderr.read().decode())

# Test again
import time
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST https://yaqingo.uz/api/auth/login '
    '-H "Content-Type: application/json" '
    '-d \'{"phone":"+998998426574","password":"test"}\' '
    '| head -c 200'
)
print("\nTest result:", stdout.read().decode())

ssh.close()
print("Done!")
