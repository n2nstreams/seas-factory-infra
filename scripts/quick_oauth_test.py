#!/usr/bin/env python3
"""
Quick OAuth Test Script
Quick test to verify OAuth endpoints are accessible
"""

import requests
import time

def test_oauth_endpoints():
    """Quick test of OAuth endpoints"""
    print("🚀 Quick OAuth Endpoint Test")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    endpoints = [
        ("OAuth Status", "/auth/status"),
        ("Google OAuth Start", "/auth/google"),
        ("GitHub OAuth Start", "/auth/github"),
    ]
    
    for name, endpoint in endpoints:
        try:
            print(f"\n🔍 Testing {name}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK (200)")
                if endpoint == "/auth/status":
                    data = response.json()
                    print(f"      Google OAuth: {'✅' if data.get('google_oauth_enabled') else '❌'}")
                    print(f"      GitHub OAuth: {'✅' if data.get('github_oauth_enabled') else '❌'}")
            elif response.status_code in [302, 303]:
                print(f"   ✅ {name}: OK (Redirect - OAuth flow working)")
            elif response.status_code == 400:
                print(f"   ⚠️  {name}: Configured but disabled (400)")
            else:
                print(f"   ❌ {name}: Unexpected status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {name}: Cannot connect to backend")
        except requests.exceptions.Timeout:
            print(f"   ❌ {name}: Timeout")
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
    
    print("\n" + "=" * 40)
    print("📋 Quick Test Complete!")
    print("\nIf you see errors:")
    print("1. Make sure backend is running: cd api_gateway && python -m uvicorn app:app --reload --port 8000")
    print("2. Check OAuth configuration in environment variables")
    print("3. Run full test: python scripts/test_oauth_config.py")

if __name__ == "__main__":
    test_oauth_endpoints()
