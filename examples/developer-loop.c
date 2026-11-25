/* Host-built QNX client: read the readonly BOOT mount; no writes/restarts. */
#include <stdio.h>
int main(int argc,char **argv){
 unsigned char data[256];size_t n;FILE *f;
 if(argc!=2)return 2;
 f=fopen(argv[1],"rb");if(!f)return 3;
 puts("HOSTSHARE_DEVLOOP_BEGIN");
 while((n=fread(data,1,sizeof data,f))!=0){if(fwrite(data,1,n,stdout)!=n){fclose(f);return 4;}}
 if(ferror(f)){fclose(f);return 5;}fclose(f);
 puts("HOSTSHARE_DEVLOOP_END");return 0;
}
