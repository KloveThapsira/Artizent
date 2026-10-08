import requests
r = requests.get('http://127.0.0.1:8000/deployment/8e9c3e3b-bd3f-4447-b6d3-52a202066a79')
print(r.status_code)
print(r.text)
