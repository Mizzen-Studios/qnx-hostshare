# Inspect HostShare without QNX

**Problem:** editing a host-side test input should not require rebuilding and
transferring a guest image. HostShare lets a QNX 8 application read that host
export through a read-only mount. QEMU exports the folder; the project provides
the bounded QNX integration. No writable/general-purpose filesystem claim.

## Watch, then inspect actual bytes

- [Public demo](https://youtu.be/O0SA7W6gFyE): externally hosted; playback and
  narration were not revalidated in this update.
- [Host edit/read transcript](acceptance/recording-20261115/host-edit.txt):
  host content changed and guest cat saw it without rebuild. Timing is an
  observation, not a latency guarantee.
- [One 1MiB checksum](acceptance/recording-20261115/checksum-1MiB.txt),
  [seven-file host corpus](acceptance/recording-20261115/corpus-before.json),
  [denied write](acceptance/recording-20261115/readonly.txt), and
  [recorded result and limits](acceptance/recording-20261115/RESULT.md).
- [Exact current contract and immutable source/ELF/image pins](CURRENT_CONTRACT.md).
  Default IRQ11, no qtest/PIRQ rewrite; MSI-X unproven (PCI_ERR_IRQ_CFG).
- [Actual pending-read ESRCH3](acceptance/recording-20261115/midread-result.txt)
  and [fresh remount](acceptance/recording-20261115/remount.txt). The read handler
  was paused **before RPC/DMA**: not active-DMA crash safety. Original EIO-only
  failure receipts remain failures; no errno translation or relabelled PASS.

These are recorded observations, **not execution in your browser**. You need no
QNX licence, SDK, binary, guest image or QEMU to read them or run host checks.

## Run host checks only

From the repository root with Python3, a POSIX shell, cksum and a C compiler:

~~~sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
mkdir -p .local
cc -std=c11 -Wall -Wextra -Werror -pedantic -Icore core/transport.c core/protocol.c tests/test_core.c -o .local/test-core
.local/test-core
~~~

Host tests exercise models, the portable C core, fixture consistency, launch
preflight guards and documentation recipes. They do **not** run or prove the
QNX resource manager, PCI interrupts or native crash recovery.

## Optional licensed reproduction

[Exact prerequisites, fresh ELF/source manifest and ordinary stock route](RUN_NATIVE.md).
Existing licensed SDK and trusted external images are required, not downloaded
by the launcher. Use one shared native lock and stop/reap SDK/guest work first.
The ordinary route omits --midread and tests data/host edit/cooperative stop,
not server death. The unchanged historical --midread diagnostic knowingly
exits1 on the accepted ESRCH3 observation; keep it separate from first use.

No new native execution, media or acceptance claim is made by this judge path.
