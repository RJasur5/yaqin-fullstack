import paramiko
import sys

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(host, username=user, password=password, timeout=10)
    cmd = "docker logs --tail 200 findix-backend | grep -i payme"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("Logs:")
    print(stdout.read().decode())
except Exception as e:
    print("Error:", e)
finally:
    ssh.close()
