# Final QNX attempt2/2 — FAILED; native STOP

One explicitly granted final coldboot from clean1bcbe18. No retry, extra boot,
SDK execution, serial mount fallback or restart. **Budget exhausted:2/2 used,0 left.**
Raw runner receipt remains FAIL; no full feature-A/default/developer-loop PASS.

## Actual useful native observations

Independent private RX/TX event review proves MOUNT READY /mnt/host READONLY
arrived BEFORE the first host serial transmission (echo HS_SUITE_BOOT_READY).
No host mount/probe command triggered it. Mount/list and seven exact corpus
checksums passed. Real default conformance passed288 byte cases,4 directory scans
with189 root entries,5 denied opens; host corpus unchanged. Host edit/read and
readonly write denial passed. This is actual QNX8/TCG512MiB observation, not HOST.

The actual9488-byte SDK client171b6fae... copied from the boot-mounted share to
/data and was read back EXACTLY before chmod/execution. Independent private-frame
parsing recovers all9488 bytes and its exact ELF hash. Actual client printed BEGIN,
expected input line and END in order, then LOOP_RC=0. However driver IRQ_PULSE
logs interleaved those lines; runner demanded one contiguous output substring and
raised RuntimeError('host-built client did not read boot-mounted input'). That
assertion is stricter than actual observed client behavior. Do NOT rewrite the
original FAIL receipt or infer a full suite PASS from this review.

## Separate real hook defect — do not hide behind harness diagnosis

Before /system mount the hook attempted external printf and guest reported:
/boot/onboot[6]: printf: cannot execute - No such file or directory
The server already started and mounted, but PID-file write failed; exact PID-file
contents were not queried and are not invented. HOSTSHARE_BOOT_LAUNCHED did not
complete. The PID-based one-start guard and later normal TERM/detach acceptance
are therefore NOT established. Normal-stop command was NOT_RUN because runner
exited at client-output assertion. QEMU termination/reaping is not normal server
detach. No hook repair/rebuild/reboot was attempted under exhausted authority.

A future separately authorized correction would need early-boot-safe builtin PID
writing and framed/ordered client-output validation tolerant only of precisely
recognized diagnostic lines, with negative HOST tests. This is diagnosis, not
permission for another native attempt, pin rewrite or transparent recovery.

## Exact invocation and preserved artifacts

sh tools/run-native-suite.sh --image-kind stock --conformance
--run-id boot-a-final-20261125 --boot-stage verify
--boot-overlay .local/offline25/runtime.qcow2
--boot-pin .local/offline25/offline-overlay.json
--offline-original <pinned-original-stock-raw-disk>
--dev-app <actual-SDK-client> --dev-manifest <its-original-build.json>

Original HS_IFS68bbe1b4..., derived HS_DISK9452f062..., old driver36478be0...
and original source-binding manifest were verified. Distinct offline provenance
validated before launch; no fake native-prepared pin. Private raw receipt/serial/
append-only RX/TX/memory under .local/user-runs/boot-a-final-20261125. Adjacent
receipt-sanitized.json explicitly preserves raw FAIL and separately reports review.
No ELF/readback bytes, SDK/images/licenses or private command paths committed.

Runtime overlay now USED, SHA256d0cc0f555884c8d32bb554fb50c61b841d5a8e6f8780022cba2dec62c9b4204d.
Its pristine offline-overlay pin intentionally no longer validates; never reuse
this used overlay as an unrun artifact. Derived raw/IFS remain unchanged; attempt1
failed overlay and historical pins preserved.

## Bounds and final cleanup

CPU100%, nice15, host2GiB/swap0/reserve64MiB, QNX512MiB/smp1/TCG256, networknone.
Peak344244224 bytes; max/oom/oom_kill0. Owned QEMU terminated exit0/reaped;
runner exit1. Independent process check empty, pending queue empty, lease FREE.
No record/public posting/SDK install/login/spend/CAN/EDU/C6/other-repo changes.
Native remains STOPPED with0 authorized attempts remaining.
