# QNX attempt1 — BLOCKED: boot filesystem ENOSPC

Granted prepare1 ran once from cleanc0a9b2e. Actual reviewed source8/driver ELF,
stock IFS/raw disk and unused overlay/run paths were verified before admission.
No SDK build, probe, reboot, fallback or second QNX launch occurred.

## Exact failure, not another serial framing defect

The slot guard passed. Initialization plus512 data chunks received exact nonce/
sequence/end-offset acks, last seq512/end32768. Command seq513 targeted32832,
but actual guest printf printed "write: No space left on device". Its &&-guarded
ack correctly did not run. The20s wait expired and both helper/runner emitted
FAILED terminals. No inference from acknowledgments was promoted to integrity.

HOST-only retained-event review confirms this guest storage error; it is NOT
missing CSI normalization, a quiet timeout needing more sleep or a900s budget
exhaustion. Source MBR shows type177 /boot partition11341824 bytes, beside
78893056-byte system and64110592-byte data partitions. This proves the boot
partition allocation, not its complete live free-space accounting. ENOSPC is
observed; exact pre-run free blocks/inodes and partial guest file size were not
queried, so those are not fabricated. Existing stock IFS bytes are10910404.

Driver byte readback did not start. No chmod, hook installation, flush/unmount,
prepared pin or boot-mounted server occurred. Failed overlay is retained PRIVATE,
hashed in independent-review.json and explicitly INELIGIBLE for verify. There is
no boot-overlay-pin.json. No default conformance or developer-loop native PASS.
The real SDK client build and old custom conformance evidence remain unchanged.

## Bounds / cleanup

Exclusive canonical lease, CPU100%, nice15, host2GiB/swap0/reserve64MiB,
guest512MiB, smp1/TCG256. Peak544362496 bytes; max/oom/oom_kill0. Owned QEMU
exited0/reaped, runner exited1. Final independent process/queue checks empty,
lease FREE. Stock IFS/raw disk hashes unchanged after guest shutdown.

Raw events, original unsanitized receipt and failed overlay remain private and
byte-pinned. Public JSON is explicitly path-sanitized, not relabelled raw evidence;
serial copy commands are redacted. Previous SDK/default/custom failures untouched.

## Remaining budget and next decision — NO retry performed

QNX attempts used1 of2; remaining1 is HELD for a separate parent decision.
A blind repeat/coldboot of this unprepared overlay cannot establish boot mounting.
Host-only diagnosis suggests moving boot payload provisioning OFFLINE into a new
reviewed derived artifact using existing licensed filesystem tooling, if available:
that could preserve the final coldboot for actual verification without consuming
a third QNX boot. Tool availability, filesystem construction/preservation, new
artifact trust and parent authority must be independently established FIRST.
No offline image change or new SDK admission has been attempted or assumed.
Simply putting the driver in /data is not yet a fix: stock /boot/onboot runs
before the stock /data mount. Do not alter startup mounts/restart behavior blindly.
