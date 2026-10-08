import http.client
import mimetypes
from pathlib import Path

# create a small zip
from zipfile import ZipFile
z = ZipFile('test_upload.zip', 'w')
z.writestr('hello.txt', 'hello')
z.close()

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
data = []
with open('test_upload.zip', 'rb') as f:
    file_content = f.read()

fields = []
# file field
fields.append(('--' + boundary).encode())
fields.append(b'Content-Disposition: form-data; name="file"; filename="test_upload.zip"')
fields.append(b'Content-Type: application/zip')
fields.append(b'')
fields.append(file_content)
fields.append(('--' + boundary + '--').encode())
body = b'\r\n'.join(fields)

conn = http.client.HTTPConnection('localhost', 8000)
headers = {
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Content-Length': str(len(body))
}
conn.request('POST', '/upload', body, headers)
res = conn.getresponse()
print(res.status, res.reason)
print(res.read().decode())
conn.close()
