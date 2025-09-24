import time
from contextlib import contextmanager


@contextmanager
def timer(name: str):
    start_time = time.perf_counter()
    yield
    end_time = time.perf_counter()
    print(f"Time taken for {name}: {end_time - start_time:.6f} seconds")
