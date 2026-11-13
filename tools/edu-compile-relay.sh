#!/bin/bash
set -euo pipefail
export HOME=/home/qnx EDU_PREP_EXECUTION_GRANTED=yes EDU_SDP_ENV=/home/qnx/qnx800/qnxsdp-env.sh EDU_SOURCE_DIR=/mnt/host/hostshare-native-20261113/edu-handoff
for phase in wrong finish; do
 export EDU_OUTPUT=/mnt/host/hostshare-native-20261113/edu-$phase
 bash "$EDU_SOURCE_DIR/compile-lesson-PLAN.sh" "$phase"
done
