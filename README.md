# QNX HostShare

Private Apache-2.0 feasibility project. **No QNX filesystem driver implemented.**

F0 real QNX8 pci-tool observed virtio-9p PCI1af4/1009. Owner accepted device
feasibility; installed-SDP driver absence remains **UNVERIFIED**.
Original [F0 receipt](docs/acceptance/f0/receipt.json) is historical and unchanged.

Nov12 followup: SDK OOM diagnosis preserved; no justified clean boot, so no QEMU
retry. Installed mkqnximage help/options and stock paths remain UNVERIFIED.
Host-only Python F1/F2 reference models and17 tests added; **NOT native PASS**.
See [scope, limitations and fixture provenance](docs/HOST_F1_F2.md).

Run: PYTHONPATH=src python3 -m unittest discover -s tests -v

No MMIO/DMA/native IRQ/ring driver; no native build or F1/F2 run. No F3+ work.
Stop for parent review. Future kill gate: F1 and F2 must both achieve native PASS
by29 November2026 UK, otherwise stop. No schedule created.

## Portable C host-only closure

Added [C driver-core foundation](docs/C_CORE.md): transport descriptor/hook core and9P framing.
Native adapter/rings/DMA/QNX IRQ lifecycle NOT_IMPLEMENTED; native PASS NOT_RUN.
