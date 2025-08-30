#!/usr/bin/env python3
"""
Test Integration Endpoints with Proper Headers
Tests endpoints that were returning 422 status to see if they work with proper headers
"""

import asyncio
import httpx
import json

async def test_endpoints_with_headers():
    """Test endpoints with proper headers"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing endpoints with proper headers...")
    print("=" * 60)
    
    # Test database connectivity through user profile endpoint
    print("\n1. Testing Database Connectivity (User Profile)")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/api/users/profile",
                headers={
                    "Authorization": "Bearer test-token",
                    "x-tenant-id": "test-tenant"
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Success - Database connectivity working")
            elif response.status_code == 401:
                print("   ✅ Success - Authentication working (401 expected without valid token)")
            elif response.status_code == 422:
                print("   ⚠️ Warning - Still getting 422, may need different headers")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print("   Could not parse error response")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test marketplace products endpoint
    print("\n2. Testing API Compatibility (Marketplace Products)")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/api/marketplace/products",
                headers={
                    "x-tenant-id": "test-tenant"
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Success - API compatibility working")
            elif response.status_code == 401:
                print("   ✅ Success - Authentication working (401 expected)")
            elif response.status_code == 422:
                print("   ⚠️ Warning - Still getting 422, may need different headers")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print("   Could not parse error response")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test factory status endpoint
    print("\n3. Testing Factory Status Endpoint")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/api/factory/status",
                headers={
                    "x-tenant-id": "test-tenant"
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Success - Factory status working")
            elif response.status_code == 401:
                print("   ✅ Success - Authentication working (401 expected)")
            elif response.status_code == 422:
                print("   ⚠️ Warning - Still getting 422, may need different headers")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print("   Could not parse error response")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test ideas endpoint
    print("\n4. Testing Ideas Endpoint")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/api/ideas/my-ideas",
                headers={
                    "x-tenant-id": "test-tenant"
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Success - Ideas endpoint working")
            elif response.status_code == 401:
                print("   ✅ Success - Authentication working (401 expected)")
            elif response.status_code == 422:
                print("   ⚠️ Warning - Still getting 422, may need different headers")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print("   Could not parse error response")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_endpoints_with_headers())
