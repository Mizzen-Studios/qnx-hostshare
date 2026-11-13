# Exact bounded native launch (private, no routing rewrite)

This is an installation-specific QNX8/QEMU smoke run, not an SDK installer or a
production filesystem service. It uses the **existing historical custom image**,
not a clean stock image. N7 is dependency-blocked by EDU's stock IFS OOM receipt.
The earlier pc/shared-INTx limitation and failed attempts remain preserved.
The current runner does not invoke qtest, rewrite PIRQ routing, or silently switch
interrupt modes. An MSI-X run is always a separate fresh VM boot.

## Prerequisites, deliberately not downloaded or built by launcher

- Linux host with Python3, QEMU x86_64, systemd user scopes/cgroupv2 and nice.
- Exclusive canonical lock directory /home/ubuntu/qnx-host; no other SDK/QNX VM.
- Existing authorized IFS plus snapshot-capable raw data disk. The tested image
  emits CANOPY_SLM_IMAGE_READY, has /data/home/root and the recorded utilities.
- Current source's externally built QNX ELF. SDK headers, libraries, ELF, disk,
  IFS and credentials are not in Git. Missing prerequisites fail before boot.
- Existing licensed QNX8 SDP for a source rebuild, if required. No install/login,
  package repair, custom image generation or network service setup here.

Inside that existing licensed SDP, from this checkout (serial build, O0/g0):

~~~sh
source /home/qnx/qnx800/qnxsdp-env.sh
qcc -Vgcc_ntox86_64 -std=gnu11 -O0 -g0 -Wall -Wextra -Werror \
  -Wno-misleading-indentation -Icore native/qnx_hostshare.c \
  native/mount_checksum.c core/transport.c core/protocol.c \
  -o /absolute/external/output/qnx_hostshare -lpci
~~~

## Linux-host clean checkout and launch

~~~sh
git clone git@github.com:Mizzen-Studios/qnx-hostshare.git
cd qnx-hostshare
export HS_ELF=/home/ubuntu/qnx-host/guest/shared/hostshare-irq-restart-20261113/build2/qnx_hostshare
export HS_IFS=/home/ubuntu/qnx-host/guest/shared/incident-20261108/incident.ifs
export HS_DISK=/home/ubuntu/qnx-host/guest/shared/qnx-native/disk-qemu
export HS_BUILD_MANIFEST="$PWD/docs/acceptance/irq-restart-20261113/build2-source-hashes.json"
sh tools/run-native-readonly.sh --irq-mode pci-line --run-id intx-first
~~~

Use a new run-id for every attempt. Outputs default to .local/user-runs/<run-id>.
Optional HS_RECEIPT_BASE selects another workspace-local evidence directory.
The wrapper applies HOST1GiB (existing stricter cap), CPU100%, nice15, swap0;
guest512MiB/smp1 and reserve64MiB are checked. The SDK build owner separately uses
HOST2GiB/TCG256MiB; native accelerator argv is the established pc,accel=tcg route.
No cap can exceed2GiB. No SDK may run concurrently; the launcher holds the lease
until VM termination/reap and refuses another QEMU process.

For a **clean MSI-X-only boot**, after the previous guest is completely reaped:

~~~sh
sh tools/run-native-readonly.sh --irq-mode msix --run-id msix-clean-first
~~~

MSI-X enables PCI Memory Space before capability setup. It does NOT first run
pci-line. Its actual installed-API result is a receipt, not presumed support.

## What runner does and does not prove

Only a fresh one-file public synthetic corpus is exported readonly, with
security_model=none. The ELF is copied into a snapshot data volume and byte-exact
readback checked. Default-route 9P probe must return41 exact bytes before mount
checks run. No hidden route fallback occurs if that probe fails.

N5 deliberately SIGKILLs the **idle** mounted process only after completed reads,
checks that the old mount disappears, resets the device in a replacement process,
then tests a UID65534 mount with explicit ability reductions. Active/in-flight
SIGKILL/DMA safety, malicious hardware and physical-device resilience are NOT
claimed. INTERRUPT is retained for the existing IRQ; other abilities are not
exhaustively audited. A final SIGTERM requests cooperative detach/quiescence.
The wrapper always stops/reaps the isolated VM; failed steps remain failed.

Read exact gates and caveats in docs/acceptance/irq-restart-20261113/receipt.json.
No production, broad coherence, clean-stock or recording claim follows from CI.

Reduced-privilege cleanup resets the mapped virtio device and verifies status0
and queue_enable0 before releasing its DMA memory. It deliberately skips the
privileged PCI backend after IO ability is locked off; PCI Bus Master disable/
restore is NOT verified on that reduced path. This is trusted-QEMU-only cleanup,
not safe untrusted/physical DMA teardown. The original post-detach SIGSEGV is
preserved in intx-clean; the correction must have its own fresh receipt.
