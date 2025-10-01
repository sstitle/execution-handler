import os
import time
from typing import List, Any
from .logger import logger


def read_file_to_string(file_path: str) -> str:
    """
    Read a file and return its contents as a string.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents as a string
    """
    logger.info(f"Reading file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    logger.info(f"Successfully read {len(content)} characters from {file_path}")
    return content


def process_large_list(item_count: int) -> List[int]:
    """
    Process a large list of numbers (simulates memory-intensive operation).

    Args:
        item_count: Number of items to process

    Returns:
        List of processed items
    """
    logger.info(f"Processing list with {item_count} items")
    # Simulate some processing time
    time.sleep(0.1)

    # Create a large list
    result = [i * 2 for i in range(item_count)]
    logger.info(f"Successfully processed {len(result)} items")
    return result


def create_large_string(size_mb: int) -> str:
    """
    Create a large string of specified size.

    Args:
        size_mb: Size of the string in megabytes

    Returns:
        Large string
    """
    logger.info(f"Creating string of {size_mb}MB")
    size_bytes = size_mb * 1024 * 1024
    # Create a string by repeating a pattern
    pattern = "Hello, World! "
    pattern_size = len(pattern.encode("utf-8"))
    repetitions = size_bytes // pattern_size

    result = pattern * repetitions
    logger.info(f"Successfully created string of {len(result)} characters")
    return result


def memory_intensive_operation(data_size_mb: int) -> List[bytes]:
    """
    Perform a memory-intensive operation.

    Args:
        data_size_mb: Size of data to process in megabytes

    Returns:
        List of processed data chunks
    """
    logger.info(f"Performing memory-intensive operation with {data_size_mb}MB of data")

    # Create data chunks
    chunk_size = 1024 * 1024  # 1MB chunks
    total_size = data_size_mb * 1024 * 1024
    chunks = []

    for i in range(0, total_size, chunk_size):
        chunk = b"x" * min(chunk_size, total_size - i)
        chunks.append(chunk)

    logger.info(f"Successfully created {len(chunks)} data chunks")
    return chunks


def safe_file_operation(file_path: str, operation: str = "read") -> Any:
    """
    Perform a safe file operation with error handling.

    Args:
        file_path: Path to the file
        operation: Type of operation ("read", "write", "delete")

    Returns:
        Result of the operation
    """
    logger.info(f"Performing {operation} operation on {file_path}")

    try:
        if operation == "read":
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        elif operation == "write":
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("Test content")
                return "File written successfully"
        elif operation == "delete":
            os.remove(file_path)
            return "File deleted successfully"
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        logger.error(f"Error during {operation} operation: {e}")
        raise
