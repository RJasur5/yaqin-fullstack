import paramiko
import time

def check_server_load():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    print(f"Connecting to {host}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=15)
        print("CONNECTED!")

        def run_cmd(cmd, use_sudo=False):
            full_cmd = f"sudo -S {cmd}" if use_sudo else cmd
            stdin, stdout, stderr = client.exec_command(f"{full_cmd}", get_pty=True)
            if use_sudo:
                stdin.write(password + '\n')
                stdin.flush()
            
            # Read output
            output = stdout.read().decode('utf-8', 'ignore')
            return output

        print("\n=== SYSTEM UPTIME & LOAD AVERAGE ===")
        print(run_cmd("uptime"))

        print("\n=== MEMORY USAGE (MB) ===")
        print(run_cmd("free -m"))

        print("\n=== CPU USAGE (TOP 5 PROCESSES) ===")
        print(run_cmd("ps -eo pcpu,pmem,comm --sort=-pcpu | head -n 6"))

        print("\n=== DISK USAGE ===")
        print(run_cmd("df -h /"))

        print("\n=== DOCKER CONTAINER STATS ===")
        print(run_cmd("docker stats --no-stream"))

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_server_load()
