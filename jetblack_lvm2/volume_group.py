"""LVM"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod
from ctypes import cast, c_ulong, c_ulonglong
from typing import Any, Callable, List, Optional

from .types import lvm_pv_list_p, lvm_lv_list_p
from .bindings import (
    lvm_vg_open,
    lvm_vg_create,
    lvm_vg_close,
    lvm_vg_is_clustered,
    lvm_vg_is_exported,
    lvm_vg_is_partial,
    lvm_vg_get_name,
    lvm_vg_get_seqno,
    lvm_vg_get_uuid,
    lvm_vg_get_size,
    lvm_vg_get_free_size,
    lvm_vg_get_extent_size,
    lvm_vg_set_extent_size,
    lvm_vg_get_extent_count,
    lvm_vg_get_free_extent_count,
    lvm_vg_get_pv_count,
    lvm_vg_get_max_pv,
    lvm_vg_get_max_lv,
    lvm_vg_get_tags,
    lvm_vg_add_tag,
    lvm_vg_remove_tag,
    lvm_vg_write,
    lvm_vg_remove,
    lvm_vg_extend,
    lvm_vg_reduce,
    lvm_vg_list_pvs,
    lvm_vg_list_lvs,
    lvm_vg_create_lv_linear,
    lvm_lv_from_name,
    dm_list_empty,
    dm_list_first,
    dm_list_next,
    dm_list_end
)
from .exceptions import LVMException
from .logical_volume import LogicalVolume
from .physical_volume import PhysicalVolume
from .utils import _dm_list_to_str_list


class VolumeGroupInstance:
    """A volume group instance"""

    def __init__(
            self,
            handle: Any,
            create_exception: Callable[[], LVMException]
    ) -> None:
        """A volume group instance

        Args:
            handle(Any): The volume group handle
            create_exception(Callable[[], LVMException]): An exception factory.
        """
        self._create_exception = create_exception
        self.handle: Any = handle

    @property
    def name(self) -> str:
        """The current name of a volume group.

        Returns:
            str: The name
        """
        name = lvm_vg_get_name(self.handle)
        return name.decode('ascii')

    @property
    def is_clustered(self) -> bool:
        """Whether the volume group is clustered.

        Returns:
            bool: True if clustered; otherwise False.
        """
        return lvm_vg_is_clustered(self.handle) == 1

    @property
    def is_exported(self) -> bool:
        """Whether or not a volume group is exported

        Returns:
            bool: True if exported; otherwise False.
        """
        return lvm_vg_is_exported(self.handle) == 1

    @property
    def is_partial(self) -> bool:
        """Whether or not a volume group is partial

        Returns:
            bool: True if partial; otherwise False.
        """
        return lvm_vg_is_partial(self.handle) == 1

    @property
    def seqno(self) -> int:
        """Get the current metadata sequence number of a volume group.

        The metadata sequence number is incrented for each metadata change.
        Applications may use the sequence number to determine if any LVM objects
        have changed from a prior query.

        Returns:
            int: Metadata sequence number.
        """
        return lvm_vg_get_seqno(self.handle)

    @property
    def uuid(self) -> str:
        """The current uuid of a volume group.

        Returns:
            str: The uuid string.
        """
        uuid = lvm_vg_get_uuid(self.handle)
        return uuid.decode('ascii')

    @property
    def size(self) -> int:
        """Get the current size in bytes of a volume group.

        Returns:
            int: Size in bytes.
        """
        return lvm_vg_get_size(self.handle)

    @property
    def free_size(self) -> int:
        """Get the current unallocated space in bytes of a volume group.

        Returns:
            int: Free size in bytes.
        """
        return lvm_vg_get_free_size(self.handle)

    @property
    def extent_size(self) -> int:
        """The current extent size in bytes of a volume group.

        Returns:
            int: Extent size in bytes.
        """
        return lvm_vg_get_extent_size(self.handle)

    @extent_size.setter
    def extent_size(self, value: int) -> None:
        retcode = lvm_vg_set_extent_size(self.handle, c_ulong(value))
        if retcode != 0:
            raise self._create_exception()

    @property
    def extent_count(self) -> int:
        """Get the current number of total extents of a volume group.

        Returns:
            int: Extent count.
        """
        return lvm_vg_get_extent_count(self.handle)

    @property
    def free_extent_count(self) -> int:
        """Get the current number of free extents of a volume group.

        Returns:
            int: Free extent count.
        """
        return lvm_vg_get_free_extent_count(self.handle)

    @property
    def pv_count(self) -> int:
        """Get the current number of physical volumes of a volume group.

        Returns:
            int: Physical volume count.
        """
        return lvm_vg_get_pv_count(self.handle)

    @property
    def max_pv(self) -> int:
        """Get the maximum number of physical volumes allowed in a volume group.

        Returns:
            int: Maximum number of physical volumes allowed in a volume group.
        """
        return lvm_vg_get_max_pv(self.handle)

    @property
    def max_lv(self) -> int:
        """Get the maximum number of logical volumes allowed in a volume group.

        Returns:
            int: Maximum number of logical volumes allowed in a volume group.
        """
        return lvm_vg_get_max_lv(self.handle)

    @property
    def tags(self) -> List[str]:
        """The volume group tags

        Raises:
            LVMException: If the tags could not be obtained.

        Returns:
            List[str]: [description]
        """
        tags = lvm_vg_get_tags(self.handle)
        if not bool(tags):
            raise self._create_exception()
        return _dm_list_to_str_list(tags)

    def add_tag(self, tag: str) -> None:
        """Add a tag to a VG.

        This function requires calling lvm_vg_write() to commit the change to disk.
        After successfully adding a tag, use lvm_vg_write() to commit the
        new VG to disk.  Upon failure, retry the operation or release the VG handle
        with lvm_vg_close().

        Args:
            tag(str): Tag to add of the VG.

        Raises:
            LVMException: If the operation failed.
        """
        retcode = lvm_vg_add_tag(self.handle, tag.encode('ascii'))
        if retcode != 0:
            raise self._create_exception()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from a VG.

        This function requires calling lvm_vg_write() to commit the change to disk.
        After successfully removing a tag, use lvm_vg_write() to commit the
        new VG to disk.  Upon failure, retry the operation or release the VG handle
        with lvm_vg_close().

        Args:
            tag(str): Tag to remove from VG.

        Raises:
            LVMException: If the operation failed.
        """
        retcode = lvm_vg_remove_tag(self.handle, tag.encode('ascii'))
        if retcode != 0:
            raise self._create_exception()

    def write(self) -> None:
        """Write a VG to disk.

        This function commits the Volume Group object referenced by the VG handle
        to disk. Upon failure, retry the operation and/or release the VG handle
        with lvm_vg_close().

        Raises:
            LVMException: If the operation failed.
        """
        retcode = lvm_vg_write(self.handle)
        if retcode != 0:
            raise self._create_exception()

    def remove(self):
        """Remove a VG from the system.

        This function removes a Volume Group object in memory, and requires
        calling lvm_vg_write() to commit the removal to disk.

        Raises:
            LVMException: If the operation failed.
        """
        retcode = lvm_vg_remove(self.handle)
        if retcode != 0:
            raise self._create_exception()

    def extend(self, device: str) -> None:
        """Extend a VG by adding a device.

        Args:
            device(str): Absolute pathname of device to add to VG.

        Raises:
            LVMException: If the operation failed.
        """
        retcode = lvm_vg_extend(self.handle, device.encode('ascii'))
        if retcode != 0:
            raise self._create_exception()

    def reduce(self, device: str) -> None:
        """Reduce a VG by removing an unused device.

        Args:
            device(str): Name of device to remove from VG.

        Raises:
            LVMException: If the operation failed.
        """
        retcode = lvm_vg_reduce(self.handle, device.encode('ascii'))
        if retcode != 0:
            raise self._create_exception()

    @property
    def physical_volumes(self) -> List[PhysicalVolume]:
        """The physical volumes for this volume group

        Returns:
            List[PhysicalVolume]: The physical volumes
        """
        pv_list: List[PhysicalVolume] = []
        pv_handles = lvm_vg_list_pvs(self.handle)
        if not dm_list_empty(pv_handles):
            pv_handle = dm_list_first(pv_handles)
            while pv_handle:
                ptr = cast(pv_handle, lvm_pv_list_p)
                volume = PhysicalVolume(ptr.contents.pv)
                pv_list.append(volume)
                if dm_list_end(pv_handles, pv_handle):
                    # end of linked list
                    break
                pv_handle = dm_list_next(pv_handles, pv_handle)

        return pv_list

    @property
    def logical_volumes(self) -> List[LogicalVolume]:
        """The logical volumes for this volume group.

        Returns:
            List[LogicalVolume]: The list of logical volumes.
        """
        lv_list: List[LogicalVolume] = []
        lv_handles = lvm_vg_list_lvs(self.handle)
        if not dm_list_empty(lv_handles):
            lv_handle = dm_list_first(lv_handles)
            while lv_handle:
                ptr = cast(lv_handle, lvm_lv_list_p)
                volume = LogicalVolume(ptr.contents.lv, self._create_exception)
                lv_list.append(volume)
                if dm_list_end(lv_handles, lv_handle):
                    # end of linked list
                    break
                lv_handle = dm_list_next(lv_handles, lv_handle)

        return lv_list

    def lv_from_name(self, name: str) -> LogicalVolume:
        """Lookup an LV handle in a VG by the LV name.

        Args:
            name(str): The name of the logical volume.

        Raises:
            LVMException: If the volume could not be obtained.

        Returns:
            LogicalVolume: The logical volume
        """
        handle = lvm_lv_from_name(self.handle, name)
        if not handle:
            raise self._create_exception()
        return LogicalVolume(handle, self._create_exception)

    def create_lv_linear(self, name: str, size: int) -> LogicalVolume:
        """Create a linear logical volume.

        This function commits the change to disk and does _not_ require calling
        write.

        Args:
            name(str): Name of logical volume to create.
            size(int): Size of logical volume in extents.

        Raises:
            LVMException: If the operation was unsuccessful

        Returns:
            LogicalVolume: The logical volume created
        """
        handle = lvm_vg_create_lv_linear(
            self.handle,
            name.encode('ascii'),
            c_ulonglong(size)
        )
        if not handle:
            raise self._create_exception()
        return LogicalVolume(handle, self._create_exception)


