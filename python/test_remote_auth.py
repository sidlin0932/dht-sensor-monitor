
import requests

# URL from .env
url = "https://dht-sensor-monitor.onrender.com/api/push"
# Try the default key if the env var is missing on server
keys_to_test = ["123", "default_insecure_key"]

print(f"Testing URL: {url}")

for key in keys_to_test:
    print(f"\n[TEST] Testing Key: '{key}'")
    try:
        response = requests.post(
            url,
            json={"temperature": 25.0},
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("[OK] SUCCESS! This is the active key.")
            break
        else:
            print("[X] Rejected.")
            
    except Exception as e:
        print(f"Error: {e}")
