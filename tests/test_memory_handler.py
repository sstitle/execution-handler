import pytest
from unittest.mock import Mock
from src.core.memory_handler import MemoryConstrainedExecutionHandler
from tests.test_mocks import (
    MockMemoryMonitor,
    MockMemoryEstimator,
    MockMemoryPolicy,
    MockExecutionDecision,
    ConfigurableMemoryEstimator,
)
from src.adapters import SafetyMarginMemoryPolicyAdapter, FixedMemoryEstimatorAdapter


class TestMemoryConstrainedExecutionHandler:
    """Test suite for MemoryConstrainedExecutionHandler with ports and adapters."""

    def test_accepts_work_when_memory_available(self):
        """Test that handler accepts work when sufficient memory is available."""
        # Arrange
        memory_monitor = MockMemoryMonitor(
            available_memory=8 * 1024**3
        )  # 8GB available
        memory_estimator = MockMemoryEstimator(fixed_estimate=1024**2)  # 1MB estimate
        memory_policy = MockMemoryPolicy(should_execute=True)
        execution_decision = MockExecutionDecision()

        handler = MemoryConstrainedExecutionHandler(
            n_workers=1,
            memory_monitor=memory_monitor,
            memory_policy=memory_policy,
            execution_decision=execution_decision,
        )

        def test_function(x):
            return x * 2

        # Act
        result = handler.execute_with_memory_check(test_function, memory_estimator, 5)

        # Assert
        assert result == 10
        assert memory_estimator.get_call_count() == 1
        assert memory_policy.get_decision_count() == 1
        assert len(execution_decision.get_execution_decision_logs()) == 1

        # Verify execution was logged
        decision_logs = execution_decision.get_execution_decision_logs()
        assert decision_logs[0][0] == "test_function"
        assert decision_logs[0][1]

    def test_refuses_work_when_memory_insufficient(self):
        """Test that handler refuses work when memory is insufficient."""
        # Arrange
        memory_monitor = MockMemoryMonitor(available_memory=1024**2)  # 1MB available
        memory_estimator = MockMemoryEstimator(
            fixed_estimate=2 * 1024**2
        )  # 2MB estimate
        memory_policy = MockMemoryPolicy(should_execute=False)  # Policy says no
        execution_decision = MockExecutionDecision()

        handler = MemoryConstrainedExecutionHandler(
            n_workers=1,
            memory_monitor=memory_monitor,
            memory_policy=memory_policy,
            execution_decision=execution_decision,
        )

        def test_function(x):
            return x * 2

        # Act & Assert
        with pytest.raises(MemoryError, match="Insufficient memory"):
            handler.execute_with_memory_check(test_function, memory_estimator, 5)

        # Verify memory check was performed
        assert memory_estimator.get_call_count() == 1
        assert memory_policy.get_decision_count() == 1

        # Verify error was logged
        error_logs = execution_decision.get_memory_error_logs()
        assert len(error_logs) == 1
        assert error_logs[0][0] == 2 * 1024**2  # 2MB estimate
        assert error_logs[0][1] == 1024**2  # 1MB available

    def test_batch_execution_with_mixed_results(self):
        """Test batch execution with some tasks succeeding and others failing."""
        # Arrange
        memory_monitor = MockMemoryMonitor(
            available_memory=4 * 1024**2
        )  # 4MB available

        # Configure estimator to return different estimates for different calls
        estimator = ConfigurableMemoryEstimator()
        estimator.set_estimates([1024**2, 2 * 1024**2, 1024**2])  # 1MB, 2MB, 1MB

        # Policy that allows 1MB but not 2MB
        def policy_should_execute(estimated_usage, available_memory):
            return estimated_usage <= 1.5 * 1024**2

        memory_policy = Mock()
        memory_policy.should_execute = policy_should_execute
        memory_policy.get_safe_available_memory = lambda x: x

        execution_decision = MockExecutionDecision()

        handler = MemoryConstrainedExecutionHandler(
            n_workers=1,
            memory_monitor=memory_monitor,
            memory_policy=memory_policy,
            execution_decision=execution_decision,
        )

        def test_function(x):
            return x * 2

        # Act
        results = handler.execute_batch_with_memory_check(
            test_function, [(1,), (2,), (3,)], estimator
        )

        # Assert
        assert results == [
            2,
            None,
            6,
        ]  # Second task should be None due to memory constraint
        assert estimator.get_call_count() == 3

        # Verify execution decisions were logged
        decision_logs = execution_decision.get_execution_decision_logs()
        assert len(decision_logs) >= 3  # At least 3 individual decisions

    def test_memory_info_uses_ports(self):
        """Test that get_memory_info uses the injected ports."""
        # Arrange
        memory_monitor = MockMemoryMonitor(
            total_memory=16 * 1024**3,  # 16GB total
            available_memory=8 * 1024**3,  # 8GB available
        )
        memory_policy = SafetyMarginMemoryPolicyAdapter(safety_margin=0.2)  # 20% margin
        execution_decision = MockExecutionDecision()

        handler = MemoryConstrainedExecutionHandler(
            n_workers=1,
            memory_monitor=memory_monitor,
            memory_policy=memory_policy,
            execution_decision=execution_decision,
        )

        # Act
        memory_info = handler.get_memory_info()

        # Assert
        assert memory_info["total"] == 16 * 1024**3
        assert memory_info["available"] == 8 * 1024**3
        assert memory_info["safe_available"] == int(8 * 1024**3 * 0.8)  # 20% margin

    def test_execution_without_memory_estimator(self):
        """Test execution when no memory estimator is provided."""
        # Arrange
        memory_monitor = MockMemoryMonitor(available_memory=8 * 1024**3)
        memory_policy = MockMemoryPolicy(should_execute=True)
        execution_decision = MockExecutionDecision()

        handler = MemoryConstrainedExecutionHandler(
            n_workers=1,
            memory_monitor=memory_monitor,
            memory_policy=memory_policy,
            execution_decision=execution_decision,
        )

        def test_function(x):
            return x * 3

        # Act
        result = handler.execute_with_memory_check(test_function, None, 4)

        # Assert
        assert result == 12
        # No memory check should have been performed
        assert memory_policy.get_decision_count() == 0
        assert len(execution_decision.get_memory_check_logs()) == 0

    def test_safety_margin_policy_adapter(self):
        """Test the safety margin policy adapter."""
        # Arrange
        policy = SafetyMarginMemoryPolicyAdapter(safety_margin=0.1)  # 10% margin
        available_memory = 10 * 1024**2  # 10MB

        # Act
        safe_available = policy.get_safe_available_memory(available_memory)
        should_execute_small = policy.should_execute(
            8 * 1024**2, available_memory
        )  # 8MB
        should_execute_large = policy.should_execute(
            9.5 * 1024**2, available_memory
        )  # 9.5MB

        # Assert
        assert safe_available == int(10 * 1024**2 * 0.9)  # 9MB
        assert should_execute_small  # 8MB < 9MB
        assert not should_execute_large  # 9.5MB > 9MB

    def test_fixed_memory_estimator_adapter(self):
        """Test the fixed memory estimator adapter."""
        # Arrange
        estimator = FixedMemoryEstimatorAdapter(5 * 1024**2)  # 5MB

        # Act
        estimate1 = estimator.estimate_memory_usage("file1.txt")
        estimate2 = estimator.estimate_memory_usage("file2.txt", arg2="value")

        # Assert
        assert estimate1 == 5 * 1024**2
        assert estimate2 == 5 * 1024**2

    def test_mock_memory_monitor_configuration(self):
        """Test that mock memory monitor can be configured dynamically."""
        # Arrange
        monitor = MockMemoryMonitor(
            total_memory=8 * 1024**3, available_memory=4 * 1024**3
        )

        # Act
        initial_available = monitor.get_available_memory()
        monitor.set_available_memory(2 * 1024**3)  # Reduce to 2GB
        updated_available = monitor.get_available_memory()

        # Assert
        assert initial_available == 4 * 1024**3
        assert updated_available == 2 * 1024**3

        memory_info = monitor.get_memory_info()
        assert memory_info.available == 2 * 1024**3
        assert memory_info.used == 6 * 1024**3  # 8GB - 2GB

    def test_mock_execution_decision_logging(self):
        """Test that mock execution decision captures all logging."""
        # Arrange
        decision = MockExecutionDecision()

        # Act
        decision.log_memory_check(1024**2, 8 * 1024**2, 7 * 1024**2)
        decision.log_execution_decision("test_func", True, "sufficient memory")
        decision.log_memory_error(2 * 1024**2, 1024**2)

        # Assert
        memory_logs = decision.get_memory_check_logs()
        execution_logs = decision.get_execution_decision_logs()
        error_logs = decision.get_memory_error_logs()

        assert len(memory_logs) == 1
        assert memory_logs[0] == (1024**2, 8 * 1024**2, 7 * 1024**2)

        assert len(execution_logs) == 1
        assert execution_logs[0] == ("test_func", True, "sufficient memory")

        assert len(error_logs) == 1
        assert error_logs[0] == (2 * 1024**2, 1024**2)

        # Test clearing logs
        decision.clear_logs()
        assert len(decision.get_memory_check_logs()) == 0
        assert len(decision.get_execution_decision_logs()) == 0
        assert len(decision.get_memory_error_logs()) == 0


if __name__ == "__main__":
    pytest.main([__file__])
