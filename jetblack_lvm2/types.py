"""Conversion"""

from ctypes import Structure, Union, POINTER, c_char_p, c_uint32, c_int32

# lvm_t
#
# This is the base handle that is needed to open and create objects such as
# volume groups and logical volumes.  In addition, this handle provides a
# context for error handling information, saving any error number (see
# lvm_errno()) and error message (see lvm_errmsg()) that any function may
# generate.
class lvm(Structure):
    pass

lvm_t = POINTER(lvm)

# vg_t
#
# The volume group object is a central object in the library, and can be
# either a read-only object or a read-write object depending on the function
# used to obtain the object handle. For example, lvm_vg_create() always
# returns a read/write handle, while lvm_vg_open() has a "mode" argument
# to define the read/write mode of the handle.
class volume_group(Structure):
    pass

vg_t = POINTER(volume_group)

# pv_t
#
# This physical volume object is bound to a vg_t and has the same
# read/write mode as the vg_t.  Changes will be written to disk
# when the vg_t gets committed to disk by calling lvm_vg_write().
class physical_volume(Structure):
    pass

pv_t = POINTER(physical_volume)

# lv_t
#
# This logical volume object is bound to a vg_t and has the same
# read/write mode as the vg_t.  Changes will be written to disk
# when the vg_t gets committed to disk by calling lvm_vg_write().
class logical_volume(Structure):
    pass

lv_t = POINTER(logical_volume)

# A list consists of a list head plus elements.
# Each element has 'next' and 'previous' pointers.
# The list head's pointers point to the first and the last element.
class dm_list(Structure):
    pass

dm_list._fields_ = [('p', POINTER(dm_list)), ('n', POINTER(dm_list))]

dm_list_t = POINTER(dm_list)

# String list.
#
# This string list contains read-only strings.
# Lists of these structures are returned by functions such as
# lvm_list_vg_names() and lvm_list_vg_uuids().
class lvm_str_list(Structure):
    _fields_ = [
        ('list', dm_list),
        ('str', c_char_p),
    ]

lvm_str_list_p = POINTER(lvm_str_list)

class lvm_pv_list(Structure):
    _fields_ = [
        ('list', dm_list),
        ('pv', pv_t),
    ]

lvm_pv_list_t = lvm_pv_list
lvm_pv_list_p = POINTER(lvm_pv_list)

class lvm_lv_list(Structure):
    _fields_ = [
        ('list', dm_list),
        ('lv', lv_t),
    ]

lvm_lv_list_t = lvm_lv_list
lvm_lv_list_p = POINTER(lvm_lv_list)

class _lvm_property_value_union(Union):
    _fields_ = [
        ('string', c_char_p),
        ('integer', c_uint32),
        ('signed_integer', c_int32)
    ]

class lvm_property_value(Structure):
    _fields_ = [
        ('is_settable', c_uint32, 1),
        ('is_string', c_uint32, 1),
        ('is_integer', c_uint32, 1),
        ('is_valid', c_uint32, 1),
        ('is_signed', c_uint32, 1),
        ('padding', c_uint32, 27),
        ('value', _lvm_property_value_union)
    ]
    _anonymous_ = ('value',)

lvm_property_value_p = POINTER(lvm_property_value)
