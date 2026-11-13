# Installed stock launcher relay

Installed /home/qnx/qnx800/host/common/mkqnximage/qemu/runimage
sha2565f763fbf99508129afc06d3936a44b3e80e87bc5da13c88217aa18a93d9c8df0.
Read locally; proprietary script retained ONLY outsideGit at shared/
hostshare-native-20261113/private/runimage-_home_qnx_qnx800_host_common_mkqnximage_qemu_runimage.

Derived x86_64 launcher fields: qemu-system-x86_64; -smp OPT_CPU; CPUmax if
/dev/kvm notwritable otherwise enable-kvm/cpuhost; -m OPT_RAM; drive
file=output/disk-qemu.vmdk,if=ide,id=drv0; bridge netdev(br determined by installed
check-net), virtio-net-pci with OPT_MACADDR; -pidfile output/qemu.pid -nographic;
nonUEFI -kernel output/ifs.bin, UEFI -bios /usr/share/qemu/OVMF.fd;
-serial mon:stdio or headless file:output/qemu.out; virtio-rng-pci plus
QEMU_OPTIONS from output/build/qemu_options. Deprecated local/qemu-options is
appended; message directs users to local/snippets/qemu_options.custom.
Thus --run itself only accepts -h, but installed launcher explicitly reads
generated QEMU_OPTIONS: owner-approved -device edu must use verified option
snippet/generation route or copied exactargv, not guessed --run passthrough.
This is installed template grammar, NOT a newly generated/tested stockargv.

No verified clean stockdisk currently identified. Existing can-gate/output
disk-qemu155795968B sha256f05ab960d9d7136816ad0c705208d6f6cdcd01490623aa86401636c17e1522aa;
ifs.bin11197400B sha256aa3afceff610fa42f7b711c635ece959ce35871b1e6434ae658682377223cb9f.
Historical CANcustom; NOT stock. SDK installs libpci.so.3.0 and libslog2.so.1.
SSH/SCP/SFTP runtime on a stock image remains UNVERIFIED, no login/keys changed.
No new image build occurred.

## EDU compile grant executed same SDK boot

Verified sourcecommit4a00a4f4af71f24964450f257acc6aea30312ec4 and all3handoff
hashes. Plan ran wrong then finish serially, rc0 each. Actual outputs outsideGit:
/home/ubuntu/qnx-host/guest/shared/hostshare-native-20261113/edu-wrong/learner_bin
sha256b33336d938a1df7561552bd1c4c581a8362421043f2fbb7dc85c2d83b72e9b90;
edu-finish/learner_bin sha25666c1c767b32b5ac439dcd817101e45f3eff36f71edcf293ddf0e37717ed5f559.
Fresh object/source hashes saved in edu-*-hashes.txt and full compile log.
No correctedsource created. No EDUrepository mutation, native run or stock claim.

Requested pause failed explicitly: runtime forbids yielding with live background
exec and says it cannot resume subagent safely. Therefore sameboot SDK work
completed, then STOPrequested with mandatory reap before HOSTnative. No hidden
secondSDKboot authorized or attempted.
