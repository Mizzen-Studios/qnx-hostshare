# Fresh HostShare recording — 15 November 2026

One new stock QNX8 run captured from source
71fa9a15d69192dcc5b90caa71a8f1046d3cb509, clean at launch. No project code
change, SDK build/install, IRQ workaround, MSI-X retry or second guest run.

## Completed media (private owner-review draft only)

**160.000 seconds,1920x1080,H.264,1280 frames/8fps,zero audio streams**;
8,792,279 bytes. All nine final stills visually inspected; the entire 131-line
actual displayed terminal pool passed privacy and coverage checks. The frame map
includes1280 source-time entries, raw event IDs and1858 explicit editorial
omissions. Seven host/guest checksum results are visible together in still-077.

MP4 SHA256:9f723544c49fee11bc97be0e25d2fb172cf13bec806b954e3c29c7da6fd0a9b1.
Server-reported uploaded asset digest and size match. Repository verified PRIVATE;
release446242471 verified DRAFT with published_at=null, asset751804087 uploaded.
[Private draft asset — authenticated access](https://github.com/Mizzen-Studios/qnx-hostshare/releases/download/untagged-1d313ece153dd20b42a7/demo-video.mp4).
See private-draft-release.json and receipt.json. No existing release/asset was
overwritten. No public publication or submission occurred. MP4 stays external to
Git; raw timestamped capture, original receipt/memory and helpers remain private
outside the repository with exact locations/hashes bound in the receipt.

## Actual native observations

- Default-route IRQ11/INTx probe, byte-exact native ELF copy and readonly
  mount/list/cat passed; no qtest/PIRQ rewriting.
- All seven independent host/guest POSIX checksums passed: hello, empty, one,
  4KiB, 1MiB, nested leaf and Unicode. Write rejected; host edit became visible
  without rebuild in **0.15093365591019392 seconds** in THIS run.
- Actual POSIX read blocked in explicitly paused read handler before RPC/DMA;
  SIGKILL server wait137; client n=-1, **ESRCH errno3**, client wait3,
  elapsed **1.161165 seconds**. Fresh server remounted; hello and 1MiB checksum
  2572415250/1048576 passed; cooperative detach passed.
- Owner accepts ESRCH as QNX MsgSend server-death contract. Raw unchanged runner
  still reports BLOCKED_GATE against its superseded EIO-only assertion, with
  midread passed=false. This original failure is preserved, not translated to
  EIO5 or relabelled as an original machine PASS. The separate receipt explicitly
  evaluates the reviewed ESRCH contract. No active-DMA crash-safety claim.

## Bounds and cleanup

HOST2GiB, guest512MiB, TCG256MiB, CPU100%, nice15, smp1, swap0, reserve64MiB;
peak608628736B, no measured reserve/max/OOM/kill events. Original source/ELF/IFS/
disk hashes and every memory sample are bound by receipt.json. Snapshot disk and
IFS hashes unchanged. Guest exited0, stopped/reaped; zeroQEMU and canonical lease
FREE verified at the receipt's cleanup timestamp. Parent notified immediately;
that is a historical cleanup statement, not ownership of subsequent CAN work.
No more QEMU or lease operations for rendering.

## Authenticity, timing and privacy

The outside-repository tap profiled unchanged suite drain() calls, saving newly
arriving actual serial bytes with wall/monotonic timestamps. Actual host cksum
and post-edit cat stdout were captured in the same new run. No historical logs,
expected-result terminal text or synthetic result cards substitute for footage.
Title/source context and captions are separately labelled. Later faithful
terminal rendering is allowed; video is prominently labelled EDITED TIMING /
IDLE CUTS, not realtime. Holds and time compression map to raw event timestamps
in the frame map. The own-ELF transfer interval and its console octal/hex echoes
are omitted from displayed footage. Repetitive IRQ debug and checksum command
echo/completion-marker lines are also omitted, explicitly labelled in the video
and individually indexed by raw event ID in the frame map; actual checksum and
error/result lines remain unchanged. A 1.4x source-clock traversal within each
segment then holds its final view; the exact per-frame clock is retained.
No licensed binary, raw transfer bytes,
large memory log or MP4 is committed to Git. Personal host paths, addresses and
hostnames are redacted from displayed text; original private streams stay
external and are SHA256-bound for inspection.

Copied per-stage logs and corpus-before.json are new actual-run evidence.
Raw original native receipt, timed streams and all memory samples remain under
workspace .openclaw/tmp/hostshare-recording-20261115/; their exact relative
locations and hashes are in receipt.json. Historical acceptance bytes unchanged.
Only an authorized PRIVATE DRAFT release asset may hold the video; no public
release, visibility change, recording audio/voice/music, contacts, spend, CAN or
C6 changes. MSI-X unproven; read-only, not a production filesystem, no latency
or active-DMA recovery guarantees.
