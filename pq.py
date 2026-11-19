import numpy as np, zlib
from thr import R

def snappy(b):
    r=R(b); n=r.varint(); out=bytearray(); p=r.p
    while p<len(b):
        t=b[p]; p+=1; k=t&3
        if k==0:
            l=t>>2
            if l>=60:
                nb=l-59; l=int.from_bytes(b[p:p+nb],'little'); p+=nb
            l+=1; out+=b[p:p+l]; p+=l
        else:
            if k==1: l=((t>>2)&7)+4; o=((t>>5)<<8)|b[p]; p+=1
            elif k==2: l=(t>>2)+1; o=int.from_bytes(b[p:p+2],'little'); p+=2
            else: l=(t>>2)+1; o=int.from_bytes(b[p:p+4],'little'); p+=4
            s=len(out)-o
            if o>=l: out+=out[s:s+l]
            else:
                for i in range(l): out.append(out[s+i])
    assert len(out)==n
    return bytes(out)

def rle(buf,pos,bw,count):
    """RLE/bit-packed hybrid -> np.array(count)"""
    out=np.empty(count,dtype=np.int64); i=0; bb=(bw+7)//8
    while i<count:
        r=R(buf,pos); h=r.varint(); pos=r.p
        if h&1:
            ng=h>>1; nv=ng*8; nbytes=ng*bw
            raw=np.frombuffer(buf,dtype=np.uint8,count=nbytes,offset=pos); pos+=nbytes
            if bw==0: vals=np.zeros(nv,dtype=np.int64)
            else:
                bits=np.unpackbits(raw,bitorder='little').reshape(-1,bw)
                vals=(bits.astype(np.int64)<<np.arange(bw)).sum(axis=1)
            t=min(nv,count-i); out[i:i+t]=vals[:t]; i+=t
        else:
            rl=h>>1; v=int.from_bytes(buf[pos:pos+bb],'little') if bb else 0; pos+=bb
            t=min(rl,count-i); out[i:i+t]=v; i+=t
    return out,pos

def read_column(b,col,optional):
    cm=col[3]; typ=cm[1]; nvals=cm[5]
    start=cm.get(11) or cm[9]; end=start+cm[7]
    p=start; dic=None; res=[]; total=0
    while p<end:
        r=R(b,p); ph=r.struct(); p=r.p
        comp=ph[3]; raw=snappy(b[p:p+comp]) if cm[4]==1 else b[p:p+comp]; p+=comp
        if ph[1]==2:
            dic=decode_plain(raw,typ,ph[7][1]); continue
        if ph[1]==0:
            h=ph[5]; nv=h[1]; enc=h[2]; pos=0
            if optional:
                ln=int.from_bytes(raw[0:4],'little'); defs,_=rle(raw,4,1,nv); pos=4+ln
            else: defs=np.ones(nv,dtype=np.int64)
        else:
            h=ph[8]; nv=h[1]; enc=h[4]; dl=h[5]; rl=h[6]
            raw=b[p-comp:p] if not h.get(7,True) else raw
            defs=rle(raw,0,1,nv)[0] if optional and dl else np.ones(nv,dtype=np.int64); pos=dl+rl
        nn=int((defs==1).sum())
        if enc in(2,8):
            bw=raw[pos]; idx,_=rle(raw,pos+1,bw,nn)
            vals=[dic[i] for i in idx] if isinstance(dic,list) else dic[idx]
        else: vals=decode_plain(raw[pos:],typ,nn)
        if isinstance(vals,list) or optional:
            full=[None]*nv; it=iter(vals)
            for i,d in enumerate(defs):
                if d==1: full[i]=next(it)
            res.append(full)
        else: res.append(vals)
    if all(isinstance(x,list) for x in res): return [v for x in res for v in x]
    return np.concatenate(res)

def decode_plain(raw,typ,n):
    if typ==1: return np.frombuffer(raw,dtype='<i4',count=n)
    if typ==2: return np.frombuffer(raw,dtype='<i8',count=n)
    if typ==3:
        a=np.frombuffer(raw,dtype=np.uint8,count=12*n).reshape(n,12)
        ns=a[:,:8].copy().view('<i8').ravel(); jd=a[:,8:].copy().view('<i4').ravel().astype('i8')
        return ((jd-2440588)*86400*10**9+ns).astype('datetime64[ns]')
    if typ==4: return np.frombuffer(raw,dtype='<f4',count=n)
    if typ==5: return np.frombuffer(raw,dtype='<f8',count=n)
    if typ==6:
        out=[];p=0
        for _ in range(n):
            l=int.from_bytes(raw[p:p+4],'little'); out.append(raw[p+4:p+4+l].decode('utf-8','replace')); p+=4+l
        return out
    raise Exception('type %d'%typ)

def load(path,cols):
    import pandas as pd
    b=open(path,'rb').read(); n=int.from_bytes(b[-8:-4],'little')
    m=R(b[-8-n:-8]).struct(); schema=m[2][1:]
    names=[s[4].decode() for s in schema]
    data={}
    for rg in m[4]:
        for ci,col in enumerate(rg[1]):
            nm=names[ci]
            if nm.upper() in cols:
                data[nm.upper()]=read_column(b,col,schema[ci].get(3)==1)
    return pd.DataFrame({k:(pd.Series(v) if isinstance(v,list) else v) for k,v in data.items()})
