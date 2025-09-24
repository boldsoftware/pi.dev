import os
import sys


class HiddenPrints:
    """
    A context manager that suppresses stdout (i.e., anything that would be printed to the console).
    From https://stackoverflow.com/a/45669280
    """

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
