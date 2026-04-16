import paramiko

def diagnose_network():
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

        # 1. Check if Nginx is listening
        print("--- Ports Listening (netstat) ---")
        # Install net-tools if missing
        client.exec_command("sudo apt-get install -y net-tools")
        print(run_sudo("netstat -tulpn | grep -E ':(80|443)'"))
        
        # 2. Check Firewall (ufw)
        print("--- Firewall Status (ufw) ---")
        print(run_sudo("ufw status"))
        
        # 3. Check Nginx Logs
        print("--- Nginx Container Logs ---")
        print(run_sudo("docker logs findix-nginx --tail 20"))

    except Exception as e:
        print(f"DIAGNOSTIC FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    diagnose_network()
