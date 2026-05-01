import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e', timeout=30)

sftp = ssh.open_sftp()
print("Uploading nginx.conf...")
sftp.put(
    r'deploy\nginx.conf',
    '/home/yaqingo/yaqin-production/deploy/nginx.conf'
)
sftp.close()
print("nginx.conf uploaded.")

# Reload nginx config (no downtime)
stdin, stdout, stderr = ssh.exec_command(
    'docker exec findix-nginx nginx -t && docker exec findix-nginx nginx -s reload'
)
out = stdout.read().decode()
err = stderr.read().decode()
print("nginx test:", out, err)

time.sleep(2)

# Final test
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST https://yaqingo.uz/api/auth/login '
    '-H "Content-Type: application/json" '
    '-d \'{"phone":"+998998426574","password":"wrongpass"}\' '
    '| head -c 200'
)
result = stdout.read().decode()
print("\nAPI test result:", result)

if '<html>' in result:
    print("STILL 502! Restarting nginx container...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd /home/yaqingo/yaqin-production && docker compose restart nginx'
    )
    print(stdout.read().decode(), stderr.read().decode())
else:
    print("SUCCESS! API returns JSON correctly.")

ssh.close()
