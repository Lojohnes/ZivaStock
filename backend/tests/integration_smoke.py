"""
ZivaStock v2 API integration smoke test.

Prerequisites:
- Server running on http://127.0.0.1:8000
- Database seeded (admin@zivastock.com / Admin@12345)

This script performs live HTTP calls against every documented v1 endpoint.
It cleans up most resources it creates.
"""
import sys
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

import httpx

BASE = "http://127.0.0.1:8000"
ADMIN = {"email": "admin@zivastock.com", "password": "Admin@12345"}

errors = []


def log(method: str, path: str, status: int, ok: bool, detail=""):
    mark = "OK" if ok else "FAIL"
    print(f"[{mark}] {method} {path} -> {status} {detail}")
    if not ok:
        errors.append(f"{method} {path} -> {status} {detail}")


def call(client: httpx.Client, method: str, path: str, token: str, json=None, params=None, expect_status=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = client.request(method, f"{BASE}{path}", headers=headers, json=json, params=params, timeout=20)
    except Exception as e:
        log(method, path, 0, False, str(e))
        return None

    ok = r.status_code == expect_status if expect_status else r.is_success
    if not ok:
        log(method, path, r.status_code, False, r.text[:200])
        return None
    log(method, path, r.status_code, True)
    return r.json()


def main():
    with httpx.Client(timeout=httpx.Timeout(15.0, connect=5.0)) as client:
        # --- Health / Auth ------------------------------------------------
        r = client.get(f"{BASE}/health")
        log("GET", "/health", r.status_code, r.is_success)

        r = client.post(f"{BASE}/api/v1/auth/login", json=ADMIN)
        if not r.is_success:
            print("Admin login failed:", r.text)
            sys.exit(1)
        token = r.json()["access_token"]
        print(f"Authenticated. Token: {token[:20]}...")

        call(client, "GET", "/api/v1/auth/me", token)

        # --- Roles --------------------------------------------------------
        roles = call(client, "GET", "/api/v1/roles", token)
        perms = call(client, "GET", "/api/v1/roles/permissions/all", token)

        # --- Users --------------------------------------------------------
        users = call(client, "GET", "/api/v1/users", token)
        first_role_id = roles[0]["id"] if isinstance(roles, list) and roles else (roles["items"][0]["id"] if isinstance(roles, dict) and roles.get("items") else 1)
        test_user = call(client, "POST", "/api/v1/users", token, {
            "email": f"smoke-{uuid.uuid4().hex[:8]}@zivastock.com",
            "first_name": "Smoke",
            "last_name": "Tester",
            "password": "Smoke@12345",
            "role_id": first_role_id,
        }, expect_status=201)

        if test_user:
            user_id = test_user["id"]
            call(client, "GET", f"/api/v1/users/{user_id}", token)
            call(client, "PUT", f"/api/v1/users/{user_id}", token, {"first_name": "Updated"})
            call(client, "POST", f"/api/v1/users/{user_id}/reset-password", token, {"new_password": "Smoke@12346"})
            call(client, "POST", f"/api/v1/users/{user_id}/unlock", token)
            call(client, "DELETE", f"/api/v1/users/{user_id}", token)

        # --- Products / Categories ----------------------------------------
        call(client, "GET", "/api/v1/products/categories", token)
        category = call(client, "POST", "/api/v1/products/categories", token, {
            "name": f"SmokeCat-{uuid.uuid4().hex[:8]}"
        }, expect_status=201)

        product = call(client, "POST", "/api/v1/products", token, {
            "barcode": f"SMK{uuid.uuid4().hex[:6].upper()}",
            "product_code": f"SMK-{uuid.uuid4().hex[:4].upper()}",
            "description": "Smoke product",
            "unit_of_measure": "EA",
            "system_quantity": "100",
            "unit_cost": "10",
            "unit_price": "15",
            "category_id": category["id"] if category else None,
        }, expect_status=201)

        if product:
            product_id = product["id"]
            call(client, "GET", f"/api/v1/products/{product_id}", token)
            call(client, "GET", f"/api/v1/products/barcode/{product['barcode']}", token)
            call(client, "PUT", f"/api/v1/products/{product_id}", token, {"description": "Updated smoke product"})
            call(client, "DELETE", f"/api/v1/products/{product_id}", token)

        if category:
            call(client, "PUT", f"/api/v1/products/categories/{category['id']}", token, {"description": "updated"})
            call(client, "DELETE", f"/api/v1/products/categories/{category['id']}", token)

        # --- Locations / Shelves / Sections -------------------------------
        location = call(client, "POST", "/api/v1/locations", token, {
            "name": f"SmokeLoc-{uuid.uuid4().hex[:8]}",
            "type": "warehouse"
        }, expect_status=201)

        if location:
            loc_id = location["id"]
            call(client, "GET", f"/api/v1/locations/{loc_id}", token)
            call(client, "PUT", f"/api/v1/locations/{loc_id}", token, {"address": "123 Smoke St"})
            shelf = call(client, "POST", "/api/v1/locations/shelves", token, {
                "location_id": loc_id,
                "name": f"SmokeShelf-{uuid.uuid4().hex[:8]}"
            }, expect_status=201)

            if shelf:
                shelf_id = shelf["id"]
                call(client, "GET", "/api/v1/locations/shelves", token)
                call(client, "PUT", f"/api/v1/locations/shelves/{shelf_id}", token, {"description": "updated"})
                section = call(client, "POST", "/api/v1/locations/sections", token, {
                    "shelf_id": shelf_id,
                    "name": f"SmokeSec-{uuid.uuid4().hex[:8]}"
                }, expect_status=201)

                if section:
                    sec_id = section["id"]
                    call(client, "GET", f"/api/v1/locations/shelves/{shelf_id}/sections", token)
                    call(client, "PUT", f"/api/v1/locations/sections/{sec_id}", token, {"description": "updated"})
                    call(client, "DELETE", f"/api/v1/locations/sections/{sec_id}", token)
                call(client, "DELETE", f"/api/v1/locations/shelves/{shelf_id}", token)
            # No DELETE /locations/{id} endpoint in v2, keep location as smoke artifact

        call(client, "GET", "/api/v1/locations", token)
        call(client, "GET", "/api/v1/locations/tree", token)

        # --- Sessions -----------------------------------------------------
        # Need a valid location first. Use the seeded Main Warehouse.
        r = client.get(f"{BASE}/api/v1/locations", headers={"Authorization": f"Bearer {token}"})
        seeded_loc = r.json()[0] if r.is_success and r.json() else None
        loc_id = seeded_loc["id"] if seeded_loc else 1

        session = call(client, "POST", "/api/v1/sessions", token, {
            "name": f"SmokeSession-{uuid.uuid4().hex[:8]}",
            "description": "Smoke test session",
            "location_id": loc_id,
            "session_type": "full"
        }, expect_status=201)

        if session:
            session_id = session["id"]
            call(client, "GET", f"/api/v1/sessions/{session_id}", token)
            call(client, "GET", f"/api/v1/sessions/{session_id}/sections", token)
            call(client, "GET", f"/api/v1/sessions/{session_id}/assignments", token)
            call(client, "POST", f"/api/v1/sessions/{session_id}/start", token)
            call(client, "POST", f"/api/v1/sessions/{session_id}/pause", token)
            call(client, "POST", f"/api/v1/sessions/{session_id}/resume", token)

            # assign admin
            call(client, "POST", f"/api/v1/sessions/{session_id}/assignments", token, {
                "user_id": 1,
                "assignment_role": "first_counter"
            }, expect_status=201)

            call(client, "POST", f"/api/v1/sessions/{session_id}/counting-complete", token)

        call(client, "GET", "/api/v1/sessions", token)

        # --- Counts -------------------------------------------------------
        # Need product and section ids from seeded data.
        products = call(client, "GET", "/api/v1/products?limit=5", token)
        sections = call(client, "GET", "/api/v1/locations/shelves/1/sections", token)
        sections_all = call(client, "GET", "/api/v1/locations/shelves", token)

        prod_id = products["items"][0]["id"] if products and products.get("items") else 1
        sec_id = sections[0]["id"] if sections else (sections_all[0]["id"] if sections_all else 1)
        sess_id = session["id"] if session else 1

        # Create a dedicated counter user so we can test segregation of duties
        counter_role_id = next((r["id"] for r in roles if r["name"] == "Counter"), 1)
        counter_email = f"smoke-counter-{uuid.uuid4().hex[:8]}@zivastock.com"
        counter_user = call(client, "POST", "/api/v1/users", token, {
            "email": counter_email,
            "first_name": "Smoke",
            "last_name": "Counter",
            "password": "Counter@12345",
            "role_id": counter_role_id,
        }, expect_status=201)

        r = client.post(f"{BASE}/api/v1/auth/login", json={"email": counter_email, "password": "Counter@12345"})
        if not r.is_success:
            print("Counter login failed:", r.text)
            counter_token = None
        else:
            counter_token = r.json()["access_token"]

        admin_token = token

        first_count = call(client, "POST", "/api/v1/counts/first", admin_token, {
            "session_id": sess_id,
            "product_id": prod_id,
            "shelf_section_id": sec_id,
            "quantity": "10",
            "source": "web"
        }, expect_status=201)

        if first_count:
            fc_id = first_count["id"]
            call(client, "GET", "/api/v1/counts/first", admin_token)
            call(client, "GET", f"/api/v1/counts/first/{fc_id}", admin_token)
            call(client, "PUT", f"/api/v1/counts/first/{fc_id}", admin_token, {"quantity": "12"})

            # Second count must be by a different user (segregation of duties)
            if counter_token:
                second_count = call(client, "POST", "/api/v1/counts/second", counter_token, {
                    "session_id": sess_id,
                    "product_id": prod_id,
                    "shelf_section_id": sec_id,
                    "first_count_id": fc_id,
                    "quantity": "12",
                    "source": "web"
                }, expect_status=201)

                if second_count:
                    sc_id = second_count["id"]
                    call(client, "GET", "/api/v1/counts/second", counter_token)
                    call(client, "GET", f"/api/v1/counts/second/{sc_id}", counter_token)
                    # Update/delete require counts.update / counts.delete, which the Counter role does not hold
                    call(client, "PUT", f"/api/v1/counts/second/{sc_id}", admin_token, {"quantity": "13"})
                    call(client, "DELETE", f"/api/v1/counts/second/{sc_id}", admin_token)

            call(client, "DELETE", f"/api/v1/counts/first/{fc_id}", admin_token)

            # cleanup counter user
            if counter_user:
                call(client, "DELETE", f"/api/v1/users/{counter_user['id']}", admin_token)

        # --- Adjustments --------------------------------------------------
        if session:
            sess_id = session["id"]
            call(client, "POST", f"/api/v1/adjustments/sessions/{sess_id}/generate", token)
            adjs = call(client, "GET", "/api/v1/adjustments", token, params={"session_id": sess_id})
            call(client, "GET", f"/api/v1/adjustments/sessions/{sess_id}/variance", token)
            call(client, "GET", f"/api/v1/adjustments/sessions/{sess_id}/discrepancies", token)

            if adjs and adjs.get("items"):
                adj_id = adjs["items"][0]["id"]
                call(client, "GET", f"/api/v1/adjustments/{adj_id}", token)
                call(client, "POST", f"/api/v1/adjustments/{adj_id}/approve", token)
                call(client, "POST", f"/api/v1/adjustments/{adj_id}/post", token)

        # --- Reports ------------------------------------------------------
        call(client, "GET", "/api/v1/reports/dashboard", token)
        if session:
            call(client, "GET", "/api/v1/reports/variance", token, params={"session_id": session["id"]})
            call(client, "GET", "/api/v1/reports/session-progress", token)
            call(client, "GET", "/api/v1/reports/missing", token, params={"session_id": session["id"]})
            call(client, "GET", "/api/v1/reports/productivity", token, params={"session_id": session["id"]})
        call(client, "GET", "/api/v1/reports/audit", token)
        call(client, "GET", "/api/v1/reports/historical", token, params={"month": "2026-08"})

        # --- Sync ---------------------------------------------------------
        call(client, "GET", "/api/v1/sync/status", token)
        call(client, "GET", "/api/v1/sync/queue", token)
        call(client, "POST", "/api/v1/sync/retry", token)

        # create product on the fly to sync against
        prod = products["items"][0] if products and products.get("items") else None
        if prod:
            call(client, "POST", "/api/v1/sync/push", token, {
                "items": [{
                    "client_id": f"smoke-{uuid.uuid4().hex}",
                    "device_id": "smoke-device",
                    "entity_type": "first_count",
                    "action": "create",
                    "payload": {
                        "session_id": sess_id,
                        "product_id": prod["id"],
                        "shelf_section_id": sec_id,
                        "quantity": "5",
                        "source": "mobile"
                    }
                }]
            }, expect_status=201)
            call(client, "POST", "/api/v1/sync/retry", token)
        call(client, "GET", "/api/v1/sync/pull", token)

        # --- cleanup session ---------------------------------------------
        if session:
            try:
                client.delete(f"{BASE}/api/v1/sessions/{session['id']}", headers={"Authorization": f"Bearer {token}"}, timeout=10)
                print(f"[SKIP/DELETE] session {session['id']} cleanup attempted")
            except Exception as e:
                print(f"session cleanup: {e}")

    print("\n" + "=" * 60)
    if errors:
        print(f"SMOKE TEST FAILED with {len(errors)} error(s):")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("SMOKE TEST PASSED — all targeted endpoints returned expected status.")


if __name__ == "__main__":
    main()
