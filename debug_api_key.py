import os
from utils.config import Settings

def debug_api_key():
    """Debug the API key configuration"""
    print("🔍 Debugging API Key Configuration...")
    print("-" * 50)
    
    # Check if .env file exists
    env_exists = os.path.exists(".env")
    print(f"📁 .env file exists: {env_exists}")
    
    # Load settings
    settings = Settings()
    print(f"🔑 GEMINI_API_KEY loaded: {settings.gemini_api_key[:20] if settings.gemini_api_key else 'NOT SET'}...")
    print(f"🔑 GEMINI_API_KEY length: {len(settings.gemini_api_key) if settings.gemini_api_key else 0}")
    
    # Check environment variables
    env_key = os.getenv("GEMINI_API_KEY")
    print(f"🌍 Environment GEMINI_API_KEY: {env_key[:20] if env_key else 'NOT SET'}...")
    
    # Check if API key is valid
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        print("❌ API KEY ISSUE: No valid API key found!")
        print("💡 Solution: Create a .env file with your actual API key")
        return False
    else:
        print("✅ API key appears to be set")
        return True

if __name__ == "__main__":
    debug_api_key() 