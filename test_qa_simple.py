# -*- coding: utf-8 -*-
"""
测试 QA Agent 验证功能 - 简化版
避免 Windows 编码问题
"""

from core.testing import TestSuite, TestCase, TestStatus, create_test_report
from core.qa_checklist import QAChecklist, validate_task_completion


def run_test():
    """运行测试"""
    print("=" * 60)
    print("QA Agent Validation Test")
    print("=" * 60)

    # Test 1: Create test suite
    print("\n[Test 1] Creating test suite...")
    suite = TestSuite(
        name="Login Feature Test",
        description="Verify user login functionality"
    )

    suite.add_test(TestCase(
        id="1",
        name="Normal Login",
        description="Test normal login flow",
        steps=["Open login page", "Enter credentials", "Click login"],
        expected_result="Login successful",
        status=TestStatus.PASSED,
        actual_result="Login successful",
        notes="Test passed"
    ))

    suite.add_test(TestCase(
        id="2",
        name="Empty Username",
        description="Test empty username",
        steps=["Enter empty username", "Enter password", "Click login"],
        expected_result="Show error: Username required",
        status=TestStatus.PASSED,
        actual_result="Show error: Username required",
        notes="Correctly handled"
    ))

    suite.add_test(TestCase(
        id="3",
        name="Wrong Password",
        description="Test wrong password",
        steps=["Enter correct username", "Enter wrong password", "Click login"],
        expected_result="Show error: Wrong password",
        status=TestStatus.FAILED,
        actual_result="No error shown, redirected",
        notes="Issue: Should show error for wrong password"
    ))

    summary = suite.get_summary()
    print(f"Total tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass rate: {summary['pass_rate']}")
    print("[PASS] Test 1 completed")

    # Test 2: QA Checklist
    print("\n[Test 2] Testing QA checklist...")
    checklist = QAChecklist()
    checklist.update_item_status("1", "passed")
    checklist.update_item_status("2", "passed")
    checklist.update_item_status("3", "passed")
    checklist.update_item_status("4", "passed")
    checklist.update_item_status("5", "passed")
    checklist.update_item_status("6", "passed")
    checklist.update_item_status("10", "passed")

    summary_check = checklist.get_summary()
    print(f"Required items passed: {summary_check['required_passed']}/{summary_check['required_total']}")
    print(f"All required passed: {summary_check['all_required_passed']}")
    print("[PASS] Test 2 completed")

    # Test 3: Validate task completion
    print("\n[Test 3] Testing task completion validation...")
    test_results = {
        "happy_path_passed": True,
        "boundary_tested": True,
        "exception_tested": True,
        "result_matches": True,
        "report_generated": True,
        "core_functionality_implemented": True
    }

    is_valid, message = validate_task_completion(
        task_title="User Login Feature",
        task_description="Implement login, validation and error handling",
        test_results=test_results
    )

    print(f"Validation result: {message}")
    print(f"Is valid: {is_valid}")
    assert is_valid == True, "Expected validation to pass"
    print("[PASS] Test 3 completed")

    # Test 4: Test report generation
    print("\n[Test 4] Testing report generation...")
    report = create_test_report(
        suite,
        task_info={
            "id": "feat-001",
            "title": "User Login Feature",
            "assignee_role": "dev"
        }
    )

    # Check report contains key sections
    assert "Test Time" in report or "test_time" in report.lower()
    assert "Test Summary" in report or "test_summary" in report.lower()
    assert "Final Conclusion" in report or "conclusion" in report.lower()
    print("[PASS] Test 4 completed")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

    print("\nFeatures verified:")
    print("1. [OK] Test suite creation and management")
    print("2. [OK] QA checklist validation")
    print("3. [OK] Task completion validation")
    print("4. [OK] Enhanced test report generation")

    print("\nKey improvements:")
    print("- Emphasize end-to-end testing (not just code review)")
    print("- Detailed test report template")
    print("- Include normal, boundary, and exception tests")
    print("- Auto-generate test conclusions and recommendations")

    return True


if __name__ == "__main__":
    try:
        success = run_test()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
