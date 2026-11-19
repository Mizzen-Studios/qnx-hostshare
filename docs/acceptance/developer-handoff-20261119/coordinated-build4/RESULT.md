# Build4 — fresh custom native conformance PASS; default transfer BLOCKED

Source a57bd240a7575397caa3f0021b6ca2e11043c225.
Fresh licensed SDK ELF SHA256:
36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75.
Actual recipe, complete source/headers/ELF hashes and SDK rc0 retained. Existing
reviewed stock IFS/disk REUSED, not newly built. No old ELF promotion.

## Actual QNX custom PASS

custom/mount.txt proves MOUNT_PREFLIGHT BEGIN/PASS, nondefault dev-inputs tag,
/mnt/dev-inputs READONLY attachment, actual cat/list rc0. Absent synthetic
ancestors work; existing ancestor/collision/error guard negatives are HOST-tested.

custom/conformance.txt has 288 independently verified byte slices: two clients,
empty/one-byte/4KiB/1MiB, offsets0/1/3999/4000/4095/4096/1048575/1048576/1048581,
counts0/1/17/257 including EOF/beyondEOF and partial reads. Four exact directory
scans (rewind, repeated clients) cover187 root entries spanning multiple4000-byte
9p replies. Five mutation opens denied: WRONLY/RDWR/TRUNC/APPEND/CREATE.
Runner verified unchanged whole-corpus hashes immediately after denials.
independent-host-recheck.json reruns the byte/directory/denial oracle from raw
transcript and checks all187 files against independently constructed expected
bytes after the intentional hello edit/restore. No guest self-certified hash.

Seven QNX checksum reads independently match pinned host checksums/sizes,
including Unicode/nested inputs. custom/host-edit.txt proves edited host bytes
visible in QNX without rebuild (~0.144s observed), QEMU export still readonly.
custom/readonly.txt proves guest shell overwrite denied with host bytes intact.
custom/normal-stop.txt proves normal detach/exit0. No server-death lane added;
legacy EIO diagnostic unchanged, no active-DMA claim.

## Default compatibility is NOT accepted

Only after custom passed, the planned default f0test,/mnt/host attempt ran.
default/receipt.json records serial copy timeout COPY_6912, before byte-exact
ELF transfer/probe/mount. No default native conformance claim. Stopped immediately;
no retry. Historical defaults and strict-host CLI compatibility still pass, but
current-source default-native compatibility remains BLOCKED_TRANSFER.

## Caps, cleanup and HOST

One exclusive lease held continuously SDK->SDK stop/reap->custom->default;
SDK1GiB, native512MiB; host2GiB/swap0 CPU100 nice15 smp1 TCG256 reserve64MiB.
Actual measured peaks and raw pins in memory-summary.json files; no OOM/cap
breach. SDK and both own QEMU reaped; final lease FREE and pending queue empty.
IFS/disk hashes unchanged after each native attempt. No image build/install,
CAN/EDU/C6 change, spend, media or upload. HOST38 tests + portable strict C PASS.

This establishes bounded CUSTOM native acceptance, not full item4 acceptance or
production filesystem readiness. Parent reviews remaining default-transfer gate
before deciding further native work/item5 ordering. All earlier failures intact.
