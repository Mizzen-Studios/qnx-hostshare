# Independent offline provisioning review — 25 November 2026

Status: HOST investigation only; no new disk, IFS, SDK execution or native PASS.
Reviewed source tip: 06e7aaecd79035ef5ba27bad7b85a6c201c83543.
QNX attempts remain 1/2 consumed, final attempt HELD. Failed overlay is ineligible.

## Findings that unblock the investigation

The relevant licensed offline writer is **mkqnx6fsimg**, not a presumed
mkqnx6fs executable. QNX8 official documentation explicitly supports Linux
and Windows hosts, file manifests with SHA256 via -f, explicit num_sectors,
and filesystem creation from a buildfile/directory. This is not an in-place
filesystem repair tool. Do not write a QNX filesystem by hand.

Actual retained installed mkqnximage script has boot_files in its group_list
(line6), alongside ifs_files/system_files/data_files. Retained installed SDK
mkqnximage documentation names mkqnx6fsimg as its filesystem builder and
local/snippets as its customization interface. Therefore an existing licensed
image-building route is evidenced, not a request for a new SDK installation.
The precise boot capacity option and current mkqnx6fsimg binary/hash still
require an admitted Linux-builder inspection; they are NOT established here.

Actual retained successful stock artifact inventory lists these guest files:

- /home/qnx/edu-clean-stock-1024-20261113/output/build/boot_part.build (195 bytes)
- output/build/disk.layout (301 bytes)
- output/build/generate_files (757 bytes)
- output/build/mount_fs.sh (1628 bytes)
- output/inc/_boot_files.inc (empty in original stock build)

These are the highest-value next reads. They establish the exact installed
boot builder, partition sizing and assembly commands without inventing flags.
Their contents were not exported in the retained host inventory. Do not touch
or rerun that historical EDU directory: read only, then work in a NEW HS directory.
The retained SDK launcher source is HOST-private under
hostshare-native-20261113/private/mkqnximage-script. mkifs is historically
observed at /home/qnx/qnx800/host/linux/x86_64/usr/bin/mkifs; mkqnximage at
/home/qnx/qnx800/host/common/bin/mkqnximage. None of mkifs, mkqnximage,
mkqnx6fsimg was found on this ARM host PATH. qemu-img is present, but is not a
QNX filesystem writer.

## Read-only stock inspection actually performed

Preserved the stopped worker's untracked tools/qnx6_inspect.py unchanged:
SHA256 50c063add4879770958b6673c0cc30c41a69a886689ecf4ba5fdd044032eeb11.
It opens the raw disk rb and has no filesystem write path. Ran it against the
original independently pinned stock raw disk, not the failed qcow2 overlay:

- raw disk SHA256 before/after: 0aee00c281f8eeb5b02c66555ed9517e317bb1503002a19dbf2b0155de336532
- type177 boot partition 11341824 bytes; blocksize4096; blocks2765; selected serial3
- metadata free blocks91 (372736 nominal bytes, NOT allocatable-capacity proof)
- inode count32; root contains only dot/dotdot/.boot
- sole regular file .boot/qnx_sdp.ifs:10910404 bytes, mode0100644
- extracted file SHA25668bbe1b49a9b723c09d152773ee323ec6ab576eb29de933bfe3f08fdae21c753
  exactly matches the independently pinned original IFS

Eight bounded negative checks rejected: short disk, corrupt MBR signature,
corrupt first-superblock CRC, negative block, block==block count, 0xffffffff
block pointer, unsupported tree level3, oversize tree. Synthetic negative copies
were temporary workspace-local files and removed by TemporaryDirectory.

This is a useful corroborating inspector, NOT a general filesystem verifier or
trusted provisioning authority. Independent code review found missing robust
resource caps/partition overlap checks; whole inode tables/files are buffered,
recursion is unbounded, constructors leak their file on validation failure, and
both superblocks must pass CRC rather than supporting recovery. It rejects
long names/special inode types; it does not verify allocation bitmaps, ownership,
all inode checksums/ACLs, bootloader or filesystem consistency. Keep read-only;
do not grow it into a writer. Linux-source retrieval attempts at v6.12/v6.6/v6.1
returned404, so no independent Linux-source-layout verification is claimed.

