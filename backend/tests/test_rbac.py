import httpx
import uuid


def main():
    base = 'http://127.0.0.1:8000'
    client = httpx.Client(timeout=10)

    r = client.post(f'{base}/api/v1/auth/login', json={
        'email': 'admin@zivastock.com',
        'password': 'Admin@12345'
    })
    admin_token = r.json()['access_token']

    roles = client.get(f'{base}/api/v1/roles', headers={
        'Authorization': f'Bearer {admin_token}'
    }).json()
    counter_id = next((r['id'] for r in roles if r['name'] == 'Counter'), 1)

    email = f'rbac-{uuid.uuid4().hex[:8]}@zivastock.com'
    cu = client.post(f'{base}/api/v1/users', headers={
        'Authorization': f'Bearer {admin_token}'
    }, json={
        'email': email,
        'first_name': 'R',
        'last_name': 'B',
        'password': 'Rbac@12345',
        'role_id': counter_id
    }).json()

    ct = client.post(f'{base}/api/v1/auth/login', json={
        'email': email,
        'password': 'Rbac@12345'
    }).json()['access_token']

    # Counter should NOT be allowed to create products
    r1 = client.post(f'{base}/api/v1/products', headers={
        'Authorization': f'Bearer {ct}'
    }, json={
        'barcode': f'RBAC{uuid.uuid4().hex[:4].upper()}',
        'description': 'rbac test',
        'unit_of_measure': 'EA',
        'system_quantity': '0'
    })
    print('product create by counter:', r1.status_code,
          r1.json().get('detail', '')[:80])

    # Counter should NOT be allowed to view audit report
    r2 = client.get(f'{base}/api/v1/reports/audit', headers={
        'Authorization': f'Bearer {ct}'
    })
    print('audit report by counter:', r2.status_code,
          r2.json().get('detail', '')[:80])

    # cleanup
    client.delete(f'{base}/api/v1/users/{cu["id"]}', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    client.close()

    assert r1.status_code == 403, f'expected 403, got {r1.status_code}'
    assert r2.status_code == 403, f'expected 403, got {r2.status_code}'
    print('RBAC check passed')


if __name__ == '__main__':
    main()
