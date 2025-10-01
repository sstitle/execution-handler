#!/usr/bin/env python3
"""
Execution Handler - Memory-constrained function execution utility.

This is the main executable for running functions with memory constraints.
It demonstrates both regular and memory-constrained execution patterns.
"""

import asyncclick as click
from src import (
    logger,
    ExecutionHandler,
    MemoryConstrainedExecutionHandler,
    SafetyMarginMemoryPolicyAdapter,
    FileSizeMemoryEstimatorAdapter,
    DataSizeMemoryEstimatorAdapter,
)
from src.core.example_functions import read_file_to_string, create_large_string


def example_worker_function(task_id: int) -> str:
    """Example function that runs in a worker process."""
    logger.info(f"Worker process executing task {task_id}")
    return f"Task {task_id} completed in worker process"


def cpu_intensive_task(n: int) -> int:
    """CPU intensive task that benefits from worker processes."""
    logger.info(f"Computing factorial of {n} in worker process")
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


@click.command()
@click.option(
    "--n-workers",
    type=int,
    default=4,
    help="Number of worker processes to use.",
)
@click.option(
    "--handler-type",
    type=click.Choice(["regular", "memory-constrained"], case_sensitive=False),
    default="memory-constrained",
    help="Type of execution handler to use.",
)
@click.option(
    "--memory-safety-margin",
    type=float,
    default=0.1,
    help="Memory safety margin for memory-constrained handler (0.1 = 10% buffer).",
)
async def main(n_workers: int, handler_type: str, memory_safety_margin: float):
    """Memory-constrained function execution utility."""
    logger.info(
        f"🚀 Starting execution-handler with {n_workers} workers using {handler_type} handler"
    )

    if handler_type == "memory-constrained":
        # Use memory-constrained execution handler with ports/adapters architecture
        memory_policy = SafetyMarginMemoryPolicyAdapter(
            safety_margin=memory_safety_margin
        )

        with MemoryConstrainedExecutionHandler(
            n_workers, memory_policy=memory_policy
        ) as handler:
            # Display memory information
            memory_info = handler.get_memory_info()
            logger.info(
                f"💾 Memory info: {memory_info['available'] // (1024**2)}MB available, "
                f"{memory_info['safe_available'] // (1024**2)}MB safe to use "
                f"({memory_safety_margin:.0%} safety margin)"
            )

            # Demonstrate memory-constrained file operations
            logger.info("📁 Testing memory-constrained file operations...")
            try:
                # Create a test file in a writable location
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                    test_file = f.name
                    f.write("Memory-constrained execution test file.\n" * 1000)

                # Use file size memory estimator
                file_estimator = FileSizeMemoryEstimatorAdapter(multiplier=2.0)

                # Try to read the file with memory checking
                result = handler.execute_with_memory_check(
                    read_file_to_string, file_estimator, test_file
                )
                logger.info(f"✅ File read successfully: {len(result)} characters")

                # Demonstrate memory-intensive string creation
                logger.info("🧠 Testing memory-intensive operations...")
                data_estimator = DataSizeMemoryEstimatorAdapter()

                # Try to create a large string (1MB)
                large_string = handler.execute_with_memory_check(
                    create_large_string,
                    data_estimator,
                    1,  # 1MB
                )
                logger.info(f"✅ Large string created: {len(large_string)} characters")

                # Clean up test file
                os.remove(test_file)

            except MemoryError as e:
                logger.warning(f"⚠️  Memory constraint prevented execution: {e}")

            # Regular batch processing still works with memory checks
            logger.info("⚡ Running batch processing with memory awareness...")
            batch_args = [(i,) for i in range(1, 4)]  # 3 tasks
            results = handler.execute_batch(example_worker_function, batch_args)
            logger.info(f"✅ Batch processing completed with {len(results)} results:")
            for result in results:
                logger.info(f"   - {result}")

    else:
        # Use regular execution handler without memory constraints
        with ExecutionHandler(n_workers) as handler:
            # Single function execution
            logger.info("⚡ Executing single function in worker process...")
            result = handler.execute(example_worker_function, 1)
            logger.info(f"✅ Result: {result}")

            # CPU intensive task
            logger.info("🔢 Executing CPU intensive task...")
            factorial_result = handler.execute(cpu_intensive_task, 10)
            logger.info(f"✅ Factorial of 10: {factorial_result}")

            # Batch processing
            logger.info("⚡ Running batch processing...")
            batch_args = [(i,) for i in range(1, 6)]  # 5 tasks
            results = handler.execute_batch(example_worker_function, batch_args)
            logger.info(f"✅ Batch processing completed with {len(results)} results:")
            for result in results:
                logger.info(f"   - {result}")

    logger.info("🎉 Execution completed successfully!")


if __name__ == "__main__":
    main()
