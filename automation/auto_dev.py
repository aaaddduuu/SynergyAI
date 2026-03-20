#!/usr/bin/env python3
"""
SynergyAI 自动化开发任务领用和执行脚本

功能：
1. 从 feature_list.json 智能领取任务
2. 生成针对性的开发 prompt
3. 调用 Claude Code 执行开发
4. 更新任务状态
5. 自动提交和推送
6. 循环直到所有任务完成
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from core.features import FeatureList, FeatureStatus


class AutoDeveloper:
    """自动化开发器"""

    def __init__(self, project_dir: str = None):
        """
        初始化自动化开发器

        Args:
            project_dir: 项目根目录
        """
        if project_dir is None:
            project_dir = Path.cwd()
        self.project_dir = Path(project_dir)
        self.feature_list = FeatureList(str(self.project_dir))
        self.log_dir = self.project_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # 日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"auto_dev_{timestamp}.log"

    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def get_next_task(self):
        """获取下一个待办任务"""
        feature = self.feature_list.get_next_feature()
        if feature is None:
            self.log("没有待办任务了！")
            return None
        return feature

    def generate_prompt(self, feature) -> str:
        """
        为功能生成开发 prompt

        Args:
            feature: 功能对象

        Returns:
            开发 prompt
        """
        prompt = f"""请完成以下 SynergyAI 项目任务：

【任务ID】{feature.id}
【任务标题】{feature.title}
【任务描述】{feature.description}
【优先级】{feature.priority}
【负责人角色】{feature.assignee_role}

【任务步骤】
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(feature.steps))}

【注意事项】
{feature.notes if feature.notes else '无'}

请遵循以下开发原则：
1. 增量工作：一次只处理这一个任务，不要贪多
2. 先理解需求，再设计实现方案
3. 编写代码后必须测试验证
4. 完成后更新 feature_list.json 中此任务的状态为 "done"
5. 使用 git commit 提交代码，commit message 要清晰描述做了什么

请开始执行此任务。
"""
        return prompt

    def run_claude_code(self, prompt: str) -> bool:
        """
        调用 Claude Code 执行开发

        Args:
            prompt: 开发 prompt

        Returns:
            是否成功
        """
        self.log("=" * 80)
        self.log("调用 Claude Code 执行开发任务...")
        self.log("=" * 80)

        try:
            # 构建 Claude Code 命令
            cmd = [
                "claude",
                "--yes",
                "--no-interactive",
                "--allow-permissions",
                "--prompt", prompt,
                str(self.project_dir)
            ]

            self.log(f"命令: {' '.join(cmd)}")

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=3600  # 1小时超时
            )

            # 记录输出
            if result.stdout:
                self.log("STDOUT:")
                for line in result.stdout.split('\n'):
                    self.log(f"  {line}")

            if result.stderr:
                self.log("STDERR:")
                for line in result.stderr.split('\n'):
                    self.log(f"  {line}")

            if result.returncode == 0:
                self.log("Claude Code 执行成功")
                return True
            else:
                self.log(f"Claude Code 执行失败，返回码: {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            self.log("Claude Code 执行超时（1小时）")
            return False
        except Exception as e:
            self.log(f"调用 Claude Code 异常: {e}")
            return False

    def mark_task_in_progress(self, feature_id: str):
        """标记任务为进行中"""
        self.feature_list.update_feature_status(feature_id, FeatureStatus.IN_PROGRESS.value)
        self.log(f"任务 {feature_id} 标记为进行中")

    def mark_task_done(self, feature_id: str):
        """标记任务为完成"""
        self.feature_list.update_feature_status(feature_id, FeatureStatus.DONE.value)
        self.log(f"任务 {feature_id} 标记为完成")

    def commit_and_push(self, feature) -> bool:
        """
        提交并推送代码

        Args:
            feature: 当前功能

        Returns:
            是否成功
        """
        self.log("-" * 80)
        self.log("检查代码变更...")
        self.log("-" * 80)

        try:
            # 检查是否有变更
            result = subprocess.run(
                ["git", "diff", "--quiet"],
                cwd=self.project_dir,
                capture_output=True
            )

            if result.returncode == 0:
                self.log("没有代码变更，跳过提交")
                return True

            # 查看变更
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            self.log(f"变更文件:\n{result.stdout}")

            # 添加所有变更
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_dir,
                capture_output=True
            )
            self.log("已添加所有变更到暂存区")

            # 创建提交
            commit_msg = f"""feat: {feature.title}

任务ID: {feature.id}
描述: {feature.description}

