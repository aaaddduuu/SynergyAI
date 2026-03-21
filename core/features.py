"""
Feature List Management System

功能清单管理系统，参考 Anthropic 文章的最佳实践：
- 防止 Agent 过早认为项目完成
- 提供清晰的功能路线图
- 追踪开发进度
- 自动选择下一个待办功能
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path


class FeatureCategory(str, Enum):
    """功能类别"""
    BUG_FIX = "bug_fix"           # Bug 修复
    DEPLOYMENT = "deployment"     # 部署相关
    DOCUMENTATION = "documentation"  # 文档
    UI_ENHANCEMENT = "ui_enhancement"  # UI 优化
    TESTING = "testing"         # 测试
    REFACTORING = "refactoring"  # 重构
    FEATURE = "feature"         # 新功能
    IMPROVEMENT = "improvement"  # 改进
    AUTOMATION = "automation"    # 自动化
    QUALITY = "quality"         # 质量保证


class FeatureStatus(str, Enum):
    """功能状态"""
    PENDING = "pending"       # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    REVIEW = "review"         # 待审核
    DONE = "done"            # 完成


class FeaturePriority(str, Enum):
    """优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Feature:
    """功能项"""
    id: str
    category: str
    priority: str
    title: str
    description: str
    status: str
    assignee_role: str
    steps: List[str]
    passes: bool
    notes: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feature':
        """从字典创建实例"""
        return cls(**data)

    def mark_in_progress(self):
        """标记为进行中"""
        self.status = FeatureStatus.IN_PROGRESS.value
        self.updated_at = datetime.now().isoformat()

    def mark_done(self):
        """标记为完成"""
        self.status = FeatureStatus.DONE.value
        self.passes = True
        self.updated_at = datetime.now().isoformat()

    def mark_review(self):
        """标记为待审核"""
        self.status = FeatureStatus.REVIEW.value
        self.updated_at = datetime.now().isoformat()


