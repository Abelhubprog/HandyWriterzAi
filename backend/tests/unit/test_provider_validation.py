"""Unit tests for provider validation functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio

from backend.scripts.validate_providers import ProviderValidator
from backend.src.models.base import ChatMessage, ChatResponse


class TestProviderValidator:
    """Test provider validation functionality."""

    @pytest.fixture
    def validator(self):
        """Create a ProviderValidator instance."""
        return ProviderValidator()

    def test_load_api_keys(self, validator):
        """Test loading API keys from environment variables."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'GEMINI_API_KEY': 'test-gemini-key',
            'OPENAI_API_KEY': 'test-openai-key',
            'ANTHROPIC_API_KEY': '',  # Empty key should be filtered out
        }):
            api_keys = validator._load_api_keys()

            assert api_keys['gemini'] == 'test-gemini-key'
            assert api_keys['openai'] == 'test-openai-key'
            assert api_keys['anthropic'] == ''

    def test_filter_valid_keys(self, validator):
        """Test filtering out empty API keys."""
        # Set up mock API keys
        validator.api_keys = {
            'gemini': 'test-gemini-key',
            'openai': '',  # Empty key
            'anthropic': 'test-anthropic-key',
            'openrouter': None,  # None key
        }

        valid_keys = validator._filter_valid_keys()

        assert 'gemini' in valid_keys
        assert 'anthropic' in valid_keys
        assert 'openai' not in valid_keys  # Should be filtered out
        assert 'openrouter' not in valid_keys  # Should be filtered out
        assert len(valid_keys) == 2

    @pytest.mark.asyncio
    async def test_test_provider_success(self, validator):
        """Test successful provider testing."""
        # Mock factory and provider
        mock_provider = Mock()
        mock_provider.provider_name = 'gemini'
        mock_provider.available_models = ['gemini-pro', 'gemini-flash']
        mock_provider.get_default_model.return_value = 'gemini-pro'

        # Mock chat response
        mock_response = ChatResponse(
            content='Hello! This is a test response.',
            model='gemini-pro',
            provider='gemini'
        )
        mock_provider.chat = AsyncMock(return_value=mock_response)

        with patch.object(validator, 'factory') as mock_factory:
            mock_factory.get_provider.return_value = mock_provider

            await validator._test_provider('gemini')

            # Check that results were recorded
            assert 'gemini' in validator.results
            assert validator.results['gemini']['status'] == 'healthy'
            assert validator.results['gemini']['response_length'] == len(mock_response.content)

    @pytest.mark.asyncio
    async def test_test_provider_chat_error(self, validator):
        """Test provider testing with chat error."""
        # Mock factory and provider
        mock_provider = Mock()
        mock_provider.provider_name = 'gemini'
        mock_provider.available_models = ['gemini-pro', 'gemini-flash']
        mock_provider.get_default_model.return_value = 'gemini-pro'

        # Mock chat to raise an exception
        mock_provider.chat = AsyncMock(side_effect=Exception('API Error'))

        with patch.object(validator, 'factory') as mock_factory:
            mock_factory.get_provider.return_value = mock_provider

            await validator._test_provider('gemini')

            # Check that error was recorded
            assert 'gemini' in validator.results
            assert validator.results['gemini']['status'] == 'error'
            assert 'API Error' in validator.results['gemini']['error']

    @pytest.mark.asyncio
    async def test_test_provider_initialization_error(self, validator):
        """Test provider testing with initialization error."""
        with patch.object(validator, 'factory') as mock_factory:
            mock_factory.get_provider.side_effect = Exception('Provider not found')

            await validator._test_provider('nonexistent')

            # Check that error was recorded
            assert 'nonexistent' in validator.results
            assert validator.results['nonexistent']['status'] == 'error'
            assert 'Provider not found' in validator.results['nonexistent']['error']

    @pytest.mark.asyncio
    async def test_test_role_mappings(self, validator):
        """Test role mapping validation."""
        # Mock factory stats
        mock_stats = {
            'role_mappings': {
                'writer': 'gemini',
                'researcher': 'perplexity'
            }
        }

        with patch.object(validator, 'factory') as mock_factory:
            mock_factory.get_provider_stats.return_value = mock_stats
            mock_factory.get_provider.return_value = Mock(provider_name='gemini')

            await validator._test_role_mappings()

            # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_test_health_checks(self, validator):
        """Test health check validation."""
        mock_health_status = {
            'gemini': True,
            'openai': False
        }

        validator.results = {
            'gemini': {'status': 'healthy'},
            'openai': {'status': 'error', 'error': 'API key invalid'}
        }

        with patch.object(validator, 'factory') as mock_factory:
            mock_factory.health_check_all = AsyncMock(return_value=mock_health_status)

            await validator._test_health_checks()

            # Check that health check results were added
            assert validator.results['gemini']['health_check'] is True
            assert validator.results['openai']['health_check'] is False

    def test_print_summary(self, validator, caplog):
        """Test printing validation summary."""
        validator.results = {
            'gemini': {'status': 'healthy'},
            'openai': {'status': 'error', 'error': 'API key invalid'},
            'anthropic': {'status': 'warning', 'error': 'Rate limited'}
        }

        with caplog.at_level('INFO'):
            validator._print_summary()

            # Check that summary was logged
            assert 'VALIDATION SUMMARY' in caplog.text
            assert 'Healthy: 1' in caplog.text
            assert 'Errors: 1' in caplog.text
            assert 'Warnings: 1' in caplog.text


# Mock for async functions
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


if __name__ == "__main__":
    pytest.main([__file__])
