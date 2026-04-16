import paramiko
import time

def force_migration():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        # Start interactive shell
        chan = client.invoke_shell()
        
        def send_cmd(cmd, wait_for=None):
            print(f"Sending: {cmd.strip()}")
            chan.send(cmd)
            time.sleep(2)
            out = chan.recv(9999).decode('utf-8', 'ignore')
            print(f"Server Response:\n{out}")
            return out

        # 1. Run command
        cmd = "sudo docker exec -i findix-backend python migrate_sqlite_to_postgres.py\n"
        resp = send_cmd(cmd)
        
        # 2. Handle sudo if needed
        if "[sudo]" in resp:
            send_cmd(password + "\n")
            
        # 3. Handle migration prompt
        time.sleep(3) # Give it time to think
        resp = chan.recv(9999).decode('utf-8', 'ignore')
        print(f"Buffer Check:\n{resp}")
        
        if "Continue? (y/n):" in resp or "delete all existing data" in resp:
            send_cmd("y\n")
        
        # 4. Wait for finish
        print("Waiting for migration to finish...")
        for _ in range(10):
            time.sleep(3)
            out = chan.recv(9999).decode('utf-8', 'ignore')
            print(out)
            if "successfully" in out.lower() or "completed" in out.lower():
                print("--- MIGRATION FINISHED! ---")
                break

    except Exception as e:
        print(f"FORCE MIGRATION FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    force_migration()
