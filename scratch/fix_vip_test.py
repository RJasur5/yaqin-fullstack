import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def fix_vip_and_test():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        
        print("--- Setting VIP ---")
        cmd = "cat /home/yaqingo/yaqin-production/backend/vip_script.py | docker exec -i findix-backend python"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("--- Testing Orders Fetch ---")
        cmd = "cat /home/yaqingo/yaqin-production/backend/test_orders.py | docker exec -i findix-backend python"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_vip_and_test()
