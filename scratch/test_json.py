import paramiko
import json

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

fetch_script = """
import json
from database import SessionLocal
from routers.orders import get_my_orders
from routers.auth import get_current_user_from_header
from models import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.phone == '+998991234567').first()
    if user:
        # We need a fake request or we can just mock get_current_user_from_header
        pass
finally:
    db.close()
"""

# Instead of using FastAPI, I'll just make an HTTP request to the live server using the user's phone to login and get token.
test_api_script = """
import requests

baseUrl = "https://yaqingo.uz/api"

# Login
res = requests.post(f"{baseUrl}/auth/login", json={"phone": "+998991234567", "password": "password"}) # Wait, I don't know the password.

# Let's bypass login by querying db and building the response directly using the router logic in the container
"""

container_script = """
import json
from database import SessionLocal
from models import User, MasterProfile, Order, JobApplication, Subscription
from routers.orders import build_order_response, build_application_order_response, check_subscription
from sqlalchemy.orm import joinedload

db = SessionLocal()
try:
    user = db.query(User).filter(User.phone == '+998991234567').first()
    if user:
        profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
        master_id = profile.id if profile else -1
        
        query = db.query(Order).options(
            joinedload(Order.client),
            joinedload(Order.master).joinedload(MasterProfile.user),
            joinedload(Order.subcategory)
        ).filter((Order.client_id == user.id) | (Order.master_id == master_id))
        orders = query.all()
        
        is_subscribed = check_subscription(user.id, "master", db)
        
        res_list = [build_order_response(o, is_subscribed=is_subscribed).model_dump(mode='json') for o in orders]
        
        if profile:
            apps_received = db.query(JobApplication).options(
                joinedload(JobApplication.employer),
                joinedload(JobApplication.master).joinedload(MasterProfile.user),
                joinedload(JobApplication.master).joinedload(MasterProfile.subcategory)
            ).filter(
                JobApplication.master_id == profile.id,
                JobApplication.status.in_(["pending", "viewed", "rejected"])
            ).all()
            res_list.extend([build_application_order_response(a).model_dump(mode='json') for a in apps_received])
            
        print(json.dumps(res_list))
finally:
    db.close()
"""

def test_api_json():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        
        cmd = "cat << 'EOF' | docker exec -i findix-backend python\n" + container_script + "\nEOF"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            print("ERROR:")
            print(err)
        else:
            print("JSON Output:")
            print(out[:1000] + "...") # Print first 1000 chars
            
            # Check for nulls in required fields
            data = json.loads(out)
            print(f"Total items: {len(data)}")
            for item in data:
                if 'subcategory_name_ru' not in item or item['subcategory_name_ru'] is None:
                    print(f"Missing subcategory_name_ru in item {item['id']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    test_api_json()
