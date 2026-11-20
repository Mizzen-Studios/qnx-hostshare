# Single approved default run — 20 November 2026

**BLOCKED_MISSING_GUEST_SHA256SUM_APPLET. No default native acceptance.**

The one authorized QEMU run used clean source tip
549a9bae92dfd3509ae2892e62751b0235a1c3f5 and the unchanged source-bound ELF
36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75.
All8 C/header bindings, canonical helper pin and reviewed external stock IFS/disk
were independently checked before launch. No SDK, installation or image build.
Default tag f0test and mountpoint /mnt/host were selected with --conformance.

## Observed live shared transport

807 exact nonce/sequence/offset acknowledgments passed: initialization plus806
64-byte-or-shorter data chunks, ending at offset51528. Independent review of the
private raw events verifies every acknowledged marker and reconstructs the HOST
transmitted bytes, matching the bound ELF SHA256. CSI matching worked through
startup; no acknowledgment was resent or replayed as native conformance proof.
This proves acknowledged command transfer, NOT final guest-file integrity.

At final integrity request seq807, the actual guest printed:

    toybox: Unknown command sha256sum (see "toybox --help")

The conjunction did not run wc/final acknowledgment. The20s request deadline
expired; helper and runner both emitted FAILED terminal events. The900s transfer
budget was not exhausted. Missing applet correctly failed closed: no chmod,
ELF execution, independent od readback, probe, mount, default offset/read cases,
pagination/rewind, mutation-denial or host-edit conformance ran. Guest actual
size and hash remain UNVERIFIED, never inferred from sent bytes or acknowledgments.

## Cleanup and bounds

Exclusive canonical flock held for the whole guest lifetime; no foreign QEMU or
pending queue at preflight. CPU100%, nice15, host2GiB, memory.swap.max0,
reserve64MiB; guest512MiB, smp1, TCG256. Measured peak553218048 bytes;
max/oom/oom_kill events all0. No cap/reserve breach or cap increase.
Owned QEMU exited0 and was reaped; runner exited1. Final observed lease FREE,
zero QEMU and zero pending queue jobs. Base IFS/disk hashes unchanged.
No retry, fallback hash, guest installation, extra native run or CAN capture.

## Evidence and claim boundary

receipt.json and started.json retain the original failed runner state.
blocker.txt/serial.txt contain sanitized text, not SDK/ELF bytes.
independent-transfer-review.json pins private append-only raw events and memory
samples by SHA256, plus both actual terminal events. tool-bindings.json and
build-source-hashes.json bind the exact runner/helper/native artifacts.

The earlier fresh custom dev-inputs,/mnt/dev-inputs QNX conformance PASS remains
valid only for its recorded scope (288 byte cases,4 directory scans,187 entries,
5 denied opens,7 checksums, host edit and detach). Complete current-source native
acceptance remains PARTIAL: default compatibility is now concretely blocked by
missing guest sha256sum, rather than the earlier CSI-prefixed COPY acknowledgment.
Every earlier failed receipt/pin remains unchanged. No safety/latency claim.

Any alternative integrity route or future live test requires a new explicit
owner/parent decision. This granted single attempt is consumed and stopped.

Final verification:65 Python HOST tests passed; portable strict C remains separate.
See host-tests.txt and cleanup.json. HOST success does not close the default gate.
