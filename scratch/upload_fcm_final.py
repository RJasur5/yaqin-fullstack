import paramiko
import os

def upload_final():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=15)
        sftp = client.open_sftp()
        
        # Ensure services directory exists
        try:
            sftp.mkdir('yaqin-production/backend/services')
            print("Created 'services' directory.")
        except:
            pass
            
        # Upload files
        sftp.put('backend/services/fcm_service.py', 'yaqin-production/backend/services/fcm_service.py')
        print("Uploaded fcm_service.py")
        
        sftp.put('backend/notification_manager.py', 'yaqin-production/backend/notification_manager.py')
        print("Uploaded notification_manager.py")
        
        sftp.close()
        print("Upload complete!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    upload_final()
