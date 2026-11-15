# Exact bounded native launch (no routing rewrite)

Installation-specific QNX8/QEMU readonly feasibility suite, not a production
filesystem or SDK installer. Historical results and failures stay immutable.
The earlier stock-OOM dependency block is superseded **only for this repeat** by
EDU be712b27 stock-build/boot handoff. SSH remains unverified (stock sshd fault);
this runner uses serial only, without login/network/platform repair.

## Prerequisites (not provisioned by launcher)

- Configured Linux host: Python3, QEMU x86_64, POSIX cksum, systemd user manager,
  cgroupv2, nice, and read access to this public GitHub repository.
- Existing licensed QNX8 SDP with mkqnximage for a judge-built stock BIOS/pc
  image (512MiB RAM, 1 CPU, serial root shell); stockbuild is a prerequisite,
  not performed by this launcher. Existing source rebuild also requires qcc; proprietary headers/libraries,
  ELF, IFS and disks remain outside Git. Launcher performs no downloads,
  installation, login or image build.
- /absolute/path/to/shared-native-test.lock writable; no other QEMU/SDK running.
- External hash-matching executable and raw base disk/IFS below. Missing inputs
  fail before QEMU. Source mismatch fails; do not substitute an older ELF.
- Guest image has a serial root shell, /data, ksh printf, od, cat, ls and pidin.
  No CANOPY boot marker is assumed. Both authorized images are BIOS/pc.

## Stock-generation prerequisite — recorded recipe, not a new run

