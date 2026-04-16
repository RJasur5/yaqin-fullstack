import paramiko
import time

def ultimate_fix():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED FOR ULTIMATE FIX!")

        def run_sudo(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            # Wait for completion
            while not stdout.channel.exit_status_ready():
                time.sleep(0.1)
            return stdout.read().decode()

        # 1. Prepare Directory
        print("Cleaning and preparing /var/www/yaqin...")
        run_sudo("rm -rf /var/www/yaqin && mkdir -p /var/www/yaqin/downloads")
        
        # 2. Extract Project
        print("Extracting updated project...")
        run_sudo("unzip -o /home/yaqingo/project_clean.zip -d /var/www/yaqin/")
        
        # 3. Move APK
        print("Setting up APK download link...")
        run_sudo("cp /home/yaqingo/app-release.apk /var/www/yaqin/downloads/app.apk")
        run_sudo("chmod 644 /var/www/yaqin/downloads/app.apk") # Make sure it's readable
        
        # 4. Launch Services
        print("Stopping any old containers and launching new ones...")
        run_sudo("cd /var/www/yaqin && docker compose down")
        run_sudo("cd /var/www/yaqin && docker compose up -d --build")
        
        # 5. Migrate Data
        print("Waiting for DB to breathe (15s)...")
        time.sleep(15)
        print("Migrating real data SQLite -> Postgres...")
        run_sudo("docker cp /home/yaqingo/findix.db findix-backend:/app/findix.db")
        result = run_sudo('docker exec -i findix-backend bash -c "echo y | python migrate_sqlite_to_postgres.py"')
        print(f"Migration finished. Result length: {len(result)}")
        
        print("--- ALL SYSTEMS ONLINE! ---")

    except Exception as e:
        print(f"ULTIMATE FIX FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    ultimate_fix()
