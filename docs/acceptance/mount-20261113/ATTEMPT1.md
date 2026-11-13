# Native attempt 1 — retained failure

Source c09c566; ELF b242f3779774b753f33d9232d663ba026a158b3c3e43fbd1edc20ccf244f884c.

* N1 PCI line11: real Tversion IRQ completion, then a pulse with ISR0 and unchanged
  used index1. The first implementation rejected this shared/duplicate pulse.
  No routing mutations before either N1 probe.
* N1 MSI-X: installed PCI MSI-X setup returned
  PCI_ERR_IRQ_CFG (individual setup call not logged). This is not evidence of working MSI-X.
* Authorized fallback changed only own PIRQ_D to IRQ10, separately recorded.
* Actual resource-manager cat returned original41 bytes with rc0. Write open
  rejected EROFS and host checksum unchanged. Directory ls rc0 returned no entries,
  so N2 FAIL and N3/N4 NOT_RUN (not accepted from the cat result alone).
* Peak native cgroup927485952B, no max/OOM/kill events, QEMU rc0 and reaped.

Bounded correction: keep a single absolute three-second RPC deadline while
ignoring pulses whose used index has not advanced; always acknowledge/unmask the
IRQ. Support QNX8 `_IO_XTYPE_READDIR` from installed iomsg.h, retain strict unknown
xtype rejection and use `_IO_READ_GET_NBYTES`. Same image and QEMU device options
will be used; no route writes may precede new N1 tests.
