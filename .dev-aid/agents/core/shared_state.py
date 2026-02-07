"""
Thread-safe shared state for multi-agent team orchestration.

Provides primitives for coordinating concurrent agent execution:
- SharedTaskList: task tracking with dependency resolution
- MessageBus: inter-agent messaging with pub/sub
- FileLockSet: advisory file locks to prevent write conflicts
- BudgetTracker: per-agent cost tracking with budget enforcement
"""

import logging
import threading
from typing import Callable, Dict, List, Optional

from .team_models import AgentMessage, TaskStatus, TeamTask

logger = logging.getLogger(__name__)


class SharedTaskList:
    """Thread-safe shared task list with dependency tracking.

    Agents can add, claim, complete, and fail tasks. Dependencies
    are automatically resolved: when a task completes, any tasks
    blocked by it are unblocked.
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, TeamTask] = {}
        self._lock = threading.Lock()

    def add_task(self, task: TeamTask) -> None:
        """Add a task to the shared list."""
        with self._lock:
            self._tasks[task.id] = task
            self._update_blocked_status()

    def claim_task(self, task_id: str, agent_name: str) -> bool:
        """Attempt to claim a task for an agent.

        Returns True if successfully claimed, False if task is not
        available (already claimed, not ready, or doesn't exist).
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            if not task.is_ready():
                return False
            if task.status != TaskStatus.PENDING:
                return False
            task.status = TaskStatus.CLAIMED
            task.assigned_agent = agent_name
            return True

    def complete_task(self, task_id: str, result: str = "") -> None:
        """Mark a task as completed and unblock dependents."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            task.status = TaskStatus.COMPLETED
            task.result = result
            self._update_blocked_status()

    def fail_task(self, task_id: str, error: str = "") -> None:
        """Mark a task as failed."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            task.status = TaskStatus.FAILED
            task.result = error

    def get_pending_tasks(self) -> List[TeamTask]:
        """Get all tasks that are pending and ready to be claimed."""
        with self._lock:
            return [
                t
                for t in self._tasks.values()
                if t.status == TaskStatus.PENDING and t.is_ready()
            ]

    def get_all_tasks(self) -> List[TeamTask]:
        """Get all tasks."""
        with self._lock:
            return list(self._tasks.values())

    def _update_blocked_status(self) -> None:
        """Update blocked_by lists based on completed dependencies.

        Must be called with lock held.
        """
        completed_ids = {
            t.id for t in self._tasks.values() if t.status == TaskStatus.COMPLETED
        }
        for task in self._tasks.values():
            if task.depends_on:
                task.blocked_by = [
                    dep for dep in task.depends_on if dep not in completed_ids
                ]
                # Unblock tasks whose deps are all completed
                if task.status == TaskStatus.BLOCKED and len(task.blocked_by) == 0:
                    task.status = TaskStatus.PENDING


class MessageBus:
    """Thread-safe inter-agent message bus with pub/sub.

    Agents can send messages to specific agents or broadcast to all.
    Subscribers receive callbacks when messages arrive.
    """

    def __init__(self) -> None:
        self._messages: List[AgentMessage] = []
        self._subscribers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        self._lock = threading.Lock()

    def send(self, message: AgentMessage) -> None:
        """Send a message. Notifies subscribers."""
        with self._lock:
            self._messages.append(message)
            # Notify targeted subscribers
            if message.to_agent == "*":
                for callbacks in self._subscribers.values():
                    for cb in callbacks:
                        try:
                            cb(message)
                        except Exception:
                            logger.warning(
                                "Subscriber callback failed for broadcast "
                                "message %s",
                                message.id,
                                exc_info=True,
                            )
            else:
                for cb in self._subscribers.get(message.to_agent, []):
                    try:
                        cb(message)
                    except Exception:
                        logger.warning(
                            "Subscriber callback failed for message %s " "to %s",
                            message.id,
                            message.to_agent,
                            exc_info=True,
                        )

    def subscribe(
        self,
        agent_name: str,
        callback: Callable[[AgentMessage], None],
    ) -> None:
        """Subscribe to messages for a specific agent."""
        with self._lock:
            if agent_name not in self._subscribers:
                self._subscribers[agent_name] = []
            self._subscribers[agent_name].append(callback)

    def get_messages_for(self, agent_name: str) -> List[AgentMessage]:
        """Get all messages addressed to a specific agent or broadcast."""
        with self._lock:
            return [
                m
                for m in self._messages
                if m.to_agent == agent_name or m.to_agent == "*"
            ]

    def get_all_messages(self) -> List[AgentMessage]:
        """Get all messages."""
        with self._lock:
            return list(self._messages)


class FileLockSet:
    """Advisory in-memory file locks to prevent write conflicts.

    Multiple agents may read the same file, but only one can hold
    a write lock at a time. Lock holder name is returned in errors
    so agents can coordinate.
    """

    def __init__(self) -> None:
        self._locks: Dict[str, str] = {}  # path -> agent_name
        self._lock = threading.Lock()

    def acquire(self, path: str, agent_name: str) -> bool:
        """Attempt to acquire a write lock on a file path.

        Returns True if acquired, False if already held by another agent.
        Re-acquiring by the same agent returns True.
        """
        with self._lock:
            holder = self._locks.get(path)
            if holder is None or holder == agent_name:
                self._locks[path] = agent_name
                return True
            return False

    def release(self, path: str, agent_name: str) -> None:
        """Release a write lock. Only the holder can release."""
        with self._lock:
            if self._locks.get(path) == agent_name:
                del self._locks[path]

    def release_all(self, agent_name: str) -> None:
        """Release all locks held by an agent."""
        with self._lock:
            paths_to_remove = [
                p for p, holder in self._locks.items() if holder == agent_name
            ]
            for p in paths_to_remove:
                del self._locks[p]

    def get_holder(self, path: str) -> Optional[str]:
        """Get the agent holding the lock on a path, if any."""
        with self._lock:
            return self._locks.get(path)


class BudgetTracker:
    """Thread-safe budget tracker with per-agent cost breakdown.

    Tracks cumulative costs and enforces a maximum budget.
    """

    def __init__(self, max_budget_usd: float = 0.0) -> None:
        """Initialize with optional budget limit (0 = unlimited)."""
        self._max_budget = max_budget_usd
        self._agent_costs: Dict[str, float] = {}
        self._total_cost: float = 0.0
        self._lock = threading.Lock()

    def record_cost(self, agent_name: str, cost: float) -> None:
        """Record a cost for an agent."""
        with self._lock:
            self._total_cost += cost
            self._agent_costs[agent_name] = (
                self._agent_costs.get(agent_name, 0.0) + cost
            )

    def get_remaining(self) -> float:
        """Get remaining budget in USD. Returns float('inf') if unlimited."""
        with self._lock:
            if self._max_budget <= 0:
                return float("inf")
            return max(0.0, self._max_budget - self._total_cost)

    def is_over_budget(self) -> bool:
        """Check if total cost exceeds the budget."""
        with self._lock:
            if self._max_budget <= 0:
                return False
            return self._total_cost >= self._max_budget

    def get_total_cost(self) -> float:
        """Get total cost across all agents."""
        with self._lock:
            return self._total_cost

    def get_agent_costs(self) -> Dict[str, float]:
        """Get per-agent cost breakdown."""
        with self._lock:
            return dict(self._agent_costs)
