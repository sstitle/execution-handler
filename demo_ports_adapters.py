#!/usr/bin/env python3
"""
Demo script showing the ports and adapters architecture for memory-constrained execution.

This script demonstrates how to use mocks to test memory constraints with arbitrarily
small memory limits, verifying that the handler accepts and refuses work appropriately.
"""

from unittest.mock import Mock
from src.memory_handler import MemoryConstrainedExecutionHandler
from src.test_mocks import (
    MockMemoryMonitor,
    MockMemoryEstimator,
    MockMemoryPolicy,
    MockExecutionDecision,
    ConfigurableMemoryEstimator,
)
from src.adapters import SafetyMarginMemoryPolicyAdapter


def demo_memory_constraint_testing():
    """Demonstrate testing memory constraints with mock objects."""
    print("=== Memory Constraint Testing Demo ===\n")

    # Test 1: Handler accepts work when memory is available
    print("Test 1: Handler accepts work when memory is available")
    print("-" * 50)

    # Set up a scenario with plenty of memory
    memory_monitor = MockMemoryMonitor(available_memory=8 * 1024**2)  # 8MB available
    memory_estimator = MockMemoryEstimator(fixed_estimate=1024**2)  # 1MB estimate
    memory_policy = MockMemoryPolicy(should_execute=True)
    execution_decision = MockExecutionDecision()

    handler = MemoryConstrainedExecutionHandler(
        n_workers=1,
        memory_monitor=memory_monitor,
        memory_policy=memory_policy,
        execution_decision=execution_decision,
    )

    def simple_task(x):
        return f"Processed: {x * 2}"

    try:
        result = handler.execute_with_memory_check(simple_task, memory_estimator, 5)
        print(f"✅ Task executed successfully: {result}")
        print(f"   Memory estimator called {memory_estimator.get_call_count()} times")
        print(f"   Memory policy consulted {memory_policy.get_decision_count()} times")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()

    # Test 2: Handler refuses work when memory is insufficient
    print("Test 2: Handler refuses work when memory is insufficient")
    print("-" * 50)

    # Set up a scenario with limited memory
    memory_monitor.set_available_memory(512 * 1024)  # Only 512KB available
    memory_estimator.set_estimate(1024**2)  # But task needs 1MB
    memory_policy.set_should_execute(False)  # Policy says no
    execution_decision.clear_logs()

    try:
        result = handler.execute_with_memory_check(simple_task, memory_estimator, 3)
        print(f"❌ Task should have been rejected but got: {result}")
    except MemoryError as e:
        print(f"✅ Task correctly rejected: {e}")
        print(f"   Memory estimator called {memory_estimator.get_call_count()} times")
        print(f"   Memory policy consulted {memory_policy.get_decision_count()} times")

        # Show what was logged
        error_logs = execution_decision.get_memory_error_logs()
        if error_logs:
            print(f"   Error logged: {error_logs[0]}")

    print()

    # Test 3: Batch processing with mixed results
    print("Test 3: Batch processing with mixed results")
    print("-" * 50)

    # Set up a scenario where some tasks can run and others can't
    memory_monitor.set_available_memory(2 * 1024**2)  # 2MB available

    # Configure estimator to return different estimates for different tasks
    estimator = ConfigurableMemoryEstimator()
    estimator.set_estimates(
        [512 * 1024, 1024**2, 1.5 * 1024**2, 512 * 1024]
    )  # 512KB, 1MB, 1.5MB, 512KB

    # Policy that allows up to 1MB
    def policy_should_execute(estimated_usage, available_memory):
        return estimated_usage <= 1024**2

    memory_policy = Mock()
    memory_policy.should_execute = policy_should_execute
    memory_policy.get_safe_available_memory = lambda x: x

    execution_decision.clear_logs()

    handler = MemoryConstrainedExecutionHandler(
        n_workers=1,
        memory_monitor=memory_monitor,
        memory_policy=memory_policy,
        execution_decision=execution_decision,
    )

    def batch_task(task_id):
        return f"Task {task_id} completed"

    results = handler.execute_batch_with_memory_check(
        batch_task, [(1,), (2,), (3,), (4,)], estimator
    )

    print(f"Batch results: {results}")
    print("   Expected: [Task 1 completed, Task 2 completed, None, Task 4 completed]")
    print("   (Task 3 should be None due to 1.5MB > 1MB limit)")
    print(f"   Estimator called {estimator.get_call_count()} times")

    print()

    # Test 4: Safety margin policy demonstration
    print("Test 4: Safety margin policy demonstration")
    print("-" * 50)

    memory_monitor = MockMemoryMonitor(available_memory=10 * 1024**2)  # 10MB available
    memory_policy = SafetyMarginMemoryPolicyAdapter(
        safety_margin=0.2
    )  # 20% safety margin
    execution_decision = MockExecutionDecision()

    handler = MemoryConstrainedExecutionHandler(
        n_workers=1,
        memory_monitor=memory_monitor,
        memory_policy=memory_policy,
        execution_decision=execution_decision,
    )

    # Test with different memory estimates
    test_cases = [
        (5 * 1024**2, "5MB task"),  # Should pass (5MB < 8MB safe)
        (8 * 1024**2, "8MB task"),  # Should pass (8MB = 8MB safe)
        (9 * 1024**2, "9MB task"),  # Should fail (9MB > 8MB safe)
    ]

    for estimate, description in test_cases:
        estimator = MockMemoryEstimator(fixed_estimate=estimate)
        execution_decision.clear_logs()

        try:
            result = handler.execute_with_memory_check(simple_task, estimator, 1)
            print(f"✅ {description}: Executed successfully")
        except MemoryError as e:
            print(f"❌ {description}: Rejected - {e}")

    print()

    # Test 5: Memory info using ports
    print("Test 5: Memory info using ports")
    print("-" * 50)

    memory_info = handler.get_memory_info()
    print("Memory info from ports:")
    print(f"  Total: {memory_info['total'] // (1024**2)}MB")
    print(f"  Available: {memory_info['available'] // (1024**2)}MB")
    print(f"  Safe available: {memory_info['safe_available'] // (1024**2)}MB")
    print(f"  Used: {memory_info['used'] // (1024**2)}MB")
    print(f"  Percent used: {memory_info['percent']:.1f}%")


if __name__ == "__main__":
    demo_memory_constraint_testing()
