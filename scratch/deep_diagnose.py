import paramiko

def diagnose():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            return stdout.read().decode()

        # Check logs
        print("--- Docker Logs ---")
        print(run_sudo("journalctl -u docker -n 20 --no-pager"))
        
        # Check files again carefully
        print("--- File List ---")
        print(run_sudo("ls -la /var/www/yaqin/"))

    except Exception as e:
        print(f"DIAGNOSTIC FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    diagnose()
