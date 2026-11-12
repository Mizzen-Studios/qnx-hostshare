/* Apache-2.0. Portable host-tested foundation, NOT a native QNX driver. */
#ifndef HOSTSHARE_H
#define HOSTSHARE_H
#include <stddef.h>
#include <stdint.h>
#define HS_VERSION1 (UINT64_C(1)<<32)
#define HS_NOTAG UINT16_MAX
#define HS_NOFID UINT32_MAX
struct hs_region { uint8_t bar; uint32_t offset,length,multiplier; };
int hs_caps(const uint8_t pci[256], const uint64_t bars[6], struct hs_region out[4]);
int hs_features(uint64_t offered,uint64_t *selected);
int hs_mount_tag(const uint8_t *p,size_t n,const uint8_t **tag,uint16_t *length);
/* Descriptor addresses are caller-supplied opaque test addresses. A native
 * adapter MUST supply DMA mapping, barriers, rings, MMIO and IRQ lifecycle. */
struct hs_desc { uint64_t address; uint32_t length; uint16_t flags,next; };
struct hs_queue {
 struct hs_desc desc[2]; uint16_t sequence,active; int busy;
 void (*notify)(void *,uint16_t); void (*pulse)(void *,uint16_t); void *context;
};
int hs_queue_init(struct hs_queue *,void (*)(void *,uint16_t),void (*)(void *,uint16_t),void *);
int hs_submit(struct hs_queue *,uint64_t,uint32_t,uint64_t,uint32_t,uint16_t *);
int hs_complete(struct hs_queue *,uint16_t,uint32_t);
/* Strict 9P2000.L wire framing. Body views borrow the input buffer; no malloc.
 * Supported kinds: version100/101 attach104/105 walk110/111 lopen12/13,
 * read116/117 readdir40/41 getattr24/25 clunk120/121 and Rlerror7.
 * Body encoder accepts already assembled LE fields, validates them, then copies.
 * This is not a session/fid table or filesystem implementation. */
struct hs_frame { uint8_t kind; uint16_t tag; const uint8_t *body; uint32_t body_length; };
int hs_9p_decode(const uint8_t *,size_t,uint32_t,uint16_t,uint8_t,struct hs_frame *);
int hs_9p_encode(uint8_t *,size_t,uint32_t,uint8_t,uint16_t,const uint8_t *,size_t,size_t *);
#endif
