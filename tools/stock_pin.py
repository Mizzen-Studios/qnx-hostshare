"""Strict SHA256 pin validation; no guest or external service access."""
import hashlib,json,re
from pathlib import Path
HISTORICAL_STOCK={'ifs.bin':'68bbe1b49a9b723c09d152773ee323ec6ab576eb29de933bfe3f08fdae21c753','disk-qemu':'0aee00c281f8eeb5b02c66555ed9517e317bb1503002a19dbf2b0155de336532'}
def _unique(pairs):
 result={}
 for key,value in pairs:
  if key in result: raise ValueError('duplicate stock pin key')
  result[key]=value
 return result

def load_stock_pin(path):
 data=Path(path).read_bytes()
 if len(data)>4096: raise ValueError('stock pin too large')
 pin=json.loads(data,object_pairs_hook=_unique)
 if not isinstance(pin,dict) or set(pin)!={'ifs.bin','disk-qemu'}: raise ValueError('stock pin requires exactly ifs.bin and disk-qemu')
 if any(not isinstance(v,str) or not re.fullmatch('[0-9a-f]{64}',v) or len(set(v))==1 for v in pin.values()):
  raise ValueError('stock pin requires real lowercase SHA256 digests, not placeholders')
 return pin

def verify_stock_files(image,disk,expected):
 for key,path in [('ifs.bin',image),('disk-qemu',disk)]:
  if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected[key]:
   raise ValueError('Wrong stock artifact: '+key)
