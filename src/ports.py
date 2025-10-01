from abc import ABC, abstractmethod
from typing import Protocol
from dataclasses import dataclass


@dataclass
class MemoryInfo:
    """Data class representing system memory information."""

    total: int
    available: int
    used: int
    percent: float
    safe_available: int


class MemoryMonitorPort(ABC):
    """Port interface for monitoring system memory."""

    @abstractmethod
    def get_memory_info(self) -> MemoryInfo:
        """Get current system memory information."""
        pass

    @abstractmethod
    def get_available_memory(self) -> int:
        """Get available memory in bytes."""
        pass

    @abstractmethod
    def get_total_memory(self) -> int:
        """Get total system memory in bytes."""
        pass


class MemoryEstimatorPort(Protocol):
    """Port interface for estimating memory usage of operations."""

    def estimate_memory_usage(self, *args, **kwargs) -> int:
        """
        Estimate memory usage in bytes for the given arguments.

        Args:
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Estimated memory usage in bytes
        """
        pass


class MemoryPolicyPort(ABC):
    """Port interface for memory usage policies and decisions."""

    @abstractmethod
    def should_execute(self, estimated_usage: int, available_memory: int) -> bool:
        """
        Determine if an operation should be executed based on memory constraints.

        Args:
            estimated_usage: Estimated memory usage in bytes
            available_memory: Available memory in bytes

        Returns:
            True if operation should execute, False otherwise
        """
        pass

    @abstractmethod
    def get_safe_available_memory(self, total_available: int) -> int:
        """
        Calculate safe available memory after applying policy constraints.

        Args:
            total_available: Total available memory in bytes

        Returns:
            Safe available memory in bytes
        """
        pass


class ExecutionDecisionPort(ABC):
    """Port interface for execution decisions and logging."""

    @abstractmethod
    def log_memory_check(
        self, estimated_usage: int, available_memory: int, safe_available: int
    ) -> None:
        """Log memory check information."""
        pass

    @abstractmethod
    def log_execution_decision(
        self, func_name: str, should_execute: bool, reason: str = ""
    ) -> None:
        """Log execution decision."""
        pass

    @abstractmethod
    def log_memory_error(self, estimated_usage: int, available_memory: int) -> None:
        """Log memory constraint error."""
        pass
