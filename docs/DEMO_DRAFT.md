# Demo evidence outline

[Watch the public demo](https://youtu.be/O0SA7W6gFyE).

This outline describes the evidence scope, not a new native run or recording plan.

1. Show [current contract](CURRENT_CONTRACT.md) and recorded source/ELF/image hashes.
2. Distinguish historical custom and new hashed clean-stock images. Stock SSH
   remains unverified; show existing serial receipts, not simulated output.
3. Show default IRQ11 without qtest/PIRQ rewrite, readonly mount/list and seven
   checksums. Host-edit timings are observations, not latency guarantees.
4. Show pending-read handler pause before RPC/DMA, SIGKILL, actual native read
   -1/ESRCH errno3, then fresh remount/read. Owner accepts QNX server-death ESRCH;
   never map to EIO5. Show old EIO assertion failure alongside review, not a
   fabricated PASS receipt.
5. Link prior idle-kill/remount separately. Neither HA scope proves active-DMA
   crash safety. MSI-X failed PCI_ERR_IRQ_CFG: skip, never imply success.
6. Show recorded cleanup evidence, not a claim about today's lease owner.

This documentation update performs no new recording, native run, SDK work, contacts or spending.
Native observations are only the linked existing receipts.
