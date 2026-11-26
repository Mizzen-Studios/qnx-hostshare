# Final3: scoped native boot/developer-loop PASS

Exactly one owner26Nov08:30 authorized additional QNX attempt was executed on
source ca97f605070411b33a4b84887f8e5ff6d345ec8d. Actual raw runner status is
PASS_READONLY_SUITE, exit0. All requested gates are explicit boolean true.
Attempts used3 total (prior2 failures preserved); remaining authorized0.
No retry, second boot, serial mount fallback or transparent restart.

## Actual observations

- Passive HOSTSHARE MOUNT READY /mnt/host READONLY preceded FIRST host serial TX;
  independently reconstructed from raw RX/TX events, not inferred from receipt.
- One-shot hook launch marker present. PID file digits/live-process guard RC0.
- Seven historical checksum files all pass, including1MiB2572415250/1048576B.
- Default conformance:288 byte cases,4 directory passes,189 pagination entries,
  5 denied opens; host corpus unchanged. Host-edit observed without rebuilding;
  write denied and host bytes unchanged.
- Existing licensed-SDK-built9488-byte client copied from readonly mount, actual
  guest hex readback matched all bytes BEFORE chmod/exec. ELF SHA:
  171b6fae32f6f62118fb2fa90eb0f2275ba3fbc6184abdc9273076fdfa04cb5e.
- Actual isolated client output read back exactly94 bytes, exit0:

~~~text
HOSTSHARE_DEVLOOP_BEGIN
HostShare boot-mounted developer loop verified.
HOSTSHARE_DEVLOOP_END
~~~

Output SHA7f737bc3e6293f39963c146286bd9284731f40878575530b7843915c74a5d8d5.
Independent strict parser recovered both9488/94-byte readbacks from raw events;
no IRQ-log filtering/subsequence acceptance. Original driver logs remain raw.
- Normal TERM attempted, signal RC0, exactly one TERM_DETACHED marker, actual
  server NATIVE RC0 observed; kill-0 RC1/no process and exported hello path
  absence RC0. Normal-detach gate true (not merely QEMU teardown).

## Bindings, caps and cleanup

Reviewed exact command: ../HOST_RESULT.md (executed once). Original external IFS
SHA68bbe1b49a9b723c09d152773ee323ec6ab576eb29de933bfe3f08fdae21c753;
derived raw SHA1f1fc2beb7638bb6a587cd01075210a6e7cc0cf86a69f21fa09854f5ab6a4993;
driver SHA36478be069978986271cad824d2c2799fd94c6124bd67346b09b270e92534d75.
Source/ELF/client/hook/base/offline provenance and runner-review binding revalidated
before launch. See original offline receipt and runner-review-binding.json.
Disk and IFS rehashed unchanged after runtime. Prior failed disks/overlays rehashed
unchanged. Used runtime overlay is now SHA
54088dbd63a9528125ffa54728717bba8e21755f8cec3a7ea5cafdd02cb4f197;
its preboot pristine pin remains historical, NOT reusable admission for another run.

Canonical exclusive native-test.lock held across lifetime. CPU100% nice15,
host2GiB/swap0/reserve64MiB; guest512MiB/smp1/TCG256/NICnone. Actual peak346775552B;
no max/OOM events. QEMU exit0/reaped, independent process lookup empty, lease FREE,
no queued jobs.97 HOST regressions pass separately; HOST tests are not native proof.

## Evidence retained

Private raw receipt: .local/user-runs/boot-a-final3-20261126/receipt.json
Private RX/TX events: same directory serial-events-private.jsonl
Private full serial: .local/suite-boot-a-final3-20261126-raw.bin
Private launch output: .local/finalQnx26/owner-output-private.txt
Private preflight: .local/hostFix26/final3-preflight-result.txt
Private independent verifier/proof: .local/finalQnx26/verify.py and
independent-verification.json. Exact evidence hashes committed beside this result.
Raw events/SDK binaries/private artifact contents are NOT published.

This is scoped native acceptance of this exact QNX8/x86_64 QEMU topology,
readonly boot mount/default conformance/build-host-run-QNX client and TERM detach.
Not production readiness, writable/general filesystem support, hardware coverage,
performance, active-DMA/death safety, MSI-X, or acceptance of unrelated C/D work.
C6 remains STOPPED; CAN capture HOLD. No other guest/repository, installation,
login, network/spend, Devpost/YouTube/visibility/outreach action.
