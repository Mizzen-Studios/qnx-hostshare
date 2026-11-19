# Read-only developer handoff (19 November)

Current status: fresh custom dev-inputs,/mnt/dev-inputs native conformance PASS;
current default f0test,/mnt/host native compatibility BLOCKED by serial ELF
transfer timeout COPY_6912 before probe/mount. Full item4 remains incomplete.
HOST38 tests pass; no speed or latency claim. See the dated result below.

Purpose: edit development inputs on Linux and read them from QNX without
rebuilding an image. This is a bounded diagnostic resource manager, not a
writable or production filesystem. Current-source native acceptance is reported
separately in [the dated result](acceptance/developer-handoff-20261119/RESULT.md).
Do not infer it from host CI or the older binary's receipts.

## Existing licensed setup only

Use the [existing bounded stock launch prerequisites](RUN_NATIVE.md), one shared
native lease, CPU100%, host2GiB/no swap, nice15, smp1, TCG256, guest512MiB and
64MiB reserve. Stop/reap SDK before native. No install, activation, image build,
IRQ rewrite or MSI-X fallback is required by this handoff. Existing reviewed
stock artifacts may be reused, explicitly not called a newly built image.

Build current sources using the RUN_NATIVE recipe (including native/conformance.c)
and retain the build log plus fresh complete source/ELF manifest. Historical ELF
pins remain historical; never promote an old ELF by regenerating its manifest.

Create an ordinary-file export on the host, e.g. /absolute/development-inputs.
The command below validates all inputs and PRINTS an add-on; it does not launch:

~~~sh
python3 tools/handoff-command.py --tag dev-inputs --mountpoint /mnt/dev-inputs \
  --export /absolute/development-inputs --elf "$HS_ELF" \
  --manifest "$HS_BUILD_MANIFEST" --ifs "$HS_IFS" --disk "$HS_DISK" \
  --stock-pin /absolute/trusted-stock-pin.json
~~~

Add its printed -fsdev/-device arguments to the existing bounded stock QEMU
command, replacing any prior HostShare export (one 9p device only, unique
fsdev id). Keep readonly=on, snapshot=on for the base disk and no qtest/PIRQ
changes. Transfer the verified ELF to /data/hostshare in QNX using the documented
serial route. Synthetic parents such as /mnt may be absent; target /mnt/dev-inputs must NOT exist:

~~~sh
/data/hostshare --pci-line --mount --tag dev-inputs --mountpoint /mnt/dev-inputs
~~~

From another QNX client: cat /mnt/dev-inputs/input.txt. On the host, edit
/absolute/development-inputs/input.txt, then open/read it again in QNX. No image
rebuild is involved. Guest write/create opens are denied; host editing remains
possible because QEMU's readonly export is not a host-directory permission
change. Close/reopen for changed files; no broad cache-coherence guarantee.

Default compatibility: omitting --tag and --mountpoint retains f0test and
/mnt/host, including --pci-line --mount. Tags: 1..31 ASCII alphanumeric/_.-,
not dot/dotdot. Mountpoints: absolute /mnt/... only, <=255 bytes, components
1..63 ASCII characters as above, no empty/dot/dotdot components. Duplicate,
unknown or missing options fail before device access. Mismatched device tag
fails before queue setup. Mount collisions and symlink ancestors fail rather
than shadowing an existing path. Absent prefixes are supported by QNX resource-manager attachment; existing ancestors must be ordinary directories. Use trusted, quiescent parent namespaces;
validation is not protection against malicious concurrent namespace replacement.
Export preflight rejects symlinks, special files, whitespace/comma paths.
Do not add symlinks or special files after validation; no adversarial-host claim.

## Conformance runner

~~~sh
sh tools/run-native-suite.sh --image-kind stock --run-id handoff-custom \
  --tag dev-inputs --mountpoint /mnt/dev-inputs --conformance
~~~

Uses a disposable seven-file corpus (not your arbitrary development folder).
Repeat with a fresh run-id and no tag/path options for default compatibility.
The native client emits 288 actual offset/read byte results (empty, 1-byte,
4KiB and 1MiB; zero/partial reads, boundary and beyond-EOF; two clients), four
directory iterations including rewind and five denied mutation opens. The host
oracle independently slices host bytes, rejects duplicate/missing cases and
checks unchanged corpus hashes after denials. Conformance adds 180 named files
to force more than one 4000-byte 9p directory reply, and compares all directory
names twice per client. This is a planned native gate, not evidence until run. No server-death lane is added.
Legacy EIO-only diagnostics stay unchanged; current reviewed death contract is
ESRCH3, not mapped to EIO5.

Unsupported negative contract: writable opens, create, truncate, append are
refused; chmod/chown/utime handlers are disabled; rename/unlink/mkdir and other
mutation operations are not implemented. No false PASS for unexercised ops,
write-enabled mode, active-DMA safety, MSI-X or production readiness.
