from typing import List
from .ports import (
    MemoryMonitorPort,
    MemoryEstimatorPort,
    MemoryPolicyPort,
    ExecutionDecisionPort,
    MemoryInfo,
)


class MockMemoryMonitor(MemoryMonitorPort):
    """Mock memory monitor for testing with configurable memory levels."""

    def __init__(
        self, total_memory: int = 8 * 1024**3, available_memory: int = 4 * 1024**3
    ):
        """
        Initialize mock memory monitor.

        Args:
            total_memory: Total system memory in bytes (default 8GB)
            available_memory: Available memory in bytes (default 4GB)
        """
        self._total_memory = total_memory
        self._available_memory = available_memory
        self._used_memory = total_memory - available_memory
        self._percent = (self._used_memory / total_memory) * 100

    def set_available_memory(self, available_memory: int) -> None:
        """Set available memory for testing."""
        self._available_memory = available_memory
        self._used_memory = self._total_memory - available_memory
        self._percent = (self._used_memory / self._total_memory) * 100

    def get_memory_info(self) -> MemoryInfo:
        """Get mock memory information."""
        return MemoryInfo(
            total=self._total_memory,
            available=self._available_memory,
            used=self._used_memory,
            percent=self._percent,
            safe_available=self._available_memory,
        )

    def get_available_memory(self) -> int:
        """Get mock available memory."""
        return self._available_memory

    def get_total_memory(self) -> int:
        """Get mock total memory."""
        return self._total_memory


class MockMemoryEstimator(MemoryEstimatorPort):
    """Mock memory estimator for testing with configurable estimates."""

    def __init__(self, fixed_estimate: int = 1024**2):
        """
        Initialize mock memory estimator.

        Args:
            fixed_estimate: Fixed memory estimate in bytes (default 1MB)
        """
        self._fixed_estimate = fixed_estimate
        self._call_count = 0
        self._call_history: List[tuple] = []

    def set_estimate(self, estimate: int) -> None:
        """Set fixed memory estimate for testing."""
        self._fixed_estimate = estimate

    def estimate_memory_usage(self, *args, **kwargs) -> int:
        """Return fixed memory estimate and record call."""
        self._call_count += 1
        self._call_history.append((args, kwargs))
        return self._fixed_estimate

    def get_call_count(self) -> int:
        """Get number of times estimate_memory_usage was called."""
        return self._call_count

    def get_call_history(self) -> List[tuple]:
        """Get history of calls to estimate_memory_usage."""
        return self._call_history.copy()


class MockMemoryPolicy(MemoryPolicyPort):
    """Mock memory policy for testing with configurable behavior."""

    def __init__(self, should_execute: bool = True, safety_margin: float = 0.1):
        """
        Initialize mock memory policy.

        Args:
            should_execute: Whether operations should be allowed to execute
            safety_margin: Safety margin fraction
        """
        self._should_execute = should_execute
        self._safety_margin = safety_margin
        self._decision_count = 0
        self._decision_history: List[tuple] = []

    def set_should_execute(self, should_execute: bool) -> None:
        """Set whether operations should execute."""
        self._should_execute = should_execute

    def should_execute(self, estimated_usage: int, available_memory: int) -> bool:
        """Return configured execution decision and record call."""
        self._decision_count += 1
        self._decision_history.append((estimated_usage, available_memory))
        return self._should_execute

    def get_safe_available_memory(self, total_available: int) -> int:
        """Calculate safe available memory with safety margin."""
        return int(total_available * (1 - self._safety_margin))

    def get_decision_count(self) -> int:
        """Get number of times should_execute was called."""
        return self._decision_count

    def get_decision_history(self) -> List[tuple]:
        """Get history of should_execute calls."""
        return self._decision_history.copy()


class MockExecutionDecision(ExecutionDecisionPort):
    """Mock execution decision logger for testing."""

    def __init__(self):
        self._memory_check_logs: List[tuple] = []
        self._execution_decision_logs: List[tuple] = []
        self._memory_error_logs: List[tuple] = []

    def log_memory_check(
        self, estimated_usage: int, available_memory: int, safe_available: int
    ) -> None:
        """Record memory check log."""
        self._memory_check_logs.append(
            (estimated_usage, available_memory, safe_available)
        )

    def log_execution_decision(
        self, func_name: str, should_execute: bool, reason: str = ""
    ) -> None:
        """Record execution decision log."""
        self._execution_decision_logs.append((func_name, should_execute, reason))

    def log_memory_error(self, estimated_usage: int, available_memory: int) -> None:
        """Record memory error log."""
        self._memory_error_logs.append((estimated_usage, available_memory))

    def get_memory_check_logs(self) -> List[tuple]:
        """Get memory check logs."""
        return self._memory_check_logs.copy()

    def get_execution_decision_logs(self) -> List[tuple]:
        """Get execution decision logs."""
        return self._execution_decision_logs.copy()

    def get_memory_error_logs(self) -> List[tuple]:
        """Get memory error logs."""
        return self._memory_error_logs.copy()

    def clear_logs(self) -> None:
        """Clear all logs."""
        self._memory_check_logs.clear()
        self._execution_decision_logs.clear()
        self._memory_error_logs.clear()


class ConfigurableMemoryEstimator(MemoryEstimatorPort):
    """Configurable memory estimator for testing different scenarios."""

    def __init__(self):
        self._estimates: List[int] = []
        self._current_index = 0
        self._call_count = 0

    def set_estimates(self, estimates: List[int]) -> None:
        """Set a sequence of estimates to return."""
        self._estimates = estimates.copy()
        self._current_index = 0

    def estimate_memory_usage(self, *args, **kwargs) -> int:
        """Return next estimate in sequence."""
        self._call_count += 1
        if self._current_index < len(self._estimates):
            estimate = self._estimates[self._current_index]
            self._current_index += 1
            return estimate
        else:
            # If we've exhausted the sequence, return the last estimate
            return self._estimates[-1] if self._estimates else 0

    def get_call_count(self) -> int:
        """Get number of times estimate_memory_usage was called."""
        return self._call_count
