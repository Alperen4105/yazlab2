#!/usr/bin/env python3
"""Test forgot-password endpoint directly"""

from dotenv import load_dotenv
load_dotenv()

from app import app
from backend.extensions import db

with app.app_context():
    with app.test_client() as client:
        print("Testing POST /forgot-password endpoint...")
        print("=" * 60)
        
        # Test with existing user
        response = client.post(
            '/forgot-password',
            data={'email': 'alperenplk.28@gmail.com'},
            follow_redirects=True
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Content-Type: {response.content_type}")
        print(f"Response Data:\n{response.data.decode('utf-8')[:1000]}")
        print("=" * 60)
        
        # Also test API endpoint directly
        print("\nTesting POST /api/auth/forgot-password endpoint...")
        print("=" * 60)
        
        response2 = client.post(
            '/api/auth/forgot-password',
            json={'email': 'alperenplk.28@gmail.com'}
        )
        
        print(f"Status Code: {response2.status_code}")
        print(f"JSON Response: {response2.json}")
        print("=" * 60)
