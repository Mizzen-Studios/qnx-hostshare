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
