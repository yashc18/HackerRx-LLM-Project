import asyncio
import os
from google import genai
from utils.config import Settings

async def test_gemini_direct():
    """Test Gemini API directly to debug the quota issue"""
    print("🧪 Testing Gemini API Directly...")
    print("-" * 50)
    
    # Load settings
    settings = Settings()
    api_key = settings.gemini_api_key
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🔑 API Key length: {len(api_key)}")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ No valid API key found!")
        return
    
    try:
        # Create client
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client created successfully")
        
        # Test simple generation
        print("🔄 Testing simple generation...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello, please respond with 'Test successful'",
            config={
                "max_output_tokens": 50,
                "temperature": 0.1,
            }
        )
        
        print(f"✅ API Response: {response.text}")
        print("🎉 Direct API test successful!")
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_gemini_direct()) 