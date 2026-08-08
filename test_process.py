import httpx

resp = httpx.post('http://localhost:8000/api/v1/auth/login', json={'email':'testuser2@zivastock.com','password':'Test@123'})
print('login', resp.status_code, resp.text[:200])
token = resp.json()['access_token']

resp2 = httpx.post('http://localhost:8000/api/v1/imports/process/1', headers={'Authorization':f'Bearer {token}'}, json={'field_mapping':{'barcode':'barcode','product_code':'product_code','description':'description','system_quantity':'system_quantity','unit_cost':'unit_cost','unit_of_measure':'unit_of_measure'}})
print('process', resp2.status_code, resp2.text[:500])
