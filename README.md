# QNX HostShare

Apache-2.0 read-only virtio-9p host-folder driver for QNX 8.0 (QNX Global Hackathon 2026, Low-level Software). Not a production filesystem.

## Edit on the host, read in QNX — no image rebuild

Keep development inputs on the host and read updated bytes through a read-only
QNX mount, without rebuilding or transferring a guest image for every edit.
QEMU supplies the host export; this project supplies the bounded QNX 8
integration, not a general-purpose writable filesystem.

1. **Watch:** [public demo](https://youtu.be/O0SA7W6gFyE) (external media; not revalidated here).
2. **Inspect without QNX:** [judge path](docs/JUDGES.md) links actual edit/read,
   checksum and denied-write receipts. Host-only checks need Python and a C
   compiler, not an SDK, guest image or QEMU.
3. **Reproduce with an existing licensed setup:** [prerequisites and ordinary
   data route](docs/RUN_NATIVE.md). Host tests are not native acceptance.

## Current native proof — default route, read-only

- [N1c/default-routing and idle-N5 receipt](docs/acceptance/irq-restart-20261113/receipt.json)
  establishes its recorded default-route and idle-kill/remount scope.
- [New clean-stock mount and seven-file corpus](docs/acceptance/stock-repeat-20261113/receipt.json):
  default IRQ11, no qtest/PIRQ rewrite; readonly mount/list, independent checksums,
  denied writes and host-edit visibility. Historical and clean-stock repeats also
  remount/read successfully after server kill.
- Pending-read server death returns native **ESRCH errno3**, the owner-accepted
  QNX contract; never map to EIO5. [Current contract and exact source/ELF/image pins](docs/CURRENT_CONTRACT.md).
  Original EIO-only assertion failures and all historical receipts remain unchanged.

Read-only, scoped HA only: idle/pending-read kill then fresh remount, **not
active-DMA crash safety**. MSI-X is not proven (PCI_ERR_IRQ_CFG; skip MSI-X tests).
No production-readiness or latency guarantees. [Watch the public demo](https://youtu.be/O0SA7W6gFyE).

## Proven quickstart scope

- Proven: readonly mount/list and seven-file checksums on both recorded images,
  default IRQ11, no qtest or PIRQ rewrite.
- Not proven: MSI-X (PCI_ERR_IRQ_CFG; skip MSI-X tests), production readiness,
  active-DMA crash safety or latency guarantees. Timings are observations only.
- Scoped HA: recorded idle-kill/remount and pending-read ESRCH/remount only.
  The [public demo](https://youtu.be/O0SA7W6gFyE) illustrates the project; this documentation update adds no native evidence.

## Cold-reader launch, no IRQ routing changes

See [exact clean-clone/prerequisite/build commands](docs/RUN_NATIVE.md).
Replace all /absolute/path/to/... placeholders with local files. Build stock
images using licensed mkqnximage (see prerequisites). Historical custom-image
commands below are optional replay only, not required for judge-built stock.
Use one shared HS_LOCK across all guest/SDK owners; never run concurrently.
### Direct clean-stock quickstart (no historical image required)

After the licensed stockbuild prerequisite, bind your own ELF and source with a
fresh manifest, then create stock-pin.json as documented
in RUN_NATIVE.md. In a clean checkout after SDK STOP/reap, run directly:

~~~sh
export HS_LOCK=/absolute/path/to/shared-native-test.lock
export HS_ELF=/absolute/path/to/qnx_hostshare
export HS_BUILD_MANIFEST=/absolute/path/to/fresh-build-source-hashes.json
export HS_IFS=/absolute/path/to/stock-output/ifs.bin
export HS_DISK=/absolute/path/to/stock-output/disk-qemu
sh tools/run-native-suite.sh --image-kind stock --run-id cold-stock --stock-pin /absolute/path/to/stock-pin.json
~~~

### Optional historical custom-image replay — not a stock prerequisite

Skip this block unless reproducing the historical custom-image evidence. Set
HS_LOCK, HS_ELF and HS_BUILD_MANIFEST as above; stop/reap any prior guest first.

~~~sh
export HS_IFS=/absolute/path/to/optional-historical-custom/incident.ifs
export HS_DISK=/absolute/path/to/optional-historical-custom/disk-qemu
sh tools/run-native-suite.sh --image-kind historical --run-id cold-historical
~~~

New run-id per attempt; the ordinary route checks the readonly seven-file corpus,
timed host edit and cooperative stop. It does not test server death or remount.
**Historical diagnostic only:** adding --midread enables the unchanged EIO-only
gate, known to exit1 for accepted ESRCH3; do not add it to the ordinary quickstart.
No qtest, PIRQ writes, fallback or MSI-X retry.
Fresh [stock-repeat result](docs/acceptance/stock-repeat-20261113/RESULT.md): both
images pass seven-file checksums, timed host edit, readonly mount and post-kill
remount. N7 clean-stock mount PASS. **Owner-accepted midread contract:** native
ESRCH (errno3) on server death, followed by successful remount. Never map to EIO5.
Historical --midread still exits1 against its superseded EIO-only assertion.
See [current contract and exact evidence](docs/CURRENT_CONTRACT.md); original
blocked labels/raw failures remain unchanged, not a new native failure.
The prior [N1c/idle-N5 result](docs/acceptance/irq-restart-20261113/receipt.json)
remains accepted in its own scope. Its old stock dependency block is preserved,
not a claim about the newly handed-off hashed stock image.
[Watch the public demo](https://youtu.be/O0SA7W6gFyE), or read its [evidence outline](docs/DEMO_DRAFT.md).

## Historical milestones — not the current default-route result

The earlier PIRQ workaround and N1 failure below are preserved history; they do
not replace the later N1c and clean-stock default-IRQ11 evidence above.

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
