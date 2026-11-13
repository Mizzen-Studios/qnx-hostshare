# First clean-checkout IRQ/restart attempt retained

Source ed4ab6460cdf6e28dffd29c59a4038805d4a301b, ELF1991454b...

N1c IRQ11 PASS: used-ring-first, ISR hint only, real7replies and byte-exact41B;
real mounted cat/listing also work. No qtest/PIRQ mutation or fallback.

Idle SIGKILL observed, wait137, old mount absent. Replacement process attaches,
drops uid/euid/gid65534 and IO,MEM_PHYS,PATHSPACE abilities after attach;
IO-level and root reacquire attempts fail errno1. Mounted cat and independent
checksum948244384/41 both return0. Original receipt falsely rejects checksum
because harness hardcoded838956572; raw receipt is preserved, not rewritten.

Real remaining failure: SIGTERM prints TERM_DETACHED then processfaults rc139.
No stacktrace establishes faulting instruction. Correction skips privileged PCI
backend calls after ability reduction, verifies mapped virtio status0/queue0,
and explicitly does NOT claim PCI bus-master disable verification in reduced
path. Requires fresh native evidence; no retroactive cleanup PASS.

Clean MSI-X-only separate boot: Memory Space enabled before setup; installed
set_nirq FAIL PCI_ERR_IRQ_CFG, app1. No preceding INTx probe in that VM.
That native failure remains authoritative for its ELF; MSI-X not accepted.

Both guests reaped, peaks921415680B/795086848B; max/OOM/kill events0.
