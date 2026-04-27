import paramiko

hostname = "95.182.118.245"
username = "yaqingo"
password = "nEQvV9Pi8e"

def check_mounts():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        # Get mount info for backend container
        # We try different possible container names
        for container in ["findix-backend", "backend"]:
            stdin, stdout, stderr = ssh.exec_command(f"docker inspect {container} --format '{{{{range .Mounts}}}}{{{{.Source}}}}:{{{{.Destination}}}}\\n{{{{end}}}}'")
            out = stdout.read().decode()
            if out:
                print(f"Mounts for {container}:")
                print(out)
                break
        else:
            print("Could not find backend container via inspect.")
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mounts()
