"""Tests for thread-safe shared state primitives."""

import threading
from typing import List

from agents.core.shared_state import BudgetTracker, FileLockSet, MessageBus, SharedTaskList
from agents.core.team_models import AgentMessage, TaskStatus, TeamTask


class TestSharedTaskList:
    """Tests for SharedTaskList thread safety and dependency tracking."""

    def test_add_and_get_task(self) -> None:
        stl = SharedTaskList()
        task = TeamTask(id="t1", title="Task 1")
        stl.add_task(task)
        tasks = stl.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == "t1"

    def test_claim_task_success(self) -> None:
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="Task 1"))
        assert stl.claim_task("t1", "agent-a")
        tasks = stl.get_all_tasks()
        assert tasks[0].status == TaskStatus.CLAIMED
        assert tasks[0].assigned_agent == "agent-a"

    def test_claim_nonexistent_task(self) -> None:
        stl = SharedTaskList()
        assert not stl.claim_task("missing", "agent-a")

    def test_double_claim_fails(self) -> None:
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="Task 1"))
        assert stl.claim_task("t1", "agent-a")
        assert not stl.claim_task("t1", "agent-b")

    def test_complete_task(self) -> None:
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="Task 1"))
        stl.complete_task("t1", "done!")
        tasks = stl.get_all_tasks()
        assert tasks[0].status == TaskStatus.COMPLETED
        assert tasks[0].result == "done!"

    def test_fail_task(self) -> None:
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="Task 1"))
        stl.fail_task("t1", "error occurred")
        tasks = stl.get_all_tasks()
        assert tasks[0].status == TaskStatus.FAILED
        assert tasks[0].result == "error occurred"

    def test_complete_nonexistent_task(self) -> None:
        """Completing a nonexistent task is a no-op."""
        stl = SharedTaskList()
        stl.complete_task("missing", "result")  # Should not raise

    def test_fail_nonexistent_task(self) -> None:
        """Failing a nonexistent task is a no-op."""
        stl = SharedTaskList()
        stl.fail_task("missing", "error")  # Should not raise

    def test_dependency_unblocking(self) -> None:
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="First"))
        stl.add_task(
            TeamTask(
                id="t2",
                title="Second",
                depends_on=["t1"],
                blocked_by=["t1"],
                status=TaskStatus.BLOCKED,
            )
        )

        # t2 should be blocked initially
        pending = stl.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].id == "t1"

        # Complete t1 → t2 should unblock
        stl.complete_task("t1")
        pending = stl.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].id == "t2"

    def test_multi_dependency_unblocking(self) -> None:
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="First"))
        stl.add_task(TeamTask(id="t2", title="Second"))
        stl.add_task(
            TeamTask(
                id="t3",
                title="Third",
                depends_on=["t1", "t2"],
                blocked_by=["t1", "t2"],
                status=TaskStatus.BLOCKED,
            )
        )

        # Complete t1 only → t3 still blocked
        stl.complete_task("t1")
        pending = stl.get_pending_tasks()
        pending_ids = {t.id for t in pending}
        assert "t3" not in pending_ids
        assert "t2" in pending_ids

        # Complete t2 → t3 now unblocked
        stl.complete_task("t2")
        pending = stl.get_pending_tasks()
        assert any(t.id == "t3" for t in pending)

    def test_concurrent_claim(self) -> None:
        """Only one thread should successfully claim a task."""
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="Contested"))

        results: List[bool] = []
        lock = threading.Lock()

        def try_claim(name: str) -> None:
            result = stl.claim_task("t1", name)
            with lock:
                results.append(result)

        threads = [threading.Thread(target=try_claim, args=(f"agent-{i}",)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert results.count(True) == 1
        assert results.count(False) == 9

    def test_get_pending_excludes_blocked(self) -> None:
        stl = SharedTaskList()
        stl.add_task(TeamTask(id="t1", title="Ready"))
        stl.add_task(
            TeamTask(
                id="t2",
                title="Blocked",
                blocked_by=["t1"],
            )
        )
        pending = stl.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].id == "t1"


class TestMessageBus:
    """Tests for MessageBus pub/sub."""

    def test_send_and_retrieve(self) -> None:
        bus = MessageBus()
        msg = AgentMessage(
            id="m1",
            from_agent="a",
            to_agent="b",
            content="hello",
        )
        bus.send(msg)
        messages = bus.get_messages_for("b")
        assert len(messages) == 1
        assert messages[0].content == "hello"

    def test_broadcast_received_by_all(self) -> None:
        bus = MessageBus()
        msg = AgentMessage(
            id="m1",
            from_agent="a",
            to_agent="*",
            content="broadcast",
        )
        bus.send(msg)
        assert len(bus.get_messages_for("b")) == 1
        assert len(bus.get_messages_for("c")) == 1
        assert len(bus.get_messages_for("a")) == 1

    def test_targeted_not_received_by_others(self) -> None:
        bus = MessageBus()
        msg = AgentMessage(
            id="m1",
            from_agent="a",
            to_agent="b",
            content="private",
        )
        bus.send(msg)
        assert len(bus.get_messages_for("b")) == 1
        assert len(bus.get_messages_for("c")) == 0

    def test_subscriber_callback(self) -> None:
        bus = MessageBus()
        received: List[AgentMessage] = []
        bus.subscribe("b", lambda msg: received.append(msg))

        msg = AgentMessage(
            id="m1",
            from_agent="a",
            to_agent="b",
            content="hello",
        )
        bus.send(msg)
        assert len(received) == 1

    def test_broadcast_subscriber_callback(self) -> None:
        bus = MessageBus()
        received: List[AgentMessage] = []
        bus.subscribe("b", lambda msg: received.append(msg))

        msg = AgentMessage(
            id="m1",
            from_agent="a",
            to_agent="*",
            content="broadcast",
        )
        bus.send(msg)
        assert len(received) == 1

    def test_subscriber_error_does_not_break_send(self) -> None:
        bus = MessageBus()

        def bad_callback(msg: AgentMessage) -> None:
            raise RuntimeError("Callback error")

        bus.subscribe("b", bad_callback)

        msg = AgentMessage(
            id="m1",
            from_agent="a",
            to_agent="b",
            content="hello",
        )
        # Should not raise
        bus.send(msg)
        # Message should still be stored
        assert len(bus.get_all_messages()) == 1

    def test_get_all_messages(self) -> None:
        bus = MessageBus()
        for i in range(5):
            bus.send(
                AgentMessage(
                    id=f"m{i}",
                    from_agent="a",
                    to_agent="b",
                    content=f"msg-{i}",
                )
            )
        assert len(bus.get_all_messages()) == 5


class TestFileLockSet:
    """Tests for FileLockSet advisory locks."""

    def test_acquire_and_release(self) -> None:
        locks = FileLockSet()
        assert locks.acquire("/tmp/file.py", "agent-a")
        assert locks.get_holder("/tmp/file.py") == "agent-a"
        locks.release("/tmp/file.py", "agent-a")
        assert locks.get_holder("/tmp/file.py") is None

    def test_conflict_detected(self) -> None:
        locks = FileLockSet()
        assert locks.acquire("/tmp/file.py", "agent-a")
        assert not locks.acquire("/tmp/file.py", "agent-b")

    def test_same_agent_reacquire(self) -> None:
        locks = FileLockSet()
        assert locks.acquire("/tmp/file.py", "agent-a")
        assert locks.acquire("/tmp/file.py", "agent-a")  # Re-entrant

    def test_wrong_agent_cannot_release(self) -> None:
        locks = FileLockSet()
        locks.acquire("/tmp/file.py", "agent-a")
        locks.release("/tmp/file.py", "agent-b")  # No-op
        assert locks.get_holder("/tmp/file.py") == "agent-a"

    def test_release_all(self) -> None:
        locks = FileLockSet()
        locks.acquire("/tmp/a.py", "agent-a")
        locks.acquire("/tmp/b.py", "agent-a")
        locks.acquire("/tmp/c.py", "agent-b")
        locks.release_all("agent-a")
        assert locks.get_holder("/tmp/a.py") is None
        assert locks.get_holder("/tmp/b.py") is None
        assert locks.get_holder("/tmp/c.py") == "agent-b"

    def test_get_holder_nonexistent(self) -> None:
        locks = FileLockSet()
        assert locks.get_holder("/tmp/x.py") is None

    def test_concurrent_acquire(self) -> None:
        """Only one thread should win a file lock."""
        locks = FileLockSet()
        results: List[bool] = []
        lock = threading.Lock()

        def try_acquire(name: str) -> None:
            result = locks.acquire("/tmp/contested.py", name)
            with lock:
                results.append(result)

        threads = [threading.Thread(target=try_acquire, args=(f"agent-{i}",)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert results.count(True) == 1
        assert results.count(False) == 9


class TestBudgetTracker:
    """Tests for BudgetTracker cost tracking."""

    def test_record_cost(self) -> None:
        bt = BudgetTracker(max_budget_usd=10.0)
        bt.record_cost("agent-a", 2.5)
        assert bt.get_total_cost() == 2.5
        assert bt.get_agent_costs() == {"agent-a": 2.5}

    def test_multiple_agents(self) -> None:
        bt = BudgetTracker(max_budget_usd=10.0)
        bt.record_cost("agent-a", 2.0)
        bt.record_cost("agent-b", 3.0)
        bt.record_cost("agent-a", 1.0)
        assert bt.get_total_cost() == 6.0
        costs = bt.get_agent_costs()
        assert costs["agent-a"] == 3.0
        assert costs["agent-b"] == 3.0

    def test_over_budget(self) -> None:
        bt = BudgetTracker(max_budget_usd=5.0)
        bt.record_cost("agent-a", 3.0)
        assert not bt.is_over_budget()
        bt.record_cost("agent-b", 2.0)
        assert bt.is_over_budget()

    def test_remaining_budget(self) -> None:
        bt = BudgetTracker(max_budget_usd=10.0)
        bt.record_cost("agent-a", 3.0)
        assert bt.get_remaining() == 7.0

    def test_unlimited_budget(self) -> None:
        bt = BudgetTracker(max_budget_usd=0.0)
        bt.record_cost("agent-a", 100.0)
        assert not bt.is_over_budget()
        assert bt.get_remaining() == float("inf")

    def test_concurrent_cost_recording(self) -> None:
        bt = BudgetTracker(max_budget_usd=0.0)

        def record(name: str) -> None:
            for _ in range(100):
                bt.record_cost(name, 0.01)

        threads = [threading.Thread(target=record, args=(f"agent-{i}",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 5 agents * 100 calls * 0.01 = 5.0
        assert abs(bt.get_total_cost() - 5.0) < 0.001
        costs = bt.get_agent_costs()
        assert len(costs) == 5
        for cost in costs.values():
            assert abs(cost - 1.0) < 0.001

    def test_remaining_never_negative(self) -> None:
        bt = BudgetTracker(max_budget_usd=1.0)
        bt.record_cost("agent-a", 5.0)
        assert bt.get_remaining() == 0.0
