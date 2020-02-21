"""Exceptions"""


class LVMException(Exception):
    """An LVM Exception"""

    def __init__(self, errno: int, msg: str) -> None:
        super().__init__(msg)
        self.errno = errno

    def __str__(self):
        return f'{self.errno}: {super().__str__()}'
