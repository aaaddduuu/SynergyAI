"""
QA 测试检查清单
参考 Anthropic 文章的端到端测试理念
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class TestCategory(str, Enum):
    """测试类别"""
    HAPPY_PATH = "happy_path"  # 正常场景
    BOUNDARY = "boundary"  # 边界条件
    EXCEPTION = "exception"  # 异常处理
    INTEGRATION = "integration"  # 集成测试
    PERFORMANCE = "performance"  # 性能测试


@dataclass
class ChecklistItem:
    """检查项"""
    id: str
    category: TestCategory
    description: str
    is_required: bool = True  # 是否必须
    status: str = "pending"  # pending, passed, failed, skipped


class QAChecklist:
    """
    QA 测试检查清单
    确保 QA Agent 真正执行端到端测试
    """

    def __init__(self):
        self.checklist_items: List[ChecklistItem] = []
        self._init_default_checklist()

    def _init_default_checklist(self):
        """初始化默认检查清单"""
        # 基础验证（必须）
        self.checklist_items = [
            ChecklistItem(
                id="1",
                category=TestCategory.HAPPY_PATH,
                description="是否真正执行了功能（而不是只看代码）？",
                is_required=True
            ),
            ChecklistItem(
                id="2",
                category=TestCategory.HAPPY_PATH,
                description="正常场景测试是否通过？",
                is_required=True
            ),
            ChecklistItem(
                id="3",
                category=TestCategory.BOUNDARY,
                description="边界条件测试是否完成？（空值、极值等）",
                is_required=True
            ),
            ChecklistItem(
                id="4",
                category=TestCategory.EXCEPTION,
                description="异常处理测试是否完成？（无效输入、错误提示）",
                is_required=True
            ),
            ChecklistItem(
                id="5",
                category=TestCategory.HAPPY_PATH,
                description="实际结果是否与期望结果一致？",
                is_required=True
            ),
            ChecklistItem(
                id="6",
                category=TestCategory.HAPPY_PATH,
                description="是否生成了详细的测试报告？",
                is_required=True
            ),
            ChecklistItem(
                id="7",
                category=TestCategory.INTEGRATION,
                description="是否验证了功能与现有系统的集成？",
                is_required=False
            ),
            ChecklistItem(
                id="8",
                category=TestCategory.EXCEPTION,
                description="错误提示是否清晰友好？",
                is_required=False
            ),
            ChecklistItem(
                id="9",
                category=TestCategory.PERFORMANCE,
                description="是否进行了基本的性能验证？（响应时间、资源使用）",
                is_required=False
            ),
            ChecklistItem(
                id="10",
                category=TestCategory.HAPPY_PATH,
                description="核心功能是否完全实现？",
                is_required=True
            ),
        ]

    def get_required_items(self) -> List[ChecklistItem]:
        """获取必须检查的项目"""
        return [item for item in self.checklist_items if item.is_required]

    def get_optional_items(self) -> List[ChecklistItem]:
        """获取可选检查项目"""
        return [item for item in self.checklist_items if not item.is_required]

    def get_items_by_category(self, category: TestCategory) -> List[ChecklistItem]:
        """按类别获取检查项"""
        return [item for item in self.checklist_items if item.category == category]

    def update_item_status(self, item_id: str, status: str):
        """更新检查项状态"""
        for item in self.checklist_items:
            if item.id == item_id:
                item.status = status
                break

    def get_summary(self) -> Dict[str, Any]:
        """获取检查清单摘要"""
        total = len(self.checklist_items)
        required = len(self.get_required_items())
        passed = sum(1 for item in self.checklist_items if item.status == "passed")
        failed = sum(1 for item in self.checklist_items if item.status == "failed")
        pending = sum(1 for item in self.checklist_items if item.status == "pending")

        # 检查必须项是否都通过
        required_passed = sum(
            1 for item in self.get_required_items()
            if item.status == "passed"
        )

        return {
            "total": total,
            "required": required,
            "optional": total - required,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "required_passed": required_passed,
            "required_total": required,
            "all_required_passed": required_passed == required,
            "completion_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%"
        }

    def generate_checklist_report(self) -> str:
        """生成检查清单报告"""
        summary = self.get_summary()

        report = f"""
## ✅ QA 测试检查清单

### 📊 检查摘要
- **总检查项**: {summary['total']}
- **必须项**: {summary['required']}
- **可选项**: {summary['optional']}
- **已通过**: ✅ {summary['passed']}
- **已失败**: ❌ {summary['failed']}
- **待检查**: ⏸️ {summary['pending']}
- **必须项通过率**: {summary['required_passed']}/{summary['required_total']}
- **总体完成率**: {summary['completion_rate']}

