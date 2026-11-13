/* Original QNX8/QEMU-only bounded read-only diagnostic; no SDK source. */
#include "hostshare.h"
#include <pci/pci.h>
#include <sys/neutrino.h>
#include <sys/mman.h>
#include <sys/siginfo.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
struct adapter {
 volatile uint8_t *common,*isr,*notify; uint32_t multiplier;
 uint8_t *dma; off_t physical; int channel,connection,interrupt,irq;
 uint16_t avail,used;volatile uint16_t *doorbell;
};
static uint16_t r16(volatile uint8_t *p){return *(volatile uint16_t *)p;}
static uint32_t r32(volatile uint8_t *p){return *(volatile uint32_t *)p;}
static void w16(volatile uint8_t *p,uint16_t n){*(volatile uint16_t *)p=n;}
static void w32(volatile uint8_t *p,uint32_t n){*(volatile uint32_t *)p=n;}
static void w64(volatile uint8_t *p,uint64_t n){*(volatile uint64_t *)p=n;}
static void le32(uint8_t *p,uint32_t n){for(int i=0;i<4;i++)p[i]=(uint8_t)(n>>(i*8));}
static uint32_t get32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int exchange(struct adapter *a,uint8_t type,uint16_t tag,const uint8_t *body,size_t len,uint8_t reply,struct hs_frame *frame){
 uint8_t *tx=a->dma+8192,*rx=a->dma+12288;size_t n;struct hs_desc *d=(struct hs_desc *)a->dma;struct _pulse pulse;
 if(hs_9p_encode(tx,4096,4096,type,tag,body,len,&n))return -1;
 memset(rx,0,4096);d[0]=(struct hs_desc){(uint64_t)a->physical+8192,(uint32_t)n,1,1};d[1]=(struct hs_desc){(uint64_t)a->physical+12288,4096,2,0};
 w16(a->dma+128+4+2*(a->avail%8),0);__sync_synchronize();a->avail++;w16(a->dma+130,a->avail);__sync_synchronize();*a->doorbell=0;
 uint64_t timeout=UINT64_C(3000000000);
 if(TimerTimeout(CLOCK_MONOTONIC,_NTO_TIMEOUT_RECEIVE,NULL,&timeout,NULL)<0)return -1;
 if(MsgReceivePulse(a->channel,&pulse,sizeof pulse,NULL)<0){perror("IRQ pulse wait");return -1;}
 uint8_t isr=*a->isr;__sync_synchronize();
 if(pulse.code!=_PULSE_CODE_MINAVAIL+1||!(isr&1)||r16(a->dma+4098)!=(uint16_t)(a->used+1)){fprintf(stderr,"IRQ/used mismatch code=%d isr=%u used=%u\n",pulse.code,isr,r16(a->dma+4098));return -1;}
 size_t entry=4100+8*(a->used%8);uint32_t id=r32(a->dma+entry),count=r32(a->dma+entry+4);a->used++;
 if(InterruptUnmask(a->irq,a->interrupt)<0){perror("InterruptUnmask");return -1;}
 if(id!=0||count<7||count>4096||hs_9p_decode(rx,count,4096,tag,reply,frame))return -1;
 if(frame->kind==7){fprintf(stderr,"9P remote errno=%u\n",get32(frame->body));return -1;}
 printf("HOSTSHARE IRQ_PULSE type=%u reply=%u bytes=%u\n",type,frame->kind,count);return 0;
}
/* main follows after installed PCI API inspection. */

