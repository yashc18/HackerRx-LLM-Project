import requests
import json
import time

# API Configuration
API_URL = "http://localhost:8001/hackrx/run"
API_TOKEN = "5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8"

# Headers
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Your actual request with the real document
request_body = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}

def test_final_fix():
    """Test the final quota-optimized API"""
    try:
        print("🧪 Testing Final Quota-Optimized API...")
        print(f"URL: {API_URL}")
        print(f"Document: {request_body['documents'][:50]}...")
        print(f"Questions: {len(request_body['questions'])}")
        print("-" * 50)
        
        # Wait for server to be ready
        print("⏳ Waiting for server to be ready...")
        time.sleep(3)
        
        # Make the request
        start_time = time.time()
        response = requests.post(API_URL, headers=headers, json=request_body)
        end_time = time.time()
        
        print(f"⏱️  Request took: {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Quota optimization working!")
            result = response.json()
            
            print("\n📋 Real Answers (No Hardcoded Responses):")
            for i, answer in enumerate(result.get('answers', []), 1):
                print(f"\n{i}. {answer[:200]}...")
                
            # Check if we got real responses or quota errors
            quota_errors = 0
            for answer in result.get('answers', []):
                if "429 RESOURCE_EXHAUSTED" in answer or "quota" in answer.lower():
                    quota_errors += 1
            
            if quota_errors == 0:
                print("\n🎉 PERFECT! All questions answered with real API responses!")
            else:
                print(f"\n⚠️  {quota_errors} questions still hit quota limits")
                
        else:
            print("❌ ERROR!")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on localhost:8001")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    test_final_fix() 