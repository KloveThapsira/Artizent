import requests
import sys

token='nfp_PQ3BWuLNLcZiUaM1CE1wpNEyjfxeftfr40ec'
headers={'Authorization':f'Bearer {token}'}
for ep in ['https://api.netlify.com/api/v1/user','https://api.netlify.com/api/v1/sites']:
    try:
        r=requests.get(ep, headers=headers, timeout=15)
        print(ep, r.status_code)
        print(r.text[:2000])
    except Exception as e:
        print('ERR', e)
