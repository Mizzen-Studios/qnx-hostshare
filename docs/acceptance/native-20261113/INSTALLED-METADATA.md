# Installed metadata relay,2026-11-13

SDK boot READY, existing QEMU accepted SDK-only -accel tcg,tb-size=256;
QMP reports generated code capacity268,430,336B. Guest512,smp1,nice15,
HOST2GiB CPU100 swap0 reserve64 remain checked continuously by owned monitor.

Installed mkqnximage --help=run: --run=[<options>] supports ONLY -h (headless/
background); no arbitrary QEMU -device passthrough documented. --ram=<X>[M|G]
default1G; --cpu=[1|2|3|4] default2. Explicit512M/1 required for this policy.
IMPORTANT --tcg=[yes|no|cmdline] concerns Trusted Computing Group/TPM services,
NOT QEMU TCG accelerator/cache control. Do not confuse the meanings.

qnx-user --help initially printed mkqnximg_options permission denied because
helper creates temporary file in current working directory. Root trusted queue
help succeeds without repair, chmod, SDK login/install or package changes.
Source scripts/headers/docs remain outside Git in shared/.../private.

Only existing candidate found in searched /home/qnx/qnx-work maxdepth5:
can-gate/output/disk-qemu and ifs.bin. This is a historical customized CAN project,
NOT verified stock. Do not relabel it as an EDU stock image. Stockdisk provenance,
runimage exactargv, SSH/transfer parameters remain pending focused inspection.
No new stock image build started.

Installed filename inventory searched target/qnx/x86_64 and usr/include using
9p/virtio/virtiofs/pci patterns. devr-virtio.so and vtnet modules present; no 9p/
virtiofs-named guest filesystem driver observed. Filename absence is bounded,
not global proof. Fresh HostShare native adapter qcc compilation is in progress;
EDU hash-verified wrong/finish compile phases queued serially in SAME owned boot.
No correctsource created; no native hostQNX concurrent guest.
