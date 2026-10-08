import sys
import requests
if len(sys.argv) < 2:
    print('Usage: check_url.py <url>')
    sys.exit(1)
url = sys.argv[1]
try:
    r = requests.get(url, timeout=10)
    print(r.status_code)
except Exception as e:
    print('ERR', e)
