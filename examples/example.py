"""Example"""

import sys
sys.path.append('/home/BHDGSYSTEMATIC.COM/rblackbourn/Development/Scratch/python/lvm-explore')

from jetblack_lvm2 import LVM

with LVM() as lvm:
    vg_names = lvm.list_vg_names()
    print(vg_names)

    print(lvm.errno)
    print(lvm.errmsg)
    print(lvm.version)

    for pv in lvm.physical_volumes:
        print(pv.name)

    vg_uuids = lvm.list_vg_uuids()
    print(vg_uuids)

    for uuid in vg_uuids:
        print(lvm.vgname_from_pvid(uuid))

    lvm.scan()

    with lvm.vg_open(vg_names[0]) as vg:
        print(vg.name)
        print(vg.is_clustered)

        for pv in vg.physical_volumes:
            print(pv.name)
            print(pv.uuid)

        for lv in vg.logical_volumes:
            print(lv.name)
            print(lv.size)

print("done")