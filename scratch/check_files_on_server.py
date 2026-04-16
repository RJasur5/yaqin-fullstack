import paramiko

def check_files():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_cmd(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(command)
            return stdout.read().decode().strip()

        print("--- Home Folder ---")
        print(run_cmd("ls -la"))
        
        print("--- Project Path (/var/www/yaqin) ---")
        print(run_cmd("ls -la /var/www/yaqin/ || echo 'NOT FOUND'"))

    except Exception as e:
        print(f"Check failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_files()
