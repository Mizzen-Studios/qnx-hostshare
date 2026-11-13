# IRQ/restart wave — stopped for review

## Actual native results

- **N1c PASS**, final clean detached checkout `ed27a3448ff043d6b7fe50467fbdb234b9e932bb`: default PCI line11, used-ring-first / ISR hint-only, byte-exact41B read, app0 and mounted cat/list. Original QEMU pc argv, no qtest, no PIRQ write, no interrupt-mode fallback. API reports10/config11; adapter attaches11. Shared unchanged-used pulses observed and ignored.
- **Clean MSI-X-only FAIL**: fresh VM, Memory Space enabled before installed set_nirq; PCI_ERR_IRQ_CFG. No preceding pci-line. Evidence uses first build; no MSI-X retest claimed for cleanup-only second build.
- **N5 measured PASS**: idle mounted process SIGKILL wait137; old mount inaccessible; new process resets/attaches/remounts and serves cat plus independently matching POSIX checksum948244384/41. After attach UID/EUID/GID65534; IO,MEM_PHYS,PATHSPACE deny-locked root+nonroot; IO and root reacquisition both fail errno1. INTERRUPT retained, other abilities not exhaustively audited.
- Final SIGTERM: TERM_DETACHED, mapped virtio status0/queue_enable0, app/wait0. Reduced cleanup skips privileged PCI backend; Bus Master disable/restore **NOT verified**, trusted QEMU only. Idle crash recovery is not active/in-flight DMA crash safety or physical/untrusted-device teardown.
- **N6 delivered**: user-visible launcher, README exact external-prerequisite clean-checkout commands, hash-bound source/ELF preflight. Final actual execution from clean detached checkout. Written demo only: recorded/published/media_generated false.
- **N7 DEPENDENCY_BLOCKED_NOT_RUN**: EDU stock mkqnximage guest OOM, no valid stock IFS/disk. This historical custom image is NOT stock. No EDU retry/repair.

## Preserved failures / provenance

`intx-clean` retains the initial successful read/mount/reduced remount but erroneous hardcoded checksum assertion and real SIGTERM post-detach fault139. `ATTEMPT1.md` explains them; neither original receipt nor logs were rewritten. Second build avoids PCI backend calls after ability drop and derives checksum from host fixture; only its fresh `intx-fixed` receipt establishes final PASS.

Final ELF SHA256 `84cecd6d797b1c27d5c0a8009fd6031d2ca3a37590ab72f0216013154fdbd10d`; current source file hashes and installed-header metadata in build2-source-hashes.json. SDK headers, executables/readback, IFS/disk stay outside Git. Original c4e4f258/F0/mounted receipts unchanged.

## Bounds / cleanup

Two serialized SDK boots HOST2GiB/cache256MiB, sampled peaks895627264B /899575808B; three serialized native boots stricter HOST1GiB, peaks921415680B /795086848B /819765248B. Guest512MiB, CPU100%, nice15,smp1,swap0,reserve64MiB. Native original pc,accel=tcg retained; native cache256 is not claimed. Native max/OOM/kill events0; raw SDK samples retained.

All guests stopped/reaped, zero QEMU and exclusive canonical lease FREE, verified by finalizer. Private existing SDK, £0, no image build/install/login/platform repair/CAN/C6/media/public/PR. Host tests17 and portable C tests PASS, separately not native evidence. Parent owns next authorization; **STOPPED for review**.
