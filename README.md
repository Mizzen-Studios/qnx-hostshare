# QNX HostShare

Private Apache-2.0 feasibility project. No production filesystem driver is
delivered. The bounded read-only resource-manager follow-up is documented in
[Mount wave](docs/MOUNT_WAVE.md); only its fresh receipts establish native status.

- F0: real QNX8 pci-tool observed virtio-9p. Original [receipt](docs/acceptance/f0/receipt.json) unchanged.
- Host reference work: [portable C core](docs/C_CORE.md), Python models and host tests.
- Nov13: actual [QNX diagnostic adapter](docs/NATIVE_ADAPTER.md) now source-bound
  and cross-built with installed qcc. Native results are ONLY those in fresh
  [attempt receipts](docs/acceptance/native-20261113/), not host CI or READY lines.
- SDK-host2GiB/guest512 boot with256MiB TCG cache completed inventory/standalone
  builds without OOM. No SDK install/login/repair, swap, custom IFS or image build.
- Installed stock-run grammar and EDU compile handoff: [relay](docs/acceptance/native-20261113/STOCK-RELAY.md).
  Existing CANcustom images are NOT stock; stock SSH/transfer remains UNVERIFIED.

Run host tests: PYTHONPATH=src python3 -m unittest discover -s tests -v

Native F1 requires actual completion/IRQ evidence; F2 requires byte-exact read.
No production-readiness claim. Mounted gates require their separate follow-up
receipts. Original kill gate: F1+F2 native PASS by
29November2026 UK, otherwise stop. No schedule created.

**Nov13 bounded native F1/F2 PASS:** seven actual QNX IRQ-pulse replies and byte-exact
readonly41-byte synthetic file read; app rc0. Requires explicitly recorded own-device
PIRQ_D-toIRQ10 routing. See [result and limits](docs/acceptance/native-20261113/RESULT.md).
Not default-routing, production filesystem or hardware-support acceptance.

**Historical mount follow-up (c4e4f25):** N1 default routing was FAIL. N2/N3/N4 bounded native PASS
with explicitly documented IRQ10 workaround: real read-only resource manager,
seven mounted-file checksums, host edit observed without rebuild. See
[result and limitations](docs/acceptance/mount-20261113/RESULT.md).


## Cold-reader launch, no IRQ routing changes

See [exact clean-clone/prerequisite/build commands](docs/RUN_NATIVE.md).
On the configured host, in a clean checkout after SDK STOP/reap:

~~~sh
export HS_ELF=/home/ubuntu/qnx-host/guest/shared/hostshare-stock-repeat-20261113/build2/qnx_hostshare
export HS_BUILD_MANIFEST="$PWD/docs/acceptance/stock-repeat-20261113/build-source-hashes.json"
export HS_IFS=/home/ubuntu/qnx-host/guest/shared/incident-20261108/incident.ifs
export HS_DISK=/home/ubuntu/qnx-host/guest/shared/qnx-native/disk-qemu
sh tools/run-native-suite.sh --image-kind historical --run-id cold-historical --midread
~~~

After that guest is reaped, clean-stock repeat:

~~~sh
export HS_IFS=/home/ubuntu/qnx-host/guest/shared/edu-stock-control-1024-20261113/stock-output/ifs.bin
export HS_DISK=/home/ubuntu/qnx-host/guest/shared/edu-stock-control-1024-20261113/stock-output/disk-qemu
sh tools/run-native-suite.sh --image-kind stock --run-id cold-stock --midread
~~~

New run-id per attempt; readonly seven-file corpus, timed host edit and explicit
pending-read kill/error observation. No qtest, PIRQ writes, fallback or MSI-X retry.
Fresh [stock-repeat result](docs/acceptance/stock-repeat-20261113/RESULT.md): both
images pass seven-file checksums, timed host edit, readonly mount and post-kill
remount. N7 clean-stock mount PASS. **MIDREAD EIO gate BLOCKED:** actual native
read returns -1/errno3, not EIO5; --midread intentionally exits1. No translation.
The prior [N1c/idle-N5 result](docs/acceptance/irq-restart-20261113/receipt.json)
remains accepted in its own scope. Its old stock dependency block is preserved,
not a claim about the newly handed-off hashed stock image.
[Written demo draft](docs/DEMO_DRAFT.md) remains unrecorded/unpublished.
