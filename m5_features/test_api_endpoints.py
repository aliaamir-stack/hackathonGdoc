import httpx
import sys
import os
import cv2
import numpy as np
import base64

API_URL = "http://localhost:8000"

def create_dummy_image():
    # Create a 400x200 white image
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    # Add some text to simulate OCR
    cv2.putText(img, "ASPIRIN 500mg", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "EXP: 12/2026", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # Encode to base64
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

def test_api():
    print(f"Testing PULSE API at {API_URL}...\n")
    
    with httpx.Client(base_url=API_URL, timeout=30.0) as client:
        # 1. Health Check
        print("1. Testing /health...")
        try:
            r = client.get("/health")
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print("Health check PASSED")
                for key, val in r.json().get('components', {}).items():
                    print(f"  - {key}: {val}")
            else:
                print(f"Health check FAILED: {r.text}")
        except Exception as e:
            print(f"Error connecting: {e}")
            sys.exit(1)
        print("-" * 40)
        
        # 2. Get Protocols
        print("2. Testing /api/emergency/protocols...")
        r = client.get("/api/emergency/protocols")
        if r.status_code == 200 and len(r.json()) == 15:
            print(f"Protocol list PASSED (Found {len(r.json())} protocols)")
        else:
            print(f"Protocol list FAILED: {r.status_code} - {r.text}")
        print("-" * 40)
        
        # 3. Identify Emergency
        print("3. Testing /api/emergency/identify (Speech-to-Protocol)...")
        r = client.post("/api/emergency/identify", json={
            "text": "My friend just grabbed his chest and collapsed, I think it's his heart"
        })
        if r.status_code == 200:
            data = r.json()
            print(f"Identification PASSED! Matched: {data['matched_protocol']['id']}")
            print(f"Action priority: {data['matched_protocol']['title']}")
        else:
            print(f"Identification FAILED: {r.status_code} - {r.text}")
        print("-" * 40)
        
        # 4. Emergency Email Alert
        print("4. Testing /api/emergency/alert (Email Dispatch)...")
        r = client.post("/api/emergency/alert", json={
            "latitude": 24.8607,
            "longitude": 67.0011,
            "situation": "Automated system test from backend checker",
            "contact_name": "Test Runner",
            "contact_phone": "N/A"
        })
        if r.status_code == 200:
            data = r.json()
            if data["sent"]:
                print(f"Email Alert PASSED! (Sent to recipient)")
            else:
                print(f"Email Alert FAILED (API returned 200 but sent=False): {data['message']}")
        else:
            print(f"Email Alert FAILED: {r.status_code} - {r.text}")
        print("-" * 40)

        # 5. Medicine Scanner
        print("5. Testing /api/medicine/scan (OCR & DB integration)...")
        base64_img = create_dummy_image()
        r = client.post("/api/medicine/scan", json={
            "image_base64": base64_img,
            "current_medications": []
        })
        if r.status_code == 200:
            data = r.json()
            print(f"Medicine Scan PASSED!")
            print(f"Drug found: {data.get('ocr_result', {}).get('drug_name', 'Unknown')}")
            print(f"Interactions checked: {len(data.get('interactions', []))}")
            # print(data)
        else:
            print(f"Medicine Scan FAILED: {r.status_code} - {r.text}")
        print("-" * 40)

if __name__ == "__main__":
    test_api()
