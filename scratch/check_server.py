import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e')

commands = [
    'echo "=== CPU ===" && top -bn1 | head -5',
    'echo "=== RAM ===" && free -h',
    'echo "=== DISK ===" && df -h / /var',
    'echo "=== DOCKER ===" && docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"',
    'echo "=== UPTIME ===" && uptime',
]

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print('ERR:', err)

ssh.close()
