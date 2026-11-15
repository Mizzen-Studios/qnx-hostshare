# Private publication-preparation audit — 15 November 2026

**Not publication approval. Keep this repository PRIVATE.** No history rewrite,
visibility change, recording, submission, contacts, spend, native run, SDK install
or login was performed. Historical receipts are unchanged. CAN frozen; C6 off.
This is a scoped history/artifact/identifier audit, not a general code-security audit.

## Audited baseline and exact scope

Baseline: **0a5c543e2191ebb55d02a4fc3269366617dd6762**, including the portability
changes, fresh-CI scratch fix and bounded stock-pin reader. Initially requested
base eba655cdc2d2952326a477798aa026b8a3e5d08b is included in that history.
After fetch, exact local refs (all at this baseline):

- refs/heads/main
- refs/remotes/origin/main
- refs/audit/origin/heads/main

One advertised remote branch, zero tags, three local refs. Scanned **33 reachable
commits**, **544 stored Git objects: 33 commits, 166 trees, 345 blobs**, totaling
**8,664,735 blob bytes**. Every stored blob was read, including objects not limited
to current HEAD; all historical tree aliases were mapped with ls-tree per commit.
All stored commit/tag bodies also passed through the secret detector. Author and
committer metadata were explicitly checked: 33 commits, 66 address fields, all
noreply-class; no personal author/committer mailbox found in this repository.

Report-commit boundary: these counts describe the baseline BEFORE this report's
commit. The report commit will be rescanned privately after commit/push; that
post-commit inventory is in the private summary and final handoff, not a fictional
self-referential audited hash in this document. No later commit is implicitly covered.

## Commands and retained evidence

Installed scanner: /home/linuxbrew/.linuxbrew/bin/gitleaks **8.30.0**. No install.
Private evidence directory (workspace-relative, mode700):
.openclaw/tmp/qnx-publish-audit-20261115/hostshare/

Commands run from this repository, with O set to that absolute private directory:

~~~sh
git fetch --all --tags
git fetch origin '+refs/*:refs/audit/origin/*'
git for-each-ref --format='%(refname) %(objectname)'
git rev-list --all
git cat-file --batch-all-objects --batch-check='%(objectname) %(objecttype) %(objectsize)'
/home/linuxbrew/.linuxbrew/bin/gitleaks git --log-opts='--all --full-history' --redact=100 --no-banner --no-color --ignore-gitleaks-allow --report-format json --report-path "$O/gitleaks-history.json" .
python3 "$O/audit.py"
~~~

The trusted local audit.py walks ls-tree for every commit, reads every unique
blob via cat-file, scans magic/size/path and identifiers, and streams raw bytes
ONLY through a pipe to gitleaks stdin --redact=100. No raw blob export. It streams
commit/tag bodies too. No match allowlisting or ignore-comment suppression was
used. Detector exit1 means findings, not a suppressed successful scan. Full
redacted detector reports/logs, classified-gitleaks.json, privacy-findings.json
(all aliases, blob/path/representative commit/line), binary-findings.json,
commit-metadata-findings.json, identity-classes.json, refs.txt, summary.json and
the exact scanner script remain private outside Git. No secret values copied
into this report or chat. IPv4, validated IPv6 candidates, tailnet ranges,
private-hostname/account paths, emails and credential markers were inspected.

## Secret-detector findings — six classified false positives

Both all-history diffs and all stored blob/metadata stdin scans found six
matches (generic-api-key), zero confirmed credentials. Exact locations:

- docs/acceptance/mount-20261113/receipt.json:102
  - blob 60af0f388ae1ab54c4ad13f9fbc436469c92bdf8
  - commit 4038d40a462d2344c0ef7d6e1c22828b9bd53b81
  - **False positive:** artifact SHA256 manifest value, not an API credential.
- docs/acceptance/f0/search/oss-9p.headers:7
  - blob 1a34465fa184f7ebe1fc4cb628341ca9705be277
- docs/acceptance/f0/search/oss-input.headers:7
  - blob 9b1bf26cf176027b7cfacd7188784c8e8fe75dfb
- docs/acceptance/f0/search/oss-virtio.headers:7
  - blob 325b43943512c54b829e70838c4b901fefb52389
  - all three introduced in commit 41e788524faa0442076443083bc3ebcdadf5e31f
  - **False positives:** public HTTP API gateway request identifiers, not keys.
- docs/acceptance/sdk-gate-20261112/serial.txt:353,376
  - blob 247d1a4f62d475fbcd180a1b689496ae76ce2543
  - commit c5926cf5eb09f2b77ba8345185838d003193b6a6
  - **Two false positives:** public kernel X.509 certificate identifiers.

