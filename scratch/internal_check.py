import paramiko

def internal_check():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            return stdout.read().decode()

        # 1. Check Docker PS
        print("--- Docker PS ---")
        print(run_sudo("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"))
        
        # 2. Try to connect from INSIDE the server
        print("--- Internal Connection Test (curl localhost:80) ---")
        print(run_sudo("curl -I http://localhost:80/app.apk"))

    except Exception as e:
        print(f"INTERNAL CHECK FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    internal_check()
