"""Strict READ-ONLY QNX6 boot-partition inspector. Never writes filesystem bytes.
Limited to little-endian regular/directories, short names, <=2 indirect levels.
Bounded corroborating reader, not fsck/allocation/ACL validation. No SDK code.
"""
import argparse,hashlib,json,stat,struct
from pathlib import Path

def crc32_be(data):
    value=0
    for byte in data:
        value^=byte<<24
        for _ in range(8):value=((value<<1)^0x04c11db7)&0xffffffff if value&0x80000000 else (value<<1)&0xffffffff
    return value

class BootFS:
    def __init__(self,path):
        self.path=Path(path)
        if self.path.is_symlink() or not self.path.is_file():raise ValueError('regular disk required')
        self.length=self.path.stat().st_size
        if not 512<=self.length<=512*1024*1024:raise ValueError('disk size cap')
        self.file=self.path.open('rb');self.read_budget=128*1024*1024
        try:self.initialize()
        except BaseException:self.file.close();raise
    def initialize(self):
        mbr=self.read(0,512)
        if mbr[510:]!=b'\x55\xaa':raise ValueError('MBR signature')
        parts=[]
        for i in range(4):
            entry=mbr[446+16*i:462+16*i];start,count=struct.unpack_from('<II',entry,8)
            if entry[4]==177:parts.append((start*512,count*512))
        if len(parts)!=1:raise ValueError('unique type177 required')
        self.offset,self.bytes=parts[0]
        if self.offset<512 or self.offset+self.bytes>self.length:raise ValueError('partition bounds')
        first=self.super(self.offset+8192)
        self.blocksize=struct.unpack_from('<I',first,48)[0];self.blocks=struct.unpack_from('<I',first,60)[0]
        if self.blocksize not in (512,1024,2048,4096,8192,16384,32768) or not self.blocks:raise ValueError('geometry')
        self.data=self.offset+8192+4096
        second_at=self.data+self.blocks*self.blocksize
        if second_at+4096>self.offset+self.bytes:raise ValueError('superblock/partition geometry')
        second=self.super(second_at)
        if first[48:64]!=second[48:64]:raise ValueError('superblock geometry mismatch')
        self.sb=max((first,second),key=lambda b:struct.unpack_from('<Q',b,8)[0])
        self.inodes=struct.unpack_from('<I',self.sb,52)[0]
        self.inode_node=self.node(self.sb,72)
    def close(self):self.file.close()
    def read(self,offset,size):
        if offset<0 or size<0 or size>16*1024*1024 or offset+size>self.length:raise ValueError('disk bounds/cap')
        self.read_budget-=size
        if self.read_budget<0:raise ValueError('read budget exhausted')
        self.file.seek(offset);data=self.file.read(size)
        if len(data)!=size:raise ValueError('short disk read')
        return data
    def super(self,offset):
        b=self.read(offset,512)
        if struct.unpack_from('<I',b)[0]!=0x68191122 or struct.unpack_from('<I',b,4)[0]!=crc32_be(b[8:]):raise ValueError('superblock magic/CRC')
        return b
    @staticmethod
    def node(b,at):return (struct.unpack_from('<Q',b,at)[0],struct.unpack_from('<16I',b,at+8),b[at+72])
    def block(self,n):
        if not 0<=n<self.blocks:raise ValueError('invalid/hole block pointer')
        return self.read(self.data+n*self.blocksize,self.blocksize)
    def content(self,node):
        size,pointers,levels=node
        if levels>2 or size>min(self.blocks*self.blocksize,16*1024*1024):raise ValueError('unsupported tree/size')
        capacity=self.blocksize//4
        if size>16*(capacity**levels)*self.blocksize:raise ValueError('tree capacity')
        data=bytearray()
        for number in range((size+self.blocksize-1)//self.blocksize):
            n=pointers[number//(capacity**levels)];remainder=number%(capacity**levels)
            for level in range(levels,0,-1):
                table=self.block(n);index=remainder//(capacity**(level-1));remainder%=capacity**(level-1)
                n=struct.unpack_from('<I',table,index*4)[0]
            data.extend(self.block(n))
        return bytes(data[:size])
    def inode(self,n):
        if not 1<=n<=self.inodes:raise ValueError('inode bounds')
        if not hasattr(self,'inode_table'):self.inode_table=self.content(self.inode_node)
        table=self.inode_table;b=table[(n-1)*128:n*128]
        if len(b)!=128:raise ValueError('inode table bounds')
        mode=struct.unpack_from('<H',b,32)[0]
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):raise ValueError('unsupported inode type')
        return mode,(struct.unpack_from('<Q',b)[0],struct.unpack_from('<16I',b,36),b[100])
    def entries(self,n):
        mode,node=self.inode(n)
        if not stat.S_ISDIR(mode):raise ValueError('not directory')
        content=self.content(node)
        if len(content)%32:raise ValueError('directory alignment')
        result={}
        for at in range(0,len(content),32):
            b=content[at:at+32];ino=struct.unpack_from('<I',b)[0]
            if not ino:continue
            length=b[4]
            if not 1<=length<=27:raise ValueError('unsupported long directory name')
            name=b[5:5+length].decode('ascii')
            if '/' in name or '\x00' in name or name in result:raise ValueError('directory name')
            result[name]=ino
        return result
    def summary(self):
        files={};visited=set()
        def walk(n,path):
            if n in visited or len(visited)>=32 or path.count('/')>8:raise ValueError('directory cycle/depth cap')
            visited.add(n)
            for name,ino in self.entries(n).items():
                if name in ('.','..'):continue
                mode,node=self.inode(ino);path_name=path+name
                if stat.S_ISDIR(mode):walk(ino,path_name+'/')
                else:
                    data=self.content(node);files[path_name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'mode':oct(mode)}
        walk(1,'')
        return {'read_only':True,'partition_bytes':self.bytes,'blocksize':self.blocksize,'blocks':self.blocks,
                'selected_serial':struct.unpack_from('<Q',self.sb,8)[0],
                'metadata_free_blocks':struct.unpack_from('<I',self.sb,64)[0],
                'free_blocks_not_an_allocatable_capacity_guarantee':True,'files':files}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('disk',type=Path);o=p.parse_args();fs=BootFS(o.disk)
    try:print(json.dumps(fs.summary(),indent=2))
    finally:fs.close()
