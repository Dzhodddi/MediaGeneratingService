import asyncio
import functools
import time


def timer(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        end_time = time.time()
        if args and hasattr(args[0], "_logger"):
            logger = args[0]._logger
            logger.info(
                f"Function {func.__name__} took {end_time - start_time:.4f} seconds."
            )
        else:
            print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result

    return wrapper
