import asyncclick as click
from typing import Callable, Any
from mpire import WorkerPool
from src import logger


class ExecutionHandler:
    def __init__(self, n_workers: int = 4):
        self.n_workers = n_workers
        self.worker_pool = WorkerPool(n_jobs=n_workers)

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function in worker process and return result"""
        results = self.worker_pool.map(
            func,
            [args],  # mpire expects iterable of argument tuples
            iterable_len=1,
        )
        return list(results)[0]

    def execute_batch(self, func: Callable, args_list: list) -> list:
        """Execute multiple functions in worker processes"""
        return list(self.worker_pool.map(func, args_list))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.worker_pool.terminate()

    def close(self):
        self.worker_pool.terminate()


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
async def main(n_workers: int):
    """Entry point for execution-handler - runs functions in worker processes."""
    logger.info(f"Hello from execution-handler! Using {n_workers} worker processes")

    # Use context manager for proper cleanup
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
