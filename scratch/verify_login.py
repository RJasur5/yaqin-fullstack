import paramiko

def verify_login():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Testing login...")
    stdin, stdout, stderr = ssh.exec_command("""curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"phone": "+998998426574", "password": "789789"}' | head -c 200""")
    resp = stdout.read().decode()
    print("Login:", resp)
    
    if "access_token" in resp:
        print("SUCCESS!")
    else:
        print("FAIL - checking logs...")
        stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-backend --tail 30")
        stdin.write(password + "\n")
        stdin.flush()
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    verify_login()
