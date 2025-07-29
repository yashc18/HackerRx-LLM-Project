import requests
import json

# API Configuration
API_URL = "http://localhost:8001/hackrx/run"
API_TOKEN = "5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8"

# Headers
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Correct request body format
request_body = {
    "documents": "https://example.com/sample-document.pdf",  # Replace with actual document URL
    "questions": [
        "What is the main topic of this document?",
        "What are the key findings mentioned?",
        "Who are the primary authors?"
    ]
}

def test_api_request():
    """Test the HackRx API with correct request format"""
    try:
        print("🚀 Testing HackRx API with correct request format...")
        print(f"URL: {API_URL}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Request Body: {json.dumps(request_body, indent=2)}")
        print("-" * 50)
        
        response = requests.post(API_URL, headers=headers, json=request_body)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ ERROR!")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on localhost:8001")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    test_api_request() 