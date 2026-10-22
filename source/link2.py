import numpy as np, itertools
exec(open('link.py').read().split('best=[]')[0].replace('A=np.array([10.,0]); B=np.array([10.,-108])',''))
H0=14
res=[]
for Bx in (10,12,14):
    A=np.array([10.,0]); zB=-54-(A[0]+54-Bx); B=np.array([float(Bx),zB])
    globals().update(A=A,B=B)
    band_x=A[0]+H0; rim_x=Bx
    for ra,rb in itertools.product((8,10,12,14,16),(8,10,12,14,16)):
      for al in range(0,360,5):
        for be in range(0,360,5):
          Pf=A+ra*u(al-90); Qf=B+rb*u(be+90)
          # folded link must pass behind the ring band and the basket rim where they cross lateral ~27
          def xat(z):
              t=(z-Pf[1])/(Qf[1]-Pf[1]); return Pf[0]+t*(Qf[0]-Pf[0])
          if not (min(Pf[1],Qf[1])<-94 and max(Pf[1],Qf[1])>-14): continue
          if max(xat(z) for z in (-14,-22))>band_x-2 or max(xat(z) for z in (-86,-94))>band_x-2: continue
          if max(xat(z) for z in (-26,-31,-77,-83))>rim_x-2: continue
          c0=np.linalg.norm(A+ra*u(al)-B-rb*u(be)); c1=np.linalg.norm(Pf-Qf)
          if abs(c0-c1)>0.3: continue
          r=solve_path(ra,al,rb,be)
          if r is None: continue
          th,c=r
          if abs(th[-1]-90)>1.5 or (np.diff(th)<=0).any(): continue
          d=np.diff(th); res.append((d.max()/d.min(),Bx,ra,al,rb,be,round(c,1),(A+ra*u(al)).round(1),(B+rb*u(be)).round(1),Pf.round(1),Qf.round(1)))
res.sort(key=lambda t:t[0])
for r in res[:15]: print(r)
print(len(res))
