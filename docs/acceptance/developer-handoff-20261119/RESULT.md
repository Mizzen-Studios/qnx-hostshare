> Latest20Nov: [Single default run BLOCKED by missing guest sha256sum; no ELF execution](../default-final-20261120/RESULT.md). Custom PASS remains unchanged; full native acceptance still partial.

> Latest22:43UTC: [Build4 custom native conformance PASS; default serial transfer BLOCKED](coordinated-build4/RESULT.md). Earlier failures below are preserved historical attempts, not the latest custom status.

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

## First current-source native attempt (retained failure)

custom-first/probe.txt: actual QNX rc0, nondefault dev-inputs device tag,
default IRQ11/no routing rewrite, seven replies and byte-exact41-byte probe.
custom-first/mount.txt: after the old fixed2s delay, mount log was still empty
and path absent. Runner failed the mount/list gate and stopped/reaped QEMU;
no conformance case or host-edit PASS claimed. Peak601235456, no OOM/cap events,
IFS/disk hashes unchanged. Raw per-drain memory retained privately with hash in
custom-first/memory-summary.json; original failure receipt unchanged.
A separate fresh attempt uses bounded10s startup allowance; no cap increase,
reserve bypass, new ELF, image build or failure-lane extension.

Second custom attempt (custom-second) again passed actual nondefault-tag probe
but mount log stayed empty/path absent after10s. Peak599982080; clean cleanup,
no cap/OOM events, artifacts unchanged. This disproves assuming a2s-only issue.
Native conformance and custom mounted host-edit remain NOT_ACCEPTED. A separate
default-route compatibility attempt captures pidin state to identify whether the
mount process runs; no SDK/image/resource retry is involved.

## Final native status: NOT_ACCEPTED / blocked

Default compatibility attempt default-first failed serial transfer at COPY_7040
(timeout20s), before ELF byte verification, probe or mount. Peak438329344;
QEMU stopped/reaped rc0, no OOM/cap events, reviewed image hashes unchanged.
No default native compatibility claim and no third custom retry.

Fresh current-source compilation and two real nondefault-tag byte-exact probes
are proven. Mounted custom/default paths, all288 offset cases, four pagination/
rewind scans, five denials and host-edit visibility on the NEW ELF are NOT_RUN
or blocked by native mount/transfer failures, NOT native PASS. Prior Nov13/15
read-only mount/checksum/edit/ESRCH evidence remains valid only for its exact old
source/ELF pins. Do not proceed to item5 recording on this new implementation
until the parent reviews these blockers; do not imply acceptance from host CI.
