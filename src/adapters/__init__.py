import psutil
from ..ports import (
    MemoryMonitorPort,
    MemoryEstimatorPort,
    MemoryPolicyPort,
    ExecutionDecisionPort,
    MemoryInfo,
)
from ..infrastructure.logger import logger


class PsutilMemoryMonitorAdapter(MemoryMonitorPort):
    """Adapter for psutil-based memory monitoring."""

    def get_memory_info(self) -> MemoryInfo:
        """Get current system memory information using psutil."""
        memory = psutil.virtual_memory()
        return MemoryInfo(
            total=memory.total,
            available=memory.available,
            used=memory.used,
            percent=memory.percent,
            safe_available=memory.available,  # Will be overridden by policy
        )

    def get_available_memory(self) -> int:
        """Get available memory in bytes using psutil."""
        return psutil.virtual_memory().available

    def get_total_memory(self) -> int:
        """Get total system memory in bytes using psutil."""
        return psutil.virtual_memory().total


class SafetyMarginMemoryPolicyAdapter(MemoryPolicyPort):
    """Adapter for safety margin-based memory policy."""

    def __init__(self, safety_margin: float = 0.1):
        """
        Initialize the safety margin memory policy.

        Args:
            safety_margin: Safety margin as a fraction (0.1 = 10% buffer)
        """
        self.safety_margin = safety_margin

    def should_execute(self, estimated_usage: int, available_memory: int) -> bool:
        """Determine if operation should execute based on safety margin."""
        safe_available = self.get_safe_available_memory(available_memory)
        return estimated_usage <= safe_available

    def get_safe_available_memory(self, total_available: int) -> int:
        """Calculate safe available memory after applying safety margin."""
        return int(total_available * (1 - self.safety_margin))


class LoggerExecutionDecisionAdapter(ExecutionDecisionPort):
    """Adapter for execution decision logging using the logger."""

    def log_memory_check(
        self, estimated_usage: int, available_memory: int, safe_available: int
    ) -> None:
        """Log memory check information."""
        logger.info(
            f"Memory check: Available={available_memory // (1024**2)}MB, "
            f"Estimated={estimated_usage // (1024**2)}MB, "
            f"Safe available={safe_available // (1024**2)}MB"
        )

    def log_execution_decision(
        self, func_name: str, should_execute: bool, reason: str = ""
    ) -> None:
        """Log execution decision."""
        if should_execute:
            logger.info(f"Executing function {func_name} with sufficient memory")
        else:
            logger.warning(f"Skipping function {func_name}: {reason}")

    def log_memory_error(self, estimated_usage: int, available_memory: int) -> None:
        """Log memory constraint error."""
        error_msg = (
            f"Insufficient memory: estimated {estimated_usage // (1024**2)}MB "
            f"exceeds available memory"
        )
        logger.warning(error_msg)


# Memory estimator adapters (keeping existing functionality)
class FileSizeMemoryEstimatorAdapter(MemoryEstimatorPort):
    """Adapter for file size-based memory estimation."""

    def __init__(self, multiplier: float = 2.0):
        self.multiplier = multiplier

    def estimate_memory_usage(self, file_path: str, *args, **kwargs) -> int:
        """Estimate memory usage based on file size."""
        import os

        try:
            file_size = os.path.getsize(file_path)
            return int(file_size * self.multiplier)
        except (OSError, FileNotFoundError):
            return 0


class DataSizeMemoryEstimatorAdapter(MemoryEstimatorPort):
    """Adapter for data size-based memory estimation."""

    def __init__(self, multiplier: float = 1.5):
        self.multiplier = multiplier

    def estimate_memory_usage(self, data_size: int, *args, **kwargs) -> int:
        """Estimate memory usage based on data size."""
        return int(data_size * self.multiplier)


class FixedMemoryEstimatorAdapter(MemoryEstimatorPort):
    """Adapter for fixed memory estimation (useful for testing)."""

    def __init__(self, fixed_amount: int):
        self.fixed_amount = fixed_amount

    def estimate_memory_usage(self, *args, **kwargs) -> int:
        """Return fixed memory estimation."""
        return self.fixed_amount


class CustomMemoryEstimatorAdapter(MemoryEstimatorPort):
    """Adapter for custom memory estimation functions."""

    def __init__(self, estimator_func: callable):
        self.estimator_func = estimator_func

    def estimate_memory_usage(self, *args, **kwargs) -> int:
        """Use custom function for memory estimation."""
        return self.estimator_func(*args, **kwargs)
