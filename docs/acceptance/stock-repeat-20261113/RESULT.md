# Cold-reader / clean-stock repeat — stopped for review

**PARTIAL_PRECISE_BLOCKED**, not all gates PASS. Prior28882093 N1c/idle-N5 acceptance and every historical receipt remain unchanged.

## Fresh measured results

- **Cold reader launcher PASS:** authenticated HTTPS clone, clean checkout44a2ffc3fdcd9a6de035d10f6bff134504826b1d, exact README/RUN_NATIVE environment and commands, no edits in clone, serial transfer/exact ELF hex readback. Cold-reader gaps fixed: no historical CANOPY boot-marker assumption, mkdir /data/hostshare, exact full seven-file fixtures and independent hashes/checksums, explicit image kind/stock hash checks, TCG256+HOST2GiB bounds, fresh run-id and documented external prerequisites. Host CI43415115066 SUCCESS, separately not native proof.
- **Historical native repeat PASS for data gates:** no qtest/PIRQ mutation; default IRQ11 probe byte-exact41B; mount/list; all7 independent POSIX checksums including empty,1B,4KiB,1MiB,nested,Unicode; denied write; host edit seen without rebuild in0.181886312s; SIGTERM0.
- **N7 new CLEAN STOCK native mount repeat PASS:** the new handed-off stock IFS/disk, not CANcustom. Default IRQ11 probe byte-exact41B; mount/list, all7 checksums and denied write PASS; host edit0.136499088s without rebuild; SIGTERM0. IFS/disk hashes match upstream before/after, fresh QEMU snapshot each boot, serial only. No stock SSH claim (known sshd boot memory fault, not repaired).
- **Post-kill native remount/read PASS on both:** new server resets/attaches, serves hello and correct1MiB checksum2572415250/1048576, SIGTERM0.

## Required MIDREAD EIO gate: BLOCKED, actual errno is3 not5

Explicit opt-in diagnostic scheduling window: the native POSIX client opens normally, calls read; server receives actual _IO_READ, logs rcvid/count4000/offset0, and pauses before submitting its RPC. Harness observes handler-enter and CALL_BEGIN with no RESULT, then SIGKILLs the server; server wait137. This is actual client blocked in read, NOT active virtio DMA crash safety.

Historical client: **read n=-1, errno=3, EIO constant5**, elapsed1.157177s; client wait3.
Stock client: **read n=-1, errno=3, EIO constant5**, elapsed1.139556s; client wait3.

No EOF, timeout or missing result was treated as EIO. No errno translation or hidden client shim. The QNX server-death return is errno3 (ESRCH), **not the requested EIO**. A killed resource manager cannot itself reply EIO after its death. A surviving supervisor/frontend or explicit documented client-boundary error policy would be a different failure contract and needs review; do not relabel this observed result or infer an EIO PASS. No further native/SDK retry undertaken to hide this failure.

## Source, artifacts, failure preservation and bounds

- ELF84bb0bd51836e8e9e6f06f1abd97221974e43a3fc5429ea60c7e66493d19e959,42736B. Build-source-hashes binds all core/native C/header bytes. Source updates add opt-in pause and actual native read observer; normal transport/data path unchanged.
- Stock IFS68bbe1b49a9b723c09d152773ee323ec6ab576eb29de933bfe3f08fdae21c753; disk0aee00c281f8eeb5b02c66555ed9517e317bb1503002a19dbf2b0155de336532. Licensed artifacts stay external, not Git.
- SDK boot once512MiB, first compile type-format failure retained; corrected cast compiled to NEW build2 in same boot. SDK peak883838976B; native peaks723689472B historical /597225472B stock. HOST2GiB, TCG256MiB,guest512,CPU100,nice15,smp1,swap0,reserve64. All observed max/OOM/kill/reserve violations0.
- Full immutable native memory logs stay in the clean clone .local; memory-summary.json indexes their exact hashes, sample counts and all-sample maxima/event checks. Native receipts/serial/failure logs committed unchanged. SDK full samples retained. MANIFEST binds tracked evidence; finalizer rechecks external full memory hashes and all source/image gates.
- Host20 tests + portable C strict build/tests + Python/shell syntax PASS, not substitutes for native evidence. Demo still recorded/published/media_generated false. No MSI-X/EDU retry, routing rewrite, CAN/C6, image build/install/login/repair, paid resources, media/public/PR.

All SDK/native guests stopped/reaped, zero QEMU, canonical lease FREE. **STOPPED for parent review; no next guest authorized by this result.**
