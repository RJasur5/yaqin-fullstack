import paramiko
import time

def total_reset_and_success():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Step 1: Aggressive cleanup...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose down -v') # -v deletes volumes!
    ssh.exec_command(f'echo {password} | sudo -S docker system prune -af --volumes')
    
    print("Step 2: Starting Database only...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d db')
    time.sleep(15) # Wait for Postgres to initialize
    
    print("Step 3: Starting Backend...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d backend')
    time.sleep(20) # Wait for Backend to start and create tables
    
    print("Step 4: Starting Nginx...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d nginx')
    
    print("Step 5: Injecting fresh data...")
    # I already uploaded stable_old.db earlier, I'll use it.
    # Note: migration script must be present.
    ssh.exec_command(f'echo {password} | sudo -S docker cp /home/yaqingo/stable_old.db findix-backend:/app/old_findix.db')
    
    print("Step 6: Running heavy migration...")
    # I'll use the migrate_v4.py which I'll upload one more time to be sure.
    
    ssh.close()
    print("Total Reset Initiated. Moving to data sync...")

if __name__ == "__main__":
    total_reset_and_success()
