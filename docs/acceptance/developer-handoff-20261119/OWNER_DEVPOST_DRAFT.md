# Local owner draft — not submitted

HostShare lets developers edit inputs on the host and read updated bytes in
QNX 8 without rebuilding the guest image. It is a bounded read-only virtio-9p
resource manager, not a writable or production filesystem.

Fresh current-source QNX evidence proves a configurable export named dev-inputs
mounted at /mnt/dev-inputs:288 independent offset/partial-read/EOF byte cases,
four directory pagination/rewind scans across187 entries, five denied mutation
opens and seven file checksums. Expected bytes were independently computed on
the host, not certified by a guest-generated hash. Host edits became visible
through the same QEMU readonly export without an image rebuild; denied guest
mutations preserved the host corpus. Normal detach also passed.

HOST38 tests separately validate configuration bounds, source/artifact bindings,
namespace safety guards and negative controls. Existing symlink/non-directory
ancestors, collisions and permission errors remain denied; absent QNX synthetic
namespace prefixes are supported. Host CI is not native acceptance.

Acceptance is partial: original f0test,/mnt/host defaults remain in the code and
host compatibility tests, but CURRENT-SOURCE DEFAULT NATIVE COMPATIBILITY IS
BLOCKED by serial ELF-transfer timeout COPY_6912, before probe or mount. We do
not claim full item4 acceptance. Historical default-route and ESRCH3 server-death
receipts apply only to their exact old source/ELF pins; all failures remain
preserved. No speed/latency, active-DMA safety, MSI-X or production-readiness claim.

Fresh build used the existing licensed SDK and reused reviewed stock artifacts;
no new guest image was built. Exact current proof and remaining blocker:
coordinated-build4/RESULT.md.

No Devpost, YouTube, visibility, upload or outreach action taken. £0.
