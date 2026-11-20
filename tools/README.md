# HostShare tool contracts

20 November 2026. Start with [the HOST judge path](../README.md); no SDK or guest is needed there. These tools are not all interchangeable launchers.

| Tool | Current contract |
|---|---|
| preview-handoff.py | HOST-only illustrative template; no SDK or external files required. Explicitly NOT VALIDATED and never launches; does not replace handoff-command.py. |
| handoff-command.py | Validate external source/ELF/stock/export bindings and print a read-only QEMU add-on; never launches. Requires real external artifacts, not a no-SDK demo fixture. |
| handoff_preflight.py / handoff_oracle.py | Validate bounded tag and mount path / HOST expected-byte oracle; HOST checks are not QNX conformance. |
| run-native-suite.sh / .py | Authorized licensed stock or historical image route; new run-id, external pins and sole shared lease required. Ordinary route checks readonly data/host edit/cooperative stop. |
| run-native-readonly.sh / .py | Readonly native runner; requires licensed external setup and separate execution authority. Not run by HOST CI. |
| stock_pin.py | Strict stock manifest and file binding checks; no arbitrary-image admission or pin replacement. |

**Historical diagnostics:** native-f0.py, run-hostshare-native*, run-hostshare-mount*, *-sdk-owner*, queue-*, finalize-* and the dated inventory/build relays preserve old experiment contracts and machine-specific assumptions. They are not the cold-reader entry route. Do not execute them as a repair recipe.

The historical --midread assertion expects EIO5 and intentionally still fails on the owner-accepted ESRCH3 result. Do not change errno translation or weaken that old exit gate. See [current contract](../docs/CURRENT_CONTRACT.md). Current custom-tag/path conformance is partial native acceptance; default compatibility is still blocked before mount. No SDK, QEMU or lease is acquired by reading this index.
