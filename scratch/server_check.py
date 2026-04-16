import paramiko
import time

def diagnose_server():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=10)
        print("CONNECTED TO SERVER!")

        def run_remote_cmd(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            # Wait for some output
            time.sleep(2)
            if stdout.channel.recv_ready():
                return stdout.channel.recv(4096).decode('utf-8', 'ignore')
            return "No output"

        # 1. Container status
        print("--- Docker PS ---")
        print(run_remote_cmd("docker ps -a"))
        
        # 2. Detailed Nginx Logs
        print("--- Nginx Logs ---")
        print(run_remote_cmd("docker logs findix-nginx"))
        
        # 3. Port check
        print("--- Port 80 Check ---")
        print(run_remote_cmd("ss -tulpn | grep :80"))

    except Exception as e:
        print(f"FAILED TO CONNECT: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    diagnose_server()