int main(void){
 struct adapter a={.dma=MAP_FAILED,.channel=-1,.connection=-1,.interrupt=-1,.irq=-1};
 pci_ba_t bars[6]={{0}};int_t nb=6;uint8_t config[256],body[256];uint64_t sizes[6]={0};void *maps[6]={0};size_t maplen[6]={0};struct hs_region regions[4];struct hs_frame frame;
 pci_err_t error=PCI_ERR_OK;pci_devhdl_t h=NULL;pci_cmd_t original=0,current=0;int changed=0,rc=1;size_t contiguous=0;uint64_t selected;uint16_t taglen;const uint8_t *tag;
 setvbuf(stdout,NULL,_IONBF,0);puts("HOSTSHARE NATIVE BEGIN");
 if(ThreadCtl(_NTO_TCTL_IO_LEVEL,(void *)(uintptr_t)_NTO_IO_LEVEL_1)<0){perror("IO_LEVEL");return 1;}
 pci_bdf_t bdf=pci_device_find(0,0x1af4,0x1049,PCI_CCODE_ANY);
 if(bdf==PCI_BDF_NONE)bdf=pci_device_find(0,0x1af4,0x1009,PCI_CCODE_ANY);
 if(bdf==PCI_BDF_NONE){puts("HOSTSHARE absent");goto done;}
 h=pci_device_attach(bdf,pci_attachFlags_e_EXCLUSIVE,&error);if(!h)goto done;
 if((error=pci_device_read_ba(h,&nb,bars,pci_reqType_e_UNSPECIFIED))!=PCI_ERR_OK||nb<0||nb>6)goto done;
 for(int i=0;i<256;i++)if(pci_device_cfg_rd8(bdf,(unsigned)i,&config[i])!=PCI_ERR_OK)goto done;
 for(int i=0;i<nb;i++)if(bars[i].bar_num<6&&bars[i].type==pci_asType_e_MEM)sizes[bars[i].bar_num]=bars[i].size;
 if(hs_caps(config,sizes,regions)){puts("HOSTSHARE modern caps rejected");goto done;}
 for(int k=0;k<4;k++){
  unsigned bar=regions[k].bar;
  if(maps[bar])continue;
  for(int i=0;i<nb;i++)if(bars[i].bar_num==(int_t)bar){
   if(bars[i].size>16777216)goto done;
   maplen[bar]=(size_t)bars[i].size;maps[bar]=mmap_device_memory(NULL,maplen[bar],PROT_READ|PROT_WRITE|PROT_NOCACHE,0,bars[i].addr);
   if(maps[bar]==MAP_FAILED){maps[bar]=NULL;perror("BAR mmap");goto done;}
  }
  if(!maps[bar])goto done;
 }
 a.common=(volatile uint8_t *)maps[regions[0].bar]+regions[0].offset;
 a.notify=(volatile uint8_t *)maps[regions[1].bar]+regions[1].offset;a.multiplier=regions[1].multiplier;
 a.isr=(volatile uint8_t *)maps[regions[2].bar]+regions[2].offset;
 volatile uint8_t *device=(volatile uint8_t *)maps[regions[3].bar]+regions[3].offset;
 uint8_t device_config[257]={0};size_t dn=regions[3].length<sizeof device_config?regions[3].length:sizeof device_config;
 for(size_t i=0;i<dn;i++)device_config[i]=device[i];
 if(hs_mount_tag(device_config,dn,&tag,&taglen)||taglen!=6||memcmp(tag,"f0test",6))goto done;
 a.common[20]=0;for(int i=0;a.common[20]&&i<100;i++)usleep(1000);if(a.common[20])goto done;
 a.common[20]=1;a.common[20]=3;w32(a.common,0);uint64_t offered=r32(a.common+4);w32(a.common,1);offered|=(uint64_t)r32(a.common+4)<<32;
 if(hs_features(offered,&selected))goto done;
 w32(a.common+8,0);w32(a.common+12,(uint32_t)selected);w32(a.common+8,1);w32(a.common+12,(uint32_t)(selected>>32));a.common[20]=11;
 if(!(a.common[20]&8))goto done;
 w16(a.common+22,0);if(r16(a.common+24)<8||r16(a.common+28))goto done;w16(a.common+24,8);
 a.dma=mmap(NULL,16384,PROT_READ|PROT_WRITE|PROT_NOCACHE,MAP_PRIVATE|MAP_ANON|MAP_PHYS,NOFD,0);
 if(a.dma==MAP_FAILED||mem_offset(a.dma,NOFD,16384,&a.physical,&contiguous)<0||a.physical<0||contiguous<16384)goto done;
 memset(a.dma,0,16384);w64(a.common+32,(uint64_t)a.physical);w64(a.common+40,(uint64_t)a.physical+128);w64(a.common+48,(uint64_t)a.physical+4096);
 uint64_t no=(uint64_t)r16(a.common+30)*a.multiplier;if(no+2>regions[1].length||no%2)goto done;a.doorbell=(volatile uint16_t *)(a.notify+no);
 pci_irq_t irq=-1;int_t ni=1;if(pci_device_read_irq(h,&ni,&irq)!=PCI_ERR_OK||ni!=1||irq<0)goto done;a.irq=irq;
 a.channel=ChannelCreate(0);if(a.channel<0)goto done;a.connection=ConnectAttach(0,0,a.channel,_NTO_SIDE_CHANNEL,0);if(a.connection<0)goto done;
 struct sigevent ev;SIGEV_PULSE_INIT(&ev,a.connection,10,_PULSE_CODE_MINAVAIL+1,0);
 a.interrupt=InterruptAttachEvent(irq,&ev,_NTO_INTR_FLAGS_TRK_MSK);if(a.interrupt<0){perror("InterruptAttachEvent");goto done;}
 if(pci_device_read_cmd(bdf,&original)!=PCI_ERR_OK)goto done;changed=1;
 if(pci_device_write_cmd(h,(original|6)&~0x400,&current)!=PCI_ERR_OK||(current&6)!=6)goto done;
 w16(a.common+28,1);a.common[20]=15;__sync_synchronize();printf("HOSTSHARE F1 READY tag=f0test features=%llx irq=%d dma=%llx\n",(unsigned long long)selected,irq,(unsigned long long)a.physical);
 memset(body,0,sizeof body);le32(body,4096);body[4]=8;memcpy(body+6,"9P2000.L",8);
 if(exchange(&a,100,HS_NOTAG,body,14,101,&frame)||get32(frame.body)!=4096)goto done;
 memset(body,0,sizeof body);le32(body,1);le32(body+4,HS_NOFID);body[8]=4;memcpy(body+10,"root",4); /* uname, empty aname, n_uname0 */
 if(exchange(&a,104,1,body,20,105,&frame))goto done;
 memset(body,0,sizeof body);le32(body,1);le32(body+4,2);body[8]=1;body[10]=9;memcpy(body+12,"hello.txt",9);
 if(exchange(&a,110,2,body,21,111,&frame)||frame.body_length!=15||frame.body[0]!=1)goto done;
 memset(body,0,sizeof body);le32(body,2);if(exchange(&a,12,3,body,8,13,&frame))goto done;
 memset(body,0,sizeof body);le32(body,2);le32(body+12,256);if(exchange(&a,116,4,body,16,117,&frame))goto done;
 const char expected[]="HostShare F0 public synthetic test only.\n";
 if(get32(frame.body)!=sizeof expected-1||memcmp(frame.body+4,expected,sizeof expected-1))goto done;
 puts("HOSTSHARE F2 READONLY BYTE_EXACT PASS");
 le32(body,2);if(exchange(&a,120,5,body,4,121,&frame))goto done;le32(body,1);if(exchange(&a,120,6,body,4,121,&frame))goto done;rc=0;
done:
 if(a.common){a.common[20]=0;__sync_synchronize();}
 if(changed){if(pci_device_write_cmd(h,original&~4,&current)!=PCI_ERR_OK||(current&4)){puts("HOSTSHARE cannot quiesce; retain DMA until VM stop");for(;;)pause();}}
 if(a.interrupt>=0)InterruptDetach(a.interrupt);
 if(a.connection>=0)ConnectDetach(a.connection);if(a.channel>=0)ChannelDestroy(a.channel);
 if(a.dma!=MAP_FAILED)munmap(a.dma,16384);
 for(int i=0;i<6;i++)if(maps[i])munmap(maps[i],maplen[i]);
 if(h){if(changed)pci_device_write_cmd(h,original,NULL);pci_device_detach(h);}
 ThreadCtl(_NTO_TCTL_IO_LEVEL,(void *)(uintptr_t)_NTO_IO_LEVEL_NONE);
 printf("HOSTSHARE NATIVE RC=%d pci=%s errno=%d\n",rc,pci_strerror(error),errno);return rc;
}
