# Local owner draft — not submitted

HostShare turns a host development folder into a bounded read-only QNX 8 input
mount: edit on Linux, reopen/read in QNX, without rebuilding the guest image.
The new handoff removes the laboratory-only tag/path: operators can validate a
named export and a /mnt/... destination while retaining the original defaults.
QEMU exports readonly; the resource manager denies write/create opens.

Conformance is deliberately evidence-led: the POSIX client emits actual offset,
partial-read and EOF bytes for comparison with an independent host oracle, plus
directory rewind/pagination and denied mutation checks. Host CI is not QNX
acceptance. See RESULT.md for the actual fresh SDK/native outcome before using
any new native claim. Existing reviewed stock image reuse is not a newly built
image. Historical EIO-only failures remain intact; the reviewed QNX server-death
contract is ESRCH3. No active-DMA safety, MSI-X or production-filesystem claim.

No Devpost, YouTube, visibility, upload or outreach action taken. £0.
