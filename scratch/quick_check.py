import paramiko

def quick_check():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED TO SERVER!")

        # 1. Simple docker ps
        stdin, stdout, stderr = client.exec_command("sudo -S docker ps", get_pty=True)
        stdin.write(password + "\n")
        stdin.flush()
        print("Output:", stdout.read().decode())

    except Exception as e:
        print(f"CHECK FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    quick_check()
