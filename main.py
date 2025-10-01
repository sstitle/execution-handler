import asyncclick as click
from src import logger
from src.execution_handler import ExecutionHandler
from src.memory_handler import MemoryConstrainedExecutionHandler
from src.adapters import FileSizeMemoryEstimatorAdapter, DataSizeMemoryEstimatorAdapter
from src.example_functions import read_file_to_string, create_large_string


def example_worker_function(task_id: int) -> str:
    """Example function that will run in a worker process"""
    logger.info(f"Worker process executing task {task_id}")
    return f"Task {task_id} completed in worker process"


def cpu_intensive_task(n: int) -> int:
    """CPU intensive task that benefits from worker processes"""
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
    default="regular",
    help="Type of execution handler to use.",
)
@click.option(
    "--memory-safety-margin",
    type=float,
    default=0.1,
    help="Memory safety margin for memory-constrained handler (0.1 = 10% buffer).",
)
async def main(n_workers: int, handler_type: str, memory_safety_margin: float):
    """Entry point for execution-handler - runs functions in worker processes."""
    logger.info(
        f"Hello from execution-handler! Using {n_workers} worker processes with {handler_type} handler"
    )

    if handler_type == "memory-constrained":
        # Use memory-constrained execution handler
        from src.adapters import SafetyMarginMemoryPolicyAdapter

        memory_policy = SafetyMarginMemoryPolicyAdapter(
            safety_margin=memory_safety_margin
        )
        with MemoryConstrainedExecutionHandler(
            n_workers, memory_policy=memory_policy
        ) as handler:
            # Show memory info
            memory_info = handler.get_memory_info()
            logger.info(
                f"Memory info: {memory_info['available'] // (1024**2)}MB available, "
                f"{memory_info['safe_available'] // (1024**2)}MB safe to use"
            )

            # Demonstrate memory-constrained file reading
            logger.info("Demonstrating memory-constrained file operations...")
            try:
                # Create a test file
                test_file = "test_file.txt"
                with open(test_file, "w") as f:
                    f.write(
                        "This is a test file for memory-constrained execution.\n" * 1000
                    )

                # Use file size memory estimator
                file_estimator = FileSizeMemoryEstimatorAdapter()

                # Try to read the file with memory checking
                result = handler.execute_with_memory_check(
                    read_file_to_string, file_estimator, test_file
                )
                logger.info(f"File read successfully: {len(result)} characters")

                # Demonstrate memory-intensive operation
                logger.info("Demonstrating memory-intensive operation...")
                data_estimator = DataSizeMemoryEstimatorAdapter()

                # Try to create a large string (1MB)
                large_string = handler.execute_with_memory_check(
                    create_large_string,
                    data_estimator,
                    1,  # 1MB
                )
                logger.info(f"Large string created: {len(large_string)} characters")

                # Clean up test file
                import os

                os.remove(test_file)

            except MemoryError as e:
                logger.warning(f"Memory constraint prevented execution: {e}")

            # Regular batch processing still works
            logger.info("Running regular batch processing...")
            batch_args = [(i,) for i in range(1, 4)]  # 3 tasks
            results = handler.execute_batch(example_worker_function, batch_args)
            logger.info(f"Batch processing completed with {len(results)} results:")
            for result in results:
                logger.info(f"  - {result}")

    else:
        # Use regular execution handler
        with ExecutionHandler(n_workers) as handler:
            # Single function execution in worker process
            logger.info("Executing single function in worker process...")
            result = handler.execute(example_worker_function, 1)
            logger.info(f"Result: {result}")

            # CPU intensive task in worker process
            logger.info("Executing CPU intensive task in worker process...")
            factorial_result = handler.execute(cpu_intensive_task, 10)
            logger.info(f"Factorial of 10: {factorial_result}")

            # Batch processing with multiple worker processes
            logger.info("Running batch processing with multiple worker processes...")
            batch_args = [(i,) for i in range(1, 6)]  # 5 tasks
            results = handler.execute_batch(example_worker_function, batch_args)
            logger.info(f"Batch processing completed with {len(results)} results:")
            for result in results:
                logger.info(f"  - {result}")


if __name__ == "__main__":
    main()
