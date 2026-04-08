"""Tests for shared state primitives (task list, message bus, file locks, budget)."""

import threading
from typing import List

import pytest
from agents.core.shared_state import BudgetTracker, FileLockSet, MessageBus, SharedTaskList
from agents.core.team_models import AgentMessage, TaskStatus, TeamTask


class TestSharedTaskList:
    """Tests for thread-safe SharedTaskList."""

    def test_add_and_list(self) -> None:
        tl = SharedTaskList()
        task = TeamTask(id="t1", title="Review code")
        tl.add_task(task)
        tasks = tl.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == "t1"

    def test_claim_task(self) -> None:
        tl = SharedTaskList()
        task = TeamTask(id="t1", title="Review")
        tl.add_task(task)
        assert tl.claim_task("t1", "agent-a")
        tasks = tl.get_all_tasks()
        assert tasks[0].status == TaskStatus.CLAIMED
        assert tasks[0].assigned_agent == "agent-a"

    def test_claim_already_claimed(self) -> None:
        tl = SharedTaskList()
        task = TeamTask(id="t1", title="Review")
        tl.add_task(task)
        assert tl.claim_task("t1", "agent-a")
        assert not tl.claim_task("t1", "agent-b")

    def test_claim_nonexistent(self) -> None:
        tl = SharedTaskList()
        assert not tl.claim_task("nonexistent", "agent-a")

    def test_complete_task(self) -> None:
        tl = SharedTaskList()
        tl.add_task(TeamTask(id="t1", title="Review"))
        tl.complete_task("t1", result="All good")
        tasks = tl.get_all_tasks()
        assert tasks[0].status == TaskStatus.COMPLETED
        assert tasks[0].result == "All good"

    def test_fail_task(self) -> None:
        tl = SharedTaskList()
        tl.add_task(TeamTask(id="t1", title="Review"))
        tl.fail_task("t1", error="Timeout")
        tasks = tl.get_all_tasks()
        assert tasks[0].status == TaskStatus.FAILED
        assert tasks[0].result == "Timeout"

    def test_get_pending_tasks_no_deps(self) -> None:
        tl = SharedTaskList()
        tl.add_task(TeamTask(id="t1", title="Task 1"))
        tl.add_task(TeamTask(id="t2", title="Task 2"))
        ready = tl.get_pending_tasks()
        assert len(ready) == 2

    def test_get_pending_tasks_with_deps(self) -> None:
        tl = SharedTaskList()
        tl.add_task(TeamTask(id="t1", title="First"))
        tl.add_task(TeamTask(id="t2", title="Second", depends_on=["t1"]))
        ready = tl.get_pending_tasks()
        # t2 should be blocked because t1 is not completed
        assert len(ready) == 1
        assert ready[0].id == "t1"

    def test_unblocks_after_completion(self) -> None:
        tl = SharedTaskList()
        tl.add_task(TeamTask(id="t1", title="First"))
        tl.add_task(TeamTask(id="t2", title="Second", depends_on=["t1"]))

        tl.complete_task("t1")
        ready = tl.get_pending_tasks()
        ids = [t.id for t in ready]
        assert "t2" in ids

    def test_thread_safety(self) -> None:
        """Concurrent adds don't corrupt state."""
        tl = SharedTaskList()

        def add_task(idx: int) -> None:
            tl.add_task(TeamTask(id=f"t{idx}", title=f"Task {idx}"))

        threads = [threading.Thread(target=add_task, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(tl.get_all_tasks()) == 20


class TestMessageBus:
    """Tests for pub/sub MessageBus."""

    def test_send_and_get(self) -> None:
        bus = MessageBus()
        msg = AgentMessage(
            id="msg-1",
            from_agent="a1",
            to_agent="a2",
            content="Found issue",
            message_type="finding",
        )
        bus.send(msg)
        messages = bus.get_messages_for("a2")
        assert len(messages) == 1
        assert messages[0].content == "Found issue"

    def test_broadcast(self) -> None:
        bus = MessageBus()
        msg = AgentMessage(
            id="msg-2",
            from_agent="coordinator",
            to_agent="*",
            content="All clear",
            message_type="status",
        )
        bus.send(msg)
        # Broadcasts should be visible to any agent
        for_a1 = bus.get_messages_for("a1")
        for_a2 = bus.get_messages_for("a2")
        assert len(for_a1) >= 1
        assert len(for_a2) >= 1

    def test_no_messages_for_unrelated_agent(self) -> None:
        bus = MessageBus()
        msg = AgentMessage(
            id="msg-3",
            from_agent="a1",
            to_agent="a2",
            content="Only for a2",
            message_type="finding",
        )
        bus.send(msg)
        for_a3 = bus.get_messages_for("a3")
        # a3 should not get a1->a2 messages
        assert len(for_a3) == 0

    def test_subscribe_callback(self) -> None:
        bus = MessageBus()
        received: List[AgentMessage] = []
        bus.subscribe("a2", lambda m: received.append(m))
        msg = AgentMessage(
            id="msg-4",
            from_agent="a1",
            to_agent="a2",
            content="test",
        )
        bus.send(msg)
        assert len(received) == 1
        assert received[0].content == "test"

    def test_get_all_messages(self) -> None:
        bus = MessageBus()
        bus.send(AgentMessage(id="m1", from_agent="a", to_agent="b", content="1"))
        bus.send(AgentMessage(id="m2", from_agent="b", to_agent="a", content="2"))
        all_msgs = bus.get_all_messages()
        assert len(all_msgs) == 2


class TestFileLockSet:
    """Tests for advisory file locking."""

    def test_acquire_and_release(self) -> None:
        locks = FileLockSet()
        assert locks.acquire("file.py", "agent1")
        locks.release("file.py", "agent1")

    def test_write_conflict(self) -> None:
        locks = FileLockSet()
        assert locks.acquire("file.py", "agent1")
        # Second writer should be blocked
        assert not locks.acquire("file.py", "agent2")

    def test_reacquire_same_agent(self) -> None:
        locks = FileLockSet()
        assert locks.acquire("file.py", "agent1")
        # Same agent can re-acquire
        assert locks.acquire("file.py", "agent1")

    def test_different_files_no_conflict(self) -> None:
        locks = FileLockSet()
        assert locks.acquire("file1.py", "agent1")
        assert locks.acquire("file2.py", "agent2")

    def test_release_wrong_agent(self) -> None:
        locks = FileLockSet()
        locks.acquire("file.py", "agent1")
        locks.release("file.py", "agent2")  # wrong agent, no-op
        # agent1 still holds the lock
        assert not locks.acquire("file.py", "agent2")

    def test_release_all(self) -> None:
        locks = FileLockSet()
        locks.acquire("f1.py", "agent1")
        locks.acquire("f2.py", "agent1")
        locks.release_all("agent1")
        # Both should now be free
        assert locks.acquire("f1.py", "agent2")
        assert locks.acquire("f2.py", "agent2")

    def test_get_holder(self) -> None:
        locks = FileLockSet()
        assert locks.get_holder("file.py") is None
        locks.acquire("file.py", "agent1")
        assert locks.get_holder("file.py") == "agent1"


class TestBudgetTracker:
    """Tests for cost tracking and budget enforcement."""

    def test_record_cost(self) -> None:
        bt = BudgetTracker(max_budget_usd=10.0)
        bt.record_cost("agent1", 0.05)
        assert bt.get_total_cost() == pytest.approx(0.05)

    def test_agent_costs(self) -> None:
        bt = BudgetTracker(max_budget_usd=10.0)
        bt.record_cost("agent1", 0.05)
        bt.record_cost("agent2", 0.10)
        bt.record_cost("agent1", 0.03)
        costs = bt.get_agent_costs()
        assert costs["agent1"] == pytest.approx(0.08)
        assert costs["agent2"] == pytest.approx(0.10)

    def test_budget_exceeded(self) -> None:
        bt = BudgetTracker(max_budget_usd=0.10)
        bt.record_cost("agent1", 0.08)
        assert not bt.is_over_budget()
        bt.record_cost("agent1", 0.03)
        assert bt.is_over_budget()

    def test_remaining(self) -> None:
        bt = BudgetTracker(max_budget_usd=5.0)
        bt.record_cost("agent1", 1.5)
        assert bt.get_remaining() == pytest.approx(3.5)

    def test_zero_budget_is_unlimited(self) -> None:
        bt = BudgetTracker(max_budget_usd=0.0)
        assert not bt.is_over_budget()
        bt.record_cost("agent1", 999.0)
        assert not bt.is_over_budget()
        assert bt.get_remaining() == float("inf")

    def test_default_budget_unlimited(self) -> None:
        bt = BudgetTracker()
        assert not bt.is_over_budget()
        assert bt.get_remaining() == float("inf")