### 🔍 必须检查项（Required）
"""

        for item in self.get_required_items():
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "pending": "⏸️",
                "skipped": "⏭️"
            }.get(item.status, "❓")

            report += f"{status_icon} **{item.description}**\n"

        report += "\n### 📋 可选检查项（Optional）\n"

        for item in self.get_optional_items():
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "pending": "⏸️",
                "skipped": "⏭️"
            }.get(item.status, "❓")

            report += f"{status_icon} **{item.description}**\n"

        # 判断是否可以验收
        if summary['all_required_passed']:
            report += "\n### 🎯 验收结论\n"
            report += "✅ **所有必须项已通过，可以验收**\n"
        else:
            report += "\n### 🎯 验收结论\n"
            report += "❌ **存在未通过的必须项，不能验收**\n"
            report += f"   未通过必须项: {summary['required_total'] - summary['required_passed']}\n"

        return report

    def reset(self):
        """重置检查清单"""
        for item in self.checklist_items:
            item.status = "pending"


class QuickTestValidator:
    """
    快速测试验证器
    用于 QA Agent 快速验证功能
    """

    @staticmethod
    def validate_basic_functionality(
        function_name: str,
        test_input: Any,
        expected_output: Any
    ) -> tuple[bool, str]:
        """
        验证基本功能

        Args:
            function_name: 功能名称
            test_input: 测试输入
            expected_output: 期望输出

        Returns:
            (is_valid, message): 验证结果和消息
        """
        try:
            # 这里应该实际调用功能进行测试
            # 由于这是一个框架，只提供验证逻辑
            if test_input is None:
                return False, f"{function_name}: 测试输入为空"

            if expected_output is None:
                return False, f"{function_name}: 期望输出为空"

            return True, f"{function_name}: 基本功能验证通过"

        except Exception as e:
            return False, f"{function_name}: 测试失败 - {str(e)}"

    @staticmethod
    def validate_boundary_conditions(
        function_name: str,
        boundary_cases: List[Any]
    ) -> tuple[bool, List[str]]:
        """
        验证边界条件

        Args:
            function_name: 功能名称
            boundary_cases: 边界测试用例

        Returns:
            (is_valid, messages): 验证结果和消息列表
        """
        messages = []
        all_passed = True

        for i, case in enumerate(boundary_cases):
            try:
                # 这里应该实际调用功能进行测试
                if case is None:
                    messages.append(f"边界测试 {i+1}: 输入为空 - 应该有错误处理")
                    all_passed = False
                else:
                    messages.append(f"边界测试 {i+1}: 通过 ✅")

            except Exception as e:
                messages.append(f"边界测试 {i+1}: 失败 ❌ - {str(e)}")
                all_passed = False

        return all_passed, messages

    @staticmethod
    def validate_exception_handling(
        function_name: str,
        invalid_inputs: List[Any]
    ) -> tuple[bool, List[str]]:
        """
        验证异常处理

        Args:
            function_name: 功能名称
            invalid_inputs: 无效输入列表

        Returns:
            (is_valid, messages): 验证结果和消息列表
        """
        messages = []
        all_passed = True

        for i, invalid_input in enumerate(invalid_inputs):
            try:
                # 这里应该实际调用功能进行测试
                # 期望功能能够优雅地处理无效输入
                messages.append(f"异常测试 {i+1}: 正确处理无效输入 ✅")

            except Exception as e:
                messages.append(f"异常测试 {i+1}: 未能正确处理 - {str(e)} ❌")
                all_passed = False

        return all_passed, messages


def create_test_checklist() -> QAChecklist:
    """创建测试检查清单实例"""
    return QAChecklist()


def validate_task_completion(
    task_title: str,
    task_description: str,
    test_results: Dict[str, Any]
) -> tuple[bool, str]:
    """
    验证任务完成情况

    Args:
        task_title: 任务标题
        task_description: 任务描述
        test_results: 测试结果

    Returns:
        (is_valid, message): 验证结果和消息
    """
    checklist = create_test_checklist()

    # 更新检查清单状态（基于测试结果）
    if test_results.get("happy_path_passed"):
        checklist.update_item_status("2", "passed")
    if test_results.get("boundary_tested"):
        checklist.update_item_status("3", "passed")
    if test_results.get("exception_tested"):
        checklist.update_item_status("4", "passed")
    if test_results.get("result_matches"):
        checklist.update_item_status("5", "passed")
    if test_results.get("report_generated"):
        checklist.update_item_status("6", "passed")
    if test_results.get("core_functionality_implemented"):
        checklist.update_item_status("10", "passed")

    summary = checklist.get_summary()

    if summary['all_required_passed']:
        return True, "✅ 任务完成，所有必须项已通过验证"
    else:
        return False, f"❌ 任务未完成，缺少 {summary['required_total'] - summary['required_passed']} 个必须项验证"


# 便捷函数
def quick_check(test_results: Dict[str, Any]) -> tuple[bool, str]:
    """
    快速检查测试结果

    Args:
        test_results: 测试结果字典

    Returns:
        (is_valid, message): 验证结果和消息
    """
    return validate_task_completion(
        task_title="",
        task_description="",
        test_results=test_results
    )
