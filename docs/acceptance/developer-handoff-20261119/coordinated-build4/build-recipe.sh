#!/bin/bash
set -eo pipefail
export HOME=/home/qnx
source /home/qnx/qnx800/qnxsdp-env.sh >/dev/null
s=/mnt/host/hostshare-handoff-20261119-build4/source
o=/mnt/host/hostshare-handoff-20261119-build4/build
mkdir "$o"
qcc -Vgcc_ntox86_64 -std=gnu11 -O0 -g0 -Wall -Wextra -Werror -Wno-misleading-indentation -I"$s/core" "$s/native/qnx_hostshare.c" "$s/native/mount_checksum.c" "$s/native/conformance.c" "$s/core/transport.c" "$s/core/protocol.c" -o "$o/qnx_hostshare" -lpci
sha256sum "$o/qnx_hostshare"
