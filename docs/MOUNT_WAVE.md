# Read-only mount wave

This follow-up preserves the original `790e9b2` F1/F2 receipt. New native results
belong only to `docs/acceptance/mount-20261113/`; source code and host tests alone
are not native acceptance.

Ordered gates: N1 PCI configuration line without routing changes, then installed
MSI-X API if needed; N2 real QNX resource-manager mount with cat/listing; N3 POSIX
checksums through the mount over seven synthetic files; optional N4 host edit
observed through a new open without rebuild. If N1 fails both modes, the previously
recorded own-device PIRQ workaround is authorized for subsequent mount gates and
must not be described as default routing.

Implementation is deliberately bounded: single dispatch thread, eight-entry
virtqueue with one outstanding request, 4096-byte 9P message size, per-open fids,
16 path components, regular files/directories only. No writes, symlink following,
production concurrency or general filesystem support is claimed. Native checksum
code reads with fopen/fread, independently compared with host POSIX cksum. Hashes
of source, ELF and unchanged prebuilt images bind the fresh receipts. The existing
historical IFS/data disk are not claimed stock.
