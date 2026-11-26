"""Strict boot verification helpers; no logging filters or guest launches."""
import re

def status(text,key):
 lines=text.replace('\r','').splitlines()
 values=[line for line in lines if line.startswith(key+'=')]
 if len(values)!=1 or not re.fullmatch(re.escape(key)+r'=\d+',values[0]):raise ValueError('missing/duplicate/invalid status '+key)
 return int(values[0].split('=')[1])

def client_command(app,input_path,output,nonce):
 if not re.fullmatch('[a-f0-9]{32}',nonce):raise ValueError('nonce')
 return ('chmod 700 '+app+' && '+app+' '+input_path+' > '+output+' 2>&1; '
         'echo CLIENT_RC_'+nonce+'=$?; echo CLIENT_DONE_'+nonce)

def verify_client(text,nonce,observed,input_bytes):
 expected=b'HOSTSHARE_DEVLOOP_BEGIN\n'+input_bytes+b'HOSTSHARE_DEVLOOP_END\n'
 if status(text,'CLIENT_RC_'+nonce)!=0 or observed!=expected:raise ValueError('client output/exit mismatch')
 return True

def pid_command():
 # Digits-only BEFORE kill expansion; fail closed on missing/invalid/stale PID.
 return ('HS_PID=$(cat /dev/shmem/hs-boot.pid); case "$HS_PID" in ""|*[!0-9]*) echo PID_GUARD_RC=1;; '
         '*) if [ "$HS_PID" -gt 1 ] && kill -0 "$HS_PID"; then echo PID_GUARD_RC=0; else echo PID_GUARD_RC=1; fi;; esac; echo PID_GUARD_DONE')

def stop_command(mountpoint):
 return ('kill -TERM "$HS_PID"; echo STOP_SIGNAL_RC=$?; sleep 2; kill -0 "$HS_PID"; echo STILL_ALIVE_RC=$?; '
         '[ ! -e '+mountpoint+'/hello.txt ]; echo STOP_PATH_ABSENT_RC=$?; echo NORMAL_STOP_DONE')

def verify_stop(text):
 lines=text.replace('\r','').splitlines()
 return (status(text,'STOP_SIGNAL_RC')==0 and status(text,'STILL_ALIVE_RC')!=0
         and status(text,'STOP_PATH_ABSENT_RC')==0 and lines.count('HOSTSHARE MOUNT TERM_DETACHED')==1)


from contextlib import contextmanager

@contextmanager
def detach_after_pid(report,stop):
 """Always try bounded normal detach once PID is validated; never mask primary."""
 try:
  yield
 finally:
  if report.get('boot_mount',{}).get('pid_guard') is True:
   report['normal_stop']={'attempted':True,'passed':False}
   try:
    text=stop()
    report['normal_stop']['passed']=verify_stop(text)
   except Exception as error:
    report['normal_stop']['error']=repr(error)

def requested_gates(report,conformance=False,boot_verify=False):
 gates={}
 if conformance:gates['requested_conformance']=report.get('conformance',{}).get('passed') is True
 if boot_verify:
  gates['developer_loop']=report.get('developer_loop',{}).get('passed') is True
  gates['pid_guard']=report.get('boot_mount',{}).get('pid_guard') is True
  gates['normal_detach']=report.get('normal_stop',{}).get('passed') is True
 return gates
