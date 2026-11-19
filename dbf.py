import struct, numpy as np
def open_dbf(path):
    b=open(path,'rb').read()
    nrec=struct.unpack('<I',b[4:8])[0]; hs,rl=struct.unpack('<HH',b[8:12])
    fields=[];off=1;p=32
    while b[p]!=0x0D:
        name=b[p:p+11].split(b'\0')[0].decode(); t=chr(b[p+11]); ln=b[p+16]; dec=b[p+17]
        fields.append((name,t,ln,dec,off)); off+=ln; p+=32
    arr=np.frombuffer(b,dtype=np.uint8,count=nrec*rl,offset=hs).reshape(nrec,rl)
    return arr,{f[0]:f for f in fields}
def col_str(arr,F,name):
    _,_,ln,_,off=F[name]
    return np.char.strip(np.ascontiguousarray(arr[:,off:off+ln]).view(f'S{ln}').ravel())
def col_num(arr,F,name):
    s=col_str(arr,F,name)
    out=np.full(len(s),np.nan)
    ok=s!=b''
    try: out[ok]=s[ok].astype(float)
    except ValueError:
        out[ok]=[float(x) if x.replace(b'.',b'',1).lstrip(b'-').isdigit() else np.nan for x in s[ok]]
    return out
