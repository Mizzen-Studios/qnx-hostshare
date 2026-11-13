#!/bin/bash
set -eu
out=/mnt/host/hostshare-native-20261113/private
printf 'RUNIMAGE_PATHS
'
find /home/qnx/qnx-work /home/qnx/qnx800/host/common -type f -name '*runimage*' | head -30 | while IFS= read -r f; do stat -c '%s %n' "$f"; sha256sum "$f"; cp "$f" "$out/runimage-$(echo "$f" | tr / _)"; done
printf 'LIBRARY_PRESENT
'
ls -l /home/qnx/qnx800/target/qnx/x86_64/lib/libpci.so.3.0 /home/qnx/qnx800/target/qnx/x86_64/lib/libslog2.so.1
printf 'HISTORICAL_CUSTOM_IMAGE_NOT_STOCK
'
stat -c '%s %n' /home/qnx/qnx-work/can-gate/output/disk-qemu /home/qnx/qnx-work/can-gate/output/ifs.bin
sha256sum /home/qnx/qnx-work/can-gate/output/disk-qemu /home/qnx/qnx-work/can-gate/output/ifs.bin
printf 'END
'
