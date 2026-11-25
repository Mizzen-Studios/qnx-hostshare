#!/bin/bash
set -eo pipefail
export HOME=/home/qnx
python3 /mnt/host/hs-dev-client-20261125/source/tools/dev-loop.py --sdk-env /home/qnx/qnx800/qnxsdp-env.sh --out /mnt/host/hs-dev-client-20261125/source/.local/qnx-client
