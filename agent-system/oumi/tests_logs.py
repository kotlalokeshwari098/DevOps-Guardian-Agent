import requests

payload = {
    "repository": "demo-repo",
    "workflow": "build-and-test",
    "job": "backend-tests",
    "logs": "ERROR: ModuleNotFoundError: No module named 'requests'"
}

response = requests.post("http://localhost:9000/analyze", json=payload)
print(response.json())
