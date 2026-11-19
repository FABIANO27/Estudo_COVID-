#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXB 13
typedef struct { short count[MAXB+1]; short symbol[256]; } huff;
static const unsigned char litlen[]={11,124,8,7,28,7,188,13,76,4,10,8,12,10,12,10,8,23,8,9,7,6,7,8,7,6,55,8,23,24,12,11,7,9,11,12,6,7,22,5,7,24,6,11,9,6,7,22,7,11,38,7,9,8,25,11,8,11,9,12,8,12,5,38,5,38,5,11,7,5,6,21,6,10,53,8,7,24,10,27,44,253,253,253,252,252,252,13,12,45,12,45,12,61,12,45,44,173};
static const unsigned char lenlen[]={2,35,36,53,38,23};
static const unsigned char distlen[]={2,20,53,230,247,151,248};
static const short base[16]={3,2,4,5,6,7,8,9,10,12,16,24,40,72,136,264};
static const char extra[16]={0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8};
static huff lc,lnc,dc;
static int construct(huff*h,const unsigned char*rep,int n){
  int symbol=0,len,left,i; short length[256],offs[MAXB+1];
  do{ len=*rep++; left=(len>>4)+1; len&=15; do{ length[symbol++]=len; }while(--left);}while(--n);
  int nsym=symbol;
  for(len=0;len<=MAXB;len++)h->count[len]=0;
  for(i=0;i<nsym;i++)h->count[length[i]]++;
  if(h->count[0]==nsym)return 0;
  offs[1]=0; for(len=1;len<MAXB;len++)offs[len+1]=offs[len]+h->count[len];
  for(i=0;i<nsym;i++) if(length[i]!=0) h->symbol[offs[length[i]]++]=i;
  return nsym;
}
static unsigned char*in; static long inlen,inpos; static int bitbuf,bitcnt;
static int bits(int need){
  long val=bitbuf;
  while(bitcnt<need){ if(inpos>=inlen) return -1; val|=(long)in[inpos++]<<bitcnt; bitcnt+=8; }
  bitbuf=(int)(val>>need); bitcnt-=need; return (int)(val&((1L<<need)-1));
}
static int decode(huff*h){
  int len,code=0,first=0,index=0,count; 
  for(len=1;len<=MAXB;len++){
    int b=bits(1); if(b<0)return -1;
    code|=b^1; count=h->count[len];
    if(code<first+count) return h->symbol[index+(code-first)];
    index+=count; first+=count; first<<=1; code<<=1;
  }
  return -9;
}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); fseek(f,0,SEEK_END); long sz=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*buf=malloc(sz); fread(buf,1,sz,f); fclose(f);
  int hs=buf[8]|(buf[9]<<8);
  in=buf+hs+4; inlen=sz-hs-4; inpos=0; bitbuf=0; bitcnt=0;
  construct(&lc,litlen,sizeof litlen); construct(&lnc,lenlen,sizeof lenlen); construct(&dc,distlen,sizeof distlen);
  long cap=sz*12+hs+1024, op=0; unsigned char*out=malloc(cap);
  memcpy(out,buf,hs); op=hs;
  int lit=bits(8),dict=bits(8);
  if(lit<0||lit>1||dict<4||dict>6){fprintf(stderr,"bad header %d %d\n",lit,dict);return 2;}
  for(;;){
    int b=bits(1); if(b<0){fprintf(stderr,"eof\n");break;}
    if(b){
      int s=decode(&lnc); if(s<0){fprintf(stderr,"lenerr\n");return 3;}
      int len=base[s]+bits(extra[s]); if(len==519)break;
      int sh= len==2?2:dict; int d=decode(&dc); if(d<0){fprintf(stderr,"disterr\n");return 3;}
      int dist=(d<<sh); dist+=bits(sh); dist++;
      if(dist>op-hs){fprintf(stderr,"dist too far\n");return 4;}
      if(op+len>cap){cap*=2;out=realloc(out,cap);}
      while(len--){out[op]=out[op-dist];op++;}
    } else {
      int s= lit? decode(&lc): bits(8); if(s<0){fprintf(stderr,"literr\n");return 3;}
      if(op+1>cap){cap*=2;out=realloc(out,cap);}
      out[op++]=s;
    }
  }
  FILE*o=fopen(argv[2],"wb"); fwrite(out,1,op,o); fclose(o);
  printf("%ld\n",op); return 0;
}
