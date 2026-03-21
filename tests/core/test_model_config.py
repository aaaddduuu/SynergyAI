"""Tests for core.model_config module"""

import pytest
from core.model_config import (
    ModelProvider,
    ModelConfig,
    AgentModelConfig,
    ModelConfigManager,
    MODEL_OPTIONS,
    PROVIDER_BASE_URLS,
    model_config_manager,
    create_llm_for_config
)


class TestModelConfig:
    """Test ModelConfig dataclass"""

    def test_model_config_defaults(self):
        """Test ModelConfig default values"""
        config = ModelConfig()
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.api_key == ""
        assert config.base_url == ""
        assert config.temperature == 0.7
        assert config.max_tokens == 4000

    def test_model_config_custom_values(self):
        """Test ModelConfig with custom values"""
        config = ModelConfig(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="sk-test",
            base_url="https://api.example.com",
            temperature=0.5,
            max_tokens=2000
        )
        assert config.provider == "anthropic"
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.api_key == "sk-test"
        assert config.base_url == "https://api.example.com"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000


class TestAgentModelConfig:
    """Test AgentModelConfig dataclass"""

    def test_agent_model_config_defaults(self):
        """Test AgentModelConfig default values"""
        config = AgentModelConfig(role="dev")
        assert config.role == "dev"
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.api_key == ""
        assert config.base_url == ""
        assert config.temperature == 0.7

    def test_agent_model_config_custom_values(self):
        """Test AgentModelConfig with custom values"""
        config = AgentModelConfig(
            role="qa",
            provider="anthropic",
            model="claude-3-opus-20240229",
            api_key="sk-qa-test",
            temperature=0.3
        )
        assert config.role == "qa"
        assert config.provider == "anthropic"
        assert config.model == "claude-3-opus-20240229"
        assert config.api_key == "sk-qa-test"
        assert config.temperature == 0.3


class TestModelOptions:
    """Test MODEL_OPTIONS constant"""

    def test_openai_models(self):
        """Test OpenAI model options"""
        openai_models = MODEL_OPTIONS.get("openai")
        assert openai_models is not None
        assert "gpt-4o" in openai_models
        assert "gpt-4o-mini" in openai_models
        assert "gpt-4-turbo" in openai_models
        assert "gpt-3.5-turbo" in openai_models

    def test_anthropic_models(self):
        """Test Anthropic model options"""
        anthropic_models = MODEL_OPTIONS.get("anthropic")
        assert anthropic_models is not None
        assert "claude-3-5-sonnet-20241022" in anthropic_models
        assert "claude-3-opus-20240229" in anthropic_models

    def test_zhipu_models(self):
        """Test Zhipu model options"""
        zhipu_models = MODEL_OPTIONS.get("zhipu")
        assert zhipu_models is not None
        assert "glm-4" in zhipu_models
        assert "glm-4-plus" in zhipu_models

    def test_custom_models(self):
        """Test custom model options"""
        custom_models = MODEL_OPTIONS.get("custom")
        assert custom_models is not None
        assert "custom" in custom_models


class TestProviderBaseUrls:
    """Test PROVIDER_BASE_URLS constant"""

    def test_openai_base_url(self):
        """Test OpenAI base URL"""
        assert PROVIDER_BASE_URLS["openai"] == "https://api.openai.com/v1"

    def test_anthropic_base_url(self):
        """Test Anthropic base URL"""
        assert PROVIDER_BASE_URLS["anthropic"] == "https://api.anthropic.com"

    def test_zhipu_base_url(self):
        """Test Zhipu base URL"""
        assert PROVIDER_BASE_URLS["zhipu"] == "https://open.bigmodel.cn/api/paas/v4"


