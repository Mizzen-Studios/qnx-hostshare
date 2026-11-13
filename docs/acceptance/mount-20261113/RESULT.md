# Bounded native mount wave: N2/N3/N4 PASS with routing workaround; N1 FAIL

Original790e9b2 acceptance is unchanged. Native implementation source145c9e0;
corrected ELF715b1ed187904e6c38ce43d0799cd921acfecd27f8da776557351ccd265f60db.

| Gate | Actual result |
| --- | --- |
| N1 default route | FAIL: PCI config line11 delivers two replies, then ISR0/used3 is rejected. Installed MSI-X setup returns PCI_ERR_IRQ_CFG. No routing changes before these probes. |
| N2 mount | PASS: real resource manager at /mnt/host; cat returns original41-byte file; ls lists all expected entries; attempted write fails EROFS and host bytes remain unchanged. |
| N3 corpus | PASS: seven fopen/fread checks through mount match independent host POSIX cksum and byte count: original41B, empty,1B,4KiB,1MiB,nested19B,Unicode13B. |
| N4 edit visibility | PASS: host edit observed via fresh native cat in0.168553062s, no source/ELF/image rebuild or guest restart between edit and read. Not an open-fd/cache-coherency general guarantee. |

N2/N3/N4 use only the explicitly authorized own-device PIRQ_D-toIRQ10 workaround.
They are NOT default-route or MSI-X acceptance. Exact route old0x0b0b0a0a ->
new0x0a0b0a0a is in native3/receipt.json. Native3 explicitly references native2
N1 evidence instead of rerunning or relabeling it. QEMU argv is identical across
this wave's native attempts; compared with the original accepted attempt3 only
the fresh synthetic corpus path differs. Native keeps original accelerator argv
and stricter HOST1GiB cap. SDK-only TCG256MiB is independently QMP verified.

## Retained attempts and resources

- Native1: N1 failed; mounted cat/write-negative succeeded; directory xtype
  unsupported. N2 FAIL; N3/N4 NOT_RUN. Peak927485952B.
- Native2: corrected shared-pulse handling and QNX READDIR xtype. N1 still FAIL.
  Native directory listing succeeded, but QNX octal rendering of UTF-8 caused
  the verifier to stop. Original FAIL receipt preserved; explicit adjudication
  retained. Peak784404480B.
- Native3: unchanged source/ELF; only listing verifier corrected. Fresh real
  N2/N3/N4 PASS with workaround. Peak851124224B.
- Two serialized SDK build boots, sampled peaks1316786176B and888369152B under
  HOST2GiB; guest512MiB, TCG256MiB, CPU100%, nice15, smp1, swap cap0, reserve64MiB.
  Both SDK owners stopped/reaped rc0 BEFORE subsequent native guests.
- All native attempts have zero max/OOM/kill events and QEMU exit0/reaped.
  No guest overlap. No image rebuild, installation, login, repair, CAN/C6 or EDU
  repository changes. No paid resources, public actions or media.

Source/header/build/ELF/IFS/disk/corpus bindings and raw textual results are in
receipts. Proprietary SDK contents and executable/readback bytes remain outside
Git. Serial redaction removes own ELF transfer bytes, not gate results. Original
historical IFS/data disk are reused hash-bound and are NOT claimed stock.

All guests stopped and reaped; finalizer independently requires zero QEMU and
an acquirable exclusive lease. **Lease FREE; next slot belongs to EDU through
parent coordination. Stop for review; no additional wave authorized by this result.**

This is a bounded, single-thread, synthetic read-only resource manager. No
production filesystem, general default routing, physical hardware, concurrency,
reconnect, complete error recovery or broad coherency acceptance. Independent
read-only reviewer timed out without findings; no completed-review claim.
