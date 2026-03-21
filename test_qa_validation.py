"""
测试 QA Agent 验证功能
验证新增的端到端测试能力
"""

from core.testing import TestSuite, TestCase, TestStatus, create_test_report
from core.qa_checklist import QAChecklist, validate_task_completion, quick_check


def test_basic_test_suite():
    """测试基础测试套件功能"""
    print("=== 测试 1: 基础测试套件 ===")

    suite = TestSuite(
        name="登录功能测试",
        description="验证用户登录功能"
    )

    # 添加测试用例
    suite.add_test(TestCase(
        id="1",
        name="正常登录测试",
        description="使用有效凭证登录",
        steps=["打开登录页面", "输入用户名密码", "点击登录"],
        expected_result="成功登录，跳转到首页",
        status=TestStatus.PASSED,
        actual_result="成功登录，跳转到首页",
        notes="测试通过"
    ))

    suite.add_test(TestCase(
        id="2",
        name="空用户名测试",
        description="测试空用户名场景",
        steps=["输入空用户名", "输入密码", "点击登录"],
        expected_result="显示错误提示：用户名不能为空",
        status=TestStatus.PASSED,
        actual_result="显示错误提示：用户名不能为空",
        notes="正确处理空值"
    ))

    suite.add_test(TestCase(
        id="3",
        name="错误密码测试",
        description="测试错误密码场景",
        steps=["输入正确用户名", "输入错误密码", "点击登录"],
        expected_result="显示错误提示：密码错误",
        status=TestStatus.FAILED,
        actual_result="未显示错误提示，直接跳转",
        notes="问题：错误密码应该显示提示"
    ))

    # 生成报告
    report = create_test_report(
        suite,
        task_info={
            "id": "feat-001",
            "title": "用户登录功能",
            "assignee_role": "dev"
        }
    )

    print(report)
    print("\n[PASS] 测试 1 通过\n")


def test_qa_checklist():
    """测试 QA 检查清单功能"""
    print("=== 测试 2: QA 检查清单 ===")

    checklist = QAChecklist()

    # 模拟测试结果
    test_results = {
        "happy_path_passed": True,
        "boundary_tested": True,
        "exception_tested": True,
        "result_matches": True,
        "report_generated": True,
        "core_functionality_implemented": True
    }

    # 验证任务完成情况
    is_valid, message = validate_task_completion(
        task_title="用户登录功能",
        task_description="实现用户登录、验证和错误处理",
        test_results=test_results
    )

    print(f"验证结果: {message}")

    # 生成检查清单报告
    checklist.update_item_status("1", "passed")
    checklist.update_item_status("2", "passed")
    checklist.update_item_status("3", "passed")
    checklist.update_item_status("4", "passed")
    checklist.update_item_status("5", "passed")
    checklist.update_item_status("6", "passed")
    checklist.update_item_status("10", "passed")

    checklist_report = checklist.generate_checklist_report()
    print(checklist_report)

    print("\n[PASS] 测试 2 通过\n")


def test_quick_check():
    """测试快速检查功能"""
    print("=== 测试 3: 快速检查 ===")

    # 场景1：所有测试通过
    test_results_pass = {
        "happy_path_passed": True,
        "boundary_tested": True,
        "exception_tested": True,
        "result_matches": True,
        "report_generated": True,
        "core_functionality_implemented": True
    }

    is_valid, message = quick_check(test_results_pass)
    print(f"场景1 - 所有测试通过: {message}")
    assert is_valid == True

    # 场景2：部分测试失败
    test_results_fail = {
        "happy_path_passed": False,
        "boundary_tested": True,
        "exception_tested": True,
        "result_matches": False,
        "report_generated": True,
        "core_functionality_implemented": True
    }

    is_valid, message = quick_check(test_results_fail)
    print(f"场景2 - 部分测试失败: {message}")
    assert is_valid == False

    print("\n[PASS] 测试 3 通过\n")


def test_enhanced_test_report():
    """测试增强的测试报告"""
    print("=== 测试 4: 增强测试报告 ===")

    suite = TestSuite(
        name="配置加载功能测试",
        description="验证配置加载的稳定性和默认值处理"
    )

    # 正常场景
    suite.add_test(TestCase(
        id="1",
        name="正常加载配置",
        description="测试正常加载配置文件",
        steps=["启动应用", "调用 /api/config", "检查响应"],
        expected_result="返回完整的配置信息",
        status=TestStatus.PASSED,
        actual_result="返回完整的配置信息",
    ))

    # 边界条件
    suite.add_test(TestCase(
        id="2",
        name="配置文件缺失",
        description="测试配置文件不存在时的处理",
        steps=["删除配置文件", "启动应用", "调用 /api/config"],
        expected_result="使用默认值，不报错",
        status=TestStatus.PASSED,
        actual_result="使用默认值，has_api_key=false",
    ))

    # 异常处理
    suite.add_test(TestCase(
        id="3",
        name="配置格式错误",
        description="测试配置格式错误时的处理",
        steps=["创建格式错误的配置文件", "启动应用"],
        expected_result="显示友好错误提示，使用默认值",
        status=TestStatus.FAILED,
        actual_result="应用崩溃，未处理错误",
        notes="严重问题：需要添加 try-catch 处理"
    ))

    # 核心功能
    suite.add_test(TestCase(
        id="4",
        name="核心功能-API Key 加载",
        description="验证 API Key 能正确加载",
        steps=["设置有效的 API Key", "重启应用", "验证配置加载"],
        expected_result="has_api_key=true，配置正确加载",
        status=TestStatus.PASSED,
        actual_result="has_api_key=true",
    ))

    report = create_test_report(
        suite,
        task_info={
            "id": "feat-001",
            "title": "修复配置加载 Bug",
            "assignee_role": "dev"
        }
    )

    print(report)

    # 验证报告包含必要信息
    assert "测试时间" in report
    assert "测试人" in report
    assert "通过率" in report
    assert "最终结论" in report
    assert "改进建议" in report

    print("\n✅ 测试 4 通过\n")


def test_all_scenarios():
    """运行所有测试场景"""
    print("开始测试 QA Agent 验证功能\n")
    print("=" * 60)

    try:
        test_basic_test_suite()
        test_qa_checklist()
        test_quick_check()
        test_enhanced_test_report()

        print("=" * 60)
        print("\n所有测试通过！QA Agent 验证功能正常工作\n")

        # 输出功能摘要
        print("功能摘要:")
        print("1. [OK] 基础测试套件 - 可以创建和管理测试用例")
        print("2. [OK] QA 检查清单 - 提供端到端测试验证")
        print("3. [OK] 快速检查 - 快速验证测试结果")
        print("4. [OK] 增强报告 - 生成详细的测试报告")
        print("\n核心改进:")
        print("- 强调端到端测试（不只看代码）")
        print("- 提供详细的测试报告模板")
        print("- 包含正常、边界、异常三类测试")
        print("- 自动生成测试结论和建议")

        return True

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_all_scenarios()
    exit(0 if success else 1)