class TestModelConfigManager:
    """Test ModelConfigManager class"""

    def test_manager_initialization(self):
        """Test manager initializes with default config"""
        manager = ModelConfigManager()
        default_config = manager.get_default_config()
        assert default_config.provider == "openai"
        assert default_config.model == "gpt-4o"

    def test_set_default_config(self):
        """Test setting default config"""
        manager = ModelConfigManager()
        new_config = ModelConfig(provider="anthropic", model="claude-3-opus-20240229")
        manager.set_default_config(new_config)

        default = manager.get_default_config()
        assert default.provider == "anthropic"
        assert default.model == "claude-3-opus-20240229"

    def test_set_agent_config(self):
        """Test setting agent-specific config"""
        manager = ModelConfigManager()
        config = AgentModelConfig(
            role="dev",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022"
        )
        manager.set_agent_config("dev", config)

        retrieved = manager.get_agent_config("dev")
        assert retrieved is not None
        assert retrieved.role == "dev"
        assert retrieved.provider == "anthropic"

    def test_get_agent_config_not_exists(self):
        """Test getting non-existent agent config"""
        manager = ModelConfigManager()
        config = manager.get_agent_config("nonexistent")
        assert config is None

    def test_get_config_for_role_with_agent_config(self):
        """Test getting config for role when agent config exists"""
        manager = ModelConfigManager()
        manager.set_default_config(ModelConfig(
            provider="openai",
            api_key="default-key",
            base_url="https://default.com"
        ))

        agent_config = AgentModelConfig(
            role="qa",
            provider="anthropic",
            model="claude-3-opus-20240229",
            api_key="qa-key"
        )
        manager.set_agent_config("qa", agent_config)

        config = manager.get_config_for_role("qa")
        assert config.provider == "anthropic"
        assert config.model == "claude-3-opus-20240229"
        # Should fallback to default for base_url if not specified
        assert config.base_url == "https://api.anthropic.com"

    def test_get_config_for_role_without_agent_config(self):
        """Test getting config for role when no agent config exists"""
        manager = ModelConfigManager()
        default_config = ModelConfig(
            provider="zhipu",
            model="glm-4",
            api_key="test-key"
        )
        manager.set_default_config(default_config)

        config = manager.get_config_for_role("dev")
        assert config.provider == "zhipu"
        assert config.model == "glm-4"

    def test_get_available_models_for_provider(self):
        """Test getting available models for specific provider"""
        manager = ModelConfigManager()

        openai_models = manager.get_available_models("openai")
        assert len(openai_models) > 0
        assert "gpt-4o" in openai_models

        anthropic_models = manager.get_available_models("anthropic")
        assert len(anthropic_models) > 0
        assert "claude-3-5-sonnet-20241022" in anthropic_models

    def test_get_available_models_all(self):
        """Test getting all available models"""
        manager = ModelConfigManager()
        all_models = manager.get_available_models()

        assert len(all_models) > 0
        assert "gpt-4o" in all_models
        assert "claude-3-5-sonnet-20241022" in all_models
        assert "glm-4" in all_models

    def test_get_available_models_invalid_provider(self):
        """Test getting models for invalid provider"""
        manager = ModelConfigManager()
        models = manager.get_available_models("invalid_provider")
        assert models == []

    def test_get_all_providers(self):
        """Test getting all providers"""
        manager = ModelConfigManager()
        providers = manager.get_all_providers()

        assert len(providers) == 4
        assert "openai" in providers
        assert "anthropic" in providers
        assert "zhipu" in providers
        assert "custom" in providers


class TestGlobalConfigManager:
    """Test global model_config_manager instance"""

    def test_global_manager_exists(self):
        """Test that global manager instance exists"""
        assert model_config_manager is not None
        assert isinstance(model_config_manager, ModelConfigManager)

    def test_global_manager_get_default(self):
        """Test getting default config from global manager"""
        config = model_config_manager.get_default_config()
        assert config is not None


class TestCreateLLMForConfig:
    """Test create_llm_for_config function"""

    def test_create_openai_llm(self):
        """Test creating OpenAI LLM"""
        config = ModelConfig(
            provider="openai",
            model="gpt-4o",
            api_key="test-key"
        )

        llm = create_llm_for_config(config)
        assert llm is not None
        # Check that the LLM has the correct model
        assert llm.model_name == "gpt-4o"

    def test_create_openai_llm_with_base_url(self):
        """Test creating OpenAI-compatible LLM with custom base URL"""
        config = ModelConfig(
            provider="openai",
            model="gpt-4o",
            api_key="test-key",
            base_url="https://custom.openai.com/v1"
        )

        llm = create_llm_for_config(config)
        assert llm is not None

    def test_create_custom_llm(self):
        """Test creating custom OpenAI-compatible LLM"""
        config = ModelConfig(
            provider="custom",
            model="custom-model",
            api_key="test-key",
            base_url="https://api.custom.com/v1"
        )

        llm = create_llm_for_config(config)
        assert llm is not None
