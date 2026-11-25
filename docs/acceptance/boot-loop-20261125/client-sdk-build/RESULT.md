# Real installed-SDK client build — PASS, QNX runtime NOT_RUN

Parent explicitly admitted this existing Linux SDK builder separately from the
owner's two QNX runtime boots. Actual build from clean6e9ac974 sources completed
with qcc -Vgcc_ntox86_64, rc0; strict C11/Wall/Wextra/Werror/pedantic flags.
Compiler and SDK-environment hashes, source SHA256, actual command and output ELF
hash are in build.json and owner-receipt.json. No fabricated build manifest.

Private9488-byte QNX x86_64 client ELF:
171b6fae32f6f62118fb2fa90eb0f2275ba3fbc6184abdc9273076fdfa04cb5e

/home/ubuntu/qnx-host/guest/shared/hs-dev-client-20261125/source/.local/qnx-client/loop-app
Sibling build.json is the native admission manifest. Independent host review
rechecked source/ELF/compiler binding and readelf header. The ELF was NOT executed
on QNX and this is not a native conformance PASS. No SDK binaries/images/licenses
or executable bytes are in Git. Existing driver/base artifacts remain unchanged.

Builder used its existing installed licensed SDK disk, one guest1024MiB, smp1,
TCG256, CPU100%, nice15, cgroup host2GiB/swap0/reserve64MiB. Existing launch recipe
was inspected; only private QMP socket and NIC=none differed. No network, SDK
install/login or spend. Peak1226596352 bytes,440 monitored samples; reserve held,
max/oom/oom_kill0. System-wide swap was not reconfigured; cgroup swap.max was0.

ACPI shutdown completed; owner exit0 and child reaped. Final independent checks:
zero QEMU, lease FREE, pending queue empty. Historical running markers were
preserved, not requeued/deleted. No forced native launch or automatic continuation.
Raw Linux serial/memory/owner-control code stay private, pinned by SHA256.

QNX runtime boots used:0 of2. Next step requires a separate parent grant for
prepare1, followed by independent prepared-overlay review and separate coldboot2
grant. Exact runtime commands and caps are in ../../../BOOT_DEVELOPER_LOOP.md.
