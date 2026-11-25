# Offline-derived boot admission (HOST only)

Parent-approved replacement provisioning route; final QNX attempt remains HELD.
No native preparation receipt is fabricated. tools/offline_boot.py validates
hostshare.offline-derived.v1 and a separate hostshare.offline-overlay.v1 runtime
binding, not hostshare.boot-overlay.v1. Runner --offline-original requires verify,
conformance, actual client and no --stock-pin; all passive/default runtime gates
remain unchanged. HS_DISK points to reviewed derived raw disk; HS_IFS stays exact
original. A fresh overlay backs that derived disk. Every pin/evidence byte is
rechecked before QEMU; pins establish identity, not independent build authority.

Original historical IFS/disk pins are immutable. Exact file set/modes/content,
preserved system/data partition bytes, original MBR signature/types/active flags/
nonoverlap/bounds, licensed tool hashes, IPL/build-source/evidence bindings and
at least1MiB nominal metadata spare capacity must pass. Builder requests extra2MiB
via num_sectors=*4096 with required optional reset and explicit modes.
The QNX6 inspector is strictly read-only;512MiB disk/16MiB object/128MiB read
budget/depth8/32directories cap; constructor failure closes file. It is not fsck,
ACL/allocation integrity validation or runtime free-space proof. Original partial
inspector was privately preserved before reviewed changes. SDK/image/license
bytes remain private. Host negatives do not substitute for native acceptance.
