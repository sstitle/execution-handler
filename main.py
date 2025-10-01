import click
import asyncio
from src import Logger


def example_synchronous_function(logger: Logger) -> None:
    logger.info("I'm printing from a synchronous function!")


async def example_asynchronous_function(logger: Logger) -> None:
    logger.info("I'm printing from an asynchronous function!")


@click.command()
def main():
    """Entry point for execution-handler."""
    logger = Logger()
    logger.info("Hello from execution-handler!")
    asyncio.run(example_asynchronous_function(logger))
    example_synchronous_function(logger)


if __name__ == "__main__":
    main()
