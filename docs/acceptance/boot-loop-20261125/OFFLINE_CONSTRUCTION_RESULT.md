# Offline boot construction — HOST verified, native NOT_RUN

Parent approved steps1–4. HOST gate commit93b65f3 pushed and CI45716775119
SUCCESS before execution. One capped existing Linux SDK builder launched once;
only licensed mkqnx6fsimg and diskimage built image bytes. No mkifs/compiler,
installation/login/network/spend, no QNX boot. Final QNX attempt remains HELD.

## Actual result

New derived raw disk156480000 bytes:
9452f062a4f4ad13d58735b5fee0aafe400403e585773b275ac5b83e5ce3e6fe

Boot filesystem13475840 bytes /26320 sectors, original11341824 /22152 sectors.
Required [num_sectors=*4096] requested2MiB extra; independent read-only inspection
found **2433024 nominal metadata-free bytes**. This is offline capacity evidence,
not a claim of guest allocatable capacity or successful boot.

Actual three regular files independently extracted/hashed/mode-checked:

- .boot/qnx_sdp.ifs10910404 bytes0644, exact original68bbe1b49a9b723c09d152773ee323ec6ab576eb29de933bfe3f08fdae21c753
- hsd51528 bytes0755, exact old driver36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75
- onboot294 bytes0644, exact unchanged hookbc85c70cf0fc6e3f55bec8498b12c05df2786681f352be8120361d9921045e73

Licensed -f file manifest agrees on bytes/modes/hashes and uid/gid0. Original
system/data partition sizes and every byte preserved despite relocated starts;
partition SHA256s in adjacent sanitized JSON. Original stock raw disk/IFS and
failed qcow2 hashes independently unchanged. Existing SDK client171b6fae... kept.
Existing IPL334 bytes independently bound before tool invocation and rehashed:
19e4d52a36882545f1dfb5f4f23814733aa497d3036bf556b60ea45b5c054e40.
Both licensed tool hashes exactly matched actual prior SDK inspection.

## Distinct admission, not fake native preparation

New hostshare.offline-derived.v1 provenance plus hostshare.offline-overlay.v1
binding are validated independently. Neither is a hostshare.boot-overlay.v1
native-prepared receipt. They bind actual tool/IPL/source/build evidence, exact
IFS/driver/hook/config, original/derived disks and fresh runtime overlay.

Private workspace artifacts under .local/offline25:

- derived.raw — reviewed raw disk (also preserved at builder shared output)
- offline-derived.json — SHA2567904955a5492d815c99c9b6a7729145b3093ba493b0429a4071f595b83a26640
- runtime.qcow2 — pristine overlay, SHA256a24e90ad1b1315a0670245bf1b68bec9d1224eeca35b4853dab3b46b8a91d024
- offline-overlay.json — distinct runtime binding
- file-manifest.txt/tool-ipl.json/commands.json/disk.layout/boot.build/build-result.json

Parent must independently review before final native grant. Planned runner uses
original HS_IFS, derived HS_DISK, old driver/source manifest, actual SDK client,
--boot-stage verify --offline-original <original-raw-disk> --boot-pin
<offline-overlay.json> --boot-overlay <runtime.qcow2> --conformance and real client
options. NO --stock-pin override and no fabricated native preparation. Passive
MOUNT READY before first host command, readonly share, conformance/client readback,
explicit stop/reap remain unchanged. No runtime invocation occurred here.

## Bounds, cleanup, tests

Guest1024MiB/smp1/TCG256, networknone, CPU100nice15, host2GiB/swap0/reserve64MiB.
Peak1203650560 bytes,603 guard samples, max/oom/oom_kill0. Tool recipe rc0,
OFFLINE_BUILD_DONE. ACPI shutdown had slow finalrd stop but completed within
owner bound, exit0/reaped; no QMP quit/forced kill. Final independent QEMU empty,
queue empty, canonical lease FREE. Historical running markers preserved.

89 HOST tests PASS, including8 new bounded MBR/parser/buildfile/admission negatives;
original IFS read-only hash corroboration PASS; strict C/config/conformance compile,
compileall and whitespace gates passed in preconstruction CI. Postconstruction
independent content/preservation/capacity/provenance/overlay checks PASS.
Inspector remains a bounded reader, not fsck/allocation/ACL verification. No
hand-written QNX filesystem writer or blind patch was introduced.

Preparation had a quoting failure and a JavaScript method typo before effects;
corrected and tests passed before guest construction. No tool/guest retry occurred.
No C/D, CAN/EDU/C6, media, restart, public posting or historical-pin changes.