由自动化开发脚本完成
"""
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.log("代码变更已提交")
            else:
                self.log("提交失败或没有需要提交的变更")
                return True  # 不算失败，继续

            # 推送到远程
            self.log("推送到远程仓库...")
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.log("代码已推送到远程仓库")
                return True
            else:
                self.log(f"推送失败: {result.stderr}")
                return False

        except Exception as e:
            self.log(f"提交/推送异常: {e}")
            return False

    def run_one_task(self) -> bool:
        """
        执行一个任务

        Returns:
            是否成功执行了任务
        """
        # 1. 获取下一个任务
        feature = self.get_next_task()
        if feature is None:
            return False

        self.log("\n" + "=" * 80)
        self.log(f"开始处理任务: {feature.title}")
        self.log(f"任务ID: {feature.id}")
        self.log(f"描述: {feature.description}")
        self.log("=" * 80 + "\n")

        # 2. 标记为进行中
        self.mark_task_in_progress(feature.id)

        # 3. 生成 prompt
        prompt = self.generate_prompt(feature)

        # 4. 调用 Claude Code 执行
        success = self.run_claude_code(prompt)

        # 5. 提交和推送
        if success:
            self.commit_and_push(feature)
            # 标记为完成
            self.mark_task_done(feature.id)
        else:
            self.log("任务执行失败，保持 in_progress 状态")

        # 6. 打印进度
        stats = self.feature_list.get_statistics()
        total = stats['total']
        done = stats['by_status']['done']
        progress = int(done / total * 100) if total > 0 else 0

        self.log("\n" + "=" * 80)
        self.log(f"当前进度: {done}/{total} ({progress}%)")
        self.log(f"待处理: {stats['by_status']['pending']}")
        self.log(f"进行中: {stats['by_status']['in_progress']}")
        self.log(f"已完成: {stats['by_status']['done']}")
        self.log("=" * 80 + "\n")

        return success

    def run_loop(self, max_iterations: int = None):
        """
        循环执行任务

        Args:
            max_iterations: 最大迭代次数，None 表示执行完所有任务
        """
        self.log("\n" + "🚀" * 40)
        self.log("SynergyAI 自动化开发系统启动")
        self.log(f"项目目录: {self.project_dir}")
        self.log(f"日志文件: {self.log_file}")
        self.log(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("🚀" * 40 + "\n")

        # 打印初始进度
        stats = self.feature_list.get_statistics()
        self.log(f"总任务数: {stats['total']}")
        self.log(f"待处理: {stats['by_status']['pending']}")
        self.log(f"已完成: {stats['by_status']['done']}")

        iteration = 0
        while True:
            # 检查最大迭代次数
            if max_iterations and iteration >= max_iterations:
                self.log(f"达到最大迭代次数: {max_iterations}")
                break

            # 执行一个任务
            has_task = self.run_one_task()
            if not has_task:
                self.log("所有任务已完成！")
                break

            iteration += 1

            # 等待一段时间再继续
            if iteration < (max_iterations or float('inf')):
                self.log("\n等待 10 秒后继续下一个任务...\n")
                time.sleep(10)

        # 打印最终报告
        self.log("\n" + "=" * 80)
        self.log("自动化开发完成报告")
        self.log("=" * 80)
        self.print_final_report()
        self.log("=" * 80 + "\n")

    def print_final_report(self):
        """打印最终报告"""
        stats = self.feature_list.get_statistics()
        total = stats['total']
        done = stats['by_status']['done']
        progress = int(done / total * 100) if total > 0 else 0

        self.log(f"总任务数: {total}")
        self.log(f"已完成: {done} ({progress}%)")
        self.log(f"待处理: {stats['by_status']['pending']}")
        self.log(f"进行中: {stats['by_status']['in_progress']}")
        self.log(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 打印未完成的任务
        pending = self.feature_list.get_pending_features(limit=10)
        if pending:
            self.log("\n未完成的任务:")
            for feat in pending:
                self.log(f"  - [{feat.id}] {feat.title} ({feat.priority})")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="SynergyAI 自动化开发脚本")
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=None,
        help="最大迭代次数（默认：执行完所有任务）"
    )
    parser.add_argument(
        "--project-dir", "-p",
        type=str,
        default=None,
        help="项目根目录（默认：当前目录）"
    )

    args = parser.parse_args()

    # 创建自动化开发器
    developer = AutoDeveloper(args.project_dir)

    # 运行开发循环
    developer.run_loop(args.iterations)


if __name__ == "__main__":
    main()
