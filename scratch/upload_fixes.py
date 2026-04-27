import paramiko

def upload_fixes():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        sftp = client.open_sftp()
        
        # Upload main.py
        print("Uploading main.py...")
        sftp.put(r'backend\main.py', 'yaqin-production/backend/main.py')
        
        # Upload routers/orders.py
        print("Uploading routers/orders.py...")
        sftp.put(r'backend\routers\orders.py', 'yaqin-production/backend/routers/orders.py')
        
        sftp.close()
        
        # Restart backend
        print("Restarting backend...")
        client.exec_command("cd yaqin-production && docker compose up -d --build backend")
        
        print("FIXES UPLOADED AND BACKEND RESTARTED!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    upload_fixes()
