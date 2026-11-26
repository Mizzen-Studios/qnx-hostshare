# HostShare — owner-ready draft, 26 November 2026 (not submitted)

HostShare lets developers edit inputs on a host and read updated bytes in QNX 8
without rebuilding the guest image for each edit. It is a bounded read-only
virtio-9p resource manager, not a writable or production filesystem.

The latest native verification passed on the original f0test export and /mnt/host
mountpoint in QNX 8 x86_64 under QEMU. A cold boot mounted the readonly share
passively before the first host serial command. The one-shot boot hook produced
a live, validated server PID; no serial mount fallback or transparent restart
was used.

Default conformance passed 288 independent byte-read cases, four directory
pagination/rewind scans across 189 entries, five denied mutation opens and all
seven historical file checksums. Expected bytes were independently computed on
the host. A host edit became visible through the same readonly export without
rebuilding, while a denied guest write left host bytes unchanged.

A real client previously built with the existing licensed QNX SDK was copied
from the mounted share. Its complete 9,488 bytes were read back from QNX and
matched the host artifact before execution. The client read the boot-mounted
input, returned exit status 0 and produced exactly 94 independently read-back
output bytes. Client output was isolated from driver serial logs rather than
accepted by loosely filtering them. Normal TERM detach then passed: the driver
reported detach and return code 0, the process was absent, and the exported
file path was no longer present.

The offline preparation created a new private derived boot disk using the
already installed licensed SDK tools, with sufficient boot capacity for the
driver and one-shot hook. The original IFS, system/data partition bytes, driver
and SDK client stayed unchanged. Earlier failed attempts and their raw evidence
remain preserved. The final run consumed the sole additional authorized attempt;
no further guest execution is authorized.

Separately, 97 HOST tests and portable C/syntax checks pass. These exercise
source/artifact bindings, namespace guards, strict output verification, explicit
acceptance gates and detach cleanup on failure; HOST CI is not native acceptance.

This is scoped acceptance for the exact tested QNX 8 x86_64 QEMU topology and
artifact/source bindings. It does not establish physical-hardware coverage,
performance, writable/general filesystem support, active-DMA/death safety, MSI-X
or production readiness, and does not accept unrelated feature work.

Exact native results and artifact/evidence bindings:
[26 November final3 result](../boot-loop-20261126/final3/RESULT.md).
The superseded draft is retained separately as
[historical text](OWNER_DEVPOST_DRAFT_HISTORICAL_THROUGH_20261126_PRE_FINAL3.md).

This is a local owner draft only. No Devpost submission, YouTube change, upload,
visibility change or outreach was performed. No new installation, login or spend.
