import paramiko
import time

def final_check():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # Wait for restart
    time.sleep(5)
    
    # 1. Check containers are running
    print("=== CONTAINER STATUS ===")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker ps --format '{{.Names}} {{.Status}}'")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    # 2. Check backend logs for errors
    print("=== BACKEND LOGS (last 20) ===")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-backend --tail 20")
    stdin.write(password + "\n")
    stdin.flush()
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())
    
    # 3. Try login endpoint directly
    print("=== LOGIN TEST ===")
    stdin, stdout, stderr = ssh.exec_command("""curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"phone": "+998998426574", "password": "789789"}' | head -c 200""")
    print("Login response:", stdout.read().decode())
    
    # 4. Try categories endpoint
    print("=== CATEGORIES TEST ===")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost/api/categories | head -c 200")
    print("Categories response:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    final_check()
