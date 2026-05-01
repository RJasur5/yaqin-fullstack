import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

cmds = [
    'free -m',
    'top -bn1 | head -5',
    'df -h /',
    'docker stats --no-stream --format "{{.Name}}: CPU={{.CPUPerc}} MEM={{.MemUsage}}"',
    'docker logs findix-backend --tail 10 2>&1',
    # Check response time
    'time curl -sk https://yaqingo.uz/api/categories -o /dev/null -w "HTTP %{http_code} in %{time_total}s\\n"',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"STDERR: {err}")

ssh.close()
