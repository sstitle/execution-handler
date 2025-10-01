"""Execution Handler - Memory-constrained function execution utility."""

# Infrastructure
from .infrastructure import Logger, logger, SingletonMeta, Singleton

# Application layer
from .application import ExecutionHandler

# Core domain logic
from .core import MemoryConstrainedExecutionHandler

# Ports (interfaces)
from .ports import (
    MemoryEstimatorPort,
    MemoryMonitorPort,
    MemoryPolicyPort,
    ExecutionDecisionPort,
    MemoryInfo,
)

# Adapters (implementations)
from .adapters import (
    PsutilMemoryMonitorAdapter,
    SafetyMarginMemoryPolicyAdapter,
    LoggerExecutionDecisionAdapter,
    FileSizeMemoryEstimatorAdapter,
    DataSizeMemoryEstimatorAdapter,
    FixedMemoryEstimatorAdapter,
    CustomMemoryEstimatorAdapter,
)

# Core utilities
from .core.memory_estimators import (
    FileSizeMemoryEstimator,
    DataSizeMemoryEstimator,
    ListSizeMemoryEstimator,
    CustomMemoryEstimator,
)
from .core.example_functions import (
    read_file_to_string,
    process_large_list,
    create_large_string,
    memory_intensive_operation,
    safe_file_operation,
)

__all__ = [
    "Logger",
    "logger",
    "SingletonMeta",
    "Singleton",
    "ExecutionHandler",
    "MemoryConstrainedExecutionHandler",
    "MemoryEstimatorPort",
    "MemoryMonitorPort",
    "MemoryPolicyPort",
    "ExecutionDecisionPort",
    "MemoryInfo",
    "PsutilMemoryMonitorAdapter",
    "SafetyMarginMemoryPolicyAdapter",
    "LoggerExecutionDecisionAdapter",
    "FileSizeMemoryEstimatorAdapter",
    "DataSizeMemoryEstimatorAdapter",
    "FixedMemoryEstimatorAdapter",
    "CustomMemoryEstimatorAdapter",
    "FileSizeMemoryEstimator",
    "DataSizeMemoryEstimator",
    "ListSizeMemoryEstimator",
    "CustomMemoryEstimator",
    "read_file_to_string",
    "process_large_list",
    "create_large_string",
    "memory_intensive_operation",
    "safe_file_operation",
]
