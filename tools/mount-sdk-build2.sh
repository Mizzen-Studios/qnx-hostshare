#!/bin/bash
set -euo pipefail
export HOME=/home/qnx
set +u
source /home/qnx/qnx800/qnxsdp-env.sh >/dev/null
set -u
src=/mnt/host/hostshare-mount-20261113/source
out=/mnt/host/hostshare-mount-20261113/build2
test ! -e "$out";mkdir -p "$out"
free -k
qcc -Vgcc_ntox86_64 -std=gnu11 -O0 -g0 -Wall -Wextra -Werror -Wno-misleading-indentation -I"$src/core" "$src/native/qnx_hostshare.c" "$src/native/mount_checksum.c" "$src/core/transport.c" "$src/core/protocol.c" -o "$out/qnx_hostshare" -lpci
sha256sum "$out/qnx_hostshare" "$src/native/qnx_hostshare.c" "$src/core/"*.c
free -k
