/* Bounded ASCII operator configuration; portable validation. */
#ifndef HANDOFF_CONFIG_H
#define HANDOFF_CONFIG_H
#include <string.h>
struct hs_options { const char *tag,*mountpoint; int mount,drop,pause,pci_line,msix; };
static int hs_safe_char(unsigned char c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_'||c=='-'||c=='.';}
static int hs_tag_valid(const char *s){size_t n=strlen(s);if(!n||n>31)return 0;for(size_t i=0;i<n;i++)if(!hs_safe_char((unsigned char)s[i]))return 0;return strcmp(s,".")&&strcmp(s,"..");}
static int hs_mountpoint_valid(const char *s){
 size_t n=strlen(s),start=1;if(n<2||n>255||s[0]!='/')return 0;
 for(size_t i=1;i<=n;i++){
  if(s[i]=='/'||!s[i]){size_t len=i-start;if(!len||len>63||(len==1&&s[start]=='.')||(len==2&&s[start]=='.'&&s[start+1]=='.'))return 0;start=i+1;}
  else if(!hs_safe_char((unsigned char)s[i]))return 0;
 }
 return strncmp(s,"/mnt/",5)==0;
}
static int hs_options_parse(int argc,char **argv,struct hs_options *o){
 int tag=0,path=0;*o=(struct hs_options){"f0test","/mnt/host",0,0,0,0,0};
 for(int i=1;i<argc;i++){
  if(!strcmp(argv[i],"--tag")){if(tag++||++i==argc)return -1;o->tag=argv[i];}
  else if(!strcmp(argv[i],"--mountpoint")){if(path++||++i==argc)return -1;o->mountpoint=argv[i];}
  else if(!strcmp(argv[i],"--pci-line")){if(o->pci_line++)return -1;}
  else if(!strcmp(argv[i],"--msix")){if(o->msix++)return -1;}
  else if(!strcmp(argv[i],"--mount")||!strcmp(argv[i],"--mount-drop")||!strcmp(argv[i],"--mount-pause-read")){
   if(o->mount++)return -1;
   o->drop=!strcmp(argv[i],"--mount-drop");o->pause=!strcmp(argv[i],"--mount-pause-read");
  }else return -1;
 }
 return !hs_tag_valid(o->tag)||!hs_mountpoint_valid(o->mountpoint)||(path&&!o->mount)||(o->msix&&o->pci_line)?-1:0;
}
#endif
