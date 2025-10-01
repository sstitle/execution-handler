from typing import Callable, Any, Optional
from .execution_handler import ExecutionHandler
from .ports import (
    MemoryMonitorPort,
    MemoryEstimatorPort,
    MemoryPolicyPort,
    ExecutionDecisionPort,
)


class MemoryConstrainedExecutionHandler(ExecutionHandler):
    """
    Execution handler that checks available memory before executing functions.

    This handler estimates memory usage of functions and only executes them
    if there's sufficient available memory on the system.
    """

    def __init__(
        self,
        n_workers: int = 4,
        memory_monitor: Optional[MemoryMonitorPort] = None,
        memory_policy: Optional[MemoryPolicyPort] = None,
        execution_decision: Optional[ExecutionDecisionPort] = None,
    ):
        """
        Initialize the memory-constrained execution handler.

        Args:
            n_workers: Number of worker processes to use
            memory_monitor: Memory monitoring port (uses default if None)
            memory_policy: Memory policy port (uses default if None)
            execution_decision: Execution decision port (uses default if None)
        """
        super().__init__(n_workers)

        # Use dependency injection with defaults
        if memory_monitor is None:
            from .adapters import PsutilMemoryMonitorAdapter

            self.memory_monitor = PsutilMemoryMonitorAdapter()
        else:
            self.memory_monitor = memory_monitor

        if memory_policy is None:
            from .adapters import SafetyMarginMemoryPolicyAdapter

            self.memory_policy = SafetyMarginMemoryPolicyAdapter()
        else:
            self.memory_policy = memory_policy

        if execution_decision is None:
            from .adapters import LoggerExecutionDecisionAdapter

            self.execution_decision = LoggerExecutionDecisionAdapter()
        else:
            self.execution_decision = execution_decision

    def _check_memory_availability(self, estimated_usage: int) -> bool:
        """
        Check if there's enough memory available for the estimated usage.

        Args:
            estimated_usage: Estimated memory usage in bytes

        Returns:
            True if there's enough memory, False otherwise
        """
        available_memory = self.memory_monitor.get_available_memory()
        safe_available = self.memory_policy.get_safe_available_memory(available_memory)

        # Log memory check
        self.execution_decision.log_memory_check(
            estimated_usage, available_memory, safe_available
        )

        # Use policy to make decision
        return self.memory_policy.should_execute(estimated_usage, available_memory)

    def execute_with_memory_check(
        self,
        func: Callable,
        memory_estimator: Optional[MemoryEstimatorPort] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with memory constraint checking.

        Args:
            func: Function to execute
            memory_estimator: Optional memory estimator for the function
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Function result if executed, None if skipped due to memory constraints

        Raises:
            MemoryError: If function is skipped due to insufficient memory
        """
        if memory_estimator is not None:
            estimated_usage = memory_estimator.estimate_memory_usage(*args, **kwargs)

            if not self._check_memory_availability(estimated_usage):
                available_memory = self.memory_monitor.get_available_memory()
                self.execution_decision.log_memory_error(
                    estimated_usage, available_memory
                )
                error_msg = (
                    f"Insufficient memory: estimated {estimated_usage // (1024**2)}MB "
                    f"exceeds available memory"
                )
                raise MemoryError(error_msg)

        # Log execution decision
        self.execution_decision.log_execution_decision(func.__name__, True)

        # Execute the function
        return func(*args, **kwargs)

    def execute_batch_with_memory_check(
        self,
        func: Callable,
        args_list: list,
        memory_estimator: Optional[MemoryEstimatorPort] = None,
    ) -> list:
        """
        Execute multiple functions with memory constraint checking.

        Args:
            func: Function to execute
            args_list: List of argument tuples for batch execution
            memory_estimator: Optional memory estimator for the function

        Returns:
            List of results for successfully executed functions
        """
        results = []
        skipped_count = 0

        for args in args_list:
            try:
                if isinstance(args, tuple):
                    result = self.execute_with_memory_check(
                        func, memory_estimator, *args
                    )
                else:
                    result = self.execute_with_memory_check(
                        func, memory_estimator, args
                    )
                results.append(result)
            except MemoryError as e:
                self.execution_decision.log_execution_decision(
                    func.__name__, False, str(e)
                )
                skipped_count += 1
                results.append(None)

        if skipped_count > 0:
            self.execution_decision.log_execution_decision(
                f"batch_{func.__name__}",
                False,
                f"Skipped {skipped_count} out of {len(args_list)} executions due to memory constraints",
            )

        return results

    def get_memory_info(self) -> dict:
        """Get current memory information."""
        memory_info = self.memory_monitor.get_memory_info()
        safe_available = self.memory_policy.get_safe_available_memory(
            memory_info.available
        )

        return {
            "total": memory_info.total,
            "available": memory_info.available,
            "used": memory_info.used,
            "percent": memory_info.percent,
            "safe_available": safe_available,
        }
