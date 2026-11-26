> 26Nov HOST/offline milestone: isolated exact client output, builtin-echo PID hook,
> strict PID/normal-TERM process/path gates;93 HOST tests pass. New private disk
> rebuilt with existing licensed SDK; original IFS/driver/client unchanged.
> Additional owner-authorized QNX attempt3 **HELD, NOT_RUN** pending parent review.
> Prior two native failures remain preserved; no full PASS. [Exact proof](docs/acceptance/boot-loop-20261126/HOST_RESULT.md).

> Latest25Nov final2: passive boot mount/default conformance observed; raw suite FAIL.
> Client byte-exact readback and exit0 observed, but IRQ logs broke contiguous-output
> assertion; hook also failed early printf/PID write. Normal detach NOT_RUN.
> **2/2 QNX attempts consumed;0 remaining. Native STOP.** [Exact result](docs/acceptance/boot-loop-20261125/final2/RESULT.md).
> Earlier dated readiness statements below are historical, not current authority.

> Latest25Nov: QNX prepare1 BLOCKED by guest /boot ENOSPC; no hook/seal/pin.
> Attempts used1 of2, final attempt HELD; no boot/default/developer-loop PASS.
> [Actual failure and clean lease/process proof](docs/acceptance/boot-loop-20261125/prepare1/RESULT.md).

> Latest25Nov: real licensed SDK client build PASS, all builder processes reaped,
> lease FREE. QNX boot/default/developer-loop verification remains NOT_RUN (0 of2).
> [Build artifact/provenance](docs/acceptance/boot-loop-20261125/client-sdk-build/RESULT.md).

> 25Nov feature A: one-shot boot mount + build-host/run-QNX implementation is
> HOST-tested only. Native NOT_RUN; no new full/default acceptance. [Readiness and
> SDK-client build proof and runtime plan](docs/BOOT_DEVELOPER_LOOP.md). Older failures
> below retain their exact historical scope and bytes.

# Current evidence and limits — 20 November 2026

## Status — 20 November 2026

| Area | Evidence-backed state |
|---|---|
| Repository | PUBLIC; older private/visibility-pending wording is stale. No visibility change performed here. |
| HOST regression | 81 Python tests passed; portable C checks are separate, not native proof. |
| Current-source native | Partial acceptance at 3a338a03: custom dev-inputs / /mnt/dev-inputs conformance PASS. |
| Default native compatibility | BLOCKED: final20Nov run acknowledged all806 data chunks, but guest toybox has no sha256sum; integrity/ELF execution/default conformance did not run. No complete native acceptance. |
| Historical HA contract | Pending-read server death returns ESRCH3, then fresh remount; never translate to EIO5. Not active-DMA crash safety. |
| Limits | MSI-X unproven; no production-readiness, safety or latency guarantee. |

[Current exact contract](docs/CURRENT_CONTRACT.md) · [Custom conformance evidence](docs/acceptance/developer-handoff-20261119/coordinated-build4/RESULT.md) · [Latest single default-run failure](docs/acceptance/default-final-20261120/RESULT.md) · [Tool contracts](tools/README.md) · [Dated history](docs/HISTORY.md) · [Path preservation policy](docs/PATHS.md).


Earlier status narrative follows; dated receipts retain their original scope.

