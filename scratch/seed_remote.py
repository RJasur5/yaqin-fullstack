import paramiko

def seed_remote():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Seeding remote database...")
    cmd = "sudo -S docker exec findix-backend python3 seed_data.py"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"Error: {err}")
    
    ssh.close()
    print("Seeding finished.")

if __name__ == "__main__":
    seed_remote()
