import paramiko

def check_mounts():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker inspect findix-backend")
    stdin.write(password + "\n")
    stdin.flush()
    import json
    data = json.loads(stdout.read().decode())
    print("Mounts for findix-backend:")
    for mount in data[0].get("Mounts", []):
        print(f"  {mount['Source']} -> {mount['Destination']}")
    
    # Check what is in /home/yaqingo/yaqin-production
    stdin, stdout, stderr = ssh.exec_command("ls -la ~/yaqin-production/backend/routers/orders.py")
    print("File on host:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_mounts()
