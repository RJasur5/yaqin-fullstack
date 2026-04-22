import paramiko
import time

def force_sqlite_compose():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Modifying docker-compose.yml to enforce SQLite...")
    # Update docker compose to explicitly remove postgresql injection and use sqlite
    code = """
import ruamel.yaml
import sys

yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True

with open('/home/yaqingo/yaqin-production/docker-compose.yml', 'r') as f:
    data = yaml.load(f)

if 'environment' in data['services']['backend']:
    if 'DATABASE_URL' in data['services']['backend']['environment']:
        data['services']['backend']['environment']['DATABASE_URL'] = 'sqlite:///findix.db'
elif 'env_file' in data['services']['backend']:
    pass

with open('/home/yaqingo/yaqin-production/docker-compose.yml', 'w') as f:
    yaml.dump(data, f)
"""
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > force_sqlite.py"')
    
    print("Writing new docker-compose via sed...")
    # Much simpler to just replace via sed
    ssh.exec_command(f"sed -i 's|DATABASE_URL: postgresql://.*|DATABASE_URL: sqlite:///findix.db|g' /home/yaqingo/yaqin-production/docker-compose.yml")
    
    print("Making sure .env is correctly set...")
    ssh.exec_command("echo 'DATABASE_URL=sqlite:///findix.db\nSECRET_KEY=findix-secret-key-2026-change-in-production\nALGORITHM=HS256\nTOKEN_EXPIRE_DAYS=30\nLOG_LEVEL=INFO' > /home/yaqingo/yaqin-production/backend/.env")
    
    print("Restarting docker compose...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose down')
    time.sleep(3)
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d')
    time.sleep(5)
    
    print("Verifying ENV in container...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend env | grep DATABASE_URL")
    stdin.write(password + "\n")
    stdin.flush()
    print("NEW ENV:", stdout.read().decode())
    
    print("Verifying row counts in container...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 -c 'from database import SessionLocal; from models import Order; db=SessionLocal(); print(db.query(Order).count()); db.close()'")
    stdin.write(password + "\n")
    stdin.flush()
    print("Orders inside:", stdout.read().decode())
    
    ssh.close()
    print("Done!")

if __name__ == "__main__":
    force_sqlite_compose()
