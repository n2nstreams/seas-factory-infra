#!/usr/bin/env python3
"""
OAuth Status Check Script
Quickly check OAuth configuration status
"""

import requests

def check_oauth_status():
    """Check OAuth status from the API"""
    try:
        # Try to connect to the API
        response = requests.get("http://localhost:8000/auth/status", timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            print("OAuth Status:")
            print(f"  Google OAuth: {'✅ Enabled' if status['google_oauth_enabled'] else '❌ Disabled'}")
            print(f"  GitHub OAuth: {'✅ Enabled' if status['github_oauth_enabled'] else '❌ Disabled'}")
            print(f"  Google Client ID: {'✅ Configured' if status['google_client_id_configured'] else '❌ Not Configured'}")
            print(f"  GitHub Client ID: {'✅ Configured' if status['github_client_id_configured'] else '❌ Not Configured'}")
        else:
            print(f"❌ API returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the backend running?")
    except Exception as e:
        print(f"❌ Error checking OAuth status: {e}")

if __name__ == "__main__":
    check_oauth_status()
