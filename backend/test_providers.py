"""
Test script for multi-provider AI system
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to Python path
import sys
sys.path.append('src')

from models.factory import initialize_factory, get_provider
from models.base import ChatMessage, ModelRole

async def test_providers():
    """Test the multi-provider system"""

    print("🤖 Testing Multi-Provider AI System")
    print("=" * 50)

    # Initialize factory with API keys
    api_keys = {
        "gemini": os.getenv("GEMINI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "perplexity": os.getenv("PERPLEXITY_API_KEY")
    }

    print(f"API Keys available: {[k for k, v in api_keys.items() if v]}")

    try:
        # Initialize the factory
        factory = initialize_factory(api_keys)
        print(f"✅ Factory initialized with {len(factory.get_available_providers())} providers")

        # Get provider statistics
        stats = factory.get_provider_stats()
        print(f"📊 Available providers: {stats['available_providers']}")
        print(f"🎭 Role mappings: {stats['role_mappings']}")

        # Test health checks
        print("\n🏥 Running health checks...")
        health_status = await factory.health_check_all()
        for provider, status in health_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {provider}: {'Healthy' if status else 'Unhealthy'}")

        # Test specific provider
        if "gemini" in factory.get_available_providers():
            print("\n🧪 Testing Gemini provider...")
            provider = get_provider(provider_name="gemini")
            messages = [ChatMessage(role="user", content="Hello! Say 'Multi-provider system working!' in exactly those words.")]

            response = await provider.chat(messages, max_tokens=50)
            print(f"   Response: {response.content}")
            print(f"   Model: {response.model}")
            print(f"   Usage: {response.usage}")

        # Test role-based selection
        print("\n🎭 Testing role-based selection...")
        judge_provider = get_provider(role=ModelRole.JUDGE)
        print(f"   Judge role assigned to: {judge_provider.provider_name}")

        writer_provider = get_provider(role=ModelRole.WRITER)
        print(f"   Writer role assigned to: {writer_provider.provider_name}")

        print("\n🎉 Multi-provider system test completed successfully!")

    except Exception as e:
        print(f"❌ Error testing providers: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_providers())
