import paramiko
import time

def final_launch():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_cmd(command):
            print(f"Executing: {command}")
            # We use bash -c to handle cd and redirects properly
            stdin, stdout, stderr = client.exec_command(f'sudo -S bash -c "{command}"', get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            # Read output in real-time
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    print(stdout.channel.recv(1024).decode(errors='ignore'), end="")
                time.sleep(0.1)
            return stdout.read().decode()

        # Final Launch Sequence
        print("Launching project...")
        run_cmd("cd /var/www/yaqin && docker compose up -d --build")
        
        print("Waiting 10s...")
        time.sleep(10)
        
        # Migration
        print("Migrating data...")
        run_cmd("docker cp /home/yaqingo/findix.db findix-backend:/app/findix.db")
        run_cmd('docker exec -i findix-backend bash -c "echo y | python migrate_sqlite_to_postgres.py"')
        
        print("SUCCESS! ALL SYSTEMS READY.")

    except Exception as e:
        print(f"LAUNCH FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    final_launch()
