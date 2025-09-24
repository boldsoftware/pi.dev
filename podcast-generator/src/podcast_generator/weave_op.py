from collections.abc import Callable
from typing import TypeVar, cast

import weave

C = TypeVar("C", bound=Callable)


def weave_op():
    """
    Decorator to mark a function as a wandb weave operation. Workaround for
    https://github.com/wandb/weave/issues/3423
    """

    def ret(fn: C) -> C:
        return cast(C, weave.op()(fn))

    return ret
