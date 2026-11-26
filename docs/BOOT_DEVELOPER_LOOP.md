> 26Nov HOST/offline milestone: isolated exact client output, builtin-echo PID hook,
> strict PID/normal-TERM process/path gates;93 HOST tests pass. New private disk
> rebuilt with existing licensed SDK; original IFS/driver/client unchanged.
> Additional owner-authorized QNX attempt3 **HELD, NOT_RUN** pending parent review.
> Prior two native failures remain preserved; no full PASS. [Exact proof](acceptance/boot-loop-20261126/HOST_RESULT.md).

> Latest25Nov final2: passive boot mount/default conformance observed; raw suite FAIL.
> Client byte-exact readback and exit0 observed, but IRQ logs broke contiguous-output
> assertion; hook also failed early printf/PID write. Normal detach NOT_RUN.
> **2/2 QNX attempts consumed;0 remaining. Native STOP.** [Exact result](acceptance/boot-loop-20261125/final2/RESULT.md).
> Earlier dated readiness statements below are historical, not current authority.

> Latest25Nov22:11UTC: granted prepare1 FAILED on actual guest /boot ENOSPC
> after512 acknowledged data chunks. No hook/seal/prepared pin; failed overlay
> must NOT be cold-boot verified. [Exact failure/cleanup](acceptance/boot-loop-20261125/prepare1/RESULT.md).
> QNX attempts used1 of2; remaining1 HELD. SDK client build remains valid.

> Latest25Nov22:06UTC: the separately admitted existing Linux SDK builder
> produced the real source-bound QNX client successfully and was stopped/reaped.
> [Actual build/cleanup proof](acceptance/boot-loop-20261125/client-sdk-build/RESULT.md).
> Client provisioning is READY; QNX runtime boots remain0 of2, awaiting parent
> prepare1 grant. The direct ARM-host SDK remains absent; no install was performed.

# Feature A — boot mount + build-host/run-QNX loop (25 November)

**HOST implementation only. No new native acceptance or execution authority.**
81 Python HOST tests pass; portable strict C is separate. Earlier custom native
PASS and every default/SDK failure remain unchanged. No restart/recovery feature
is added: the boot hook starts the server once, refuses a duplicate within that
boot, and never respawns a dead or stopped server.

## Actual stock integration, not serial-triggered mounting

Read-only inspection of the already reviewed stock IFS found its real startup
flow: PCI is started before filesystem mounting, and mount_fs.sh executes
/boot/onboot with ksh when that file exists. The old driver ELF needs libpci.so.3.0,
libc.so.6 and libgcc_s.so.1; all three are represented in that IFS. This is
prerequisite inspection, **not proof the new hook booted**.

The new bounded route uses two explicitly coordinated runtime boots:

1. **prepare:** create a private qcow2 overlay of the independently pinned stock
   raw disk. Do not overwrite /boot/hsd or any existing /boot/onboot. Stage the
   exact source-bound driver and one-shot script, independently read them back
   from QNX and compare every byte BEFORE making the ELF executable. Unmount
   /boot successfully to flush it, stop/reap QEMU, then hash/pin the sealed overlay.
2. **verify:** reject any overlay/base/driver/hook/config pin mismatch before
   launch. Cold boot that same private overlay. Passively observe MOUNT READY
   before sending ANY host serial command—no --mount command or second PCI probe
   is used to fake boot mounting. Then run the real default mounted conformance
   and developer-loop gates. Stop the boot server explicitly and reap the guest.

Base IFS and raw disk remain immutable/hash-checked, not rebuilt. The private
writable overlay is modified only for this boot experiment and never committed.
The exported development folder remains QEMU readonly and the driver read-only.
Existing symlink/non-directory/collision/path guards remain; no IRQ rewrite,
MSI-X fallback, SDK install/login, transparent restart or writable filesystem mode.

## Integrity without a nonexistent guest hash applet

The HS-local serial_readback.py adapter retains nonce/sequence/end-offset acks,
64-byte blocks, <=512-byte commands, no resend after uncertainty and one900s
transfer deadline. It does NOT call the absent toybox sha256sum or infer file
integrity from acknowledgments. It invokes actual guest od, requires its successful
exit, parses strictly framed hex, compares ALL read-back bytes with the host ELF,
and computes host SHA256 from those guest bytes. Missing od, bad/duplicate frames,
truncation, corrupted bytes or deadline exhaustion fail closed before execution.
The immutable canonical CAN helper/vendor pin is not rewritten or reclassified.