class VolumeGroupContextManager(metaclass=ABCMeta):
    """The volume group context manager"""

    def __init__(
            self,
            lvm_handle: Any,
            create_exception: Callable[[], LVMException],
            name: str
    ) -> None:
        """The volume group context manager

        Args:
            lvm_handle (Any): The lvm handle
            create_exception (Callable[[], LVMException]): An exception factory
            name (str): The volume group name.
        """
        self.lvm_handle = lvm_handle
        self._create_exception = create_exception
        self.name = name
        self.handle: Optional[Any] = None

    @abstractmethod
    def __enter__(self) -> VolumeGroupInstance:
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.handle:
            retcode = lvm_vg_close(self.handle)
            if retcode != 0:
                raise self._create_exception()


class VolumeGroupOpen(VolumeGroupContextManager):
    """The volume group context manager for an existing volume group"""

    def __init__(
            self,
            lvm_handle: Any,
            create_exception: Callable[[], LVMException],
            name: str,
            mode: str = "r",
            flags: int = 0
    ) -> None:
        """The volume group context manager for an existing volume group

        Args:
            lvm_handle (Any): The lvm handle
            create_exception (Callable[[], LVMException]): An exception factory
            name (str): The volume group name
            mode (str, optional): The mode in which to open the volume group.
                Defaults to "r".
            flags (int, optional): The flags to use. Defaults to 0.
        """
        super().__init__(lvm_handle, create_exception, name)
        self.mode = mode
        self.flags = flags
        self.handle: Optional[Any] = None

    def __enter__(self) -> VolumeGroupInstance:
        self.handle = lvm_vg_open(
            self.lvm_handle,
            self.name.encode('ascii'),
            self.mode.encode('ascii'),
            self.flags
        )
        if not self.handle:
            raise self._create_exception()
        return VolumeGroupInstance(self.handle, self._create_exception)


class VolumeGroupCreate(VolumeGroupContextManager):
    """The volume group context manager for creating a new volume group"""

    def __enter__(self) -> VolumeGroupInstance:
        self.handle = lvm_vg_create(
            self.lvm_handle,
            self.name.encode('ascii')
        )
        if not self.handle:
            raise self._create_exception()
        return VolumeGroupInstance(self.handle, self._create_exception)
