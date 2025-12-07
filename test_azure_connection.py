#!/usr/bin/env python3
"""
Test Azure AI Foundry Connection
Run this to verify your Azure credentials are working
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or manually set environment variables")
    sys.exit(1)

print("🔍 Testing Azure AI Foundry Connection...")
print("=" * 60)

# Check credentials
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")

print("\n📋 Credentials Check:")
print(f"  API Key: {'✅ Set' if api_key else '❌ Missing'} ({len(api_key)} chars)")
print(f"  Endpoint: {endpoint if endpoint else '❌ Missing'}")
print(f"  Deployment: {deployment if deployment else '❌ Missing'}")
print(f"  API Version: {api_version if api_version else '❌ Missing'}")

if not all([api_key, endpoint, deployment]):
    print("\n❌ Missing credentials! Check your .env file.")
    sys.exit(1)

# Test Azure OpenAI client
print("\n🧪 Testing Azure OpenAI Client...")
try:
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    print("  ✅ Azure OpenAI client created successfully")
except ImportError:
    print("  ❌ openai package not installed")
    print("     Install with: pip install openai")
    sys.exit(1)
except Exception as e:
    print(f"  ❌ Error creating client: {str(e)}")
    sys.exit(1)

# Test Azure AI Service
print("\n🤖 Testing Azure AI Service...")
try:
    from services.azure_ai_service import AzureAIService
    
    ai_service = AzureAIService()
    
    if ai_service.is_available():
        print("  ✅ Azure AI Service is CONNECTED!")
        print(f"  ✅ Deployment: {ai_service.deployment_name}")
        print(f"  ✅ Endpoint: {ai_service.endpoint}")
        print(f"  ✅ API Version: {ai_service.api_version}")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your Azure AI Foundry is configured correctly!")
        print("=" * 60)
        print("\n✅ You can now:")
        print("  1. Start backend: ./start_backend.sh")
        print("  2. Start frontend: ./start_frontend.sh")
        print("  3. Upload files and get AI-powered recommendations!")
    else:
        print("  ❌ Azure AI Service is NOT connected")
        print("  ⚠️  System will use mock analysis mode")
        print("\n  Check:")
        print("    1. .env file exists in project root")
        print("    2. Credentials are correct")
        print("    3. Deployment exists in Azure Portal")
        
except Exception as e:
    print(f"  ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

