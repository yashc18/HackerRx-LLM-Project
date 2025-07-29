#!/usr/bin/env python3
"""
Simple test script to verify HackRx server is working correctly
"""

import requests
import json
import time

def test_health_check():
    """Test the health check endpoint"""
    print("Testing Health Check...")
    try:
        response = requests.get("http://localhost:8001/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']} - {data['message']}")
            return True
        else:
            print(f"❌ Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting Root Endpoint...")
    try:
        response = requests.get("http://localhost:8001/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root Endpoint: {data['message']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ Root Endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root Endpoint error: {e}")
        return False

def test_main_endpoint():
    """Test the main evaluation endpoint"""
    print("\nTesting Main Evaluation Endpoint...")
    
    headers = {
        "Authorization": "Bearer 5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
        "questions": [
            "What is the grace period for premium payment?"
        ]
    }
    
    try:
        start_time = time.time()
        response = requests.post("http://localhost:8001/hackrx/run", 
                               headers=headers, 
                               json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main Endpoint: Success!")
            print(f"   Response time: {end_time - start_time:.2f} seconds")
            print(f"   Answer: {data['answers'][0][:100]}...")
            return True
        else:
            print(f"❌ Main Endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Main Endpoint error: {e}")
        return False

def test_authentication():
    """Test authentication with invalid token"""
    print("\nTesting Authentication...")
    
    headers = {
        "Authorization": "Bearer invalid_token",
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": "https://example.com/test.pdf",
        "questions": ["Test question"]
    }
    
    try:
        response = requests.post("http://localhost:8001/hackrx/run", 
                               headers=headers, 
                               json=payload)
        
        if response.status_code == 401:
            print("✅ Authentication: Correctly rejected invalid token")
            return True
        else:
            print(f"❌ Authentication test failed: Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 HackRx Server Test Suite")
    print("=" * 40)
    
    tests = [
        test_health_check,
        test_root_endpoint,
        test_main_endpoint,
        test_authentication
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Server is ready for Postman testing.")
        print("\n📋 Next Steps:")
        print("1. Open Postman")
        print("2. Import the collection from LOCAL_POSTMAN_TESTING_GUIDE.md")
        print("3. Set environment variables:")
        print("   - base_url: http://localhost:8001")
        print("   - auth_token: 5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8")
        print("4. Start testing!")
    else:
        print("❌ Some tests failed. Please check the server logs.")

if __name__ == "__main__":
    main() 