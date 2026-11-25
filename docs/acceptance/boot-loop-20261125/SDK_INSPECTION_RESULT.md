# Existing licensed SDK inspection — actual result, 25 November

Parent separately admitted ONE Linux-builder inspection. Completed at approximately
22:46UTC from44bbc449; no QNX boot, compilation or image construction. Native
attempts remain1/2 used, remaining1 HELD. This supersedes only tool-availability
unknowns in OFFLINE_PROVISIONING_REVIEW.md, not historical acceptance.

## Actual tool bindings

All binaries below are existing Linux x86-64 ELF64, dynamically linked to Linux
ld-linux-x86-64.so.2; mkqnximage is an existing Bash script. Prefix for binaries:
/home/qnx/qnx800/host/linux/x86_64/usr/bin/.

- mkqnx6fsimg: bfd530ca2a944f42162491600c34cb6dea9f47e560fe4ff295b049e0284467ab
- diskimage: d73cd6cf64b9956948d2d7bc6fdfe0b041ad0e44d4bc0df4c940771940c75d2e
- mkifs: 4c48513a9e31771194dedf1d12eee7151c3ecfb5a1818d2c39dfa217926e0fb2
- mkxfs: 0124554f47965fc773a1e19aa0996d4d644a79f50f57be185b998997e4e3c3e1
- /home/qnx/qnx800/host/common/bin/mkqnximage:
  39089b2bb5d4c450c922699185faf6bf9632e71545def36feb44d2ee246f965a

Actual mkqnx6fsimg -? returned its supported buildfile/directory/image interface
and -f target-path/uid/gid/mode/size/SHA256 manifest option. mkqnximage
--help=brief produced no body within its20s timeout; it is NOT claimed successful
help output. Direct installed source inspection resolved capacity instead.

## Concrete installed sizing and customization

Installed opt_defaults/standard documents **--boot-size=<size>** as EXTRA MB
beyond initial requirements, default0. Actual builddisk BIOS code maps0 to
BOOT_SECTORS='*80'; a nonzero value maps to '*'+(size*2048). Thus --boot-size=2
means a generated **[num_sectors=*4096]**, i.e. automatic filesystem requirements
plus4096 spare512-byte sectors. This is not a fixed2MiB total filesystem.

Installed inputs/boot_part.build includes .boot/qnx_sdp.ifs, followed by
[+optional] and output/inc/_boot_files.inc. A future local/snippets/boot_files.hs
must explicitly reset **[-optional]** before mandatory hsd/onboot entries and
set file permissions explicitly. Otherwise missing payload sources may be silently
optional. Keep exact reviewed one-shot hook and old driver; no startup changes.

Actual historical generated boot build is195 bytes, SHA256
325596d509f681b955a42dacc3e049aba98b6a4e6b935d7f6b4e7329f1d3d664:
search paths, [num_sectors=*80], [+dupignore], original IFS mapping, [+optional].
No additional original boot file existed. Historical mount_fs.sh confirms
/boot mounted, /boot/onboot invoked via ksh, then system/data mounted.

## Highest-confidence construction recommendation — NOT executed

Use **direct licensed filesystem construction and disk assembly in a NEW HS
private directory**, preserving original IFS/system/data byte-for-byte. This avoids
a needless mkifs rebuild; the derived disk still requires a new trust boundary. Installed
builddisk always calls mkifs for the b lane; do not assume --build=b preserves IFS.
Installed --part-sizes is an installer/update path: do not use it as a shortcut.

Exact future recipe for parent review/admission:

1. Copy the pinned ORIGINAL raw disk/IFS and exact old driver/hook into a new
   private staging directory. Hash and compare all inputs. Derive the existing
   system/data partition blobs by bounded read-only MBR slicing, not filesystem
   rewriting. Current original MBR entries (sector size512):
   boot type177 start1 count22152; system type178 start22153 count154088;
   data type179 start176241 count125216. Require signature/types/bounds/no overlap
   and original disk SHA before extracting. Hash every extracted partition.
2. Create a reviewed buildfile using [num_sectors=*4096], explicit required
   mappings for /.boot/qnx_sdp.ifs, /hsd mode0755 and /onboot mode0644, uid/gid0.
   Use absolute staged source paths and [-optional]; do not inherit global
   optional/dupignore. Invoke installed mkqnx6fsimg -f file-manifest.txt
   boot.build boot.part once. No mkifs/compiler needed.
3. Compute actual generated boot.part sectors from exact output length. Assemble
   a NEW disk using licensed diskimage and an explicit layout with sector_size512,
   heads1/sectors_per_track1/start_at_cylinder1; partitions177/178/179; original
   system/data sector counts; new boot sector count; cylinders=sum(counts)+1.
   Installed rundiskimage uses **diskimage -p -s 163840 -c <layout> -o <newdisk>
   -b $QNX_TARGET/x86_64/boot/sys/ipl-diskpc1-nomsg** for this BIOS layout.
   Hash/bind that existing IPL input before use. It was identified in installed
   source but its file hash has NOT yet been inventoried; fail closed if missing.
4. Independently compare assembled system/data slices with originals, and extract
   all three boot files for exact bytes/modes checks. Verify capacity, collect -f
   SHA256 manifest, exact commands/tool hashes/buildfile/layout/IPL hashes and
   original/derived disk hashes. Preserve external IFS exactly; no IFS rebuild.
   Offline-derived provenance must be separately admitted by the runner; do not
   mint a native-prepared pin. Parent reviews before final coldboot grant.

Read-only MBR slice extraction is not a QNX filesystem writer. Licensed
mkqnx6fsimg creates the filesystem and diskimage creates the partition table;
no hand-written allocation bitmap/inode/boot-sector patch is proposed. If any
preservation/bootloader behavior is unsupported, stop before native execution.

## Actual bounds, cleanup and evidence

One existing Linux guest1024MiB/smp1/TCG256; network=none; canonical exclusive
lease; CPU100%, nice15; host memory.max2147483648, memory.swap.max0,
reserve67108864. Peak898359296 bytes,446 guard samples, max/oom/oom_kill0.
Guest inspection rc0; final INVENTORY_DONE; ACPI system_powerdown accepted;
owner/child exit0, stopped/reaped, no forced quit. Independent final QEMU process
check empty, lease FREE, pending queue empty. Historical running markers retained.

Original stock IFS/disk and failed overlay hashes independently unchanged.
Client171b6fae... and driver36478be0... untouched. No installation, login, spend,
network, QNX boot, restart, CAN/EDU/C6/media/publication or image construction.
Linux OS boot necessarily updates its existing builder disk; SDK/content reads
were read-only and no SDK configuration was changed.

Raw inventory64622 bytes remains PRIVATE, SHA256
67021340da1d34195698508077ddf1c9e72133b040611408371a55abcb574956.
Private recipe/owner/serial/memory/receipt stay under .local/sdkInspect25;
no licensed script body or binaries are committed. Sanitized receipt is adjacent.
81 HOST tests, portable strict C/config tests, compileall and whitespace PASS.
Two preparation quoting errors occurred before any guest launch; corrected and
syntax checked. Exactly one admitted builder was launched; no retry occurred.
