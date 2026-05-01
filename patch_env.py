import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
project_dir = '/home/yaqingo/yaqin-production'

print(f"Connecting to {host}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, username=user, password=password, timeout=30)
    print("Connected!")
    
    # Use sed to replace PAYME_USE_TEST=true with PAYME_USE_TEST=false
    cmd = (
        f"cd {project_dir}/backend && "
        f"sed -i 's/PAYME_USE_TEST=true/PAYME_USE_TEST=false/g' .env && "
        f"cat .env | grep PAYME_USE_TEST && "
        f"cd .. && "
        f"docker compose restart backend"
    )
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"OUTPUT:\n{out}")
    if err: print(f"STDERR:\n{err}")
    print("Environment patched and backend restarted.")

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
