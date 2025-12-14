import urllib.request
import json
import sys

url = "http://localhost:9000/analyse"

data = {
    "repository": "kcodess/DevOps-Guardian-Agent",
    "workflow": "CI Pipeline",
    "job": "build-and-test",
    "logs": """
    Run npm install
    npm ERR! code ERESOLVE
    npm ERR! ERESOLVE unable to resolve dependency tree
    npm ERR! 
    npm ERR! While resolving: devops-guardian-dashboard@0.1.0
    npm ERR! Found: react@18.2.0
    npm ERR! node_modules/react
    npm ERR!   react@"^18.2.0" from the root project
    npm ERR! 
    npm ERR! Could not resolve dependency:
    npm ERR! peer react@"^17.0.0" from some-old-library@1.0.0
    npm ERR! node_modules/some-old-library
    npm ERR!   some-old-library@"^1.0.0" from the root project
    npm ERR! 
    npm ERR! Fix the upstream dependency conflict, or retry
    npm ERR! this command with --force, or --legacy-peer-deps
    npm ERR! to accept an incorrect (and potentially broken) dependency resolution.
    """
}

headers = {'Content-Type': 'application/json'}

try:
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("Status Code:", response.getcode())
        print("\nResponse:")
        print(json.dumps(result, indent=2))
except urllib.error.URLError as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
