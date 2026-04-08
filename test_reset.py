from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)
r = client.post("/reset", data='')
print(f"Empty data status: {r.status_code}")

r = client.post("/reset", json={})
print(f"Empty json status: {r.status_code}")
