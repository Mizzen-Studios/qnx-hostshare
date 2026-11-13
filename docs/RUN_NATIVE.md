# Exact bounded native launch (private, no routing rewrite)

Installation-specific QNX8/QEMU readonly feasibility suite, not a production
filesystem or SDK installer. Historical results and failures stay immutable.
The earlier stock-OOM dependency block is superseded **only for this repeat** by
EDU be712b27 stock-build/boot handoff. SSH remains unverified (stock sshd fault);
this runner uses serial only, without login/network/platform repair.

## Prerequisites (not provisioned by launcher)

- Configured Linux host: Python3, QEMU x86_64, POSIX cksum, systemd user manager,
  cgroupv2, nice, and authenticated read access to this private GitHub repository.
- Existing licensed QNX8 SDP only if rebuilding; proprietary headers/libraries,
  ELF, IFS and disks remain outside Git. No downloads/install/login/image build.
- /home/ubuntu/qnx-host/native-test.lock writable; no other QEMU/SDK running.
- External hash-matching executable and raw base disk/IFS below. Missing inputs
  fail before QEMU. Source mismatch fails; do not substitute an older ELF.
- Guest image has a serial root shell, /data, ksh printf, od, cat, ls and pidin.
  No CANOPY boot marker is assumed. Both authorized images are BIOS/pc.

## Cold-reader exact commands on the configured host

From a directory that does not already contain qnx-hostshare:

~~~sh
git clone https://github.com/Mizzen-Studios/qnx-hostshare.git
cd qnx-hostshare
export HS_ELF=/home/ubuntu/qnx-host/guest/shared/hostshare-stock-repeat-20261113/build2/qnx_hostshare
export HS_BUILD_MANIFEST="$PWD/docs/acceptance/stock-repeat-20261113/build-source-hashes.json"
export HS_IFS=/home/ubuntu/qnx-host/guest/shared/incident-20261108/incident.ifs
export HS_DISK=/home/ubuntu/qnx-host/guest/shared/qnx-native/disk-qemu
sh tools/run-native-suite.sh --image-kind historical --run-id cold-historical --midread
~~~

Each run-id must be fresh. Outputs default to .local/user-runs/<run-id>; the
corpus is new at .local/corpus-<run-id>. Optional HS_RECEIPT_BASE is an absolute
workspace-local directory for receipts. The source checkout must be clean.

After the previous command exits and its guest is stopped/reaped, repeat on the
**new clean-stock pair** (never replace it with the historical image):

~~~sh
export HS_IFS=/home/ubuntu/qnx-host/guest/shared/edu-stock-control-1024-20261113/stock-output/ifs.bin
export HS_DISK=/home/ubuntu/qnx-host/guest/shared/edu-stock-control-1024-20261113/stock-output/disk-qemu
sh tools/run-native-suite.sh --image-kind stock --run-id cold-stock --midread
~~~

The stock preflight hard-checks IFS68bbe1b4.../disk0aee00c2... full hashes from
upstream-handoff.json. The raw disk is snapshot=on; baseline hashes are checked
before and after. No lesson ELF or modifications are injected into an IFS.

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
malicious hardware safety, broad cache coherence, video or publication.

MSI-X is not proven (PCI_ERR_IRQ_CFG); skip MSI-X tests. Recorded idle and
pending-read kill/remount are scoped HA only, not active-DMA crash safety.
Timings are observations, not latency guarantees. Demo remains written-only,
recorded=false; no media or publication is authorized.
