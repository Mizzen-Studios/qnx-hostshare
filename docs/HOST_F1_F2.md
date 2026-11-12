# Host-only F1/F2 reference work — NOT native PASS

Owner Nov12 22:01 followup permits this source/testing wave. Historical F0
receipt remains unchanged. F0 device feasibility accepted; installed-SDP absence
remains UNVERIFIED. SDK diagnosis at acceptance/followup-20261112/diagnosis.json
finds no justified clean-boot change, so no QEMU was started in this wave.
Installed mkqnximage --help=run, options and stock paths unavailable; EDU must
not infer those from web docs or the earlier prebuilt native image.

## F1 host model

Python reference parser checks modern PCI vendor capability list, cycle,
alignment, region bounds, required common/notify/ISR/device capabilities and
notify multiplier. Negotiates VERSION_1+MOUNT_TAG only. Bounds mount-tag config.
OneQueue is a one-outstanding-request mock with descriptor/response-size limits,
completion identity validation and pulse callback interface. It is NOT a real
virtqueue ring or QNX interrupt implementation: no MMIO, DMA, memory barriers,
physical mappings, FEATURES_OK handshake or native interrupt/pulse delivery.

## F2 host model

Strict 9P2000.L framing subset: version, attach, walk, read, clunk, flush,
Rlerror and responses. Rejects bad lengths, trailing bytes, unsupported types,
reserved/mismatched tags, invalid live fids, overlong walks and oversized frames.
Not a complete session/fid lifecycle manager, filesystem, resource manager,
mount, directory service or production parser security assurance. No F3+ work.

## Fixture provenance

All PCI config bytes and 9P wire vectors in tests are synthetic specification-
derived fixtures authored here. The literal Tversion hex vector is independently
written rather than produced by the encoder under test. Mock request/response
bytes are captured in-process, never from QEMU, QNX, hardware or a live 9P server.
No native captured protocol frames exist. Historical F0 native serial is PCI
identity evidence only, not modern-capability or protocol negotiation evidence.
Definitions follow OASIS Virtio1.2 PCI transport and 9P2000.L message layouts;
compatibility with this QEMU target remains UNVERIFIED.

Run: PYTHONPATH=src python3 -m unittest discover -s tests -v

F1 native build/run and F2 native roundtrip NOT_RUN. Kill gate unchanged:
F1+F2 native PASS by29 November2026 UK, else stop. No schedule created.
