# F0 — stopped for parent review

Native device feasibility PASS: real QNX 8.0.0 guest, pci-server PID28676,
`pci-tool -v` rc0 lists B000:D04:F00 vendor/device 1af4/1009 (virtio 9p).
QEMU accepted the exact fsdev security_model=none, readonly=on command.
Only the fresh synthetic corpus .local/f0-corpus was exported. Nothing mounted
or exercised 9P in QNX; this is enumeration, not a working filesystem driver.
`pidin ar` was captured. `pci -v` fails rc126; retained as an attempted
fallback command, not hidden. Startup also logs a memory fault around sshd;
no SSH success, platform-health or broader native acceptance is claimed.

Overall F0 BLOCKED: the installed-SDP novelty inventory could not execute.
The only SDK boot, default512MiB at unchanged CPU100%, HOST1GiB, swap0,
nice15 and smp1, was OOM-killed before ready at21:09:53UTC. The owner reaped
its child; stop command failed connection-refused because QEMU was already dead.
No SDK retry, cap adjustment, swap, repair or image build was attempted.
Thus absence of an installed QNX8 guest9p driver is UNVERIFIED.
No virtio-input fallback is needed: 9P host/native enumeration succeeded;
input native F0 remains NOT_RUN. No F1+ work authorized or implemented.

## Exact public search scope

On2026-11-12 queried first100 qnx-ports repositories, GitHub repository search
org:qnx-ports 9p, first30 indexed code hits for 9p, then indexed code searches
virtio-9p, 9pfs, virtio-input and virtio_input in org:qnx-ports. Specific searches
returned0; broad9p143 hits were unrelated snippets and are not absence proof.
Fetched oss.qnx.com index and its own public package API, package_name substring
queries9p,virtio,input size100. 9p returned0. Virtio results are screen packages;
input first100 results are Linux input-code headers and multimedia input packages.
All raw responses and URLs retained. These bounded searches do NOT prove global
absence, nor do they substitute for the blocked installed-SDP inventory.

## Provenance limits

Native receipt binds exact prebuilt IFS, disk, three existing application ELFs,
recorded prebuilt source SHA, and current collector source. Historical source
snapshot has no .git directory: recorded source SHA is provenance metadata,
not a newly verified clean rebuild. No SDK binary/image/disk is committed.
SDK full serial retained locally at .local/sdk-serial-full.txt; committed tail,
scope result and journal cover this failure without unrelated historical logs.
EDU requested mkqnximage help/run/stock inventory NOT_RUN because SDK never ready.
No CAN/EDU checkout was changed. Future kill gate documented in README only.
