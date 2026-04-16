import paramiko
import time

def total_deploy():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(cmd):
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S bash -c '{cmd}'", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            # Wait and read
            time.sleep(5)
            return stdout.read().decode('utf-8', 'ignore')

        # 1. Clear Docker mess
        print("Clearing old containers...")
        run_sudo("docker stop $(docker ps -aq) || true")
        run_sudo("docker rm $(docker ps -aq) || true")
        
        # 2. Setup folders
        print("Setting up folders...")
        run_sudo("mkdir -p /var/www/yaqin/downloads")
        run_sudo("cp -r /home/yaqingo/project/* /var/www/yaqin/")
        run_sudo("cp /home/yaqingo/app.apk /var/www/yaqin/downloads/app.apk")
        run_sudo("chmod -R 777 /var/www/yaqin")
        
        # 3. Launch
        print("Launching Docker Compose...")
        res = run_sudo("cd /var/www/yaqin && docker compose up -d --build")
        print(f"Launch result: {res[:200]}")
        
        # 4. Wait and verify
        print("Waiting for startup...")
        time.sleep(15)
        
        # 5. Migration
        print("Migrating database...")
        run_sudo("docker cp /home/yaqingo/findix.db findix-backend:/app/findix.db")
        migration = run_sudo("docker exec -i findix-backend python migrate_sqlite_to_postgres.py")
        print(f"Migration: {migration[:100]}")
        
        # 6. Port 80 check
        print("Final verification...")
        status = run_sudo("ss -tulpn | grep :80")
        if ":80" in status:
            print("--- SUCCESS: PORT 80 IS OPEN! ---")
        else:
            print("--- WARNING: PORT 80 STILL CLOSED! ---")

    except Exception as e:
        print(f"TOTAL DEPLOY FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    total_deploy()
