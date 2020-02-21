"""LVM"""

from __future__ import annotations
from ctypes import cast, c_uint64
from typing import Any, List, Optional

from .bindings import (
    lvm_init,
    lvm_quit,
    lvm_config_reload,
    lvm_config_override,
    lvm_config_find_bool,
    lvm_list_vg_names,
    lvm_list_vg_uuids,
    lvm_errno,
    lvm_errmsg,
    lvm_library_get_version,
    lvm_vgname_from_pvid,
    lvm_vgname_from_device,
    lvm_vg_name_validate,
    lvm_scan,
    lvm_list_pvs,
    lvm_list_pvs_free,
    lvm_pv_create,
    lvm_pv_remove,
    dm_list_empty,
    dm_list_first,
    dm_list_next,
    dm_list_end
)
from .types import lvm_pv_list_p

from .exceptions import LVMException
from .physical_volume import PhysicalVolume
from .utils import _dm_list_to_str_list
from .volume_group import (
    VolumeGroupContextManager,
    VolumeGroupCreate,
    VolumeGroupOpen
)


class LVMInstance:
    """An lvm instance"""

    def __init__(self, handle: Any) -> None:
        """An lvm instance.

        Args:
            handle (Any): The handle
        """
        self.handle = handle

    def list_vg_names(self) -> List[str]:
        """Return the list of volume group names.

        The memory allocated for the list is tied to the lvm_t handle and will be
        released when lvm_quit() is called.

        NOTE: This function normally does not scan devices in the system for LVM
        metadata.  To scan the system, use lvm_scan().

        Returns:
            List[str]: A list with entries of type struct lvm_str_list,
                containing the VG name strings of the Volume Groups known to the
                system. NULL is returned if unable to allocate memory. An empty
                list (verify with dm_list_empty) is returned if no VGs exist on
                the system.
        """
        vg_names = lvm_list_vg_names(self.handle)
        if not bool(vg_names):
            raise LVMException(self.errno, self.errmsg)
        return _dm_list_to_str_list(vg_names)

    def list_vg_uuids(self) -> List[str]:
        """Return the list of volume group uuids.

        The memory allocated for the list is tied to the lvm_t handle and will be
        released when lvm_quit() is called.

        NOTE: This function normally does not scan devices in the system for LVM
        metadata.  To scan the system, use lvm_scan().

        Returns:
            List[str]: A list with entries of type struct lvm_str_list, containing
                the VG UUID strings of the Volume Groups known to the system.
                NULL is returned if unable to allocate memory. An empty list
                (verify with dm_list_empty) is returned if no VGs exist on the
                system.
        """
        vg_uuids = lvm_list_vg_uuids(self.handle)
        if not bool(vg_uuids):
            raise LVMException(self.errno, self.errmsg)
        return _dm_list_to_str_list(vg_uuids)

    @property
    def errno(self) -> int:
        """Return stored error no describing last LVM API error.

        Users of LVM should use lvm_errno to determine the details of a any
        failure of the last call.  A basic success or fail is always returned by
        every function, either by returning a 0 or -1, or a non-NULL / NULL.
        If a function has failed, lvm_errno may be used to get a more specific
        error code describing the failure.  In this way, lvm_errno may be used
        after every function call, even after a 'get' function call that simply
        returns a value.

        Returns:
            int: An errno value describing the last LVM error.
        """
        return lvm_errno(self.handle)

    @property
    def errmsg(self) -> str:
        """Return stored error message describing last LVM error.

        Returns:
            str: An error string describing the last LVM error.
        """
        msg = lvm_errmsg(self.handle)
        return msg.decode('iso-8859-1')

    def _create_exception(self) -> LVMException:
        return LVMException(self.errno, self.errmsg)

    @property
    def version(self) -> str:
        """Retrieve the library version.

        The library version is the same format as the full LVM version.
        The format is as follows:
           LVM_MAJOR.LVM_MINOR.LVM_PATCHLEVEL(LVM_LIBAPI)[-LVM_RELEASE]
        An application wishing to determine compatibility with a particular version
        of the library should check at least the LVM_MAJOR, LVM_MINOR, and
        LVM_LIBAPI numbers.  For example, assume the full LVM version is
        2.02.50(1)-1.  The application should verify the "2.02" and the "(1)".

        Returns:
            A string describing the library version.: [description]
        """
        return lvm_library_get_version(self.handle).decode('ascii')

    def vgname_from_pvid(self, pvid: str) -> Optional[str]:
        """Return the volume group name given a PV UUID

        The memory allocated for the name is tied to the lvm_t handle and will be
        released when lvm_quit() is called.

        Args:
            pvid (str): The PV uuid

        Returns:
            str: The volume group name for the given PV UUID. NULL is returned
                if the PV UUID is not associated with a volume group.
        """
        name = lvm_vgname_from_pvid(self.handle, pvid.encode('ascii'))
        return name.decode('ascii') if name else None

    def vgname_from_device(self, device: str) -> Optional[str]:
        """Return the volume group name given a device name

        Args:
            device (str): The device name

        Returns:
            Optional[str]: The volume group name for the given device name.
                NULL is returned if the device is not an LVM device.
        """
        name = lvm_vgname_from_device(self.handle, device.encode('ascii'))
        return name.decode('ascii') if name else None

    def scan(self) -> None:
        """Scan all devices on the system for VGs and LVM metadata.

        Raises:
            LVMException: If the scan failed.
        """
        result = lvm_scan(self.handle)
        if result != 0:
            raise LVMException(self.errno, self.errmsg)

    def vg_open(self, name: str, mode: str = "r", flags: int = 0) -> VolumeGroupContextManager:
        """Open a volume group

        Args:
            name (str): The name
            mode (str, optional): The mode. Defaults to "r".
            flags (int, optional): The flags. Defaults to 0.

        Returns:
            VolumeGroupContextManager: A volume group context.
        """
        return VolumeGroupOpen(self.handle, self._create_exception, name, mode, flags)

    def vg_create(self, name: str) -> VolumeGroupContextManager:
        """Create a volume group

        Args:
            name (str): The name of the volume group

        Returns:
            VolumeGroupContextManager: The volume group context
        """
        return VolumeGroupCreate(self.handle, self._create_exception, name)

    def vg_name_validate(self, name: str) -> bool:
        """Validate a volume group name

        Args:
            name (str): The name

        Returns:
            bool: True if this is a valid name.
        """
        retcode = lvm_vg_name_validate(self.handle, name.encode('ascii'))
        return retcode == 0

    @property
    def physical_volumes(self) -> List[PhysicalVolume]:
        """The physical volumes for this volume group

        Returns:
            List[PhysicalVolume]: The physical volumes.
        """
        pv_list: List[PhysicalVolume] = []
        handles = lvm_list_pvs(self.handle)
        if not dm_list_empty(handles):
            handle = dm_list_first(handles)
            while handle:
                ptr = cast(handle, lvm_pv_list_p)
                physical_volume = PhysicalVolume(ptr.contents.pv)
                pv_list.append(physical_volume)
                if dm_list_end(handles, handle):
                    # end of linked list
                    break
                handle = dm_list_next(handles, handle)

        lvm_list_pvs_free(handles)

        return pv_list

    def reload_config(self) -> None:
        """Reload the original configuration from the system directory.

        This function should be used when any LVM configuration changes in the LVM
        system_dir or by another lvm_config* function, and the change is needed by
        the application.

        Raises:
            LVMException: If the reload fails
        """
        retcode = lvm_config_reload(self.handle)
        if retcode != 0:
            raise self._create_exception()

    def config_override(self, value: str) -> None:
        """Override the LVM configuration with a configuration string.

        Args:
            value (str): LVM configuration string to apply.  See the lvm.conf
                file man page for the format of the config string.

        Raises:
            LVMException: If the reload fails
        """
        retcode = lvm_config_override(self.handle, value.encode('ascii'))
        if retcode != 0:
            raise self._create_exception()

    def config_find_bool(self, config_path: str, fail: bool) -> bool:
        """Find a boolean value in the LVM configuration.

        Args:
            config_path (str): A path in LVM configuration
            fail (bool): Value to return if the path is not found.

        Returns:
            bool: boolean value for 'config_path' (success) or the value of 'fail' (error)
        """
        retval = lvm_config_find_bool(
            self.handle, config_path, 1 if fail else 0)
        return retval == 1

    def pv_create(self, name: str, size) -> None:
        """Create a physical volume.

        Args:
            name (str): The physical volume name.
            size ([type]): Size of physical volume, 0 = use all available.

        Raises:
            LVMException: If the physical volume could not be created
        """
        retcode = lvm_pv_create(
            self.handle, name.encode('ascii'), c_uint64(size))
        if retcode != 0:
            raise self._create_exception()

    def pv_remove(self, name: str) -> None:
        """Remove a physical volume.

        Args:
            name (str): The physical volume name.

        Raises:
            LVMException: If the physical volume could not be created
        """
        retcode = lvm_pv_remove(self.handle, name.encode('ascii'))
        if retcode != 0:
            raise self._create_exception()


class LVM:
    """The lvm context manager"""

    def __init__(self, path: Optional[str] = None) -> None:
        """Create an lvm context

        Args:
            path (Optional[str], optional): The path to the config. Defaults to None.
        """
        self.path = path
        self.handle: Optional[Any] = None

    def __enter__(self) -> LVMInstance:
        bytes_path = self.path.encode('ascii') if self.path else None
        self.handle = lvm_init(bytes_path)
        return LVMInstance(self.handle)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.handle:
            lvm_quit(self.handle)
