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

Preview the folder handoff without any SDK files or guest:

~~~sh
python3 tools/preview-handoff.py --tag dev-inputs --mountpoint /mnt/dev-inputs
~~~

This prints an **unvalidated template**, not a launch command or native PASS. A tag is simply the shared folder label that QEMU and QNX must match. Real operation still requires [strict external-file validation](tools/README.md) and separate native authority.

## Evidence at a glance

| Evidence route | State |
|---|---|
| Recorded journey | Bounded source-bound observations; not current live health. |
| HOST checks | 81 Python tests passed; portable C separate; not native acceptance. |
| Native / reproduction scope | Custom native conformance PASS; latest default run BLOCKED by missing guest sha256sum before execution. [Exact status](STATUS.md). |
| Repository | PUBLIC; earlier private-state wording is stale. |

**Demo in QEMU; not a safety or latency claim.** Historical default-route receipts retain their original source/ELF pins, not current-source default acceptance. [Licensed reproduction](docs/RUN_NATIVE.md) is separate and not authorized by this HOST path. No SDK, secret, image or binary is distributed.

## New feature A — HOST-ready, boot preparation BLOCKED

One-shot boot mounting plus a source-bound build-host/run-QNX loop is implemented
and HOST-tested. It uses a private stock-disk overlay and exact guest byte readback,
not the missing sha256sum applet or transfer ACK inference. **No new native PASS**:
SDK-client build PASS; prepare1 hit actual guest /boot ENOSPC before hook
installation. One of two QNX attempts is used; final attempt HELD for parent
review, not an automatic retry. [Exact failure](docs/acceptance/boot-loop-20261125/prepare1/RESULT.md). No transparent restart. [Design and exact planned commands](docs/BOOT_DEVELOPER_LOOP.md).

## Why QNX

The QNX resource manager exposes read-only host files via virtio-9p, PCI and interrupt/pulse completion. Per-open read state and explicit denied mutations turn an exported development folder into bounded ordinary QNX I/O.

## How we used AI

Developed with an AI coding agent under human direction: implementation, tests, documentation and evidence review were AI-assisted. HOST checks and recorded native receipts support only their stated scope; AI output is not independent human learner validation, attestation or QNX acceptance.
