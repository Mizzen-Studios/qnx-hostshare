# Feature A HOST milestone — 25 November

81 Python HOST tests PASS; strict portable C PASS; compileall/diff checks PASS.
No QEMU/SDK start, lease acquisition, recording or external posting. Native
boot/default/developer-loop gates are NOT_RUN, not accepted by HOST CI.

Implemented: source-bound host builder and portable C client; exact guest od
readback transport without sha256sum; one-shot real stock /boot/onboot hook;
validated private overlay prepare/seal/pin then passive boot verification; actual
built-client copy/readback/run gate alongside readonly/default conformance.
The host-stage tests really compile and execute the POSIX client on Linux and
really transfer/read back51,528 bytes through a host shell. Neither is QNX proof.
Corruption, unavailable od, duplicate/stale/echo acknowledgments, budget exhaustion,
wrong backing/hash, target collisions/symlinks and HOST-only build admission fail
closed. An exact extracted runner readback callback is also exercised.

Existing reviewed driver8-source binding remains unchanged; no driver rebuild or
historical re-pin. All old failures/receipts remain untouched. The shared canonical
CAN helper/vendor pin is unchanged; new HS-local adapter is separate. No CAN/EDU
files or C6 changes. No transparent restart/respawn or queue recovery feature.

Design/commands/resource budgets: ../../BOOT_DEVELOPER_LOOP.md.
Native readiness blocker: no direct SDK at /home/qnx on this ARM host; the existing
licensed Linux SDK builder needs explicit parent provisioning/lease (or a reviewed
external QNX client build). A HOST cc build is explicitly rejected as a QNX client.
Runtime plan is TWO explicit attempts: prepare private boot overlay, then cold
boot/conformance/client verification. No automatic second run and no retries.

Additional HOST metadata smoke: real qemu-img create/info against a temporary
1MiB synthetic raw file proved the overlay helper backing/format contract.
This started no QEMU VM and used no QNX image. Temporary artifacts were reaped.
