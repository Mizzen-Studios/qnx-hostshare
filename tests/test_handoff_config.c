#include "handoff_config.h"
#include <assert.h>
#include <stdio.h>
int main(int argc,char **argv){
 struct hs_options o;
 if(argc>1)return hs_options_parse(argc,argv,&o)?2:0;
 char *defaults[]={"hs","--pci-line","--mount"};
 assert(!hs_options_parse(3,defaults,&o)&&!strcmp(o.tag,"f0test")&&!strcmp(o.mountpoint,"/mnt/host"));
 char *custom[]={"hs","--tag","dev-inputs","--mountpoint","/mnt/dev-inputs","--mount","--pci-line"};
 assert(!hs_options_parse(7,custom,&o)&&!strcmp(o.tag,"dev-inputs"));
 assert(!hs_tag_valid(""));assert(!hs_tag_valid("a/b"));assert(!hs_tag_valid(".."));
 assert(!hs_mountpoint_valid("/mnt/a/../b"));assert(!hs_mountpoint_valid("/mnt/a/"));assert(!hs_mountpoint_valid("/etc/passwd"));
 puts("HANDOFF_CONFIG_PASS HOST_ONLY");return 0;
}
