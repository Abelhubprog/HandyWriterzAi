#!/usr/bin/env python3
"""
Provider validation script for HandyWriterzAI.
Validates API keys and tests error handling for all configured providers.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List
import traceback

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.models.factory import initialize_factory, get_factory, ModelRole
from backend.src.models.base import ChatMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProviderValidator:
    """Validate provider configurations and error handling."""

    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.factory = None
        self.results = {}

    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables."""
        return {
            "gemini": os.getenv("GEMINI_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "openrouter": os.getenv("OPENROUTER_API_KEY", ""),
            "perplexity": os.getenv("PERPLEXITY_API_KEY", ""),
        }

    def _filter_valid_keys(self) -> Dict[str, str]:
        """Filter out empty API keys."""
        return {k: v for k, v in self.api_keys.items() if v}

    async def validate_providers(self):
        """Validate all configured providers."""
        logger.info("🔍 Starting provider validation...")

        # Initialize factory with available keys
        valid_keys = self._filter_valid_keys()
        if not valid_keys:
            logger.error("❌ No valid API keys found!")
            return False

        logger.info(f"🔑 Found {len(valid_keys)} valid API keys: {list(valid_keys.keys())}")

        try:
            self.factory = initialize_factory(valid_keys)
        except Exception as e:
            logger.error(f"❌ Failed to initialize provider factory: {e}")
            return False

        # Test each provider
        providers = self.factory.get_available_providers()
        logger.info(f"🔧 Testing {len(providers)} providers: {providers}")

        for provider_name in providers:
            await self._test_provider(provider_name)

        # Test role mappings
        await self._test_role_mappings()

        # Test health checks
        await self._test_health_checks()

        # Print summary
        self._print_summary()

        return True

    async def _test_provider(self, provider_name: str):
        """Test a specific provider."""
        logger.info(f"🧪 Testing provider: {provider_name}")

        try:
            # Get provider instance
            provider = self.factory.get_provider(provider_name)

            # Test basic properties
            provider_info = {
                "name": provider.provider_name,
                "available_models": provider.available_models,
                "default_model": provider.get_default_model()
            }

            logger.info(f"   📋 Provider info: {provider_info}")

            # Test chat functionality with a simple message
            test_messages = [ChatMessage(role="user", content="Hello, this is a test message.")]

            try:
                response = await provider.chat(
                    messages=test_messages,
                    max_tokens=50,
                    temperature=0.7
                )

                if response and response.content:
                    logger.info(f"   ✅ Chat test successful: {len(response.content)} characters received")
                    self.results[provider_name] = {
                        "status": "healthy",
                        "response_length": len(response.content),
                        "model_used": response.model
                    }
                else:
                    logger.warning(f"   ⚠️ Chat test returned empty response")
                    self.results[provider_name] = {
                        "status": "warning",
                        "error": "Empty response"
                    }

            except Exception as e:
                logger.error(f"   ❌ Chat test failed: {e}")
                self.results[provider_name] = {
                    "status": "error",
                    "error": str(e)
                }

        except Exception as e:
            logger.error(f"   ❌ Provider test failed: {e}")
            self.results[provider_name] = {
                "status": "error",
                "error": str(e)
            }

    async def _test_role_mappings(self):
        """Test role-based provider mappings."""
        logger.info("🎯 Testing role mappings...")

        try:
            role_stats = self.factory.get_provider_stats()
            role_mappings = role_stats.get("role_mappings", {})

            logger.info(f"   📋 Role mappings: {role_mappings}")

            # Test each role mapping
            for role in ModelRole:
                try:
                    provider = self.factory.get_provider(role=role)
                    logger.info(f"   ✅ Role {role.value} -> {provider.provider_name}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Role {role.value} mapping failed: {e}")

        except Exception as e:
            logger.error(f"   ❌ Role mapping test failed: {e}")

    async def _test_health_checks(self):
        """Test provider health checks."""
        logger.info("🏥 Testing health checks...")

        try:
            health_status = await self.factory.health_check_all()
            logger.info(f"   📋 Health status: {health_status}")

            # Update results with health check info
            for provider_name, is_healthy in health_status.items():
                if provider_name in self.results:
                    self.results[provider_name]["health_check"] = is_healthy
                else:
                    self.results[provider_name] = {"health_check": is_healthy}

        except Exception as e:
            logger.error(f"   ❌ Health check test failed: {e}")

    def _print_summary(self):
        """Print validation summary."""
        logger.info("\n" + "="*60)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*60)

        healthy_count = 0
        error_count = 0
        warning_count = 0

        for provider_name, result in self.results.items():
            status = result.get("status", "unknown")
            if status == "healthy":
                healthy_count += 1
                logger.info(f"✅ {provider_name}: Healthy")
            elif status == "error":
                error_count += 1
                error_msg = result.get("error", "Unknown error")
                logger.info(f"❌ {provider_name}: Error - {error_msg}")
            elif status == "warning":
                warning_count += 1
                error_msg = result.get("error", "Warning")
                logger.info(f"⚠️ {provider_name}: Warning - {error_msg}")
            else:
                logger.info(f"❓ {provider_name}: {result}")

        logger.info("-"*60)
        logger.info(f"Total: {len(self.results)} providers")
        logger.info(f"Healthy: {healthy_count}")
        logger.info(f"Warnings: {warning_count}")
        logger.info(f"Errors: {error_count}")

        if error_count > 0:
            logger.info("\n⚠️ Some providers have issues. Check the logs above for details.")
        elif warning_count > 0:
            logger.info("\n✅ All providers are functional with minor warnings.")
        else:
            logger.info("\n✅ All providers are healthy and ready for use.")


async def main():
    """Main validation function."""
    validator = ProviderValidator()

    try:
        success = await validator.validate_providers()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
