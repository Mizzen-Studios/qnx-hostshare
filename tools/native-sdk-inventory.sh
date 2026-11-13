#!/bin/bash
set -u
out=/mnt/host/hostshare-native-20261113
mkdir -p "$out/private"
printf 'INVENTORY_START
'
find /home/qnx/qnx800/target/qnx/x86_64 -type f | grep -Ei '(9p|virtio|virtiofs|pci)' | head -120
printf '
HEADERS
'
find /home/qnx/qnx800/target/qnx/usr/include -type f | grep -Ei '(pci|virtio|9p)' | head -100
printf '
MKQNXIMAGE_HELP
'
su -s /bin/bash qnx -c 'source /home/qnx/qnx800/qnxsdp-env.sh >/dev/null; command -v mkqnximage; timeout 20 mkqnximage --help; timeout 20 mkqnximage --help=run' 2>&1
printf '
MKQNXIMAGE_FILES
'
find /home/qnx/qnx800 -type f -iname '*mkqnximage*' -print
printf '
EXISTING_STOCK
'
find /home/qnx/qnx-work -maxdepth 6 -type f | grep -E '(ifs|disk|qemu|run.*sh)' | head -100 | while IFS= read -r f; do stat -c '%s %n' "$f"; case "$f" in *ifs*|*disk*) sha256sum "$f";; esac; done
printf '
API_DETAILS_PRIVATE
'
cp -r /home/qnx/qnx800/target/qnx/usr/include/pci "$out/private/" 2>/dev/null || true
cp /home/qnx/qnx800/target/qnx/usr/include/sys/neutrino.h /home/qnx/qnx800/target/qnx/usr/include/sys/mman.h "$out/private/" 2>/dev/null || true
find /home/qnx/qnx800 -type f -iname '*mkqnximage*' | head -5 | while IFS= read -r f; do cp "$f" "$out/private/$(basename "$f")"; done
printf 'INVENTORY_DONE
'
