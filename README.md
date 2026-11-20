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

## Evidence at a glance

| Evidence route | State |
|---|---|
| Recorded journey | Bounded source-bound observations; not current live health. |
| HOST checks | 39 Python tests passed; portable C separate; not native acceptance. |
| Native / reproduction scope | [Complete current status and limits](STATUS.md); separate licensed setup required. |
| Repository | PUBLIC; earlier private-state wording is stale. |

**Demo in QEMU; not a safety or latency claim.** Historical default-route receipts retain their original source/ELF pins, not current-source default acceptance. [Licensed reproduction](docs/RUN_NATIVE.md) is separate and not authorized by this HOST path. No SDK, secret, image or binary is distributed.

## Why QNX

The QNX resource manager exposes read-only host files via virtio-9p, PCI and interrupt/pulse completion. Per-open read state and explicit denied mutations turn an exported development folder into bounded ordinary QNX I/O.

## How we used AI

Developed with an AI coding agent under human direction: implementation, tests, documentation and evidence review were AI-assisted. HOST checks and recorded native receipts support only their stated scope; AI output is not independent human learner validation, attestation or QNX acceptance.
