# QNX8 HostShare diagnostic adapter (Nov13)

native/qnx_hostshare.c is original native QNX adapter source, not the Python
reference or portable C core mislabeled as a driver. It uses installed PCI API
cfg_rd8/read_ba/attach/read_irq, maps bounded modern virtio regions, negotiates
VERSION_1+MOUNT_TAG, allocates16KiB checked physically contiguous memory, publishes
one8-entry split ring with two descriptors, enables PCI mastering and delivers
completion via InterruptAttachEvent/SIGEV_PULSE to a channel with finite waits.
It acknowledges ISR, validates used index/id/length and unmasks the tracked IRQ.
Native-header hashes and actual qcc logs are in acceptance/native-20261113.

Bounded workload only:9P2000.L version/attach/walk(hello.txt)/lopen(read-only)/read/
clunk over one queue. Host export only a fresh public synthetic corpus, readonly
and security_model=none. No workspace/SDK/secret export. Byte-exact read is a gate,
not presumed from compile, PCI enumeration, mocked frames or READY marker.

Cleanup resets device, disables/reads-back bus mastering, detaches IRQ/channel,
unmaps only owned buffers/BARs and relinquishes PCI/thread I/O ownership. If
mastering cannot be quiesced, buffer is deliberately retained and isolated VM
owner deadline supplies stop. This QEMU-specific diagnostic is NOT a production
resource manager/mount driver, multi-client service, reconnect implementation,
physical hardware safety guarantee, security audit, or F3+ feature delivery.

Fresh ELF cross-build uses installed qcc -O0 -g0 -Wall -Wextra -Werror
-Wno-misleading-indentation, -lpci. First compile sign-compare failure preserved;
second fresh build rc0. No mkifs/image build, SDK install/login/repair or swap.
Existing prebuilt historical IFS+disk remain hash-bound, provenance metadata not
new stock images. Serial-copy transport uses snapshot writable data volume only.
Native acceptance status MUST be read from fresh native attempt receipts.

Historical F0/host-model receipts remain unchanged. Kill gate unchanged:
F1+F2 native PASS by29Nov2026 UK; not scheduled.
