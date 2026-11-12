#include "hostshare.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void w32(uint8_t *p,uint32_t v){unsigned i;for(i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static void hook(void *p,uint16_t token){unsigned *n=p;(void)token;(*n)++;}
static void transport(void){
 uint8_t pci[256]={0};uint64_t bars[6]={4096},features;struct hs_region regions[4];
 const unsigned at[4]={64,84,104,120},len[4]={56,16,1,32};unsigned i,calls=0;struct hs_queue q;uint16_t token;
 const uint8_t config[]={6,0,'f','0','t','e','s','t'};const uint8_t *tag;uint16_t taglen;
 pci[6]=16;pci[0x34]=64;
 for(i=0;i<4;i++){unsigned a=at[i];pci[a]=9;pci[a+1]=(uint8_t)(i==3?0:at[i+1]);pci[a+2]=(uint8_t)(i==1?20:16);pci[a+3]=(uint8_t)(i+1);w32(pci+a+8,i*128);w32(pci+a+12,len[i]);if(i==1)w32(pci+a+16,4);}
 assert(!hs_caps(pci,bars,regions));assert(regions[1].multiplier==4);
 pci[121]=64;assert(hs_caps(pci,bars,regions));pci[121]=0;
 bars[0]=100;assert(hs_caps(pci,bars,regions));bars[0]=4096;
 pci[66]=255;assert(hs_caps(pci,bars,regions));pci[66]=16;
 assert(!hs_features(HS_VERSION1|17,&features)&&features==(HS_VERSION1|1));assert(hs_features(1,&features));
 assert(!hs_mount_tag(config,sizeof config,&tag,&taglen)&&taglen==6);assert(hs_mount_tag(config,3,&tag,&taglen));
 assert(!hs_queue_init(&q,hook,hook,&calls));
 assert(hs_submit(&q,100,8,104,8,&token)); /* overlaps */
 assert(!hs_submit(&q,100,8,1000,256,&token));assert(calls==1&&q.desc[0].flags==1&&q.desc[1].flags==2);
 assert(hs_submit(&q,100,8,1000,256,&token));assert(hs_complete(&q,token,257));assert(hs_complete(&q,(uint16_t)(token+1),7));
 assert(!hs_complete(&q,token,16)&&calls==2);assert(hs_complete(&q,token,16));
}
static void roundtrip(uint8_t kind,uint8_t *body,size_t nb){
 uint8_t wire[512];size_t n,i;struct hs_frame f;uint16_t tag=(kind==100||kind==101)?HS_NOTAG:12;
 assert(!hs_9p_encode(wire,sizeof wire,512,kind,tag,body,nb,&n));
 assert(!hs_9p_decode(wire,n,512,tag,kind,&f));assert(f.body_length==nb);
 for(i=0;i<n;i++)assert(hs_9p_decode(wire,i,512,tag,kind,&f));
 assert(hs_9p_decode(wire,n,512,(uint16_t)(tag-1),kind,&f));
 wire[n]=0;w32(wire,(uint32_t)n+1);assert(hs_9p_decode(wire,n+1,512,tag,kind,&f));
}
static void protocol(void){
 uint8_t body[256]={0},wire[512];size_t n;struct hs_frame f;unsigned i;
 const uint8_t version[]={0,32,0,0,8,0,'9','P','2','0','0','0','.','L'};
 memcpy(body,version,sizeof version);roundtrip(100,body,14);roundtrip(101,body,14);
 memset(body,0,sizeof body);body[0]=1;memset(body+4,255,4);roundtrip(104,body,16);
 memset(body,0,sizeof body);roundtrip(105,body,13);body[0]=1;body[4]=2;roundtrip(110,body,10);
 memset(body,0,sizeof body);roundtrip(111,body,2);
 for(i=0;i<2;i++){body[0]=1;roundtrip(i?40:116,body,16);}
 memset(body,0,sizeof body);body[0]=1;roundtrip(12,body,8);roundtrip(24,body,12);roundtrip(120,body,4);
 memset(body,0,sizeof body);roundtrip(13,body,17);roundtrip(25,body,153);roundtrip(121,body,0);roundtrip(7,body,4);
 roundtrip(117,body,4);roundtrip(41,body,4);
 body[0]=25;body[26]=1;body[28]='x';roundtrip(41,body,29); /* one dirent */
 body[26]=2;assert(hs_9p_encode(wire,sizeof wire,512,41,12,body,29,&n));
 memset(body,255,4);assert(hs_9p_encode(wire,sizeof wire,512,120,12,body,4,&n));
 memset(body,0,sizeof body);body[0]=1;assert(hs_9p_encode(wire,sizeof wire,512,117,12,body,4,&n));
 assert(hs_9p_encode(wire,sizeof wire,512,121,HS_NOTAG,body,0,&n));
 assert(!hs_9p_encode(wire,sizeof wire,512,121,12,NULL,0,&n));assert(hs_9p_decode(wire,n,512,12,117,&f));
 /* Deterministic malformed inputs; zero payloads are not live traffic. */
 for(i=0;i<512;i++){memset(wire,0,sizeof wire);assert(hs_9p_decode(wire,i,512,12,117,&f));}
}
int main(void){transport();protocol();puts("C_CORE_PASS transport/protocol groups; synthetic fixtures only; native NOT_RUN");return 0;}
