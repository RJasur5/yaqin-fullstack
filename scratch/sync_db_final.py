import paramiko

def sync():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e')
    
    sql = """
    SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users;
    SELECT setval(pg_get_serial_sequence('orders', 'id'), COALESCE(MAX(id), 1)) FROM orders;
    SELECT setval(pg_get_serial_sequence('app_reviews', 'id'), COALESCE(MAX(id), 1)) FROM app_reviews;
    SELECT setval(pg_get_serial_sequence('master_profiles', 'id'), COALESCE(MAX(id), 1)) FROM master_profiles;
    SELECT setval(pg_get_serial_sequence('subscriptions', 'id'), COALESCE(MAX(id), 1)) FROM subscriptions;
    SELECT setval(pg_get_serial_sequence('chat_messages', 'id'), COALESCE(MAX(id), 1)) FROM chat_messages;
    SELECT setval(pg_get_serial_sequence('reviews', 'id'), COALESCE(MAX(id), 1)) FROM reviews;
    """
    
    # Use a heredoc to pass the SQL safely
    cmd = f"docker exec -i findix-db psql -U findix_user -d findix_db << 'EOF'\n{sql}\nEOF\n"
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode())
    print(stderr.read().decode())
    client.close()

if __name__ == '__main__':
    sync()
