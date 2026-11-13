#include "hostshare.h"
#include <string.h>
static uint16_t u16(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static uint32_t u32(const uint8_t *p){return (uint32_t)u16(p)|((uint32_t)u16(p+2)<<16);}
static void w32(uint8_t *p,uint32_t n){unsigned i;for(i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static int text(const uint8_t *p,size_t n,size_t *at,int component){
 size_t len,i;
 if(*at>n||n-*at<2)return -1;
 len=u16(p+*at);*at+=2;
 if(len>n-*at||(component&&(!len||len>255)))return -1;
 for(i=0;i<len;i++)if(!p[*at+i]||(component&&p[*at+i]=='/'))return -1;
 if(component==1&&((len==1&&p[*at]=='.')||(len==2&&p[*at]=='.'&&p[*at+1]=='.')))return -1;
 *at+=len;return 0;
}
static int live(const uint8_t *p){return u32(p)!=HS_NOFID;}
static int valid(uint8_t k,const uint8_t *p,size_t n){
 size_t at=0,i,count;
 switch(k){
 case 100:case 101:
  return n==14&&u32(p)>=256&&u32(p)<=1048576&&u16(p+4)==8&&!memcmp(p+6,"9P2000.L",8)?0:-1;
 case 104:
  if(n<8||!live(p))return -1;
  at=8;if(text(p,n,&at,0)||text(p,n,&at,0))return -1;
  return n-at==4?0:-1;
 case 105:return n==13?0:-1;
 case 110:
  if(n<10||!live(p)||!live(p+4))return -1;
  count=u16(p+8);at=10;if(count>16)return -1;
  for(i=0;i<count;i++)if(text(p,n,&at,1))return -1;
  return at==n?0:-1;
 case 111:return n>=2&&u16(p)<=16&&n==2+(size_t)u16(p)*13?0:-1;
 case 12:return n==8&&live(p)?0:-1; /* Tlopen fid flags */
 case 13:return n==17?0:-1; /* Rlopen qid iounit */
 case 116:case 40:return n==16&&live(p)?0:-1;
 case 117:return n>=4&&u32(p)==n-4?0:-1;
 case 41: /* Rreaddir: count + packed qid/offset/type/name entries */
  if(n<4||u32(p)!=n-4)return -1;
  at=4;
  while(at<n){if(n-at<24)return -1;at+=22;if(text(p,n,&at,2))return -1;}
  return 0;
 case 24:return n==12&&live(p)?0:-1; /* Tgetattr fid request_mask */
 case 25:return n==153?0:-1; /* valid[8], qid[13], mode/uid/gid[12],15*u64 */
 case 120:return n==4&&live(p)?0:-1;
 case 121:return n==0?0:-1;
 case 7:return n==4?0:-1;
 default:return -1;
 }
}
int hs_9p_decode(const uint8_t *p,size_t n,uint32_t msize,uint16_t expected_tag,uint8_t expected_kind,struct hs_frame *out){
 uint8_t kind;uint16_t tag;
 if(!p||!out||msize<256||msize>1048576||n<7||n>msize||u32(p)!=n)return -1;
 kind=p[4];tag=u16(p+5);
 if(((kind==100||kind==101)!=(tag==HS_NOTAG))||tag!=expected_tag||(kind!=expected_kind&&kind!=7))return -1;
 if(valid(kind,p+7,n-7))return -1;
 *out=(struct hs_frame){kind,tag,p+7,(uint32_t)(n-7)};return 0;
}
int hs_9p_encode(uint8_t *out,size_t capacity,uint32_t msize,uint8_t kind,uint16_t tag,const uint8_t *body,size_t n,size_t *written){
 if(!out||!written||(!body&&n)||msize<256||msize>1048576||n>msize-7||capacity<n+7)return -1;
 if(((kind==100||kind==101)!=(tag==HS_NOTAG))||valid(kind,body,n))return -1;
 /* memmove allows a body initially placed in the output area. */
 if(n)memmove(out+7,body,n);
 w32(out,(uint32_t)n+7);out[4]=kind;out[5]=(uint8_t)tag;out[6]=(uint8_t)(tag>>8);*written=n+7;return 0;
}
