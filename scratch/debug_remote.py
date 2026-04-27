import paramiko

def get_logs():
    hostname = "95.182.118.245"
    username = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        print("Connected. Fetching backend logs...")
        
        # Get the last 50 lines of logs from the backend container
        stdin, stdout, stderr = client.exec_command("docker logs --tail 50 findix-backend")
        print("\n--- BACKEND LOGS ---")
        print(stdout.read().decode('utf-8', errors='ignore'))
        print(stderr.read().decode('utf-8', errors='ignore'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    get_logs()
