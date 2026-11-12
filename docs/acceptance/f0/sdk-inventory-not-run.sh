#!/bin/bash
set -u
export LC_ALL=C
printf 'SDP_INVENTORY_START
'
find /home/qnx/qnx800 -maxdepth 2 -type d | head -60
printf '
9P_INPUT_FILENAME_SCOPE: all installed /home/qnx/qnx800 filenames
'
find /home/qnx/qnx800 -type f | grep -Ei '(^|/)([^/]*(9p|virtio|input)[^/]*)$' | head -250
printf '
BOUNDED_METADATA_TEXT: documentation/catalog/pkg metadata filenames, max 1500 files max1MiB each
'
find /home/qnx/qnx800 -type f -size -1024k | grep -Ei '(doc|manifest|catalog|package|metadata).*(txt|xml|json|html|md)$' | head -1500 | while IFS= read -r f; do grep -IinE 'virtio.?9p|9pfs|devb.*9p|virtio.?input' "$f" 2>/dev/null | head -5 | sed "s|^|$f:|"; done
printf '
MKQNXIMAGE_HELP
'
su -s /bin/bash qnx -c 'source /home/qnx/qnx800/qnxsdp-env.sh >/dev/null; command -v mkqnximage; timeout 25 mkqnximage --help' 2>&1
printf '
PREBUILT_STOCK_PATHS
'
find /home/qnx/qnx800 -type f | grep -Ei '(qemu|ifs|prebuilt|.build$)' | head -150
printf '
SDP_INVENTORY_DONE
'

printf '
INSTALLED_MKQNXIMAGE_RUN_HELP
'
su -s /bin/bash qnx -c 'source /home/qnx/qnx800/qnxsdp-env.sh >/dev/null; for h in run ram cpu tcg build proc; do echo HELP=$h; timeout 10 mkqnximage --help=$h 2>&1; done'
printf '
EXISTING_STOCK_IMAGE_SIZES
'
find /home/qnx/qnx-work -maxdepth 6 -type f | grep -E '(ifs|disk|qemu|mkqnximage)' | head -120 | while IFS= read -r f; do stat -c '%s %n' "$f"; done
printf '
EXISTING_QEMU_LAUNCH_TEXT
'
find /home/qnx/qnx800/host/linux/x86_64 -type f -name '*mkqnximage*' -print
