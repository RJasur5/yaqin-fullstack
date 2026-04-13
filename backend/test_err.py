from fastapi.testclient import TestClient
from main import app
import traceback

client = TestClient(app)
try:
    response = client.get("/api/masters/1")
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
except Exception as e:
    traceback.print_exc()
