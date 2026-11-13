# Native bounded F1+F2 PASS — not production readiness

Actual QNX8 process, sourcehash8b972a28..., ELFdec8b0a8..., IFS764e7e9f...
and disk903598dd... are bound in attempt3/receipt.json. Native ELF copy was
verified byte-exact by readback against host ELF, not assumed from upload rc.

Observed:1af4:1049; mounttagf0test; selectedfeatures0x100000001;
16KiB physical DMAallocation at0x1f821000; seven IRQ-pulse completions:
T/Rversion100/101, attach104/105, walk110/111, lopen12/13,
read116/117, clunk120/121 twice. Read response52B includes41B exact expected
synthetic content. Applicationrc0; QEMUstopped/reaped0.

Important configuration dependence: first real adapter run reached F1READY but
timed out on first pulse. PCI config interruptline11 vs QNXreportedIRQ10.
Following existing QNX PC collector pattern, second actual probe changed ONLY
own9P PIRQ_D routing from0x0b0b0a0a to0x0a0b0a0a via qtest and verified readback.
Driver ELF/source unchanged. All responses and read came from actual QNX DMA/
IRQ path, NOT qtest-synthesized replies; qtest supplied chipset route only.
This does not prove default routing, physical devices, general interrupts,
resilience or a mounted filesystem works. Earlier failure is preserved.

Three native VM attempts total: first transfer/hash-tool gate aborted before
adapter execution; second default-route actual adapter rc1; third route-bound
actual adapter rc0. No native memory caps changed; max peaks792915968B,
643567616B,677834752B respectively; all memory.events max/oom/kill0.
Only fresh synthetic readonly corpus exported withsecurity_model=none.

Sole SDK boot completed installed inventory and HostShare/EDUstandalone builds,
374 monitor samples, peak1190170624B under2147483648B, minimumscopeheadroom
957833216B, reserve64MiB preserved, swap0 and max/oom/kill0. SDKstopped/reaped
before native start. No imagebuild/customIFS/reinstall/login/repair happened.
Native uses historical prebuilt image, not new stock evidence.

SDK stock metadata and EDU standalone outputs are in STOCK-RELAY.md; cleanstock
image and stock SSH/SCP/SFTP remain UNVERIFIED. Parent owns EDUcontinuation;
no correctedsource or EDUrepository mutation. All guests stopped, leasefree.

Exact raw serial logs kept locally with hashes in serial-preservation.json.
Committed serial redacts encoded ownELF upload/readback bytes to avoid executable
artifacts inGit; protocol/IRQ/probe/error lines retained. Installed SDKscripts/
headers/docs and compiledELFs remain outsideGit. Prior receipts unchanged.
No F3+, media, publicposting, PR, paidresource change, C6/CANmutation.
