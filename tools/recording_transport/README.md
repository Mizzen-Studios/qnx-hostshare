# Pinned shared serial transport — HOST ONLY

Byte-identical vendor of CANopy's additive tools/recording_transport/__init__.py;
PIN.json binds canonical repository, exact commit, helper SHA256 and identical
shared tests. No runtime sibling-checkout/network dependency. Local test and
native-runner preflight reject pin drift. Canonical source remains CANopy tooling,
not its frozen product. EDU may adopt this pinned release later; not integrated.

The helper is not newly QNX-accepted. Native verification is reserved for the
separately authorized SINGLE default HostShare run, after parent timeline gates.
No SDK/image/native C change, capture deadline change or CAN recording permission.

Protocol:64-byte octal blocks; command <=512 bytes; fresh128-bit nonce, sequence
and actual end offset; exact standalone ack. CSI normalization is matching-only;
private raw logs remain unchanged. Echoes, duplicate/stale/wrong acks abort with
no resend. Guest existing /proc/boot/toybox sha256sum and wc -c must match before
caller chmod/exec; missing applets fail closed. HS additionally requires exact
independent od readback before executing the ELF. Destination is a short validated
/tmp/... or /data/hostshare/... path. No arbitrary shell/path input.

HS uses a900s total transfer deadline, per-ack20s clipped to remaining time,
bounded partial nonblocking writes and caps monitored while waiting. Boot180s,
hex readback60s, conformance240s are separate existing stage budgets. Other
native commands/checksums retain their explicit bounds. This is not a speed claim
or an8060-second multiplication of per-chunk timeouts.

Private serial-events-private.jsonl appends exact TX/RX and helper terminal events
with monotonic timestamps and fsync; it contains OWN executable bytes and MUST
NOT be committed/uploaded. Existing public serial views redact executable copy
commands/readback. Raw append logs include traffic before a timeout; failure
receipt and owned-QEMU terminate/wait/kill-wait cleanup remain mandatory. A
transfer VERIFIED event is not runner/native conformance success.

HOST tests use an actual PTY and /bin/sh, not mocked QNX:51528 synthetic bytes,
806 data chunks,808 acknowledgments, max371-byte commands for HOST path; actual
2ms delayed acks/7-byte fragmented writes. A separate virtual-clock1s/request
model finishes808s under900s (not measured QNX latency). Real4096-byte
nonblocking-pipe backpressure and global-deadline exhaustion are exercised.
Neither the old CAN447/963 result nor HOST success is reclassified as native PASS.
