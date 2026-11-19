/* POSIX client: emits actual bytes; independent HOST oracle decides PASS. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
int mount_conformance(const char *root){
 const char *names[]={"empty","one","4KiB","1MiB"};
 const long offsets[]={0,1,3999,4000,4095,4096,1048575,1048576,1048581};
 const size_t counts[]={0,1,17,257};char path[512];unsigned char b[257];
 for(int client=0;client<2;client++)for(size_t f=0;f<4;f++){
  snprintf(path,sizeof path,"%s/%s",root,names[f]);int fd=open(path,O_RDONLY);if(fd<0)return 2;
  for(size_t o=0;o<9;o++)for(size_t c=0;c<4;c++){
   if(lseek(fd,offsets[o],SEEK_SET)<0){close(fd);return 3;}
   ssize_t n=read(fd,b,counts[c]);if(n<0){close(fd);return 4;}
   printf("HS_CASE %d %s %ld %zu %ld ",client,names[f],offsets[o],counts[c],(long)n);
   for(ssize_t i=0;i<n;i++){printf("%02x",b[i]);}puts("-");
  }close(fd);
 }
 for(int client=0;client<2;client++){
  DIR *dir=opendir(root);if(!dir)return 5;
  for(int pass=0;pass<2;pass++){
   if(pass){rewinddir(dir);}struct dirent *d;errno=0;
   while((d=readdir(dir)))printf("HS_DIR %d %d %s\n",client,pass,d->d_name);
   if(errno){closedir(dir);return 6;}
   printf("HS_DIR_END %d %d\n",client,pass);
  }closedir(dir);
 }
 snprintf(path,sizeof path,"%s/one",root);
 int flags[]={O_WRONLY,O_RDWR,O_WRONLY|O_TRUNC,O_WRONLY|O_APPEND};
 for(int i=0;i<4;i++){errno=0;int fd=open(path,flags[i]);int e=errno;if(fd>=0)close(fd);printf("HS_DENY open%d %d %d\n",i,fd,e);if(fd>=0)return 7;}
 snprintf(path,sizeof path,"%s/forbidden-new",root);errno=0;int fd=open(path,O_WRONLY|O_CREAT,0600);int e=errno;if(fd>=0)close(fd);printf("HS_DENY create %d %d\n",fd,e);if(fd>=0)return 8;
 puts("HS_CONFORMANCE_COMPLETE");return 0;
}
