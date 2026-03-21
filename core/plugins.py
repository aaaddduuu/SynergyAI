"""
自定义智能体插件系统
允许用户自定义 Agent 角色和技能
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentPlugin:
    """自定义 Agent 插件定义"""
    id: str
    name: str
    description: str
    role: str  # 角色标识符，如 "custom_analyst"
    display_name: str  # 显示名称
    system_prompt: str  # 系统提示词
    capabilities: List[str]  # 能力列表
    temperature: float = 0.7
    max_tokens: int = 2000
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = ""  # 创建者
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPlugin":
        """从字典创建实例"""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)

    def validate(self) -> tuple[bool, str]:
        """验证插件定义"""
        if not self.name or not self.name.strip():
            return False, "插件名称不能为空"

        if not self.role or not self.role.strip():
            return False, "角色标识符不能为空"

        if not self.system_prompt or not self.system_prompt.strip():
            return False, "系统提示词不能为空"

        if not self.capabilities:
            return False, "至少需要一个能力"

        # 验证 role 格式（只能包含字母、数字、下划线）
        if not self.role.replace("_", "").isalnum():
            return False, "角色标识符只能包含字母、数字和下划线"

        return True, ""


class PluginManager:
    """插件管理器"""

    def __init__(self, plugin_dir: str = None):
        """
        初始化插件管理器

        Args:
            plugin_dir: 插件存储目录
        """
        if plugin_dir is None:
            # 默认使用项目根目录下的 plugins 文件夹
            self.plugin_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "plugins"
        else:
            self.plugin_dir = Path(plugin_dir)

        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, AgentPlugin] = {}
        self._load_all_plugins()

    def _get_plugin_path(self, plugin_id: str) -> Path:
        """获取插件文件路径"""
        return self.plugin_dir / f"{plugin_id}.json"

    def _load_all_plugins(self):
        """加载所有插件"""
        try:
            for plugin_file in self.plugin_dir.glob("*.json"):
                try:
                    with open(plugin_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        plugin = AgentPlugin.from_dict(data)
                        is_valid, error_msg = plugin.validate()
                        if is_valid:
                            self.plugins[plugin.id] = plugin
                            logger.info(f"已加载插件: {plugin.name} ({plugin.id})")
                        else:
                            logger.warning(f"插件验证失败 {plugin_file}: {error_msg}")
                except Exception as e:
                    logger.error(f"加载插件失败 {plugin_file}: {e}")
        except Exception as e:
            logger.error(f"加载插件目录失败: {e}")

    def create_plugin(self, plugin: AgentPlugin) -> tuple[bool, str]:
        """
        创建新插件

        Args:
            plugin: 插件定义

        Returns:
            (成功状态, 消息)
        """
        # 验证插件
        is_valid, error_msg = plugin.validate()
        if not is_valid:
            return False, error_msg

        # 检查 ID 是否已存在
        if plugin.id in self.plugins:
            return False, f"插件 ID {plugin.id} 已存在"

        # 检查 role 是否已存在
        for existing_plugin in self.plugins.values():
            if existing_plugin.role == plugin.role:
                return False, f"角色标识符 {plugin.role} 已被使用"

        # 保存插件
        try:
            plugin_path = self._get_plugin_path(plugin.id)
            with open(plugin_path, "w", encoding="utf-8") as f:
                json.dump(plugin.to_dict(), f, ensure_ascii=False, indent=2)

            self.plugins[plugin.id] = plugin
            logger.info(f"创建插件成功: {plugin.name} ({plugin.id})")
            return True, "插件创建成功"
        except Exception as e:
            logger.error(f"保存插件失败: {e}")
            return False, f"保存插件失败: {str(e)}"

    def update_plugin(self, plugin_id: str, plugin: AgentPlugin) -> tuple[bool, str]:
        """
        更新插件

        Args:
            plugin_id: 插件 ID
            plugin: 新的插件定义

        Returns:
            (成功状态, 消息)
        """
        if plugin_id not in self.plugins:
            return False, f"插件 {plugin_id} 不存在"

        # 验证插件
        is_valid, error_msg = plugin.validate()
        if not is_valid:
            return False, error_msg

        # 检查 role 是否与其他插件冲突
        for existing_id, existing_plugin in self.plugins.items():
            if existing_plugin.role == plugin.role and existing_id != plugin_id:
                return False, f"角色标识符 {plugin.role} 已被其他插件使用"

        # 更新插件
        try:
            plugin.updated_at = datetime.now()
            plugin_path = self._get_plugin_path(plugin_id)
            with open(plugin_path, "w", encoding="utf-8") as f:
                json.dump(plugin.to_dict(), f, ensure_ascii=False, indent=2)

            self.plugins[plugin_id] = plugin
            logger.info(f"更新插件成功: {plugin.name} ({plugin_id})")
            return True, "插件更新成功"
        except Exception as e:
            logger.error(f"更新插件失败: {e}")
            return False, f"更新插件失败: {str(e)}"

    def delete_plugin(self, plugin_id: str) -> tuple[bool, str]:
        """
        删除插件

        Args:
            plugin_id: 插件 ID

        Returns:
            (成功状态, 消息)
        """
        if plugin_id not in self.plugins:
            return False, f"插件 {plugin_id} 不存在"

        try:
            plugin_path = self._get_plugin_path(plugin_id)
            plugin_path.unlink()
            del self.plugins[plugin_id]
            logger.info(f"删除插件成功: {plugin_id}")
            return True, "插件删除成功"
        except Exception as e:
            logger.error(f"删除插件失败: {e}")
            return False, f"删除插件失败: {str(e)}"

    def get_plugin(self, plugin_id: str) -> Optional[AgentPlugin]:
        """获取插件"""
        return self.plugins.get(plugin_id)

    def get_plugin_by_role(self, role: str) -> Optional[AgentPlugin]:
        """根据角色获取插件"""
        for plugin in self.plugins.values():
            if plugin.role == role:
                return plugin
        return None

    def list_plugins(self, enabled_only: bool = False) -> List[AgentPlugin]:
        """
        列出所有插件

        Args:
            enabled_only: 是否只返回启用的插件

        Returns:
            插件列表
        """
        plugins = list(self.plugins.values())
        if enabled_only:
            plugins = [p for p in plugins if p.enabled]
        return plugins

    def enable_plugin(self, plugin_id: str) -> tuple[bool, str]:
        """启用插件"""
        if plugin_id not in self.plugins:
            return False, f"插件 {plugin_id} 不存在"

        self.plugins[plugin_id].enabled = True
        # 更新文件
        return self.update_plugin(plugin_id, self.plugins[plugin_id])

    def disable_plugin(self, plugin_id: str) -> tuple[bool, str]:
        """禁用插件"""
        if plugin_id not in self.plugins:
            return False, f"插件 {plugin_id} 不存在"

        self.plugins[plugin_id].enabled = False
        # 更新文件
        return self.update_plugin(plugin_id, self.plugins[plugin_id])

    def export_plugin(self, plugin_id: str) -> tuple[bool, str, Optional[Dict]]:
        """
        导出插件

        Returns:
            (成功状态, 消息, 插件数据)
        """
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return False, f"插件 {plugin_id} 不存在", None

        return True, "导出成功", plugin.to_dict()

    def import_plugin(self, plugin_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        导入插件

        Args:
            plugin_data: 插件数据

        Returns:
            (成功状态, 消息)
        """
        try:
            # 生成新的 ID（避免冲突）
            original_id = plugin_data.get("id", "")
            new_id = f"{original_id}_{uuid.uuid4().hex[:8]}"

            plugin_data["id"] = new_id
            plugin = AgentPlugin.from_dict(plugin_data)

            return self.create_plugin(plugin)
        except Exception as e:
            logger.error(f"导入插件失败: {e}")
            return False, f"导入插件失败: {str(e)}"

    def search_plugins(self, keyword: str) -> List[AgentPlugin]:
        """搜索插件"""
        keyword = keyword.lower()
        results = []

        for plugin in self.plugins.values():
            if (keyword in plugin.name.lower() or
                keyword in plugin.description.lower() or
                keyword in plugin.role.lower() or
                any(keyword in tag.lower() for tag in plugin.tags)):
                results.append(plugin)

        return results


# 全局插件管理器实例
plugin_manager = PluginManager()
