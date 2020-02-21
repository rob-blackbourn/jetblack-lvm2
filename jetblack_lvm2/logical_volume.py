"""Physical Volume"""

from typing import Any, Callable, Optional

from .bindings import (
    lvm_lv_get_name,
    lvm_lv_get_uuid,
    lvm_lv_get_size,
    lvm_lv_is_active,
    lvm_lv_is_suspended,
    lvm_lv_activate,
    lvm_lv_deactivate,
    lvm_vg_remove_lv,
    lvm_lv_get_attr,
    lvm_lv_get_origin
)
from .exceptions import LVMException


class LogicalVolume:
    """A logical volume"""

    def __init__(
            self,
            handle: Any,
            create_exception: Callable[[], LVMException]
    ) -> None:
        """Initialise a logical volume

        Args:
            handle (Any): The handle
            create_exception (Callable[[], LVMException]): An exception factory
        """
        self.handle = handle
        self._create_exception = create_exception

    @property
    def name(self) -> str:
        """The name of the logical volume.

        Returns:
            str: The logical volume name.
        """
        return lvm_lv_get_name(self.handle).decode('ascii')

    @property
    def uuid(self) -> str:
        """The uuid of the logical volume.

        Returns:
            str: The logical volume uuid.
        """
        return lvm_lv_get_uuid(self.handle).decode('ascii')

    @property
    def size(self) -> int:
        """The size in bytes of a logical volume.

        Returns:
            int: Size in bytes.
        """
        return lvm_lv_get_size(self.handle)

    @property
    def is_active(self) -> bool:
        """the current activation state of a logical volume.

        Returns:
            bool: True if the LV is active in the kernel.
        """
        return lvm_lv_is_active(self.handle) == 1

    @is_active.setter
    def is_active(self, value: bool) -> None:
        if value and not self.is_active:
            self.activate()
        elif not value and self.is_active:
            self.deactivate()

    @property
    def is_suspended(self) -> bool:
        """The current suspended state of a logical volume.

        Returns:
            bool: True if the LV is suspended in the kernel.
        """
        return lvm_lv_is_suspended(self.handle) == 1

    @property
    def attr(self) -> str:
        """The attributes of a logical volume.

        Returns:
            str: The logical volume attributes.
        """
        return lvm_lv_get_attr(self.handle).decode('ascii')

    @property
    def origin(self) -> Optional[str]:
        """Get the origin of a snapshot.

        Returns:
            str: Null if the logical volume is not a snapshot, else origin name.
        """
        origin = lvm_lv_get_origin(self.handle)
        return origin.decode('ascii') if origin else None

    def activate(self) -> None:
        """ Activate a logical volume.

        This function is the equivalent of the lvm command "lvchange -ay".

        NOTE: This function cannot currently handle LVs with an in-progress pvmove or
        lvconvert.

        Raises:
            LVMException: If the operation was not successful.
        """
        retcode = lvm_lv_activate(self.handle)
        if retcode != 0:
            raise self._create_exception()

    def deactivate(self):
        """Deactivate a logical volume.

        Raises:
            LVMException: If the operation was not successful.
        """
        retcode = lvm_lv_deactivate(self.handle)
        if retcode != 0:
            raise self._create_exception()

    def remove(self):
        """Remove a logical volume from a volume group.

        This function commits the change to disk and does _not_ require calling
        lvm_vg_write().

        Currently only removing linear LVs are possible.

        Raises:
            LVMException: If the operation was not successful.
        """
        retcode = lvm_vg_remove_lv(self.handle)
        if retcode != 0:
            raise self._create_exception()
