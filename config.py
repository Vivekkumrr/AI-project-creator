import os
import secrets
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Database Configuration
DATABASE_NAME = "llm_app.db"

print(f"🔧 Config loaded: OPENAI_API_KEY exists: {bool(OPENAI_API_KEY)}")