The exact generator invocation is recorded in
[EDU JUDGES.md at a26962acd737f57bd6d3199384ccfa9cbd63f0f6](https://github.com/Mizzen-Studios/qnx-edu-kit/blob/a26962acd737f57bd6d3199384ccfa9cbd63f0f6/docs/JUDGES.md).
Its [1GiB builder success](https://github.com/Mizzen-Studios/qnx-edu-kit/blob/a26962acd737f57bd6d3199384ccfa9cbd63f0f6/docs/acceptance/stock-retry-20261113/RESULT.md)
and [512MiB builder failure](https://github.com/Mizzen-Studios/qnx-edu-kit/blob/a26962acd737f57bd6d3199384ccfa9cbd63f0f6/docs/acceptance/stock-20261113/NOTES.md)
establish the observed resource boundary. Use an existing licensed SDP8.0
builder with **at least 1GiB RAM**; target RAM remains 512MiB/one CPU. This is
not a universal minimum guarantee or authorization to start a builder here.

Inside that existing licensed environment, with HS_SDP_ENV pointing to its
existing environment file and a fresh project directory:

~~~sh
. "$HS_SDP_ENV"
mkdir stock-hostshare-project
cd stock-hostshare-project
mkqnximage --type=qemu --arch=x86_64 --ram=512M --cpu=1 --ssh-ident=none --build
~~~

Only the generator invocation is reused from EDU's recorded stock-build evidence;
**do not add its EDU device snippet to HostShare**. This HostShare change is
documentation only: no new build, native validation, SDK install/login or image
claim. Stop/reap the builder before native launch. Independently pin your trusted
stock output using --stock-pin below; existing historical artifact pins and
acceptance bytes are unchanged.

## Cold-reader exact commands on the configured host

Replace every /absolute/path/to/... placeholder with an actual local path.
### Direct judge-built stock setup — no historical image required

Complete the stockbuild prerequisite and create stock-pin.json using the command
below before launch. From a directory without qnx-hostshare:

~~~sh
git clone https://github.com/Mizzen-Studios/qnx-hostshare.git
cd qnx-hostshare
export HS_LOCK=/absolute/path/to/shared-native-test.lock
export HS_ELF=/absolute/path/to/qnx_hostshare
export HS_BUILD_MANIFEST="$PWD/docs/acceptance/stock-repeat-20261113/build-source-hashes.json"
export HS_IFS=/absolute/path/to/stock-output/ifs.bin
export HS_DISK=/absolute/path/to/stock-output/disk-qemu
~~~

Each run-id must be fresh. Outputs default to .local/user-runs/<run-id>; the
corpus is new at .local/corpus-<run-id>. Optional HS_RECEIPT_BASE is an absolute
workspace-local directory for receipts. The source checkout must be clean.

For judge-built stock, create /absolute/path/to/stock-pin.json independently
from your trusted mkqnximage output BEFORE launch:

~~~sh
python3 - /absolute/path/to/stock-output/ifs.bin /absolute/path/to/stock-output/disk-qemu > /absolute/path/to/stock-pin.json <<'PY'
import hashlib,json,sys
from pathlib import Path
print(json.dumps(dict(zip(('ifs.bin','disk-qemu'),
    (hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sys.argv[1:])))))
PY
~~~

Launch stock directly after setup and pin creation; no historical run is needed:

~~~sh
sh tools/run-native-suite.sh --image-kind stock --run-id cold-stock --stock-pin /absolute/path/to/stock-pin.json --midread
~~~

Schema: exactly two keys, ifs.bin and disk-qemu, each a real lowercase 64-hex
SHA256 string. Duplicate/extra/missing keys, malformed/placeholder digests and
artifact mismatches fail closed before QEMU; --stock-pin is stock-only. Pins
establish byte identity, not artifact trust; do not regenerate them from an
untrusted replacement merely to bypass a mismatch. With no --stock-pin, the
original recorded stock hashes remain mandatory, NOT an unchecked fallback.
Raw disk uses snapshot=on and hashes are checked before/after. No IFS injection.
HS_LOCK overrides the historical installation default; all guest/SDK owners
must agree on the SAME absolute shared lock. Parent directory must already exist.
This portable path/pin option has host-only tests; no new native run is claimed.

### Optional historical custom-image replay — not a stock prerequisite

Skip unless reproducing historical evidence. Keep the common environment above;
stop/reap any prior guest before launching this separate optional run:

~~~sh
export HS_IFS=/absolute/path/to/optional-historical-custom/incident.ifs
export HS_DISK=/absolute/path/to/optional-historical-custom/disk-qemu
sh tools/run-native-suite.sh --image-kind historical --run-id cold-historical --midread
~~~

## Measured result / accepted server-death contract

Both commands ran from the fresh clean clone at source
44a2ffc3fdcd9a6de035d10f6bff134504826b1d. Data, seven-file corpus, host-edit and
post-kill remount passed on both images; N7 clean-stock mount passed.
Owner review on Nov13 accepted observed native read -1/ESRCH (errno3) as correct
QNX MsgSend server-death behavior. Keep it unchanged; never map to EIO5.
Historical --midread still exits1 against its old EIO-only assertion. Receipts
and raw failures remain byte-identical; this docs review changes no code,
runs no native test and does not relabel original machine status.
See [current contract and exact evidence](CURRENT_CONTRACT.md).
Omitting --midread selects data gates only, not a server-death test.

## What is actually exercised

- HOST2GiB, TCG256MiB, guest512MiB, CPU100%, nice15, smp1, swap0; reserve64MiB.
  Canonical lease held until termination/reap, refuses an existing QEMU.
- Fixed pc topology; historical uses user virtio NIC, stock uses nic none and
  virtio-rng (as stock serial recipe). Both add only readonly virtio-9p. No
  qtest, PIRQ rewrite, fallback or MSI-X retry. Topology fixed before boot.
- Serial copy of own ELF, byte-for-byte hex readback, default pci-line probe
  requiring41 exact bytes, mounted listing, seven independent POSIX checksums
  (empty/1B/4KiB/1MiB/nested/Unicode/hello), denied writes, timed host edit.
- Optional --midread explicitly uses --mount-pause-read: normal open completes,
  client enters native POSIX read, server emits handler-enter rcvid/count then
  pauses **before RPC**, and harness SIGKILLs that server. Client prints actual
  read n and errno unchanged, with10s timeout. Old automation requires EIO;
  owner review accepts observed ESRCH server-death behavior instead.
  EOF, timeout or missing result does not establish that contract.
- Fresh server resets/remounts and checks hello plus1MiB checksum, then SIGTERM.
  This pending-read test is not active virtio DMA/physical-device crash safety.
- Any failure is retained as FAIL/BLOCKED, never silently rerouted. VM always
  stopped/reaped. Read actual receipts, not CI, for native claims.

## Existing licensed SDK source rebuild (inside SDP guest)

~~~sh
source /home/qnx/qnx800/qnxsdp-env.sh
qcc -Vgcc_ntox86_64 -std=gnu11 -O0 -g0 -Wall -Wextra -Werror \
  -Wno-misleading-indentation -Icore native/qnx_hostshare.c \
  native/mount_checksum.c core/transport.c core/protocol.c \
  -o /absolute/external/output/qnx_hostshare -lpci
~~~

A rebuild needs a fresh manifest binding every core/native C/header and the ELF;
this suite does not start an SDK. Existing owner helper scripts are bounded
installation-specific receipts, not portable provisioning tools. Stop/reap SDK
before any native run. No cap increase beyond2GiB.

## Earlier scope and remaining caveats

Prior measured N1c/idle N5/UID65534 results are in irq-restart-20261113. The older
one-file launcher run-native-readonly.sh remains historical; its old ELF cannot
be used against changed source. Clean MSI-X-only failed PCI_ERR_IRQ_CFG and is
not retried here. Reduced-privilege cleanup verifies virtio status0/queue0 but
does NOT verify PCI bus-master disable/restore; trusted QEMU only. Other abilities
not exhaustively audited. This repeat does not claim a production service,
malicious hardware safety or broad cache coherence.

MSI-X is not proven (PCI_ERR_IRQ_CFG); skip MSI-X tests. Recorded idle and
pending-read kill/remount are scoped HA only, not active-DMA crash safety.
Timings are observations, not latency guarantees. The [public demo](https://youtu.be/O0SA7W6gFyE) is available; publication does not broaden these native acceptance claims.
