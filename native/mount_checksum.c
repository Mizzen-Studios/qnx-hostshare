/* POSIX cksum (CRC + length), reads only through the normal filesystem API. */
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
static uint32_t step(uint32_t crc,unsigned char b){crc^=(uint32_t)b<<24;for(int i=0;i<8;i++)crc=(crc<<1)^((crc&0x80000000u)?0x04c11db7u:0);return crc;}
int mount_checksum(const char *path){
 FILE *f=fopen(path,"rb");if(!f){perror(path);return 1;}
 unsigned char b[4096];size_t n;uint32_t crc=0;uint64_t size=0;
 while((n=fread(b,1,sizeof b,f))){for(size_t i=0;i<n;i++)crc=step(crc,b[i]);size+=n;}
 if(ferror(f)){perror("fread");fclose(f);return 1;}fclose(f);
 for(uint64_t nsize=size;nsize;nsize>>=8)crc=step(crc,(unsigned char)nsize);
 printf("HOSTSHARE CHECKSUM %" PRIu32 " %" PRIu64 " %s\n",~crc,size,path);return 0;
}
#ifdef CHECKSUM_STANDALONE
int main(int argc,char **argv){return argc==2?mount_checksum(argv[1]):2;}
#endif

/* Observe actual POSIX read result after server death; never translate errno. */
#ifndef CHECKSUM_STANDALONE
#include <sys/neutrino.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
int mount_read_once(const char *path){
 setvbuf(stdout,NULL,_IONBF,0);
 int fd=open(path,O_RDONLY);if(fd<0){printf("HOSTSHARE READ_ONCE OPEN_FAIL errno=%d\n",errno);return 2;}
 unsigned char b[4096];uint64_t timeout=UINT64_C(10000000000);
 puts("HOSTSHARE READ_ONCE CALL_BEGIN");
 struct timespec before,after;clock_gettime(CLOCK_MONOTONIC,&before);
 if(TimerTimeout(CLOCK_MONOTONIC,_NTO_TIMEOUT_SEND|_NTO_TIMEOUT_REPLY,NULL,&timeout,NULL)<0){perror("read deadline");close(fd);return 2;}
 errno=0;
 ssize_t n=read(fd,b,sizeof b);int saved=errno;clock_gettime(CLOCK_MONOTONIC,&after);
 double elapsed=(double)(after.tv_sec-before.tv_sec)+(after.tv_nsec-before.tv_nsec)/1e9;
 printf("HOSTSHARE READ_ONCE RESULT n=%lld errno=%d EIO=%d elapsed_seconds=%.6f\n",(long long)n,saved,EIO,elapsed);
 close(fd);return n==-1&&saved==EIO?0:3;
}
#endif
