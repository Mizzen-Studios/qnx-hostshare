# Coordinated fresh build/native attempt — 19 November 22:17 UTC

Source tip eed53d2309cada1254f7958ee5e12d3ad6b97866. Fresh licensed SDK
build succeeded rc0, ELF581f24f16ddd53d14ef2c1dc3a47b988067bf391a3623b1fa4b3f2ba44317e39.
Actual recipe/current source/header hashes retained; no old ELF promotion.
SDK stopped/reaped rc0 before native. One exclusive flock held across complete
SDK->stop/reap->native attempt; no concurrent guest; no new image build.

## Confirmed root cause / actual blocker

mount-parent.txt records REAL QNX: mkdir -p /mnt returns1, "Function not
implemented"; ls /mnt returns "No such file or directory". This confirms /mnt
is absent in the reviewed stock image and cannot be created as a real directory
in its synthetic root namespace. The earlier preflight's real-parent requirement
was incompatible with historical QNX resource-manager attachment to /mnt/host.
The runner's new diagnostic gate correctly stops before transfer/device access;
it cannot repair a synthetic namespace using mkdir. Empty earlier mount log is
therefore explained by silent missing-parent return before startup logging,
not insufficient sleep, background-shell syntax or an IRQ problem.

No blind retry. Custom mount/conformance, host-edit and default native cases
NOT_RUN; native acceptance remains false. SDK build PASS is NOT native PASS.
Native512MiB; SDK1024MiB; host2GiB/no swap CPU100 nice15 smp1 TCG256 reserve64.
Measured peaks are in the two memory summaries; no OOM/cap events.
Existing reviewed stock IFS/disk reused unchanged; receipt includes after hashes.
All own QEMU stopped/reaped; owner exited and released lease. No pending queue.

## Smallest next architectural fix (NOT implemented/tested natively here)

Permit absent synthetic mount ancestors while checking every EXISTING ancestor
is an ordinary directory, rejecting symlink/other errors and target collisions.
Do NOT require mkdir on QNX root. Existing validated /mnt/... grammar remains;
resource-manager resmgr_attach registers the absent path as the historical
working adapter did. Add exact host mock regressions for absent prefix+symlink
and current-source fresh SDK/native proof under another parent-coordinated lease.
No cap change, image build or native failure-lane work is needed by that fix.
Parent authorization is needed for another native attempt; this granted one ends.
