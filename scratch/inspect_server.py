import paramiko

def inspect():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        print("--- DOCKERFILE ---")
        stdin, stdout, stderr = client.exec_command("cat yaqin-production/backend/Dockerfile")
        print(stdout.read().decode())
        
        print("--- REQUIREMENTS.TXT ---")
        stdin, stdout, stderr = client.exec_command("cat yaqin-production/backend/requirements.txt")
        print(stdout.read().decode())
        
        print("--- DOCKER PS ---")
        stdin, stdout, stderr = client.exec_command("docker ps")
        print(stdout.read().decode())

        print("--- TRYING CLEAN REBUILD WITH OUTPUT ---")
        cmd = "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose build --no-cache backend"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect()
