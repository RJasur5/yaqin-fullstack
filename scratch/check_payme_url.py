import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

debug_script = """
from services.payme_service import payme_service
from routers.subscriptions import PLAN_PRICES

role = "master"
plan = "day"
amount = PLAN_PRICES[role][plan]
account = {"user_id": 26, "plan": plan, "role": role}

url = payme_service.generate_payment_url(amount, account)
print(f"Generated URL: {url}")
"""

def check_url():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        cmd = "cat << 'EOF' | docker exec -i findix-backend python\n" + debug_script + "\nEOF"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_url()
