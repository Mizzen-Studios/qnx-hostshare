#!/bin/sh
# No qtest, PIRQ write, automatic fallback, installation or image build.
set -eu
: "${HS_ELF:?Set HS_ELF to the externally built QNX executable}"
: "${HS_IFS:?Set HS_IFS to the existing authorized IFS}"
: "${HS_DISK:?Set HS_DISK to the existing authorized data disk}"
: "${HS_BUILD_MANIFEST:?Set HS_BUILD_MANIFEST to source/ELF hash metadata}"
for f in "$HS_ELF" "$HS_IFS" "$HS_DISK" "$HS_BUILD_MANIFEST"; do test -r "$f" || { echo "Missing prerequisite: $f" >&2; exit 2; }; done
cd "$(dirname "$0")/.."
# Choose one absolute shared lock for ALL guest/SDK owners; never per-run locks.
HS_LOCK=${HS_LOCK:-/home/ubuntu/qnx-host/native-test.lock}
case "$HS_LOCK" in /*) ;; *) echo 'HS_LOCK must be absolute' >&2; exit 2;; esac
export HS_LOCK
# Selected lock remains exclusive across every guest lifetime.
exec systemd-run --user --scope --quiet -p CPUQuota=100% -p MemoryMax=2G -p MemorySwapMax=0 nice -n 15 python3 tools/run-native-suite.py "$@"
