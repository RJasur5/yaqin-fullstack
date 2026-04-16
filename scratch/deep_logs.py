import paramiko

def deep_logs():
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

        # 1. Check Compose Config
        print("--- Docker Compose Config Check ---")
        print(run_sudo("cd /var/www/yaqin && docker compose config"))
        
        # 2. Check Build Logs
        print("--- Docker Compose Build Logs ---")
        print(run_sudo("cd /var/www/yaqin && docker compose logs --tail 50"))

    except Exception as e:
        print(f"DIAGNOSTIC FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deep_logs()
