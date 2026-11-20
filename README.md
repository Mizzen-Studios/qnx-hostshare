# QNX HostShare — edit on the host, read in QNX

A bounded read-only virtio-9p host-folder driver for QNX 8. Edit development inputs without rebuilding the guest image. Apache-2.0; not a production or writable filesystem. [Watch the demo](https://youtu.be/O0SA7W6gFyE).

## Five-minute HOST ONLY judge path

No QNX hardware, SDK, image or QEMU required. From the repository root with Python 3 and a C compiler:

1. Read [the judge evidence path](docs/JUDGES.md): actual host-edit/read, checksums and denied writes.
2. Run the reference checks locally:

~~~sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
mkdir -p .local
cc -std=c11 -Wall -Wextra -Werror -pedantic -Icore core/transport.c core/protocol.c tests/test_core.c -o .local/test-core
.local/test-core
~~~

These exercise HOST models, not QNX PCI interrupts, mounted I/O or native crash recovery.

## Status — 20 November 2026

| Area | Evidence-backed state |
|---|---|
| Repository | PUBLIC; older private/visibility-pending wording is stale. No visibility change performed here. |
| HOST regression | 39 Python tests passed; portable C checks are separate, not native proof. |
| Current-source native | Partial acceptance at 3a338a03: custom dev-inputs / /mnt/dev-inputs conformance PASS. |
| Default native compatibility | BLOCKED at serial COPY_6912 before verified ELF/mount; not full item4 acceptance. |
| Historical HA contract | Pending-read server death returns ESRCH3, then fresh remount; never translate to EIO5. Not active-DMA crash safety. |
| Limits | MSI-X unproven; no production-readiness, safety or latency guarantee. |

[Current exact contract](docs/CURRENT_CONTRACT.md) · [Custom conformance evidence](docs/acceptance/developer-handoff-20261119/coordinated-build4/RESULT.md) · [Tool contracts](tools/README.md) · [Dated history](docs/HISTORY.md) · [Path preservation policy](docs/PATHS.md).

**Demo in QEMU; not a safety or latency claim.** Historical default-route receipts retain their original source/ELF pins, not current-source default acceptance. [Licensed reproduction](docs/RUN_NATIVE.md) is separate and not authorized by this HOST path. No SDK, secret, image or binary is distributed.
