import sys
import requests
if len(sys.argv) < 2:
    print('Usage: real_deploy.py <NETLIFY_TOKEN>')
    sys.exit(1)
token = sys.argv[1]
project_id = '8e9c3e3b-bd3f-4447-b6d3-52a202066a79'
url = 'http://127.0.0.1:8000/deploy'
resp = requests.post(url, json={'project_id': project_id, 'platform': None, 'token': token, 'mode': 'real'})
print(resp.status_code)
print(resp.text)
