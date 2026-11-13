/* Original bounded read-only QNX resource manager; included after adapter RPC. */
#include <sys/iofunc.h>
#include <sys/dispatch.h>
#include <dirent.h>
#include <fcntl.h>
#include <stddef.h>
#include <signal.h>
#include <grp.h>
#include <sys/procmgr.h>
static uint64_t get64(const uint8_t *p){return get32(p)|((uint64_t)get32(p+4)<<32);}
static void put64(uint8_t *p,uint64_t n){le32(p,n);le32(p+4,n>>32);}
struct mount_attr { iofunc_attr_t base; uint32_t fid; };
static struct adapter *mount_adapter;
/* Diagnostic scheduling window, disabled normally; no DMA submitted during pause. */
static int mount_pause_read;
static uint32_t next_fid=2;
static uint16_t next_tag=1;
static uint8_t mount_reply[8192];
static int rpc(uint8_t type,const void *body,size_t n,uint8_t reply,struct hs_frame *f){
 uint16_t tag=next_tag++;if(next_tag==HS_NOTAG)next_tag=1;
 return exchange(mount_adapter,type,tag,body,n,reply,f)?EIO:EOK;
}
static void clunk(uint32_t fid){uint8_t b[4];struct hs_frame f;le32(b,fid);(void)rpc(120,b,4,121,&f);}
static int mount_open(resmgr_context_t *ctp,io_open_t *msg,RESMGR_HANDLE_T *handle,void *extra){
 (void)handle;(void)extra;uint8_t b[2048]={0};struct hs_frame f;size_t at=10;unsigned count=0;int e;
 if((msg->connect.ioflag&_IO_FLAG_WR)||(msg->connect.ioflag&(O_CREAT|O_TRUNC|O_APPEND)))return EROFS;
 uint32_t fid=next_fid++;if(fid==HS_NOFID)return EMFILE;
 le32(b,1);le32(b+4,fid);
 const char *p=msg->connect.path;
 while(*p){const char *end=strchr(p,'/');size_t n=end?(size_t)(end-p):strlen(p);
  if(n==0||n>255||count>=16||at+2+n>sizeof b||(n==1&&p[0]=='.')||(n==2&&p[0]=='.'&&p[1]=='.'))return EINVAL;
  b[at]=n;b[at+1]=n>>8;memcpy(b+at+2,p,n);at+=2+n;count++;p+=n;if(*p)p++;
 }
 b[8]=count;
 if((e=rpc(110,b,at,111,&f)))return e;
 if(f.body[0]!=count||f.body[1]){clunk(fid);return ENOENT;}
 memset(b,0,12);le32(b,fid);put64(b+4,UINT64_C(0x7ff));
 if((e=rpc(24,b,12,25,&f))){clunk(fid);return e;}
 mode_t mode=get32(f.body+21);uint64_t size=get64(f.body+49);
 if(!S_ISREG(mode)&&!S_ISDIR(mode)){clunk(fid);return ENOTSUP;}
 struct mount_attr *a=calloc(1,sizeof *a);if(!a){clunk(fid);return ENOMEM;}
 iofunc_attr_init(&a->base,(mode&S_IFMT)|(S_ISDIR(mode)?0555:0444),NULL,NULL);a->base.nbytes=size;a->fid=fid;
 memset(b,0,8);le32(b,fid);
 if((e=rpc(12,b,8,13,&f))){free(a);clunk(fid);return e;}
 e=iofunc_open(ctp,msg,&a->base,NULL,NULL);
 if(e==EOK)e=iofunc_ocb_attach(ctp,msg,NULL,&a->base,NULL);
 if(e!=EOK){clunk(fid);free(a);}return e;
}
static int mount_read(resmgr_context_t *ctp,io_read_t *msg,iofunc_ocb_t *ocb){
 int e=iofunc_read_verify(ctp,msg,ocb,NULL);if(e)return e;
 int xtype=msg->i.xtype&_IO_XTYPE_MASK;
 if(xtype!=_IO_XTYPE_NONE && !(S_ISDIR(ocb->attr->mode)&&xtype==_IO_XTYPE_READDIR))return ENOSYS;
 size_t limit=_IO_READ_GET_NBYTES(msg);if(limit>4000)limit=4000;
 if(!limit){_IO_SET_READ_NBYTES(ctp,0);return EOK;}
 struct mount_attr *a=(struct mount_attr *)ocb->attr;uint8_t b[16]={0};struct hs_frame f;
 if(mount_pause_read && S_ISREG(a->base.mode)){
  printf("HOSTSHARE MIDREAD_HANDLER_ENTER rcvid=%lld count=%zu offset=%lld DIAGNOSTIC_PAUSE_BEFORE_RPC\n",(long long)ctp->rcvid,limit,(long long)ocb->offset);
  sleep(30);
 }
 le32(b,a->fid);put64(b+4,ocb->offset);le32(b+12,S_ISDIR(a->base.mode)?4000:limit);
 if((e=rpc(S_ISDIR(a->base.mode)?40:116,b,16,S_ISDIR(a->base.mode)?41:117,&f)))return e;
 size_t n=0;
 if(S_ISDIR(a->base.mode)){
  size_t at=4;
  while(at<f.body_length){const uint8_t *d=f.body+at;size_t len=d[22]|((size_t)d[23]<<8);size_t rec=(offsetof(struct dirent,d_name)+len+1+7)&~(size_t)7;
   if(n+rec>limit){if(!n)return EINVAL;break;}
   struct dirent *entry=(struct dirent *)(mount_reply+n);memset(entry,0,rec);entry->d_ino=get64(d+5);entry->d_offset=get64(d+13);entry->d_reclen=rec;entry->d_namelen=len;memcpy(entry->d_name,d+24,len);
   ocb->offset=entry->d_offset;n+=rec;at+=24+len;
  }
 }else{n=get32(f.body);if(n>limit)return EIO;memcpy(mount_reply,f.body+4,n);ocb->offset+=n;}
 _IO_SET_READ_NBYTES(ctp,n);return _RESMGR_PTR(ctp,mount_reply,n);
}
static int mount_close(resmgr_context_t *ctp,void *reserved,iofunc_ocb_t *ocb){
 struct mount_attr *a=(struct mount_attr *)ocb->attr;clunk(a->fid);
 int e=iofunc_close_ocb_default(ctp,reserved,ocb);free(a);return e;
}
static int mount_write(resmgr_context_t *ctp,io_write_t *msg,iofunc_ocb_t *ocb){(void)ctp;(void)msg;(void)ocb;return EROFS;}
static int mount_drop_privileges(void){
 if(ThreadCtl(_NTO_TCTL_IO_LEVEL,(void *)(uintptr_t)_NTO_IO_LEVEL_NONE)<0){perror("drop IO level");return 1;}
 unsigned deny=PROCMGR_ADN_ROOT|PROCMGR_ADN_NONROOT|PROCMGR_AOP_DENY|PROCMGR_AOP_LOCK;
 if(procmgr_ability(0,PROCMGR_ADN_NONROOT|PROCMGR_AOP_ALLOW|PROCMGR_AID_INTERRUPT,
   deny|PROCMGR_AID_IO,deny|PROCMGR_AID_MEM_PHYS,deny|PROCMGR_AID_PATHSPACE,PROCMGR_AID_EOL)<0){perror("drop abilities");return 1;}
 if(setgroups(0,NULL)<0||setgid(65534)<0||setuid(65534)<0){perror("drop uid/gid");return 1;}
 int io=ThreadCtl(_NTO_TCTL_IO_LEVEL,(void *)(uintptr_t)_NTO_IO_LEVEL_1);int io_errno=errno;
 if(io==0){ThreadCtl(_NTO_TCTL_IO_LEVEL,(void *)(uintptr_t)_NTO_IO_LEVEL_NONE);puts("HOSTSHARE PRIVILEGE IO reacquire unexpectedly allowed");return 1;}
 int root=setuid(0);int root_errno=errno;
 printf("HOSTSHARE PRIVILEGE uid=%u euid=%u gid=%u IO_REACQUIRE_RC=%d errno=%d ROOT_REACQUIRE_RC=%d errno=%d\n",(unsigned)getuid(),(unsigned)geteuid(),(unsigned)getgid(),io,io_errno,root,root_errno);
 puts("HOSTSHARE ABILITIES deny-lock IO,MEM_PHYS,PATHSPACE root+nonroot; INTERRUPT explicitly retained nonroot for existing IRQ; other abilities NOT exhaustively audited");
 return getuid()==65534&&geteuid()==65534&&io<0&&root<0?0:1;
}
static volatile sig_atomic_t mount_stop;
static void mount_signal(int signo){(void)signo;mount_stop=1;}
static int serve_mount(struct adapter *a,int drop){
 mount_adapter=a;dispatch_t *dpp=dispatch_create();if(!dpp){perror("dispatch_create");return 1;}
 resmgr_connect_funcs_t connect;resmgr_io_funcs_t io;resmgr_attr_t r={0};iofunc_attr_t root;
 iofunc_func_init(_RESMGR_CONNECT_NFUNCS,&connect,_RESMGR_IO_NFUNCS,&io);
 connect.open=mount_open;io.chmod=NULL;io.chown=NULL;io.utime=NULL;io.read=mount_read;io.write=mount_write;io.close_ocb=mount_close;
 iofunc_attr_init(&root,S_IFDIR|0555,NULL,NULL);r.nparts_max=1;r.msg_max_size=8192;
 int attach_id;
 if((attach_id=resmgr_attach(dpp,&r,"/mnt/host",_FTYPE_ANY,_RESMGR_FLAG_DIR,&connect,&io,&root))<0){perror("resmgr_attach");return 1;}
 dispatch_context_t *ctp=dispatch_context_alloc(dpp);if(!ctp)return 1;
 struct sigaction sa={0};sa.sa_handler=mount_signal;sigemptyset(&sa.sa_mask);sigaction(SIGTERM,&sa,NULL);sigaction(SIGINT,&sa,NULL);
 if(drop){a->privileges_reduced=1;if(mount_drop_privileges())return 1;}
 puts("HOSTSHARE MOUNT READY /mnt/host READONLY");
 while(!mount_stop){
  uint64_t timeout=UINT64_C(500000000);if(TimerTimeout(CLOCK_MONOTONIC,_NTO_TIMEOUT_RECEIVE,NULL,&timeout,NULL)<0)return 1;
  dispatch_context_t *next=dispatch_block(ctp);
  if(!next){if(errno==EINTR||errno==ETIMEDOUT)continue;perror("dispatch_block");return 1;}
  ctp=next;dispatch_handler(ctp);
 }
 resmgr_detach(dpp,attach_id,0);dispatch_context_free(ctp);dispatch_destroy(dpp);
 puts("HOSTSHARE MOUNT TERM_DETACHED");return 0;
}
