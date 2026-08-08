import httpx

resp = httpx.post('http://localhost:8000/api/v1/auth/login', json={'email':'testuser2@zivastock.com','password':'Test@123'})
token = resp.json()['access_token']

r = httpx.get('http://localhost:8000/api/v1/products', params={'page':1,'limit':500,'search':''}, headers={'Authorization':f'Bearer {token}'})
print(r.status_code, r.text[:800])
