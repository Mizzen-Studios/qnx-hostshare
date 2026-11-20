# C — shared serial transport implementation, HOST ONLY

Canonical additive CAN tooling pinned by tools/recording_transport/PIN.json;
HS helper and shared19-test suite are byte-identical to canonical source/tests.
No frozen CAN product, native C/header, EDU or historical evidence changed.

HS63 HOST tests pass (includes the actual extracted runner exchange on a real
HOST shell); canonical164 Python tests pass with8 skips; canonical178 Node tests
pass. No observer replay is native proof. No SDK/QEMU/lease/queue or recording
operation took place. Native authority remains with the parent gates.

Full-size HOST PTY test sends51528 synthetic bytes,806 octal64 data chunks,
808 acknowledgments total, max371-byte commands for the HOST destination,
actual2ms ack delays and7-byte write fragmentation; separate real4096-byte
nonblocking pipe forces backpressure. The virtual-clock1s/ack model completes808s
inside900s; this is NOT measured QNX latency/performance. Global exhaustion and
clipping negatives fail closed. Per-ack20s cannot multiply into8060s: all writes,
reads and helper requests share a900s transfer deadline.

CSI is removed ONLY from matching view. Exact nonce/sequence/end-offset markers
exclude echoed commands, stale/wrong/duplicate acks; no uncertain retransmission.
Missing hash applet, wrong size/hash, corruption, truncated command, partial/zero
writes and deadline failures are HOST-tested. Before HS chmod/exec, existing guest
toybox sha256sum AND wc -c must match, followed by exact independent od readback.
Applet availability remains an actual native gate, never inferred from HOST tests.

HS startup180s, transfer900s, hex readback60s and conformance240s remain explicit
stage budgets, not capture-deadline changes. Caller uses bounded nonblocking TX,
monitors existing cap/reserve guards while waiting and retains owned-Popen cleanup.
Private append-only fsynced TX/RX/terminal events preserve all exact raw bytes,
even before timeout. They contain OWN ELF data and must NOT be committed. Public
serial views redact copy commands/readback. Existing failed native pins unchanged.

Existing ELF36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75
still matches all8 native source/header hashes. No fresh SDK needed. The one
future DEFAULT conformance run awaits original-polish+A+B+C+D timeline parent
grant. No new current default native acceptance or CAN capture claim is made.
