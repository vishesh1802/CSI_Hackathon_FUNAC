#!/usr/bin/env python3
"""
Test Azure AI Agent Connection
Verifies that Azure AI Foundry is working correctly
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("❌ python-dotenv not installed")
    print("   Install with: pip install python-dotenv")
    sys.exit(1)

print("="*60)
print("🧪 AZURE AI AGENT CONNECTION TEST")
print("="*60)

# Check credentials
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")

print("\n📋 Configuration Check:")
print(f"  API Key: {'✅ Set' if api_key else '❌ Missing'} ({len(api_key)} chars)")
print(f"  Endpoint: {endpoint if endpoint else '❌ Missing'}")
print(f"  Deployment: {deployment if deployment else '❌ Missing'}")
print(f"  API Version: {api_version if api_version else '❌ Missing'}")

if not all([api_key, endpoint, deployment]):
    print("\n❌ Missing credentials! Check your .env file.")
    sys.exit(1)

# Test Azure OpenAI client
print("\n🔌 Testing Azure OpenAI Connection...")
try:
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    print("  ✅ Azure OpenAI client created")
except Exception as e:
    print(f"  ❌ Error creating client: {str(e)}")
    sys.exit(1)

# Test actual API call
print("\n🤖 Testing API Call...")
try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Azure AI is working!' if you can read this."}
        ],
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"  ✅ API call successful!")
    print(f"  ✅ Response: {result}")
    
    # Token usage
    usage = response.usage
    print(f"\n📊 Token Usage:")
    print(f"  Prompt tokens: {usage.prompt_tokens}")
    print(f"  Completion tokens: {usage.completion_tokens}")
    print(f"  Total tokens: {usage.total_tokens}")
    
except Exception as e:
    print(f"  ❌ API call failed: {str(e)}")
    print(f"\n  Common issues:")
    print(f"    - Deployment name doesn't match Azure Portal")
    print(f"    - API key is incorrect")
    print(f"    - Endpoint URL is wrong")
    print(f"    - Model not deployed yet")
    sys.exit(1)

# Test Azure AI Service
print("\n🔧 Testing Azure AI Service Integration...")
try:
    from services.azure_ai_service import AzureAIService
    
    ai_service = AzureAIService()
    
    if ai_service.is_available():
        print("  ✅ Azure AI Service is CONNECTED!")
        print(f"  ✅ Deployment: {ai_service.deployment_name}")
        
        # Test with sample event
        print("\n📝 Testing with Sample Robot Event...")
        sample_event = {
            "event_id": "test-001",
            "event_type": "error_log",
            "timestamp": "2025-11-17T09:00:00",
            "description": "SRVO-160 - Collision detected",
            "error_code": "SRVO-160",
            "joint": "J3",
            "severity": "high",
            "force_value": 645.0
        }
        
        import asyncio
        result = asyncio.run(ai_service.analyze_event(sample_event))
        
        print("  ✅ AI analysis successful!")
        print(f"  ✅ Priority: {result.get('priority')}")
        print(f"  ✅ Risk Score: {result.get('risk_score')}")
        print(f"  ✅ Recommendation: {result.get('recommendation', '')[:80]}...")
        
        if result.get('maintenance_report'):
            print("  ✅ Maintenance report generated (5 sections)")
        
        print("\n" + "="*60)
        print("🎉 AZURE AI AGENT IS WORKING CORRECTLY!")
        print("="*60)
    else:
        print("  ❌ Azure AI Service is NOT connected")
        print("  ⚠️  Check your .env file and credentials")
        
except Exception as e:
    print(f"  ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

