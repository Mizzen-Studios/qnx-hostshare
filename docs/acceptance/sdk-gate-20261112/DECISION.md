# SDK boot gate — stop, no inventory/build/native continuation

Authorized SDK-host cap change ONLY1GiB to2GiB; guest512MiB,CPU100%,nice15,
smp1,swap0 unchanged. Controller backup retained outside Git. Native caps unchanged.
One boot only. Raw pre-ready series records QEMU smaps/status, complete scope
process census and descendants, memory.stat/events and host meminfo every~2s.

QMP info ramblock confirms pc.ram512MiB HVA matching smaps candidate. QMP info
jit generated code grew53,342,884 to534,363,540B (capacity1,073,736,704B).
Corresponding anonymous executable~1GiB region resident growth strongly supports
TCG code-cache growth as the main non-guest-RAM contributor. This is real evidence,
not an inference that guest RAM was secretly enlarged or sibling processes caused
OOM. Residual non-executable allocations and why Nov10 differed remain unproven.
No allocator backtrace/profile proves complete attribution; gate conservatively
stays UNRESOLVED, not a memory-fit/build guarantee.

Operator issued existing controller stop while owner still monitoring because
unresolved attribution requires wholewave stop. Owner retains lease and reaps its
child on exit. An owner error saying guest exited before gate is the expected
result of this deliberate stop, NOT a second boot or concealed SDK failure.
Inventory/mkqnximage/stock paths NOT_RUN; installed driver absence UNVERIFIED.
No SDK package installation, login, repair, native adapter/build/run or EDU/CAN
mutation. Parent must adjudicate next authorization; no second boot authorized.

Final result: ready marker observed;153 samples; peak cgroup1,748,148,224B,
no max/oom/oom_kill events, swap0. Last guestRAMresident421,236,736B;
otheranonymous1,205,944,320B including executablemapping1,073,737,728B.
Operator ACPI timed out at120s then QMPquit; owner concurrent stop observed
stopped. Both stop commands rc0, owner rc0, zeroQEMU and leasefree verified.
Raw owner qemu_processes field was pgrep exitcode1 (no matches), corrected
in reconciled receipt with raw retained. No inventory or compilation followed.
