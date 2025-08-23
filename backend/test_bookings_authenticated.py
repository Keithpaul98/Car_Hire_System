#!/usr/bin/env python3
"""
Authenticated Booking API Test Script
Run Django server first, then run this script.
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


def get_auth_token():
    login_data = {"username": "testuser", "password": "TestPass123!"}
    try:
        r = requests.post(f"{API_BASE}/auth/login/", json=login_data)
        if r.status_code == 200:
            return r.json().get('access')
        # Try register if login failed
        reg = requests.post(f"{API_BASE}/auth/register/", json={
            "username": "testuser",
            "email": "testuser@test.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890"
        })
        if reg.status_code in (200, 201):
            r = requests.post(f"{API_BASE}/auth/login/", json=login_data)
            if r.status_code == 200:
                return r.json().get('access')
    except Exception as e:
        print(f"Auth error: {e}")
    return None


def pick_any_vehicle(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/vehicles/", headers=headers)
    if r.status_code == 200:
        data = r.json()
        items = data.get('results', data if isinstance(data, list) else [])
        if items:
            return items[0]['id']
    return None


def main():
    print("🚗 Testing Booking API")
    token = get_auth_token()
    if not token:
        print("❌ Could not obtain token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    vehicle_id = pick_any_vehicle(token)
    if not vehicle_id:
        print("❌ No vehicle available to test bookings")
        return

    pickup = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
    ret = (datetime.utcnow() + timedelta(days=4)).isoformat() + 'Z'

    # Quote
    quote_payload = {
        "vehicle_id": vehicle_id,
        "pickup_date": pickup,
        "return_date": ret,
        "pickup_location": "Main Branch",
        "return_location": "Main Branch",
    }
    qr = requests.post(f"{API_BASE}/bookings/quote/", headers=headers, json=quote_payload)
    print("Quote:", qr.status_code, qr.text[:200])

    # Create booking
    cr = requests.post(f"{API_BASE}/bookings/", headers=headers, json=quote_payload)
    print("Create:", cr.status_code)
    if cr.status_code not in (200, 201):
        print(cr.text)
        return
    booking = cr.json()
    booking_id = booking['id']

    # List bookings
    lr = requests.get(f"{API_BASE}/bookings/", headers=headers)
    print("List:", lr.status_code)

    # Detail
    dr = requests.get(f"{API_BASE}/bookings/{booking_id}/", headers=headers)
    print("Detail:", dr.status_code)

    # Cancel
    can = requests.post(f"{API_BASE}/bookings/{booking_id}/cancel/", headers=headers)
    print("Cancel:", can.status_code, can.text[:200])

    print("🏁 Booking API test complete")


if __name__ == "__main__":
    main()
