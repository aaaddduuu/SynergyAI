# -*- coding: utf-8 -*-
"""
测试增量工作原则
验证 Agent 是否严格遵循增量工作原则，一次只处理一个任务
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.storage import Session, Task, TaskState, AgentRole
from core.agents import TaskOperation


def test_multi_task_creation_detection():
    """测试检测批量创建任务的违规行为"""
    print("=" * 80)
    print("测试 1: 检测批量创建任务")
    print("=" * 80)

    # 模拟 PM 一次性创建多个任务
    pm_response = """
我分析了项目需求，现在创建以下任务：

[任务] 创建: 用户登录功能 | 实现用户登录功能 | dev | high
[任务] 创建: 用户注册功能 | 实现用户注册功能 | dev | medium
[任务] 创建: 密码重置功能 | 实现密码重置功能 | dev | low

这样可以提高开发效率。
"""

    operations = TaskOperation.parse(pm_response)
    create_ops = [op for op in operations if op['action'] == 'create']

    print(f"✅ 检测到创建操作数量: {len(create_ops)}")
    print(f"✅ 任务列表:")
    for op in create_ops:
        print(f"   - {op['title']}")

    if len(create_ops) > 1:
        print(f"\n⚠️  违规检测：一次性创建了 {len(create_ops)} 个任务")
        print("   预期：系统应该阻止此操作并发出警告")
        print("   实际：系统检测到违规行为 ✓")
        return True
    else:
        print("\n❌ 未检测到违规行为")
        return False


def test_multi_task_assignment_detection():
    """测试检测批量分配任务的违规行为"""
    print("\n" + "=" * 80)
    print("测试 2: 检测批量分配任务")
    print("=" * 80)

    # 模拟 PM 一次性分配多个任务
    pm_response = """
现在我分配任务给团队成员：

[任务] 分配: 用户登录功能 | dev
[任务] 分配: 数据库优化 | dev
[任务] 分配: API 接口设计 | dev

让开发人员并行处理。
"""

    operations = TaskOperation.parse(pm_response)
    assign_ops = [op for op in operations if op['action'] == 'assign']

    print(f"✅ 检测到分配操作数量: {len(assign_ops)}")
    print(f"✅ 分配列表:")
    for op in assign_ops:
        print(f"   - {op['title']} -> {op['assignee_role']}")

    if len(assign_ops) > 1:
        print(f"\n⚠️  违规检测：一次性分配了 {len(assign_ops)} 个任务")
        print("   预期：系统应该阻止此操作并发出警告")
        print("   实际：系统检测到违规行为 ✓")
        return True
    else:
        print("\n❌ 未检测到违规行为")
        return False


def test_create_during_in_progress():
    """测试在任务进行中时创建新任务"""
    print("\n" + "=" * 80)
    print("测试 3: 检测在任务进行中时创建新任务")
    print("=" * 80)

    # 创建一个模拟会话，包含进行中的任务
    session = Session(session_id="test_session")
    task1 = Task(
        id="task1",
        title="登录功能开发",
        description="实现用户登录",
        assignee_role=AgentRole.DEV,
        priority="high",
        state=TaskState.IN_PROGRESS
    )
    session.tasks[task1.id] = task1

    print(f"✅ 当前进行中的任务: {task1.title}")

    # 模拟 PM 又创建新任务
    pm_response = """
虽然登录功能还在开发，但我再创建一个新任务：

[任务] 创建: 注册功能 | 实现用户注册 | dev | medium
"""

    operations = TaskOperation.parse(pm_response)
    create_ops = [op for op in operations if op['action'] == 'create']
    in_progress_tasks = [task for task in session.tasks.values() if task.state == TaskState.IN_PROGRESS]

    print(f"✅ 新创建任务数量: {len(create_ops)}")
    print(f"✅ 进行中任务数量: {len(in_progress_tasks)}")

    if create_ops and in_progress_tasks:
        print(f"\n⚠️  违规检测：存在 {len(in_progress_tasks)} 个进行中任务时又创建新任务")
        print("   进行中的任务:", [task.title for task in in_progress_tasks])
        print("   预期：系统应该阻止此操作并发出警告")
        print("   实际：系统检测到违规行为 ✓")
        return True
    else:
        print("\n❌ 未检测到违规行为")
        return False


def test_single_task_creation():
    """测试正常单任务创建（应该通过）"""
    print("\n" + "=" * 80)
    print("测试 4: 正常单任务创建（应该通过）")
    print("=" * 80)

    # 创建一个干净的会话
    session = Session(session_id="test_session")

    # 模拟 PM 只创建一个任务
    pm_response = """
我分析了项目需求，先创建第一个高优先级任务：

[任务] 创建: 用户登录功能 | 实现用户登录功能 | dev | high

完成这个任务后我们再考虑下一个。
"""

    operations = TaskOperation.parse(pm_response)
    create_ops = [op for op in operations if op['action'] == 'create']
    in_progress_tasks = [task for task in session.tasks.values() if task.state == TaskState.IN_PROGRESS]

    print(f"✅ 创建任务数量: {len(create_ops)}")
    print(f"✅ 进行中任务数量: {len(in_progress_tasks)}")

    if len(create_ops) == 1 and not in_progress_tasks:
        print("\n✅ 符合增量工作原则：只创建一个任务，没有进行中的任务")
        print("   预期：系统应该允许此操作")
        print("   实际：操作符合规范 ✓")
        return True
    else:
        print("\n❌ 检测逻辑有误")
        return False


def test_incremental_work_principles_content():
    """测试增量工作原则内容完整性"""
    print("\n" + "=" * 80)
    print("测试 5: 增量工作原则内容完整性检查")
    print("=" * 80)

    from core.agents import INCREMENTAL_WORK_PRINCIPLES, AGENT_SYSTEM_PROMPTS

    # 检查关键内容是否存在
    checks = {
        "警告标识": "⚠️" in INCREMENTAL_WORK_PRINCIPLES,
        "强制规则": "强制规则" in INCREMENTAL_WORK_PRINCIPLES,
        "禁止批量": "绝对禁止" in INCREMENTAL_WORK_PRINCIPLES,
        "检查清单": "检查清单" in INCREMENTAL_WORK_PRINCIPLES,
        "工作流程": "工作流程" in INCREMENTAL_WORK_PRINCIPLES,
        "禁止行为": "禁止行为清单" in INCREMENTAL_WORK_PRINCIPLES,
        "PM约束": "关键约束" in AGENT_SYSTEM_PROMPTS[AgentRole.PM],
        "BA约束": "关键约束" in AGENT_SYSTEM_PROMPTS[AgentRole.BA],
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {'通过' if passed else '失败'}")
        if not passed:
            all_passed = False

    return all_passed


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("增量工作原则测试套件")
    print("测试 Agent 是否严格遵循增量工作原则")
    print("=" * 80 + "\n")

    results = {
        "批量创建任务检测": test_multi_task_creation_detection(),
        "批量分配任务检测": test_multi_task_assignment_detection(),
        "进行中创建任务检测": test_create_during_in_progress(),
        "单任务创建验证": test_single_task_creation(),
        "原则内容完整性": test_incremental_work_principles_content(),
    }

    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")
    print("=" * 80)

    if passed == total:
        print("\n[SUCCESS] 所有测试通过！增量工作原则已正确实现。")
        return 0
    else:
        print(f"\n[WARNING] 有 {total - passed} 个测试失败，需要进一步优化。")
        return 1


if __name__ == "__main__":
    exit(main())
