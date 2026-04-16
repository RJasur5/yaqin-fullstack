import paramiko

def check():
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

        # Check containers
        print("--- Docker PS ---")
        print(run_sudo("docker ps -a"))
        
        # Check logs if backend is there
        print("--- Docker Compose Logs ---")
        print(run_sudo("docker compose -f /var/www/yaqin/docker-compose.yml logs --tail 20"))

    except Exception as e:
        print(f"Check failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check()
