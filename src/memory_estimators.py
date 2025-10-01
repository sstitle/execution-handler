import os
from .ports import MemoryEstimatorPort


class FileSizeMemoryEstimator(MemoryEstimatorPort):
    """
    Memory estimator for file operations based on file size.

    Estimates memory usage as a multiple of the file size to account for
    string overhead, encoding, and processing buffers.
    """

    def __init__(self, multiplier: float = 2.0):
        """
        Initialize the file size memory estimator.

        Args:
            multiplier: Multiplier for file size to account for overhead
        """
        self.multiplier = multiplier

    def estimate_memory_usage(self, file_path: str, *args, **kwargs) -> int:
        """
        Estimate memory usage based on file size.

        Args:
            file_path: Path to the file
            *args: Additional arguments (ignored)
            **kwargs: Additional keyword arguments (ignored)

        Returns:
            Estimated memory usage in bytes
        """
        try:
            file_size = os.path.getsize(file_path)
            estimated_usage = int(file_size * self.multiplier)
            return estimated_usage
        except (OSError, FileNotFoundError):
            # If file doesn't exist or can't be accessed, return 0
            return 0


class DataSizeMemoryEstimator(MemoryEstimatorPort):
    """
    Memory estimator for data processing operations.

    Estimates memory usage based on the size of data structures.
    """

    def __init__(self, multiplier: float = 1.5):
        """
        Initialize the data size memory estimator.

        Args:
            multiplier: Multiplier for data size to account for overhead
        """
        self.multiplier = multiplier

    def estimate_memory_usage(self, data_size: int, *args, **kwargs) -> int:
        """
        Estimate memory usage based on data size.

        Args:
            data_size: Size of the data in bytes
            *args: Additional arguments (ignored)
            **kwargs: Additional keyword arguments (ignored)

        Returns:
            Estimated memory usage in bytes
        """
        return int(data_size * self.multiplier)


class ListSizeMemoryEstimator(MemoryEstimatorPort):
    """
    Memory estimator for list processing operations.

    Estimates memory usage based on the number of items in a list.
    """

    def __init__(self, bytes_per_item: int = 100):
        """
        Initialize the list size memory estimator.

        Args:
            bytes_per_item: Estimated bytes per item in the list
        """
        self.bytes_per_item = bytes_per_item

    def estimate_memory_usage(self, item_count: int, *args, **kwargs) -> int:
        """
        Estimate memory usage based on list size.

        Args:
            item_count: Number of items in the list
            *args: Additional arguments (ignored)
            **kwargs: Additional keyword arguments (ignored)

        Returns:
            Estimated memory usage in bytes
        """
        return item_count * self.bytes_per_item


class CustomMemoryEstimator(MemoryEstimatorPort):
    """
    Custom memory estimator that uses a provided function.
    """

    def __init__(self, estimator_func: callable):
        """
        Initialize the custom memory estimator.

        Args:
            estimator_func: Function that takes (*args, **kwargs) and returns bytes
        """
        self.estimator_func = estimator_func

    def estimate_memory_usage(self, *args, **kwargs) -> int:
        """
        Estimate memory usage using the custom function.

        Args:
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Estimated memory usage in bytes
        """
        return self.estimator_func(*args, **kwargs)
