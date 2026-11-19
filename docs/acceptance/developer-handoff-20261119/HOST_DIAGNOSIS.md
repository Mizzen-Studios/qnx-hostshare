# Host-only follow-up diagnosis

No SDK, QEMU, native lease or queue action performed for this follow-up.
Original failed receipts and their manifest remain unchanged.

## Identified implementation/runner mismatch

The new mountpoint_available() runs BEFORE HOSTSHARE NATIVE BEGIN and before
queue/device initialization. It requires every parent (including /mnt) to
lstat as an ordinary directory. Its original ancestor-failure branch returned1
without printing anything. main returned2 immediately. Thus an absent /mnt
produces exactly an empty redirected log and absent mount, regardless of2s/10s
wait. The runner prepared only /data/hostshare, not /mnt. The historical adapter
had no parent-lstat prerequisite: QNX resource-manager attachment can register
/mnt/host without an underlying real parent directory.

This is a concrete silent-failure defect and missing runner prerequisite.
The retained serial transcripts do NOT contain ls/stat of /mnt or the server's
wait status, so absence of /mnt on those exact boots is a strong causal
hypothesis, NOT conclusively observed native fact. A hung lstat or another
pre-main issue cannot be excluded from old logs. Increasing sleeps was not a
root-cause fix. CLI parsing for the exact custom invocation passes strict-host
C tests; identical historical shell background grammar worked on the same
reviewed image. No evidence supports changing IRQs or caps.

## Small safe fix

- Runner prepares the validated mountpoint's parent before ELF transfer,
  records mkdir status and ls -ld; aborts on failure.
- Preserve strict collision/symlink rejection (do not simply remove lstat).
- C emits unbuffered MOUNT_PREFLIGHT BEGIN/PASS and explicit parent path/errno
  or non-directory diagnostic. This makes any remaining preflight failure
  observable instead of silent.
- Host regression compiles the ACTUAL extracted C preflight with mocked lstat:
  missing parent fails with diagnostic; ordinary parent passes; symlink parent
  and existing target remain denied. Runner ordering/status regression added.
- 38 Python tests pass; portable C/protocol strict checks pass. HOST ONLY.

Changed native C/header means the old freshly-built ELF is now stale for current
source. No manifest regeneration to promote it. A later native verification
requires a NEW source-bound licensed compile, after parent allocates the lease.

## Coordinated native plan (NOT started)

1. Parent grants sole lease; recheck foreign QEMU/pending jobs/headroom.
2. One bounded SDK compile with fresh staged source/output/run IDs, retain recipe
   and hashes, monitored reserve64; stop/reap before native. No image build.
3. Reuse the already independently pinned reviewed Nov13 stock IFS/disk.
4. Custom tag/path run: parent receipt must show existing /mnt; expect explicit
   preflight BEGIN/PASS then READY. If failure, capture log plus pidin and actual
   server exit status before cleanup; stop, diagnose, no blind repeat.
5. Only after mount works, require288 byte cases, pagination/rewind, denied opens,
   unchanged corpus hashes and host-edit visibility; then default compatibility
   under a separate fresh run ID. No server-death lane.
6. All paths stop/reap own guests and free lease; cap/reserve breach ends native.

Native acceptance remains false until those actual runs pass. Parent owns
lease coordination and item5 ordering.
