import paramiko

def verify():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # 1. Check if the code inside the container matches our fix
        print("Checking code inside container...")
        cmd_check = "docker exec findix-backend grep -n 'replace(tzinfo=None)' /app/routers/subscriptions.py"
        stdin, stdout, stderr = client.exec_command(cmd_check)
        print("Grep result:\n", stdout.read().decode())
        
        # 2. Check latest logs
        print("Checking latest logs...")
        stdin, stdout, stderr = client.exec_command("docker logs --tail 30 findix-backend")
        print("Latest logs:\n", stdout.read().decode() + stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    verify()
