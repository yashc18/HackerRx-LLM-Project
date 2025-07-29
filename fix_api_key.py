import os
import shutil

def fix_api_key():
    """Help fix the API key issue"""
    print("🔧 API Key Fix Helper")
    print("=" * 50)
    
    print("❌ Current Issue: API quota exceeded (50 requests/day limit reached)")
    print("\n💡 Solutions:")
    print("1. Get a new API key from: https://makersuite.google.com/app/apikey")
    print("2. Update your .env file with the new key")
    print("3. Restart the server")
    
    print("\n📝 Steps to fix:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Copy the new key")
    print("4. Update your .env file")
    print("5. Restart the server")
    
    # Check current .env
    if os.path.exists(".env"):
        print(f"\n📁 Current .env file exists")
        with open(".env", "r") as f:
            content = f.read()
            if "GEMINI_API_KEY=" in content:
                print("✅ GEMINI_API_KEY found in .env")
            else:
                print("❌ GEMINI_API_KEY not found in .env")
    else:
        print("❌ No .env file found")
    
    print("\n🔄 After updating the API key, restart the server with:")
    print("   py main.py")

if __name__ == "__main__":
    fix_api_key() 