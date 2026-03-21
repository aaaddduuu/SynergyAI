"""
轻量级测试验证框架
参考 Anthropic 文章中的端到端测试理念
"""

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import json


class TestStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    description: str
    steps: List[str]  # 测试步骤
    expected_result: str  # 期望结果
    status: TestStatus = TestStatus.PENDING
    actual_result: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "expected_result": self.expected_result,
            "status": self.status.value,
            "actual_result": self.actual_result,
            "notes": self.notes
        }


@dataclass
class TestSuite:
    """测试套件"""
    name: str
    description: str
    test_cases: List[TestCase] = None

    def __post_init__(self):
        if self.test_cases is None:
            self.test_cases = []

    def add_test(self, test: TestCase):
        """添加测试用例"""
        self.test_cases.append(test)

    def get_summary(self) -> dict:
        """获取测试摘要"""
        total = len(self.test_cases)
        passed = sum(1 for t in self.test_cases if t.status == TestStatus.PASSED)
        failed = sum(1 for t in self.test_cases if t.status == TestStatus.FAILED)
        pending = sum(1 for t in self.test_cases if t.status == TestStatus.PENDING)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%"
        }


class BasicValidator:
    """
    基础验证器
    提供常用的验证方法
    """

    @staticmethod
    def validate_not_empty(value: Any, field_name: str = "值") -> tuple[bool, str]:
        """验证非空"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{field_name} 不能为空"
        return True, "验证通过"

    @staticmethod
    def validate_length(value: str, min_len: int = 0, max_len: int = 1000, field_name: str = "值") -> tuple[bool, str]:
        """验证长度"""
        if len(value) < min_len:
            return False, f"{field_name} 长度不能少于 {min_len} 字符"
        if len(value) > max_len:
            return False, f"{field_name} 长度不能超过 {max_len} 字符"
        return True, "验证通过"

    @staticmethod
    def validate_format(value: str, pattern: str, field_name: str = "值") -> tuple[bool, str]:
        """验证格式（简单版）"""
        import re
        if not re.match(pattern, value):
            return False, f"{field_name} 格式不正确"
        return True, "验证通过"

    @staticmethod
    def validate_in_range(value: int, min_val: int, max_val: int, field_name: str = "值") -> tuple[bool, str]:
        """验证数值范围"""
        if not (min_val <= value <= max_val):
            return False, f"{field_name} 必须在 {min_val} 到 {max_val} 之间"
        return True, "验证通过"

    @staticmethod
    def validate_contains(text: str, keyword: str, field_name: str = "文本") -> tuple[bool, str]:
        """验证包含关键词"""
        if keyword.lower() not in text.lower():
            return False, f"{field_name} 不包含关键词 '{keyword}'"
        return True, "验证通过"


class TaskValidator:
    """
    任务验证器
    用于验证任务完成情况
    """

    def __init__(self):
        self.validator = BasicValidator()

    def validate_task_completion(self, task_info: dict) -> tuple[bool, List[str]]:
        """
        验证任务是否真正完成

        Args:
            task_info: 任务信息，包含 title, description, status 等

        Returns:
            (is_valid, issues): 是否完成，问题列表
        """
        issues = []

        # 1. 检查基本信息
        if "title" not in task_info or not task_info["title"]:
            issues.append("缺少任务标题")

        if "description" not in task_info or not task_info["description"]:
            issues.append("缺少任务描述")

        # 2. 检查状态
        status = task_info.get("state", "")
        if status not in ["done", "review"]:
            issues.append(f"任务状态 '{status}' 不是完成状态 (done/review)")

        # 3. 检查是否有实现（如果有代码相关内容）
        if "code" in task_info:
            code = task_info["code"]
            if not code or len(code) < 10:
                issues.append("代码实现不完整或缺失")

        # 4. 检查是否有测试记录
        if "test_result" not in task_info:
            issues.append("缺少测试结果记录")

        is_valid = len(issues) == 0
        return is_valid, issues

    def create_test_cases_for_task(self, task_title: str, task_description: str) -> TestSuite:
        """
        为任务创建基础测试用例

        这是一个模板方法，QA Agent 可以参考
        """
        suite = TestSuite(
            name=f"{task_title} - 测试套件",
            description=f"验证任务: {task_description}"
        )

        # 基础测试用例
        suite.add_test(TestCase(
            id="1",
            name="功能完整性检查",
            description="验证任务要求的所有功能都已实现",
            steps=[
                "1. 查看任务描述",
                "2. 检查每个需求点是否有对应实现",
                "3. 确认没有遗漏的功能"
            ],
            expected_result="所有需求点都有对应实现"
        ))

        suite.add_test(TestCase(
            id="2",
            name="基本功能测试",
            description="测试核心功能是否能正常工作",
            steps=[
                "1. 执行核心功能",
                "2. 验证输出是否符合预期",
                "3. 检查是否有错误"
            ],
            expected_result="功能正常运行，无错误"
        ))

        suite.add_test(TestCase(
            id="3",
            name="边界条件测试",
            description="测试边界情况和异常处理",
            steps=[
                "1. 测试空值/无效输入",
                "2. 测试极端值",
                "3. 验证错误提示是否友好"
            ],
            expected_result="正确处理边界情况，有友好的错误提示"
        ))

        return suite


def create_test_report(test_suite: TestSuite, task_info: dict = None) -> str:
    """
    生成增强的测试报告

    Args:
        test_suite: 测试套件
        task_info: 任务信息（可选）

    Returns:
        格式化的测试报告（Markdown）
    """
    summary = test_suite.get_summary()
    from datetime import datetime

    report = f"""
