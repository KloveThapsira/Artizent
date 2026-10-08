import requests
pid='8e9c3e3b-bd3f-4447-b6d3-52a202066a79'
r=requests.post('http://127.0.0.1:8000/deploy', json={'project_id':pid,'platform':None,'token':'','mode':'simulation'})
print(r.status_code)
print(r.text)
