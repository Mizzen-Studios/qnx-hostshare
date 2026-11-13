#!/bin/bash
set -u
export HOME=/home/qnx
source /home/qnx/qnx800/qnxsdp-env.sh >/dev/null
out=/mnt/host/hostshare-native-20261113/private
cp /home/qnx/qnx800/host/common/bin/mkqnximage "$out/mkqnximage-script"
printf 'ROOT_HELP
'
timeout 15 mkqnximage --help=run 2>&1
timeout 15 mkqnximage --help=ram 2>&1
timeout 15 mkqnximage --help=cpu 2>&1
timeout 15 mkqnximage --help=tcg 2>&1
printf 'OPTIONS_FILES
'
find /home/qnx/qnx800/host -type f -name '*qnximg*' -printf '%m %s %p
' | head -30
printf 'RUNIMAGE_STOCK_CANDIDATES
'
find /home/qnx/qnx-work -maxdepth 5 -name runimage -o -name '*.qcow2' -o -name 'disk.raw' -o -name 'ifs.bin' -o -name 'disk-qemu' | head -40
for f in /home/qnx/qnx-work/can-gate/output/runimage /home/qnx/qnx-work/can-gate/output/build/runimage /home/qnx/qnx-work/can-gate/output/runimage.sh; do if test -f "$f"; then cp "$f" "$out/runimage-$(basename $(dirname "$f"))"; fi; done
printf 'METADATA_DONE
'
