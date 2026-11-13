# Native attempt 2 — N1 FAIL, directory verifier false negative retained

Same native QEMU argv as attempt1; new corrected ELF715b1ed187904e6c38ce43d0799cd921acfecd27f8da776557351ccd265f60db.

N1 line11 completed Tversion and Tattach, ignored40 pulses without a used-ring
advance, then rejected ISR0 with used index3. MSI-X setup again returned
PCI_ERR_IRQ_CFG. Neither N1 test used routing mutation. No default-route PASS.
Possible ISR/used read ordering race is not established or fixed by this wave;
no further N1 retries are performed. Authorized own-device route workaround is
used for the mounted gate.

N2 actual cat and ls both rc0; real Treaddir replies show all expected entries.
QNX ls prints the UTF-8 lambda bytes as `\316\273`, so the strict literal-name
harness incorrectly stopped. Its original FAIL receipt is preserved. Separate
listing-adjudication.json decodes only octal byte escapes and verifies the names.
No N3/N4 result is inferred; attempt3 uses the SAME ELF/source/images for a fresh
mounted corpus run after correcting only output verification. Native3 references
these N1 failures explicitly instead of pretending they were rerun.

Peak784404480B, zero max/OOM/kill events, QEMU rc0 and reaped.
