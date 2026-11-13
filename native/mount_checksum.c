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
