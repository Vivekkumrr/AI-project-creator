import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "your_random_secret_key"
    print("⚠️ Using fallback SECRET_KEY - set SECRET_KEY in .env for production")

# App Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
def is_valid_api_key(api_key):
    if not api_key:
        return False
    return api_key.startswith('sk-') and len(api_key) > 20

# Validate the key
if OPENAI_API_KEY and is_valid_api_key(OPENAI_API_KEY):
    print("✅ Valid OpenAI API key detected")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
else:
    print("❌ No valid OpenAI API key found")
    print("💡 Set OPENAI_API_KEY in your .env file")
    OPENAI_API_KEY = None  # Explicitly set to None
    OPENAI_MODEL = None

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Database Configuration
DATABASE_NAME = "llm_app.db"

print(f"🔧 Config loaded: OPENAI_API_KEY exists: {bool(OPENAI_API_KEY)}")