# 🧪 测试报告：{test_suite.name}

## 📋 测试概况
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试人**: QA Agent
- **测试范围**: {test_suite.description}
"""

    if task_info:
        report += f"""
- **任务标题**: {task_info.get('title', 'N/A')}
- **任务ID**: {task_info.get('id', 'N/A')}
- **负责人**: {task_info.get('assignee_role', 'N/A')}
"""

    report += f"""

## 📊 测试摘要
- **总测试数**: {summary['total']}
- **通过**: ✅ {summary['passed']}
- **失败**: ❌ {summary['failed']}
- **待测试**: ⏸️ {summary['pending']}
- **通过率**: {summary['pass_rate']}

## 📝 测试详情

"""

    for test in test_suite.test_cases:
        status_icon = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌",
            TestStatus.PENDING: "⏸️",
            TestStatus.SKIPPED: "⏭️"
        }.get(test.status, "❓")

        report += f"""
### {status_icon} 测试 {test.id}: {test.name}

**描述**: {test.description}

**测试步骤**:
"""
        for step in test.steps:
            report += f"- {step}\n"

        report += f"""
**期望结果**: {test.expected_result}

**状态**: {test.status.value}
"""

        if test.actual_result:
            report += f"**实际结果**: {test.actual_result}\n"

        if test.notes:
            report += f"**备注**: {test.notes}\n"

        report += "---\n"

    # 添加测试总结和结论
    report += f"""

## 🎯 测试总结

### 通过率分析
"""
    if summary['total'] > 0:
        pass_rate = float(summary['pass_rate'].replace('%', ''))
        if pass_rate >= 90:
            report += "✅ **优秀**: 通过率 ≥ 90%\n"
        elif pass_rate >= 70:
            report += "⚠️ **良好**: 通过率 ≥ 70%\n"
        elif pass_rate >= 50:
            report += "⚠️ **一般**: 通过率 ≥ 50%\n"
        else:
            report += "❌ **不合格**: 通过率 < 50%\n"

    report += f"""
### 失败用例分析
- **失败数量**: {summary['failed']}
- **待测试数量**: {summary['pending']}
"""

    if summary['failed'] > 0:
        failed_tests = [t for t in test_suite.test_cases if t.status == TestStatus.FAILED]
        report += "\n**失败用例详情**:\n"
        for test in failed_tests:
            report += f"- 测试 {test.id}: {test.name}\n"
            if test.notes:
                report += f"  问题: {test.notes}\n"

    report += f"""

## 📌 最终结论

"""

    # 判断测试是否通过
    all_critical_passed = all(
        t.status == TestStatus.PASSED for t in test_suite.test_cases
        if 'critical' in t.name.lower() or '核心' in t.name or '关键' in t.name
    ) if summary['total'] > 0 else True

    if summary['failed'] == 0 and summary['pending'] == 0:
        report += """**✅ 测试通过**

所有测试用例均已通过，功能符合预期。

"""
    elif summary['failed'] == 0 and all_critical_passed:
        report += """**✅ 测试基本通过**

核心功能测试通过，仍有部分测试待完成。

"""
    else:
        report += """**❌ 测试未通过**

存在失败的测试用例，需要修复后重新测试。

"""

    # 添加改进建议
    if summary['failed'] > 0:
        report += """
## 💡 改进建议

1. 优先修复失败的测试用例
2. 确保核心功能正常工作
3. 完善错误处理机制
4. 补充边界条件测试
"""

    return report


# 导出便捷函数
def quick_validate(value: Any, validation_type: str, **kwargs) -> tuple[bool, str]:
    """
    快速验证函数

    Args:
        value: 要验证的值
        validation_type: 验证类型 (not_empty, length, format, contains, range)
        **kwargs: 额外参数

    Returns:
        (is_valid, message): 验证结果和消息
    """
    validator = BasicValidator()

    if validation_type == "not_empty":
        return validator.validate_not_empty(value, kwargs.get("field_name", "值"))
    elif validation_type == "length":
        return validator.validate_length(
            value,
            kwargs.get("min_len", 0),
            kwargs.get("max_len", 1000),
            kwargs.get("field_name", "值")
        )
    elif validation_type == "format":
        return validator.validate_format(value, kwargs.get("pattern"), kwargs.get("field_name", "值"))
    elif validation_type == "contains":
        return validator.validate_contains(value, kwargs.get("keyword"), kwargs.get("field_name", "文本"))
    elif validation_type == "range":
        return validator.validate_in_range(
            value,
            kwargs.get("min_val"),
            kwargs.get("max_val"),
            kwargs.get("field_name", "值")
        )
    else:
        return False, f"未知的验证类型: {validation_type}"
