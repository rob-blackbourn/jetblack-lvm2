"""LVM"""

from ctypes import cast
from typing import List

from .types import (
    lvm_str_list_p
)
from .bindings import (
    dm_list_first,
    dm_list_next,
    dm_list_end,
    dm_list_empty
)


def _dm_list_to_str_list(values) -> List[str]:
    names: List[str] = []
    if not dm_list_empty(values):
        value = dm_list_first(values)
        while value:
            c = cast(value, lvm_str_list_p)
            names.append(c.contents.str.decode('ascii'))
            if dm_list_end(values, value):
                # end of linked list
                break
            value = dm_list_next(values, value)
    return names