## Exact next admission requested from parent — inspection ONLY

One separately admitted existing Linux SDK builder session, NO QNX boot,
network disabled, same canonical lease and caps as successful client build:
1GiB guest/oneCPU/TCG256, host2GiB/swap0/reserve64MiB, CPU100%, nice15,
bounded inspection then ACPI stop/reap. No install/login/spend. Adapt the reviewed
client owner recipe to a NEW private output directory; do not execute/reuse its
already-completed owner.py or overwrite its receipts. Read only:

1. Source /home/qnx/qnx800/qnxsdp-env.sh; command -v and SHA256/readelf for
   mkifs, mkqnximage, mkqnx6fsimg, mkxfs, diskimage. Absence fails closed.
2. Read the historical generated boot_part.build, disk.layout, generate_files,
   mount_fs.sh and corresponding installed common/generate/definitions snippets.
3. Capture installed mkqnximage --help=brief, then only evidenced boot-size
   option help; capture mkqnx6fsimg -? under a short timeout. No --run/--build.
4. Export these limited private text inventories and stop/reap. Parent reviews
   exact commands before any derived-image construction. If files are missing,
   report that blocker; do not rebuild EDU to recover them.

## Recommended construction decision AFTER those reads

Prefer the installed generator's boot_files customization plus explicit spare
boot capacity in a NEW HS-only image directory. If existing generator permits
reusing exact IFS/system/data blobs, preserve them byte-for-byte and reconstruct
only the boot filesystem/assembled disk with licensed mkqnx6fsimg/diskimage.
Otherwise a fresh derived mkqnximage build is a NEW image trust boundary, not
historical stock acceptance. Exact command/size knobs must follow captured
installed code; no ad-hoc writer, boot-sector patch, borrowed EDU run or filesystem
expansion guess is approved. Include original .boot IFS, exact old driver hsd and
exact hook onboot, with explicit modes and adequate spare capacity (e.g. target
at least1MiB spare beyond payload plus filesystem metadata, verified by output).
Use the reviewed one-shot hook unchanged; no mount-order/restart workaround.

Before final coldboot: independently inspect derived content/permissions and
all retained partitions/IFS, compare file bytes with exact original driver/hook,
keep a licensed -f SHA256 file manifest and full tool/source/build provenance,
record real capacity, hash/pin new artifacts, stop/reap builder. Base disk, base IFS,
failed overlay and all historical pins remain untouched. SDK client171b6fae...
and old driver36478be0... remain valid separate artifacts, not rebuilt by this plan.

## Runner gate that must not be bypassed

Current verify expects an overlay backed by its selected raw disk and a sealed
hostshare.boot-overlay.v1 pin. That pin historically means successful QNX
prepare/readback/unmount. An offline provisioner must NOT fabricate that success.
The runner also checks the stock IFS/disk pin; --stock-pin can select new hashes
but does not itself grant derived-image trust. Before using the final attempt,
add/review/test a distinct offline-derived provenance/admission contract (or an
explicitly reviewed equivalent), binding original+derived disk, exact IFS,
licensed tool manifest, extracted payload hashes/modes and hook configuration.
Then create a fresh private runtime overlay of the reviewed derived raw disk.
Existing passive-ready-before-any-host-command, readonly share, conformance,
actual SDK client readback/run, explicit stop and reap gates must remain intact.
Do not relabel HOST checks as native or launch the failed overlay.

## Official references

- https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkqnx6fsimg.html
  Retrieved HTTP200 during review; explicit Linux/Windows, -f SHA256 manifest,
  num_sectors and spare sizing documented.
- Retained installed SDK mkqnximage.html and mkqnximage-script, privately inspected.

No SDK/QEMU/lease/record execution, no image changes, CAN/EDU/C6 or publication
occurred in this investigation. Native completion remains NOT_RUN/HELD.