class FeatureList:
    """功能清单管理"""

    def __init__(self, project_dir: Optional[str] = None):
        """
        初始化功能清单

        Args:
            project_dir: 项目根目录
        """
        if project_dir is None:
            project_dir = str(Path.cwd())
        self.project_dir = Path(project_dir)
        self.feature_file = self.project_dir / "feature_list.json"
        self.features: Dict[str, Feature] = {}
        self._load()

    def _load(self):
        """加载功能清单"""
        if not self.feature_file.exists():
            print(f"Warning: Feature list file not found: {self.feature_file}")
            return

        try:
            with open(self.feature_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for feat_data in data.get('features', []):
                feature = Feature.from_dict(feat_data)
                self.features[feature.id] = feature

            print(f"Loaded {len(self.features)} features from feature list")
        except Exception as e:
            print(f"Error loading feature list: {e}")

    def save(self):
        """保存功能清单"""
        try:
            # 构建数据结构
            features_list = [f.to_dict() for f in self.features.values()]

            data = {
                "project_name": "SynergyAI",
                "project_description": "多智能体协作系统",
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "features": features_list,
                "statistics": self.get_statistics()
            }

            # 保存到文件
            with open(self.feature_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Saved {len(self.features)} features to feature list")
        except Exception as e:
            print(f"Error saving feature list: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.features)

        by_status = {"pending": 0, "in_progress": 0, "review": 0, "done": 0}
        by_priority = {"high": 0, "medium": 0, "low": 0}
        by_category: Dict[str, int] = {}

        for feature in self.features.values():
            # 按状态统计
            by_status[feature.status] = by_status.get(feature.status, 0) + 1

            # 按优先级统计
            by_priority[feature.priority] = by_priority.get(feature.priority, 0) + 1

            # 按类别统计
            by_category[feature.category] = by_category.get(feature.category, 0) + 1

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_category": by_category
        }

    def get_next_feature(self, assignee_role: Optional[str] = None) -> Optional[Feature]:
        """
        获取下一个待处理的功能

        Args:
            assignee_role: 指定角色，只返回该角色的功能

        Returns:
            下一个待处理的功能，如果没有则返回 None
        """
        # 筛选待处理的功能
        pending_features = [
            f for f in self.features.values()
            if f.status == FeatureStatus.PENDING.value
        ]

        # 如果指定了角色，只返回该角色的功能
        if assignee_role:
            pending_features = [
                f for f in pending_features
                if f.assignee_role == assignee_role
            ]

        # 如果没有待处理的功能
        if not pending_features:
            return None

        # 按优先级排序
        priority_order = {
            FeaturePriority.HIGH.value: 0,
            FeaturePriority.MEDIUM.value: 1,
            FeaturePriority.LOW.value: 2
        }

        pending_features.sort(key=lambda f: priority_order.get(f.priority, 999))

        return pending_features[0]

    def get_pending_features(self, limit: int = 10) -> List[Feature]:
        """
        获取待处理功能列表

        Args:
            limit: 最多返回数量

        Returns:
            待处理功能列表
        """
        pending = [
            f for f in self.features.values()
            if f.status == FeatureStatus.PENDING.value
        ]

        # 按优先级排序
        priority_order = {
            FeaturePriority.HIGH.value: 0,
            FeaturePriority.MEDIUM.value: 1,
            FeaturePriority.LOW.value: 2
        }

        pending.sort(key=lambda f: priority_order.get(f.priority, 999))

        return pending[:limit]

    def update_feature_status(self, feature_id: str, status: str):
        """
        更新功能状态

        Args:
            feature_id: 功能 ID
            status: 新状态
        """
        if feature_id not in self.features:
            print(f"Warning: Feature {feature_id} not found")
            return

        feature = self.features[feature_id]
        feature.status = status
        feature.updated_at = datetime.now().isoformat()

        # 如果状态是 done，设置 passes 为 True
        if status == FeatureStatus.DONE.value:
            feature.passes = True

        self.save()
        print(f"Updated feature {feature_id} status to {status}")

    def add_feature(self, feature: Feature):
        """
        添加新功能

        Args:
            feature: 功能对象
        """
        self.features[feature.id] = feature
        self.save()
        print(f"Added new feature: {feature.title}")

    def get_progress_summary(self) -> str:
        """
        获取进度摘要

        Returns:
            进度摘要文本
        """
        stats = self.get_statistics()
        total = stats['total']
        done = stats['by_status']['done']

        progress_percent = int(done / total * 100) if total > 0 else 0

        summary = f"""
## 📊 功能清单进度摘要

**总功能数**: {total}
**已完成**: {done} ({progress_percent}%)
**待处理**: {stats['by_status']['pending']}
**进行中**: {stats['by_status']['in_progress']}
**待审核**: {stats['by_status']['review']}

### 按优先级分布
- 🔴 高优先级: {stats['by_priority']['high']}
- 🟡 中优先级: {stats['by_priority']['medium']}
- 🟢 低优先级: {stats['by_priority']['low']}

### 按类别分布
"""
        for category, count in stats['by_category'].items():
            summary += f"- **{category}**: {count}\n"

        return summary

    def generate_report(self) -> str:
        """
        生成完整报告

        Returns:
            完整的进度报告
        """
        stats = self.get_statistics()

        report = f"""
# 🎯 SynergyAI 功能清单报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总体进度

| 指标 | 数量 |
|------|------|
| 总功能数 | {stats['total']} |
| 已完成 | {stats['by_status']['done']} |
| 进行中 | {stats['by_status']['in_progress']} |
| 待处理 | {stats['by_status']['pending']} |
| 待审核 | {stats['by_status']['review']} |

## 🔴 高优先级任务

"""

        high_priority = [f for f in self.features.values() if f.priority == "high"]
        for feat in high_priority[:5]:  # 只显示前 5 个
            status_icon = {
                "pending": "⏸️",
                "in_progress": "▶️",
                "review": "👀",
                "done": "✅"
            }.get(feat.status, "❓")

            report += f"{status_icon} **{feat.title}**\n"
            report += f"   - 描述: {feat.description}\n"
            report += f"   - 负责人: {feat.assignee_role}\n"
            report += f"   - 状态: {feat.status}\n\n"

        return report
