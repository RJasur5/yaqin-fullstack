import paramiko
import os
import time

def deploy_all():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    remote_base = "/home/yaqingo/yaqin-production"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    sftp = ssh.open_sftp()
    
    files = [
        "backend/routers/auth.py",
        "backend/routers/masters.py",
        "backend/routers/orders.py",
        "backend/routers/subscriptions.py",
        "backend/routers/clients.py",
        "backend/utils/security.py",
        "backend/schemas.py",
        "backend/models.py",
        "backend/main.py",
        "deploy/nginx.conf",
    ]
    
    for f in files:
        local_path = f.replace("/", os.sep)
        remote_path = f"{remote_base}/{f}"
        print(f"  Uploading {f}...")
        sftp.put(local_path, remote_path)
    
    sftp.close()
    
    # Rebuild backend
    print("Rebuilding and restarting backend...")
    cmd = f"cd {remote_base} && sudo -S docker compose up -d --build --force-recreate backend"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    # Restart nginx
    ssh.exec_command(f"echo {password} | sudo -S docker restart findix-nginx")
    
    time.sleep(5)
    
    # Verify: login test
    print("Verifying login...")
    stdin, stdout, stderr = ssh.exec_command("""curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"phone": "+998998426574", "password": "789789"}' | head -c 100""")
    resp = stdout.read().decode()
    print("Login response:", resp)
    
    if "access_token" in resp:
        print("LOGIN OK!")
    else:
        print("LOGIN FAILED!")
    
    # Verify: categories
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost/api/categories | head -c 100")
    resp = stdout.read().decode()
    print("Categories:", resp)
    
    ssh.close()
    print("Deploy complete!")

if __name__ == "__main__":
    deploy_all()
