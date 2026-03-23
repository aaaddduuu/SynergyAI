from typing import Optional, Dict
from dataclasses import dataclass, field
from enum import Enum


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"
    CUSTOM = "custom"


MODEL_OPTIONS = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "zhipu": [
        "glm-4.7",
        "glm-4-plus",
        "glm-4-flash",
        "glm-4-air",
        "glm-4-airx",
        "glm-4",
        "glm-3-turbo",
    ],
    "custom": [
        "custom"
    ]
}

PROVIDER_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
}


@dataclass
class ModelConfig:
    provider: str = "zhipu"
    model: str = "glm-4.7"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 4000


@dataclass
class AgentModelConfig:
    role: str
    provider: str = "zhipu"
    model: str = "glm-4.7"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7


class ModelConfigManager:
    def __init__(self):
        self.default_config = ModelConfig()
        self.agent_configs: Dict[str, AgentModelConfig] = {}
    
    def set_default_config(self, config: ModelConfig):
        self.default_config = config
    
    def get_default_config(self) -> ModelConfig:
        return self.default_config
    
    def set_agent_config(self, role: str, config: AgentModelConfig):
        self.agent_configs[role] = config
    
    def get_agent_config(self, role: str) -> Optional[AgentModelConfig]:
        return self.agent_configs.get(role)
    
    def get_config_for_role(self, role: str) -> ModelConfig:
        agent_config = self.get_agent_config(role)
        if agent_config:
            # 使用 agent 配置，如果缺少某些字段则使用默认配置
            return ModelConfig(
                provider=agent_config.provider,
                model=agent_config.model,
                api_key=agent_config.api_key or self.default_config.api_key,
                base_url=agent_config.base_url or PROVIDER_BASE_URLS.get(agent_config.provider, ""),
                temperature=agent_config.temperature
            )

        return self.default_config
    
    def _get_base_url(self, provider: str) -> str:
        return PROVIDER_BASE_URLS.get(provider, "")
    
    def get_available_models(self, provider: str = None) -> list:
        if provider:
            return MODEL_OPTIONS.get(provider, [])
        all_models = []
        for models in MODEL_OPTIONS.values():
            all_models.extend(models)
        return all_models
    
    def get_all_providers(self) -> list:
        return list(MODEL_OPTIONS.keys())


model_config_manager = ModelConfigManager()


def create_llm_for_config(config: ModelConfig, provider: str = None):
    provider = provider or config.provider
    
    if provider == "openai" or config.base_url and "openai" in config.base_url:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key or "dummy",
            base_url=config.base_url or None,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.model,
            anthropic_api_key=config.api_key or "dummy",
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    elif provider == "zhipu":
        from langchain_community.chat_models import ChatZhipuAI
        return ChatZhipuAI(
            model=config.model,
            zhipuai_api_key=config.api_key or "dummy",
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key or "dummy",
            base_url=config.base_url or None,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
