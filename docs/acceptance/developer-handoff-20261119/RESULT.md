# Developer handoff — 19 November 2026

Implementation and HOST checks delivered. Native outcome will be recorded below
only after the original monitored SDK owner has stopped/reaped and fresh native
runs have returned; a successful cross-compile is not native acceptance.

## Scope and evidence layout

- Configurable tag and /mnt/... mountpoint with old f0test,/mnt/host defaults.
- Preflight validates safe bounds, no traversal/symlink export, complete current
  source/ELF bindings, strict stock pins; no image build or writable mode.
- HOST: 36 Python tests including strict C CLI validation and actual compiled
  POSIX client's writable-host negative control. Portable strict C transport/
  protocol groups PASS, including unsupported mutation RPC negatives.
- Planned native gate: 288 independent offset/read byte comparisons, four
  directory scans/rewind over 187 root entries (multi-reply pagination), five
  denied mutation opens, whole-corpus unchanged hashes, seven checksums, host
  edit visible without rebuild. Two separate runs: custom tag/path and defaults.
- Schema: build owner hostshare.handoff-build.v1; native runner retains its
  existing receipt layout with additive handoff and conformance objects.
- build1-owner-failed.json preserves an orchestration TypeError before compile,
  not a QNX/compiler failure. SDK stopped/reaped before corrected owner attempt.
- build2-recipe.sh, build2.txt, build-source-hashes.json bind actual installed
  qcc recipe/current C+headers and fresh ELF. No old ELF promoted.
- reused-stock.json independently verifies the reviewed Nov13 external stock
  IFS/disk hashes against upstream-handoff.json. REUSED, not newly built.

Historical evidence/raw failures/pins unchanged. Legacy --midread remains EIO-only;
no failure-lane extension or errno mapping, no active-DMA kill. C6 stopped; no
CAN/EDU edits, install/login/licence, spend, media, upload or external submission.
Owner draft: OWNER_DEVPOST_DRAFT.md (local only).

## Actual fresh SDK build

Corrected owner build2 completed rc0 with installed licensed qcc, guest1GiB,
CPU100%, host2GiB/no swap, nice15, smp1/TCG256. 361 monitored samples; maximum
cgroup memory.peak 990400512 bytes, below2GiB minus reserve64. No OOM events.
Fresh ELF SHA256 b7787467609ed75570ba791fb41e0ea440dba2459420e1f3d418922a5cebcc3c.
See sdk-owner.json, sdk-memory.jsonl and sdk-stop.txt: ACPI shutdown completed,
owner rc0, stopped/reaped=true, remaining QEMU empty before native launch.
Original queue job1795115002311520643 completed; no queue timeout/retry occurred.