Private append-only raw events are kept outside Git; public receipts redact ELF
copy commands/readback. Boot artifacts, ELF, overlay, SDK and licenses stay out
of Git. Boot overlay pins bind byte identity, not general artifact trust: they
are admitted only after a reviewed successful preparation receipt.

## Build on the configured SDK host

On a Linux host with an EXISTING licensed QNX8 SDK (or the existing serialized
capped SDK builder), from a checkout/staging copy of these sources:

~~~sh
python3 tools/dev-loop.py --sdk-env /home/qnx/qnx800/qnxsdp-env.sh \
  --out "$PWD/.local/feature-a-client"
~~~

This compiles examples/developer-loop.c with qcc for QNX x86_64 and records the
source/ELF hashes, compiler path/hash, SDK environment hash, exact command and
build log. It does not start QEMU or install anything. A compiler failure is not
a native result. Never manufacture a manifest for an old unrelated ELF.

On this ARM Gateway the direct /home/qnx SDK path is absent; the existing licensed
SDK is inside the capped Linux builder. A real QNX client build therefore needs
**separate parent-coordinated SDK provisioning authority/lease**, before runtime
verification, or a reviewed external client build from that installed SDK. No SDK
builder was started during this HOST milestone. Parent explicitly admitted that Linux build guest outside the TWO QNX runtime
attempts. It has now completed and been reaped; no hidden QNX boot occurred.

For a no-SDK HOST-only demonstration, --host-test uses the real host C compiler.
Its HOST_ONLY manifest is explicitly rejected by the native runner.

## Exact planned runtime commands — NOT executed / not authority

Keep the common HS_LOCK, HS_ELF, HS_BUILD_MANIFEST, HS_IFS and HS_DISK settings
from RUN_NATIVE.md. The existing reviewed build4 driver ELF is still source-bound:
36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75.
No driver rebuild is required; core/native C and headers are unchanged.

Use unused paths/run IDs. After a separate parent grant for attempt1:

~~~sh
mkdir -p .local/boot-a-20261125
sh tools/run-native-suite.sh --image-kind stock \
  --run-id boot-a-prepare-20261125 --boot-stage prepare \
  --boot-overlay "$PWD/.local/boot-a-20261125/boot.qcow2"
~~~

Only after the successful prepared-overlay receipt is independently reviewed,
and a separate parent grant for attempt2, with real QNX client build artifacts:

~~~sh
sh tools/run-native-suite.sh --image-kind stock --conformance \
  --run-id boot-a-verify-20261125 --boot-stage verify \
  --boot-overlay "$PWD/.local/boot-a-20261125/boot.qcow2" \
  --boot-pin "$PWD/.local/user-runs/boot-a-prepare-20261125/boot-overlay-pin.json" \
  --dev-app "$HS_DEV_APP" --dev-manifest "$HS_DEV_MANIFEST"
~~~

No automatic second launch, retry, resubmission or reboot. Any new blocker ends
that attempt and is reported honestly. The tools do not grant extra attempts.

Expected native gates, currently **NOT_RUN**: passive default boot attachment;
288 independently checked offset/partial/EOF cases; four pagination/rewind scans
(root corpus189 entries with the two developer-loop files); five denied mutation
opens with unchanged hashes; seven checksums; host edit visible; normal detach.
The host-built client is read through the boot-mounted share, copied to /data,
read back byte-for-byte before execution, then must print the exact expected
boot-mounted input bytes. This is NOT in-place mmap/exec support on the 9p mount.

## Bounds and HOST proof

Shared lease; CPU100%, nice15, smp1/TCG256, host2GiB/swap0/reserve64MiB,
native512MiB. Startup180s TOTAL, transfer900s including first readback (<=60s),
independent driver readback60s, hook transfer120s, conformance240s, client readback
60s. Other commands/checksums keep explicit bounds. Each SDK and runtime guest
must be stopped/reaped before another; no cap raises or reserve bypass.

HOST proof uses actual /bin/sh, cc and od, never a disguised QNX PASS: complete
51,528-byte acknowledged transfer + actual readback, corruption/missing-od/replay/
duplicate/deadline negatives; real compiled client reads expected input bytes;
its HOST_ONLY build cannot pass native admission; one-shot hook starts only once
in a host mock; overlay/backing/hash/symlink/collision negatives; the actual
runner readback callback succeeds on host bytes and rejects a missing file.
See acceptance/boot-loop-20261125/HOST_RESULT.md for the exact milestone.
