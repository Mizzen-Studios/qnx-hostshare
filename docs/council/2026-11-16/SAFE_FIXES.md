# HostShare safe fixes — 16 November 2026

## Authority and boundary

Owner 09:19 UTC authorized the queued safe judge-path/quickstart documentation
and host-test robustness fixes only, superseding the earlier scorecard's hold
for these items. Baseline main and origin/main both
9cbb5469204021647461167868fc06f7baa8a783 before editing; origin is
https://github.com/Mizzen-Studios/qnx-hostshare.git. No unrelated checkout work
was present; unrelated untracked/ignored local state is not removed or staged.

## Changes

- README leads with host edit → guest read without image rebuild, then watch,
  no-QNX inspection and optional licensed reproduction. New
  [judge path](../../JUDGES.md) links the actual host-edit, checksum, denied-write,
  pending-read errno and remount transcripts, separating inspection from execution.
- Default stock and optional historical quickstarts omit --midread. These are
  ordinary data/host-edit/cooperative-stop routes, **not server-death/remount
  tests**. The unchanged historical --midread diagnostic remains explicitly
  separate: its obsolete EIO-only assertion exits1 for accepted native ESRCH3.
  No runner, native client, errno semantics or receipt status was changed.
- [Fresh ELF/source manifest recipe](../../RUN_NATIVE.md) uses existing Python3
  and the launcher's current schema; exclusive create avoids overwriting a
  manifest. Real rebuilt bytes are hashed, never assumed deterministic or equal
  to historical ELF pins. Byte binding is not a build-provenance certificate.
- [Living contract footer](../../CURRENT_CONTRACT.md) now distinguishes the
  linked public demo, unverified playback/narration, and existing private silent
  draft evidence. Stale written-only and global-lease prose removed only from
  the living page, not historical evidence.

## Host verification

- Full unittest discovery: **30/30 PASS** (26 existing + 4 documentation tests).
- New regression checks: current local links; stock/historical ordinary command
  options and no obsolete --midread gate; media-footer consistency; execution of
  the exact documented manifest Python on synthetic non-ELF bytes; full source
  coverage; no overwrite; missing input; different rebuilt bytes yield different
  hashes; wrong ELF/source hashes rejected by the unchanged launcher's extracted
  preflight checks. No launcher guest lifecycle is executed by these tests.
- Portable C: cc -std=c11 -Wall -Wextra -Werror -pedantic, then test-core PASS.
- Python compileall, both launch shell syntax/help guards, git diff --check PASS.
- Existing stock-pin schema/mismatch, absolute-lock and source/errno preservation
  guard tests remain enabled in full discovery. Existing host-only CI already
  discovers the new tests; no CI policy/config change is needed.
- Final commit/remote equality and exact-tip host-only CI are checked after push
  and returned to the parent with the completion report, not inferred from an
  earlier green run. Parent independently verifies before accepting this work.

## Deliberately unchanged

All core/native source, runners, resource guards, historical receipts/failure
bytes and source/ELF/IFS/disk pins remain unchanged. Read-only/default IRQ11,
MSI-X unproven, and ESRCH before RPC/DMA limitations remain prominent. No native
acceptance is earned by this change. No QEMU, SDK/licence/image activity, native
rerun, media generation/upload, Devpost/YouTube/visibility/outreach or spending.
C6 untouched. Configurable native handoff, new surfaces, archive/stock-admission,
lessons/studies, comparative/loss analysis and new recording remain outside this
authorization and require Olly's decision.
