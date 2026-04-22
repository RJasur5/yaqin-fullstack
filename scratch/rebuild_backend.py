import paramiko

def rebuild():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e')
    
    print("REBUILDING BACKEND CONTAINER...")
    # Using a single string with semicolon for multiple commands to avoid shell issues
    cmd = "cd yaqin-production; echo 'nEQvV9Pi8e' | sudo -S docker compose up -d --build backend"
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode())
    print(stderr.read().decode())
    client.close()

if __name__ == '__main__':
    rebuild()
