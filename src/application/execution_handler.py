from typing import Callable, Any
from mpire import WorkerPool


class ExecutionHandler:
    """Base execution handler for running functions in worker processes."""

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
