"""
测试功能清单系统集成

验证 feat-019 的所有要求：
1. 创建 Feature 数据模型
2. 实现 Feature 管理类
3. 在初始化时创建功能清单
4. Agent 可以读取和更新功能清单
5. 自动选择下一个待办功能
6. 生成进度报告
"""

import sys
import os
from pathlib import Path

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.features import FeatureList, Feature, FeatureStatus, FeaturePriority
from core.agents import TaskOperation


def test_feature_data_model():
    """测试 1: Feature 数据模型"""
    print("\n=== 测试 1: Feature 数据模型 ===")

    feature = Feature(
        id="test-001",
        category="feature",
        priority="high",
        title="测试功能",
        description="这是一个测试功能",
        status="pending",
        assignee_role="dev",
        steps=["步骤1", "步骤2"],
        passes=False,
        notes="测试备注"
    )

    print(f"[OK] 创建功能对象: {feature.title}")
    print(f"   - ID: {feature.id}")
    print(f"   - 状态: {feature.status}")

    # 测试状态更新方法
    feature.mark_in_progress()
    assert feature.status == "in_progress"
    print(f"[OK] 标记为进行中: {feature.status}")

    feature.mark_done()
    assert feature.status == "done"
    assert feature.passes == True
    print(f"[OK] 标记为完成: {feature.status}, passes={feature.passes}")

    # 测试字典转换
    feature_dict = feature.to_dict()
    assert "id" in feature_dict
    assert "title" in feature_dict
    print(f"[OK] 转换为字典成功")

    return True


def test_feature_management():
    """测试 2: Feature 管理类"""
    print("\n=== 测试 2: Feature 管理类 ===")

    feature_list = FeatureList()

    # 检查是否加载了现有功能
    print(f"[OK] 加载功能清单: {len(feature_list.features)} 个功能")

    # 测试获取统计信息
    stats = feature_list.get_statistics()
    print(f"[OK] 获取统计信息:")
    print(f"   - 总数: {stats['total']}")
    print(f"   - 按状态: {stats['by_status']}")
    print(f"   - 按优先级: {stats['by_priority']}")

    # 测试获取下一个待办功能
    next_feature = feature_list.get_next_feature("dev")
    if next_feature:
        print(f"[OK] 获取下一个待办功能 (dev): {next_feature.title}")
    else:
        print(f"[INFO] 没有 dev 角色的待办功能")

    # 测试获取待办功能列表
    pending = feature_list.get_pending_features(limit=5)
    print(f"[OK] 获取待办功能列表: {len(pending)} 个")

    # 测试更新功能状态
    if pending:
        test_feature = pending[0]
        old_status = test_feature.status
        feature_list.update_feature_status(test_feature.id, "in_progress")
        print(f"[OK] 更新功能状态: {test_feature.id} ({old_status} -> in_progress)")
        # 恢复原状态
        feature_list.update_feature_status(test_feature.id, old_status)

    return True


def test_agent_feature_operations():
    """测试 3: Agent 功能操作解析"""
    print("\n=== 测试 3: Agent 功能操作解析 ===")

    # 测试功能状态更新指令解析
    test_text = """
    我已经完成了 feat-019 的开发工作。
    [功能] 状态: feat-019 | done
    """

    operations = TaskOperation.parse(test_text)
    feature_ops = [op for op in operations if op['action'] == 'update_feature_state']

    assert len(feature_ops) == 1
    assert feature_ops[0]['feature_id'] == 'feat-019'
    assert feature_ops[0]['state'] == 'done'

    print(f"[OK] 解析功能状态更新指令: {feature_ops[0]}")

    # 测试是否包含功能操作
    has_feature_op = TaskOperation.has_operation(test_text)
    assert has_feature_op == True
    print(f"[OK] 检测到功能操作: {has_feature_op}")

    return True


def test_progress_report():
    """测试 4: 进度报告生成"""
    print("\n=== 测试 4: 进度报告生成 ===")

    feature_list = FeatureList()

    # 测试进度摘要
    summary = feature_list.get_progress_summary()
    assert "功能清单进度摘要" in summary
    print(f"[OK] 生成进度摘要 (长度: {len(summary)} 字符)")

    # 测试完整报告
    report = feature_list.generate_report()
    assert "SynergyAI 功能清单报告" in report
    print(f"[OK] 生成完整报告 (长度: {len(report)} 字符)")

    return True


def test_initialization():
    """测试 5: 初始化时创建功能清单"""
    print("\n=== 测试 5: 初始化时创建功能清单 ===")

    feature_list = FeatureList()

    # 检查是否从 feature_list.json 加载
    assert feature_list.feature_file.exists()
    print(f"[OK] 功能清单文件存在: {feature_list.feature_file}")

    # 检查功能是否加载
    assert len(feature_list.features) > 0
    print(f"[OK] 功能已加载: {len(feature_list.features)} 个")

    # 检查关键功能是否存在
    assert "feat-019" in feature_list.features
    print(f"[OK] 找到 feat-019: {feature_list.features['feat-019'].title}")

    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("功能清单系统集成测试")
    print("=" * 60)

    tests = [
        ("Feature 数据模型", test_feature_data_model),
        ("Feature 管理类", test_feature_management),
        ("Agent 功能操作解析", test_agent_feature_operations),
        ("进度报告生成", test_progress_report),
        ("初始化功能清单", test_initialization),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n[PASS] {name} - 通过")
            else:
                failed += 1
                print(f"\n[FAIL] {name} - 失败")
        except Exception as e:
            failed += 1
            print(f"\n[FAIL] {name} - 错误: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    if failed == 0:
        print("\n[SUCCESS] 所有测试通过！feat-019 已成功实现！")
        return 0
    else:
        print(f"\n[WARNING] 有 {failed} 个测试失败，请检查")
        return 1


if __name__ == "__main__":
    exit(main())
