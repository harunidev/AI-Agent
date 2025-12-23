
import requests
import json

url = "http://localhost:8000/generate-tests"

# Read the new simulation subject
with open("simulation_code.py", "r", encoding="utf-8") as f:
    code = f.read()

payload = {
    "code_content": code,
    "language": "python",
    "file_name": "stok_yonetimi.py"
}

try:
    print("MOCK USER: Sending request to /generate-tests...")
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print("\n--- SUCCESS ---")
        print(f"Coverage: {data['coverage_estimate']}%")
        print(f"Explanation: {data['explanation']}")
        print("\n--- Generated Tests Preview ---")
        print(data['test_code'][:500] + "...")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection Failed: {e}")
