"""Physical Volume"""

from typing import Any

from .bindings import (
    lvm_pv_get_name,
    lvm_pv_get_uuid,
    lvm_pv_get_mda_count,
    lvm_pv_get_dev_size,
    lvm_pv_get_size,
    lvm_pv_get_free
)


class PhysicalVolume:
    """A physical volume"""

    def __init__(self, handle: Any) -> None:
        """A physical volume

        Args:
            handle (Any): The handle
        """
        self.handle = handle

    @property
    def name(self) -> str:
        """The name of the phiscal volume

        Returns:
            str: The name
        """
        name: bytes = lvm_pv_get_name(self.handle)
        return name.decode('ascii')

    @property
    def uuid(self) -> str:
        """The uuid of the phiscal volume

        Returns:
            str: The uuid
        """
        uuid: bytes = lvm_pv_get_uuid(self.handle)
        return uuid.decode('ascii')

    @property
    def mda_count(self) -> int:
        """Get the current number of metadata areas in the physical volume.

        Returns:
            int: Number of metadata areas in the PV.
        """
        return lvm_pv_get_mda_count(self.handle)

    @property
    def dev_size(self) -> int:
        """The current size in bytes of a device underlying a
        physical volume.

        Returns:
            int: Size in bytes.
        """
        return lvm_pv_get_dev_size(self.handle)

    @property
    def size(self) -> int:
        """The current size in bytes of a physical volume.

        Returns:
            int: Size in bytes.
        """
        return lvm_pv_get_size(self.handle)

    @property
    def free(self) -> int:
        """The current unallocated space in bytes of a physical volume.

        Returns:
            int: Free size in bytes.
        """
        return lvm_pv_get_free(self.handle)
