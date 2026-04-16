import paramiko
import io
import time

def absolute_victory():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    # EXACT content for production
    docker_compose_content = """services:
  db:
    image: postgres:15-alpine
    container_name: findix-db
    restart: always
    environment:
      POSTGRES_USER: findix_user
      POSTGRES_PASSWORD: findix_pass
      POSTGRES_DB: findix_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - findix-network

  backend:
    build: 
      context: /var/www/yaqin/backend
      dockerfile: Dockerfile
    container_name: findix-backend
    restart: always
    environment:
      DATABASE_URL: postgresql://findix_user:findix_pass@db:5432/findix_db
      SECRET_KEY: very_secret_key
    volumes:
      - /var/www/yaqin/backend/uploads:/app/uploads
    depends_on:
      - db
    networks:
      - findix-network

  nginx:
    image: nginx:stable-alpine
    container_name: findix-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    volumes:
      - /var/www/yaqin/deploy/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - /var/www/yaqin/downloads:/app/downloads:ro
    networks:
      - findix-network

volumes:
  postgres_data:
networks:
  findix-network:
"""
    
    nginx_conf_content = """server {
    listen 80;
    server_name yaqingo.uz api.yaqingo.uz;

    # Download APK
    location = /app.apk {
        root /app/downloads;
        try_files /app.apk =404;
        default_type application/vnd.android.package-archive;
    }

    # Backend API
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
"""

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")
        
        sftp = client.open_sftp()
        
        # 1. Overwrite files
        print("Overwriting docker-compose.yml...")
        sftp.putfo(io.BytesIO(docker_compose_content.encode()), "/var/www/yaqin/docker-compose.yml")
        
        print("Overwriting nginx.conf...")
        sftp.putfo(io.BytesIO(nginx_conf_content.encode()), "/var/www/yaqin/deploy/nginx.conf")
        
        sftp.close()

        # 2. Launch
        print("Launching with new configuration...")
        stdin, stdout, stderr = client.exec_command(f"sudo -S docker compose -f /var/www/yaqin/docker-compose.yml up -d --force-recreate", get_pty=True)
        stdin.write(password + '\n')
        stdin.flush()
        print("Done! Waiting for Nginx to reload...")
        time.sleep(5)
        
        # 3. Final verification
        print("Verifying link status...")
        stdin, stdout, stderr = client.exec_command("curl -I http://localhost/app.apk")
        print(f"CURL result:\n{stdout.read().decode()}")

    except Exception as e:
        print(f"ABSOLUTE VICTORY FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    absolute_victory()
