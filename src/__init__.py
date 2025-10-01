"""Execution handler package."""

from .logger import Logger, logger
from .singleton import SingletonMeta, Singleton
from .execution_handler import ExecutionHandler
from .memory_handler import MemoryConstrainedExecutionHandler
from .ports import (
    MemoryEstimatorPort,
    MemoryMonitorPort,
    MemoryPolicyPort,
    ExecutionDecisionPort,
    MemoryInfo,
)
from .adapters import (
    PsutilMemoryMonitorAdapter,
    SafetyMarginMemoryPolicyAdapter,
    LoggerExecutionDecisionAdapter,
    FileSizeMemoryEstimatorAdapter,
    DataSizeMemoryEstimatorAdapter,
    FixedMemoryEstimatorAdapter,
    CustomMemoryEstimatorAdapter,
)
from .memory_estimators import (
    FileSizeMemoryEstimator,
    DataSizeMemoryEstimator,
    ListSizeMemoryEstimator,
    CustomMemoryEstimator,
)
from .example_functions import (
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
