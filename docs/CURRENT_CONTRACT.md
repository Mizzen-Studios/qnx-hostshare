# Current acceptance index — 19 November 2026

Current-source custom-tag read-only handoff conformance **PASS**; full item4
acceptance is **incomplete** because default-native compatibility is blocked by
serial transfer timeout COPY_6912 before probe/mount. The tested current source
is a57bd240a7575397caa3f0021b6ca2e11043c225; its fresh ELF is
36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75.
[Build4 result and raw receipts](acceptance/developer-handoff-20261119/coordinated-build4/RESULT.md)
prove tag dev-inputs,/mnt/dev-inputs,288 byte cases,four pagination/rewind scans,
five denied opens,seven checksums and host-edit visibility with readonly export.
HOST38 tests cover configuration and namespace guard negatives; they do not
establish native default compatibility. No speed/latency claim. No current-source
server-death test was added; old HA evidence remains source/ELF-specific.

The reviewed ESRCH contract and immutable historical pins below remain intact.

## Historical reviewed death contract — 13 November 2026

Owner review at 12:08 UTC accepts native ESRCH (errno3) on QNX MsgSend server
death. No mapping to EIO5. This is a docs-only interpretation of existing
observations, not a new native test, changed binary or expanded guarantee.

## Proven and not proven

Recorded read-only default-IRQ11 operation, without qtest/PIRQ rewriting:
probe, mount/list, seven-file independent checksums, denied writes, host edit,
cooperative stop and post-kill fresh remount/read on both recorded images.
Scoped HA comprises prior idle-kill/remount and actual pending-read ESRCH/remount.
The latter pauses the read handler before RPC/DMA, kills that server, observes
read n=-1/errno3, then starts a fresh server and reads again. It is NOT active-DMA
crash safety, arbitrary hardware recovery or a production filesystem claim.

MSI-X remains unproven: PCI_ERR_IRQ_CFG; skip MSI-X tests. No latency guarantees:
recorded host-edit and read-return timings are observations only.

Historical runner/client/finalizer still enforce the superseded EIO-only gate;
--midread exits1, and raw receipts retain BLOCKED_GATE/PARTIAL_PRECISE_BLOCKED
and passed=false. These are preserved audit facts, not current demands to turn
ESRCH into EIO. No software changed in this review. Do not regenerate historical
receipts or manufacture a fresh PASS. The immutable [original result](acceptance/stock-repeat-20261113/RESULT.md)
describes the earlier EIO requirement; this review supersedes only that contract.

## Exact existing evidence

- Native tested source: [44a2ffc3fdcd9a6de035d10f6bff134504826b1d](https://github.com/Mizzen-Studios/qnx-hostshare/tree/44a2ffc3fdcd9a6de035d10f6bff134504826b1d).
- Preserved evidence baseline: [22ca7a77c94e7af4e7f8f182b82b9c1d0dc55fcf](https://github.com/Mizzen-Studios/qnx-hostshare/tree/22ca7a77c94e7af4e7f8f182b82b9c1d0dc55fcf).
- [Build source/ELF binding](acceptance/stock-repeat-20261113/build-source-hashes.json),
  [combined original receipt](acceptance/stock-repeat-20261113/receipt.json),
  [manifest](acceptance/stock-repeat-20261113/MANIFEST.sha256).
- ELF SHA256: 84bb0bd51836e8e9e6f06f1abd97221974e43a3fc5429ea60c7e66493d19e959.
- Historical IFS SHA256: 764e7e9f3ffcb74e851dce896a513c85abe16589d918937f3ba5157891882a22.
- Historical disk SHA256: 903598ddfcc0a3fc2f4a1907872676033f29e333cd02b5db4d5f460cd387f516.
- Clean-stock IFS SHA256: 68bbe1b49a9b723c09d152773ee323ec6ab576eb29de933bfe3f08fdae21c753.
- Clean-stock disk SHA256: 0aee00c281f8eeb5b02c66555ed9517e317bb1503002a19dbf2b0155de336532.
- [Historical raw errno](acceptance/stock-repeat-20261113/cold-historical/midread-result.txt)
  and [remount](acceptance/stock-repeat-20261113/cold-historical/remount.txt).
- [Stock raw errno](acceptance/stock-repeat-20261113/cold-stock/midread-result.txt)
  and [remount](acceptance/stock-repeat-20261113/cold-stock/remount.txt).
- [Prior idle-N5 scope](acceptance/irq-restart-20261113/receipt.json) is not rerun or expanded.

## Current inspection and media pointers — updated 16 November 2026

Licensed binaries/images remain external. Historical failures, all acceptance
bytes and the exact pins above remain unchanged. [Judge inspection](JUDGES.md)
is host-only; [ordinary native quickstart](RUN_NATIVE.md) omits the obsolete
EIO-only diagnostic and does not test server death.

[Public demo](https://youtu.be/O0SA7W6gFyE) is linked in the living
[evidence outline](DEMO_DRAFT.md). Public playback/narration was not revalidated
here. The separate [15 November recording result](acceptance/recording-20261115/RESULT.md)
and [private draft receipt](acceptance/recording-20261115/private-draft-release.json)
document existing silent footage; a private draft is not a public release.
The former written-only/unpublished footer was stale current prose, not an
immutable receipt. This update makes no new recording or native acceptance
claim and says nothing about the current global lease owner. No native/QEMU,
SDK/licence, visibility, outreach or spending changes; C6 untouched.

## Configurable read-only handoff — 19 November

See [operator recipe and current-source conformance status](DEVELOPER_HANDOFF.md).
Host checks are not native acceptance; historical pins and receipts stay unchanged.
