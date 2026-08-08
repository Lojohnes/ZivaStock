import httpx, sys

resp = httpx.post('http://localhost:8000/api/v1/auth/login', json={'email':'testuser2@zivastock.com','password':'Test@123'})
print('login', resp.status_code, resp.text[:200])
if resp.status_code != 200:
    sys.exit(1)
token = resp.json()['access_token']

with open('test_products.csv','rb') as f:
    resp2 = httpx.post(
        'http://localhost:8000/api/v1/imports/upload?source=products',
        headers={'Authorization': f'Bearer {token}'},
        files={'file': ('test_products.csv', f, 'text/csv')}
    )
print('upload', resp2.status_code, resp2.text[:1000])
