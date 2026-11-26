# 26 November HOST/offline milestone — QNX attempt3 HELD

Owner08:30 approved three host-first fixes and ONE existing licensed Linux
builder rebuild. All three are implemented; no QNX boot occurred. Historical
25Nov attempts1 and2 remain failures, preserved byte-for-byte. No full PASS.

## Changes and actual tests

- Client stdout/stderr goes to a fresh nonce-specific private guest file. The
  runner checks unique nonce-bound exit status and exact complete file bytes via
  strict hex readback. Driver serial output remains raw and unfiltered; no loose
  stripping/subsequence acceptance. Existing client ELF is unchanged.
- Hook PID write uses builtin echo, no printf. Before signaling, runner requires
  a digits-only PID greater than1 and successful kill-0, plus hook launch marker.
- Normal TERM now requires signal success, process absence, exactly one detach
  marker and absent exported hello path. No serial mount/restart fallback.
-93 HOST tests pass, including actual compiled client redirected output,
  missing/duplicate/nonzero status, truncated/extra/interleaved output negatives,
  missing/invalid/stale/live PID, actual TERM/reaper/path removal and negative
  detach/path/process gates. Strict C core/config/conformance and syntax pass.
  Implementation a2fa9fb; fresh-CI scratch correction446cae7. CI45784447057
  SUCCESS on exact446cae752f2b3c9a363727a2d8c782d5cca41732 before SDK execution.
  Initial CI45784355526 failed missing scratch setup; preserved, then corrected.

## Actual OFFLINE builtin proof (not QNX runtime)

Licensed dumpifs extracted the exact pinned original IFS. Listing binds bin/sh
and bin/ksh to /proc/boot/ksh, file offset0x195000, size0x43000. Host independently
compared the full extracted shell with that IFS slice. Shell SHA:
8f1ac35bf71cb58587052b7e07ed89935f736b0d565aa8f170b40e57cc1ba334.
Actual extracted mount_fs.sh invokes ksh /boot/onboot before /system mounting.
The shell's command table entry0x40650 binds echo to executable handler0x75a0;
print entry0x406c0 binds the SAME handler. Thus early echo is built into the
actual image shell, not inferred from Linux PATH. Empty-PATH host hook execution
also passes, but is a separate HOST test. See shell-builtin-proof.json for exact
static bindings. SDK shell binary/listing remain private, not in Git.

## New artifact and independent verification

Private .local/offline26/derived.raw:156480000 bytes, SHA
1f1fc2beb7638bb6a587cd01075210a6e7cc0cf86a69f21fa09854f5ab6a4993.
Original external/embedded IFS unchanged:
68bbe1b49a9b723c09d152773ee323ec6ab576eb29de933bfe3f08fdae21c753.
Driver unchanged:36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75.
Client unchanged:171b6fae32f6f62118fb2fa90eb0f2275ba3fbc6184abdc9273076fdfa04cb5e.
New285-byte hook:281ad0f979be7101260f8dff65db48fb0d2cb50c9efb57d2fca581fbbb947c41.

New mandatory explicit-mode build used only existing mkqnx6fsimg + diskimage,
with exact previously reviewed tool/IPL hashes checked BEFORE execution.
No compiler/mkifs/new SDK/install/login/network. Exact file set: original IFS
mode0644, hsd0755, onboot0644. Boot26320 sectors/13475840 bytes;
2433024 nominal metadata-spare bytes, not an allocator/runtime guarantee.
System/data partition lengths and hashes equal originals. Full source/tool/IPL,
helper/runner hashes and partition proof: host-offline-receipt.json.
Private provenance .local/offline26/offline-derived.json SHA
9204dc8686cfe3eed60e00c599683d031b784c695766902e94facc90d56f4e4e;
strict offline_boot.validate and validate_overlay rerun successfully.
Fresh unused runtime.qcow2 SHA
2af4aa0643820cccb3cb8fa84baf796292689c5c82747e555483942c45830cb8.
This is offline-derived provenance, NEVER a native-prepared pin.

## Builder caps and cleanup

One serialized existing Linux SDK session, canonical exclusive native-test.lock.
CPU100%, nice15, host memory2GiB/swap0/reserve64MiB, guest1024MiB/smp1,
TCG256, NIC none.586 memory samples; peak1194885120 bytes, no max/OOM events.
ACPI shutdown accepted, owner/QEMU exit0/reaped, no QEMU, no pending queue,
independent flock FREE. Receipt .local/sdkBuild26/receipt.json. Prior derived
raw and both failed overlays rehashed unchanged; original bases untouched.
C6 STOPPED, CAN HOLD. No other repo/media/publication/settings/spend action.

## Single planned command — NOT RUN; parent preflight/grant required

From repository root (same existing driver source manifest):

~~~sh
HS_LOCK=/home/ubuntu/qnx-host/native-test.lock \
HS_ELF=/home/ubuntu/qnx-host/guest/shared/hostshare-handoff-20261119-build4/build/qnx_hostshare \
HS_BUILD_MANIFEST="$PWD/.local/developer-handoff-20261119-build4/build-source-hashes.json" \
HS_IFS=/home/ubuntu/qnx-host/guest/shared/edu-stock-control-1024-20261113/stock-output/ifs.bin \
HS_DISK="$PWD/.local/offline26/derived.raw" \
sh tools/run-native-suite.sh --image-kind stock --conformance \
 --run-id boot-a-final3-20261126 --boot-stage verify \
 --boot-overlay "$PWD/.local/offline26/runtime.qcow2" \
 --boot-pin "$PWD/.local/offline26/offline-overlay.json" \
 --offline-original /home/ubuntu/qnx-host/guest/shared/edu-stock-control-1024-20261113/stock-output/disk-qemu \
 --dev-app /home/ubuntu/qnx-host/guest/shared/hs-dev-client-20261125/source/.local/qnx-client/loop-app \
 --dev-manifest /home/ubuntu/qnx-host/guest/shared/hs-dev-client-20261125/source/.local/qnx-client/build.json
~~~

QNX runtime remains512MiB/smp1/TCG256/network none under same host caps/lease.
Must observe passive MOUNT READY before first TX, then PID guard, full default
conformance, client exact pre-exec readback/output/exit and normal TERM detach.
Any failure consumes the sole additional attempt; no hidden retry/reboot.

## Parent-review HOST correction (attempt3 still HELD)

The first milestone omitted explicit requested final gates and could skip normal
detach on a client/readback exception. Corrected HOST-only: a try/finally context
attempts normal detach once a boot PID is validated, even on conformance/client/
readback/assertion failures. Stop command has a30-second bound; cleanup errors
are retained separately under normal_stop, while the original exception remains
the primary failure. A successful cleanup cannot convert failure to PASS.
Requested conformance, developer-loop, PIDguard and normal-detach now each require
explicit boolean True in final gates.97 HOST tests pass, including primary
assertion identity preserved through successful/failed cleanup, no unsafe detach
without validated PID and missing/false/nonboolean gate rejection.

No hook, image, private disk/overlay or offline admission pin changed. The original
construction receipt is immutable historical evidence of its runner source. New
runner/helper binding is recorded separately in runner-review-binding.json;
planned single native command and artifact pins above remain unchanged.
