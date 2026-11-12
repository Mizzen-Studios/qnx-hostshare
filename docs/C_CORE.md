# Portable C driver-core foundation — host only

core/hostshare.h is the future adapter boundary; core/transport.c and
core/protocol.c are C11, allocation-free and compile with the existing host cc.
They are NOT a running QNX driver. Python remains a separate reference model.

Delivered transport: modern PCI capability chain parsing with cycle/alignment/
bounds checks, VERSION_1+MOUNT_TAG feature selection, bounded mount-tag bytes,
one two-descriptor request/write-response chain with disjoint address ranges,
length/overflow/busy/completion-token checks, mocked notify and pulse hooks.
Addresses are opaque caller inputs, NOT DMA mappings. Descriptor structs are
host memory representations, NOT a published device ring. Late completion ABA
protection after16-bit token wrap and concurrent synchronization are not supplied.

Delivered9P: strict framing encode/decode for T/Rversion, attach, walk, lopen,
read, readdir, getattr, clunk and Rlerror. Enforces exact size/type/tag/msize,
NOFID live-fid rejection, nested string/count bounds, qid and fixed reply sizes,
and packed readdir entries. Encode accepts caller-built LE body bytes, validates
and copies them; decode returns borrowed body view, not typed semantic objects.
Strings are bounded byte strings with NUL/component checks, not Unicode-normalized.
No fid allocation/table, negotiated session state, request-specific read count/
walk count correlation, access policy or complete protocol implementation.

Tests author synthetic bodies/configs directly.17 request/response framing cases
include all supported kinds, truncation at each byte and trailing/tag controls;
transport tests use fake addresses and callbacks.512 zero malformed frames are
negative controls, not fuzzing. Python suite remains17 tests/1000 seeded inputs.
No live QNX/server capture is claimed. ASan+UBSan host run passed locally.

Missing native adapter: QNX PCI mapping/abilities, physical DMA allocation,
cache/barriers, available/used rings, feature status handshake, MMIO notification,
interrupt attach/masking/acknowledge and pulse lifecycle, cancellation/reset and
resource manager/mount lifecycle. Those remain NOT_IMPLEMENTED/NOT_RUN.
No SDK compile, native build, image build, QEMU boot or F3+ work in this closure.
Installed SDK/mkqnximage options/stock inventory remains UNVERIFIED.

Build/test (host only):

    mkdir -p .local
    cc -std=c11 -Wall -Wextra -Werror -pedantic -Icore core/transport.c core/protocol.c tests/test_core.c -o .local/test-core
    .local/test-core

Native F1+F2 kill gate remains29 November2026 UK; no schedule created.