No credential-marker matches from the supplementary key/token pattern scan.
Detector silence is not proof that no unknown secret format exists.

## Privacy/operational identifiers — owner review before publication

These are not authentication secrets, but do not silently publish them or rewrite
history. Exact values intentionally omitted. Full redacted location index is in
the private privacy-findings.json; it records every matching blob and all aliases.
Counts below are blob/rule records, NOT counts of unique sensitive people/hosts:

- **109 host/account-path records:** installation paths and historical hostnames,
  in README history, tools and receipts/logs. Classification: operational/private
  metadata. Current README/RUN_NATIVE now use generic user paths; old blobs and
  historical receipts remain unchanged. Example hostname location:
  docs/acceptance/followup-20261112/kernel-oom.log:23,99,
  blob 02f12a0afcec2f49071e8b7f543b5816d171d796. Representative commits and every
  additional path/blob are in the private index; not only a current-tree grep.
- **1 private-IPv4 blob record:** docs/acceptance/sdk-gate-20261112/serial.txt:
  661,671-674, blob 247d1a4f62d475fbcd180a1b689496ae76ce2543, commit
  c5926cf5eb09f2b77ba8345185838d003193b6a6. Classification: guest network/routing
  metadata; no credential. No separate tailnet IPv4 finding in this scan.
- **22 IPv6-candidate blob records:** mostly code cgroup delimiter literals and
  web syntax, not deployed addresses. Same serial blob has actual loopback,
  unspecified, link-local and other IPv6 network identifiers (including lines
  662,681). Classification: operational network metadata; review before public.
  No claim that an IPv6 address alone proves external reachability or ownership.
- **7 email-pattern blob records:** public upstream kernel maintainer addresses,
  SSH clone syntax and systemd unit strings that resemble mail addresses, not
  repository-owner personal mail. Includes serial blob above and
  docs/acceptance/f0/sdk-serial-tail.txt, blob
  b3853f2a8436d2f61838920a8b0be0c7acd0eb05. Exact lines/commits in private index.
  Commit author/committer identities were scanned separately, not inferred from
  these blob matches; all 66 baseline metadata address fields are noreply-class.

**No rewrite authorized or performed.** Owner must adjudicate identifier retention
and license/privacy/publication policy. Any proposed cleanup must first identify
exact historical path/blob/commit and obtain explicit rewrite authorization.

## Licensed/binary artifact checks

Zero ELF, QCOW, VMDK, boot-sector, ZIP, QNX4FS/QNX6FS or NUL-binary candidates
found by the configured magic checks; zero artifact-like filename candidates.
100 blob records reference SDK tools/artifact names; these are text paths, hashes,
source or logs, not embedded proprietary SDK/IFS/disk/ELF payloads.
Three size candidates are ordinary textual memory logs, not licensed binaries:

- docs/acceptance/stock-repeat-20261113/sdk/sdk-memory.jsonl — 1,861,488 bytes;
  blob 1277295bd18ed4e52c9342129e0e301146db7cc6.
- docs/acceptance/sdk-gate-20261112/memory-series.jsonl — 1,269,387 bytes;
  blob b10d6b36d257d8ecc8c755c7dea3b8bd91ae1d3f.
- docs/acceptance/native-20261113/sdk-memory.jsonl — 1,079,985 bytes;
  blob d99fd09be838295dfd42bd641f27db796168ec24.

The licensed SDK and external artifacts were NOT opened or scanned; only this
repository's Git objects. Filename/magic heuristics cannot prove licensing or
recognize every compressed/encrypted/custom IFS layout. No archive signatures
were found; no archive extraction or proprietary artifact execution performed.

## Verification and limitations

26 host tests, portable strict C tests, Python/shell syntax and whitespace checks
pass locally; host CI is not native proof. Initial portability CI 43716444302
failed because test scratch .local was absent on a fresh checkout; preserved,
fixed in 5a75b98, and CI 43716627470 passed. No native/SDK run required or claimed.
Core/native bytes and historical acceptance bytes remain unchanged.

Fetch covers advertised remote refs, not hidden/deleted server refs, GitHub caches,
other repositories, artifacts/releases or external LFS/submodule payloads.
All locally stored blobs (including unreachable objects present) were scanned;
objects absent from this clone cannot be audited. Zero current submodules.
This audit is not an entitlement/license review or a guarantee of no secrets.
Repository remains PRIVATE pending owner review, not ready-to-publish certification.
