import struct
class R:
    def __init__(s,b,p=0): s.b=b; s.p=p
    def byte(s): v=s.b[s.p]; s.p+=1; return v
    def varint(s):
        r=0;sh=0
        while True:
            c=s.byte(); r|=(c&0x7f)<<sh
            if not c&0x80: return r
            sh+=7
    def zz(s): n=s.varint(); return (n>>1)^-(n&1)
    def val(s,t):
        if t in(1,): return True
        if t==2: return False
        if t==3: return s.byte()
        if t in(4,5,6): return s.zz()
        if t==7: v=struct.unpack('<d',s.b[s.p:s.p+8])[0]; s.p+=8; return v
        if t==8: n=s.varint(); v=s.b[s.p:s.p+n]; s.p+=n; return v
        if t in(9,10):
            h=s.byte(); n=h>>4; et=h&15
            if n==15: n=s.varint()
            return [s.val(et) for _ in range(n)]
        if t==12: return s.struct()
        raise Exception('type %d'%t)
    def struct(s):
        d={};last=0
        while True:
            h=s.byte()
            if h==0: return d
            t=h&15; delta=h>>4
            fid=last+delta if delta else s.zz()
            last=fid
            if t==1: d[fid]=True
            elif t==2: d[fid]=False
            else: d[fid]=s.val(t)
