#!/bin/bash
set -eu
out=/mnt/host/hostshare-irq-restart-20261113/private
mkdir -p "$out"
inc=/home/qnx/qnx800/target/qnx/usr/include
for f in sys/procmgr.h sys/neutrino.h signal.h grp.h; do cp "$inc/$f" "$out/$(basename "$f")"; done
printf 'PRIVILEGE_HEADERS_DONE
'
