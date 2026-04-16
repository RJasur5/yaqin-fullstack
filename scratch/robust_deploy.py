import paramiko
import time

def run_command(client, command, password):
    print(f"Executing: {command}")
    stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
    stdin.write(password + '\n')
    stdin.flush()
    # Pulling output slowly to avoid buffer issues
    output = ""
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(1024).decode('utf-8', 'ignore')
            output += chunk
            print(chunk, end="")
        time.sleep(0.1)
    return output

def main():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=10)
        print("CONNECTED!")

        # 1. Force fix
        run_command(client, "dpkg --configure -a", password)
        run_command(client, "apt-get install -f -y", password)
        
        # 2. Install Docker if missing
        res = run_command(client, "docker --version || echo 'MISSING'", password)
        if "MISSING" in res:
            run_command(client, "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh", password)
            run_command(client, f"usermod -aG docker {user}", password)

        print("DOCKER READY!")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
