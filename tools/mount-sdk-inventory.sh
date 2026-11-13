#!/bin/bash
set -eu
out=/mnt/host/hostshare-mount-20261113/private
mkdir -p "$out"
inc=/home/qnx/qnx800/target/qnx/usr/include
for f in sys/iofunc.h sys/resmgr.h sys/dispatch.h sys/iomsg.h dirent.h; do cp "$inc/$f" "$out/$(basename "$f")"; done
find /home/qnx/qnx800 -type f \( -name '*iofunc*html' -o -name '*resmgr*html' -o -name '*msix*html' \) | head -100 > "$out/docs-paths.txt"
while IFS= read -r f; do cp "$f" "$out/$(basename "$f")"; done < "$out/docs-paths.txt"
sha256sum "$out"/*
