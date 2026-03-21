"""
性能测试套件

测试系统各组件的性能，包括：
- 数据库操作性能
- 缓存性能
- API 响应时间
- WebSocket 消息处理
"""

import pytest
import time
import asyncio
import json
from typing import List
from httpx import AsyncClient, ASGITransport

from main import app, cache_manager, perf_monitor
from core.storage import Storage, Session, Task, TaskState, Message, MessageType


class TestDatabasePerformance:
    """数据库性能测试"""

    @pytest.fixture
    def storage(self):
        """创建测试存储实例"""
        storage = Storage("data/test_performance.db")
        yield storage
        # 清理
        import os
        if os.path.exists("data/test_performance.db"):
            os.remove("data/test_performance.db")
            os.remove("data/test_performance.db-wal")  # 删除 WAL 文件

    def test_save_session_performance(self, storage):
        """测试会话保存性能"""
        session = Session()
        # 添加 100 条消息
        for i in range(100):
            msg = Message(
                id=str(i),
                sender=f"user_{i}",
                sender_role="user",
                content=f"Test message {i}",
                message_type=MessageType.USER
            )
            session.add_message(msg)

        # 添加 50 个任务
        for i in range(50):
            task = Task(
                id=f"task_{i}",
                title=f"Test Task {i}",
                description=f"Test task description {i}",
                state=TaskState.PENDING
            )
            session.tasks[task.id] = task

        # 测量保存时间
        start_time = time.time()
        storage.save_session(session)
        duration = time.time() - start_time

        # 保存操作应该在 1 秒内完成
        assert duration < 1.0, f"Save session took too long: {duration}s"

        print(f"✓ Save session (100 messages, 50 tasks): {duration:.3f}s")

    def test_load_session_performance(self, storage):
        """测试会话加载性能"""
        session = Session()
        # 添加数据
        for i in range(100):
            msg = Message(
                id=str(i),
                sender=f"user_{i}",
                sender_role="user",
                content=f"Test message {i}",
                message_type=MessageType.USER
            )
            session.add_message(msg)

        storage.save_session(session)

        # 测量加载时间
        start_time = time.time()
        loaded_session = storage.load_session(session.id)
        duration = time.time() - start_time

        assert loaded_session is not None
        assert len(loaded_session.messages) == 100

        # 加载操作应该在 0.5 秒内完成
        assert duration < 0.5, f"Load session took too long: {duration}s"

        print(f"✓ Load session (100 messages): {duration:.3f}s")

    def test_list_sessions_performance(self, storage):
        """测试会话列表性能"""
        # 创建 50 个会话
        session_ids = []
        for i in range(50):
            session = Session()
            storage.save_session(session)
            session_ids.append(session.id)

        # 测量列表时间
        start_time = time.time()
        sessions = storage.list_sessions()
        duration = time.time() - start_time

        assert len(sessions) == 50

        # 列表操作应该在 0.5 秒内完成
        assert duration < 0.5, f"List sessions took too long: {duration}s"

        print(f"✓ List sessions (50 sessions): {duration:.3f}s")


class TestCachePerformance:
    """缓存性能测试"""

    @pytest.mark.asyncio
    async def test_cache_set_get_performance(self):
        """测试缓存读写性能"""
        test_data = {"key": "value" * 1000}  # 约 5KB 数据

        # 测试 1000 次写入
        start_time = time.time()
        for i in range(1000):
            await cache_manager.set(f"test_key_{i}", test_data)
        write_duration = time.time() - start_time

        # 1000 次写入应该在 2 秒内完成
        assert write_duration < 2.0, f"Cache write took too long: {write_duration}s"
        print(f"✓ Cache write (1000 operations): {write_duration:.3f}s")

        # 测试 1000 次读取
        start_time = time.time()
        for i in range(1000):
            data = await cache_manager.get(f"test_key_{i}")
            assert data is not None
        read_duration = time.time() - start_time

        # 1000 次读取应该在 1 秒内完成
        assert read_duration < 1.0, f"Cache read took too long: {read_duration}s"
        print(f"✓ Cache read (1000 operations): {read_duration:.3f}s")

    @pytest.mark.asyncio
    async def test_cache_expiration_performance(self):
        """测试缓存过期清理性能"""
        # 创建 1000 个快过期的缓存项
        for i in range(1000):
            await cache_manager.set(f"expire_key_{i}", f"value_{i}", ttl=1)

        # 等待过期
        await asyncio.sleep(1.1)

        # 清理过期缓存
        start_time = time.time()
        await cache_manager.cleanup_expired()
        duration = time.time() - start_time

        # 清理操作应该在 1 秒内完成
        assert duration < 1.0, f"Cache cleanup took too long: {duration}s"
        print(f"✓ Cache cleanup (1000 expired items): {duration:.3f}s")


class TestAPIPerformance:
    """API 性能测试"""

    @pytest.mark.asyncio
    async def test_health_check_performance(self):
        """测试健康检查端点性能"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 测试 100 次请求
            durations = []
            for _ in range(100):
                start_time = time.time()
                response = await client.get("/api/health")
                duration = time.time() - start_time

                assert response.status_code == 200
                durations.append(duration)

            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)

            # 平均响应时间应该小于 100ms
            assert avg_duration < 0.1, f"Health check too slow: {avg_duration:.3f}s"
            # 最大响应时间应该小于 500ms
            assert max_duration < 0.5, f"Health check spike too high: {max_duration:.3f}s"

            print(f"✓ Health check (100 requests): avg={avg_duration:.3f}s, max={max_duration:.3f}s")

    @pytest.mark.asyncio
    async def test_performance_stats_performance(self):
        """测试性能统计端点性能"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            start_time = time.time()
            response = await client.get("/api/performance")
            duration = time.time() - start_time

            assert response.status_code == 200
            data = response.json()
            assert "total_requests" in data

            # 响应该时间应该小于 100ms
            assert duration < 0.1, f"Performance stats too slow: {duration:.3f}s"

            print(f"✓ Performance stats: {duration:.3f}s")


class TestConcurrencyPerformance:
    """并发性能测试"""

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self):
        """测试并发缓存操作性能"""
        async def cache_operation(i):
            await cache_manager.set(f"concurrent_key_{i}", f"value_{i}")
            return await cache_manager.get(f"concurrent_key_{i}")

        # 并发执行 100 个缓存操作
        start_time = time.time()
        results = await asyncio.gather(*[cache_operation(i) for i in range(100)])
        duration = time.time() - start_time

        assert len(results) == 100
        assert all(r is not None for r in results)

        # 100 个并发操作应该在 2 秒内完成
        assert duration < 2.0, f"Concurrent cache operations too slow: {duration}s"

        print(f"✓ Concurrent cache operations (100 operations): {duration:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self):
        """测试并发 API 请求性能"""
        transport = ASGITransport(app=app)

        async def make_request(i):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                start_time = time.time()
                response = await client.get("/api/health")
                duration = time.time() - start_time
                assert response.status_code == 200
                return duration

        # 并发执行 50 个请求
        start_time = time.time()
        durations = await asyncio.gather(*[make_request(i) for i in range(50)])
        total_duration = time.time() - start_time

        avg_duration = sum(durations) / len(durations)

        # 并发 50 个请求应该在 3 秒内完成
        assert total_duration < 3.0, f"Concurrent requests too slow: {total_duration}s"

        print(f"✓ Concurrent API requests (50 requests): total={total_duration:.3f}s, avg={avg_duration:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
