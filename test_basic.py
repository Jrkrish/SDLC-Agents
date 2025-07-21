#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

print("Testing basic DevPilot functionality...")
print("=" * 50)

# Test environment variables
print("1. Testing environment variables:")
groq_key = os.getenv("GROQ_API_KEY")
if groq_key and groq_key != "your_groq_api_key_here":
    print("✅ GROQ_API_KEY is configured")
else:
    print("❌ GROQ_API_KEY is not configured")

gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key and gemini_key != "your_gemini_api_key_here":
    print("✅ GEMINI_API_KEY is configured")
else:
    print("❌ GEMINI_API_KEY is not configured")

print()

# Test basic imports
print("2. Testing basic imports:")
try:
    from src.dev_pilot.cache.redis_cache import save_state_to_redis
    print("✅ Cache module import successful")
except Exception as e:
    print(f"❌ Cache module import failed: {e}")

try:
    from src.dev_pilot.state.sdlc_state import SDLCState
    print("✅ State module import successful")
except Exception as e:
    print(f"❌ State module import failed: {e}")

try:
    from src.dev_pilot.utils.constants import PROJECT_INITILIZATION
    print("✅ Constants module import successful")
except Exception as e:
    print(f"❌ Constants module import failed: {e}")

print()

print("3. Testing LLM imports (these might fail due to dependency issues):")
try:
    from src.dev_pilot.LLMS.groqllm import GroqLLM
    print("✅ GroqLLM import successful")
    
    # Test LLM initialization if API key is available
    if groq_key and groq_key != "your_groq_api_key_here":
        try:
            llm_instance = GroqLLM(model="gemma2-9b-it", api_key=groq_key)
            print("✅ GroqLLM instance created successfully")
        except Exception as e:
            print(f"⚠️  GroqLLM instance creation failed: {e}")
    else:
        print("⚠️  Cannot test GroqLLM instance - no API key")
        
except Exception as e:
    print(f"❌ GroqLLM import failed: {e}")

print()
print("=" * 50)
print("Basic test completed!")
