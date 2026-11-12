#include "hostshare.h"
#include <string.h>
static uint16_t u16(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static uint32_t u32(const uint8_t *p){return (uint32_t)u16(p)|((uint32_t)u16(p+2)<<16);}
int hs_caps(const uint8_t p[256],const uint64_t bars[6],struct hs_region out[4]){
 uint8_t seen[256]={0}; unsigned at,mask=0; struct hs_region tmp[4]={{0}};
 if(!p||!bars||!out||!(u16(p+6)&16))return -1;
 at=p[0x34];
 while(at){
  unsigned next,kind,size,bar; uint32_t off,len; static const unsigned minimum[4]={56,2,1,2};
  if(at<64||at>252||(at&3)||seen[at])return -1;
  seen[at]=1;next=p[at+1];
  if(p[at]!=9){at=next;continue;}
  size=p[at+2];kind=p[at+3];
  if(size<16||size>256-at)return -1;
  if(kind>=1&&kind<=4){
   if(mask&(1u<<(kind-1)))return -1;
   bar=p[at+4];off=u32(p+at+8);len=u32(p+at+12);
   if(bar>5||len<minimum[kind-1]||(uint64_t)off+len>bars[bar]||(kind==2&&size<20))return -1;
   tmp[kind-1]=(struct hs_region){(uint8_t)bar,off,len,kind==2?u32(p+at+16):0};
   mask|=1u<<(kind-1);
  }
  at=next;
 }
 if(mask!=15)return -1;
 memcpy(out,tmp,sizeof tmp);return 0;
}
int hs_features(uint64_t offered,uint64_t *selected){
 const uint64_t required=HS_VERSION1|1;
 if(!selected||(offered&required)!=required)return -1;
 *selected=required;return 0;
}
int hs_mount_tag(const uint8_t *p,size_t n,const uint8_t **tag,uint16_t *length){
 uint16_t len;
 if(!p||!tag||!length||n<2)return -1;
 len=u16(p);
 if(!len||len>255||len>n-2||memchr(p+2,0,len))return -1;
 *tag=p+2;*length=len;return 0;
}
int hs_queue_init(struct hs_queue *q,void (*notify)(void *,uint16_t),void (*pulse)(void *,uint16_t),void *ctx){
 if(!q||!notify||!pulse)return -1;
 memset(q,0,sizeof *q);q->notify=notify;q->pulse=pulse;q->context=ctx;return 0;
}
int hs_submit(struct hs_queue *q,uint64_t tx,uint32_t nt,uint64_t rx,uint32_t nr,uint16_t *token){
 if(!q||!token||!q->notify||!q->pulse||q->busy||nt<7||nt>1048576||nr<7||nr>1048576||tx>UINT64_MAX-nt||rx>UINT64_MAX-nr)return -1;
 if(tx<rx+nr&&rx<tx+nt)return -1;
 q->desc[0]=(struct hs_desc){tx,nt,1,1}; /* NEXT */
 q->desc[1]=(struct hs_desc){rx,nr,2,0}; /* WRITE */
 q->active=q->sequence++;q->busy=1;*token=q->active;q->notify(q->context,q->active);return 0;
}
int hs_complete(struct hs_queue *q,uint16_t token,uint32_t used){
 if(!q||!q->busy||token!=q->active||used<7||used>q->desc[1].length)return -1;
 q->busy=0;q->pulse(q->context,token);return 0;
}
