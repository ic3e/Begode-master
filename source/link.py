import numpy as np
A=np.array([10.,0]); B=np.array([10.,-108])
def u(a): a=np.radians(a); return np.array([np.cos(a),np.sin(a)])
def solve_path(ra,al,rb,be,n=91):
    c=np.linalg.norm(A+ra*u(al)-B-rb*u(be))
    th2=0.0; out=[0.0]
    for t1 in np.linspace(0,-90,n)[1:]:
        P=A+ra*u(al+t1)
        # find th2 near previous with |P-Q|=c
        cand=np.linspace(th2-15,th2+15,601)
        Q=B[None,:]+rb*np.stack([np.cos(np.radians(be+cand)),np.sin(np.radians(be+cand))],1)
        f=np.linalg.norm(Q-P,axis=1)-c
        s=np.where(np.sign(f[:-1])!=np.sign(f[1:]))[0]
        if len(s)==0: return None
        k=s[np.argmin(np.abs(cand[s]-th2))]
        th2=cand[k]-f[k]*(cand[k+1]-cand[k])/(f[k+1]-f[k]); out.append(th2)
    return np.array(out),c
best=[]
for ra in (8,10,12,14,16,18,20):
  for rb in (8,10,12,14,16,18,20):
    for al in range(0,360,5):
      for be in range(0,360,5):
        c0=np.linalg.norm(A+ra*u(al)-B-rb*u(be)); c1=np.linalg.norm(A+ra*u(al-90)-B-rb*u(be+90))
        if abs(c0-c1)>0.3: continue
        r=solve_path(ra,al,rb,be)
        if r is None: continue
        th,c=r
        if abs(th[-1]-90)>1.5: continue
        d=np.diff(th)
        if (d<=0).any(): continue
        ratio=d/1.0
        # folded link position: both pins behind A_x-2 ?
        Pf=A+ra*u(al-90); Qf=B+rb*u(be+90)
        Pd=A+ra*u(al); Qd=B+rb*u(be)
        score=ratio.max()/max(ratio.min(),1e-3)
        best.append((score,ra,al,rb,be,round(c,1),Pd.round(1),Qd.round(1),Pf.round(1),Qf.round(1)))
best.sort(key=lambda t:t[0])
for b in best[:25]: print(b)
print(len(best))
print('--- folded pins behind the ring band (x <= A_x-5)')
ok=[b for b in best if b[8][0]<=A[0]-5 and b[9][0]<=A[0]-5]
ok.sort(key=lambda t:t[0])
for b in ok[:15]: print(b)
