import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Check what format_phone does
cmd = 'docker exec findix-backend cat schemas.py'
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
print("=== FULL schemas.py ===")
print(out[:2000])

# Test format_phone directly
cmd2 = """docker exec findix-backend python -c "
from schemas import format_phone
print('format_phone(+998991234567):', format_phone('+998991234567'))
print('format_phone(+998 (99) 123-45-67):', format_phone('+998 (99) 123-45-67'))
print('format_phone(998991234567):', format_phone('998991234567'))
" """
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
out2 = stdout2.read().decode()
err2 = stderr2.read().decode()
print("\n=== format_phone RESULTS ===")
print(out2)
if err2: print("ERR:", err2)

ssh.close()
