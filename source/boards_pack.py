# Where the boards go: the real module sizes packed into the dry spaces (left bay, right bay, electronics box)
# around the housing, top plate, servo, bearing, LED bar and the lens frame's whole swing, 0.5 mm off everything.
# Writes anim/boards_placed.json for boards_export.py.
import itertools, json
exec(open('build27.py').read())
from scipy import ndimage
hs=housing12(); pl=top_plate11(); sv=servo6(); brg=H6(bearing7()); bar=led_bar(); bt=buttons8(); ld=lid10()
sweep=mf.Manifold.batch_boolean([tilt6(H6(lens_frame7()+lenses6()),a) for a in (-13,-6,0,6,13)],mf.OpType.Add)
solid=hs+pl+sv+brg+bar+bt+ld+sweep
t=to_tm(solid); P=0.5
lo=np.array([-70.0,-52.0,ZC-68.0]); hi=np.array([-12.0,24.0,ZC+68.0])
xs=np.arange(lo[0],hi[0],P)+P/2; ys=np.arange(lo[1],hi[1],P)+P/2; zs=np.arange(lo[2],hi[2],P)+P/2
from matplotlib.path import Path
occ=np.zeros((len(xs),len(ys),len(zs)),bool)
X,Z=np.meshgrid(xs,zs,indexing='ij'); pts=np.c_[X.ravel(),Z.ravel()]
for j,y in enumerate(ys):
    s=t.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
    if s is None: continue
    o=np.zeros(len(pts),int)
    for e in s.discrete: o^=Path(e[:,[0,2]]).contains_points(pts)
    occ[:,j,:]=o.reshape(len(xs),len(zs)).astype(bool)
occ=ndimage.binary_dilation(occ,iterations=1)          # 0.5 mm off every wall
def cells_(a,b): return (slice(int((a[0]-lo[0])/P),int(np.ceil((b[0]-lo[0])/P))),slice(int((a[1]-lo[1])/P),int(np.ceil((b[1]-lo[1])/P))),slice(int((a[2]-lo[2])/P),int(np.ceil((b[2]-lo[2])/P))))
for s_,w_,r_ in WIRE_SLOTS:   # keep the space over each floor slot free for the wires (8 mm up, 1 mm round it)
    occ[cells_(np.array([-43.0,HOUSE_Y0,ZC+w_-r_-1.0]),np.array([-31.0,HOUSE_Y0+11.0,ZC+w_+r_+1.0]))]=True
MODS=[('LDD-1500L #1',(22.1,11.3,8.5),'L'),('LDD-1500L #2',(22.1,11.3,8.5),'L'),('LDD-1500L #3',(22.1,11.3,8.5),'L'),('MP1584 #1 (5.0 V)',(22.0,17.0,4.5),'L'),
      ('INA219',(25.5,22.3,4.0),'RB'),('MP1584 #2 (5.1 V, USB)',(22.0,17.0,4.5),'R'),('MOSFET #2 (USB)',(18.0,11.0,4.0),'R'),('MOSFET #1 (DRL)',(18.0,11.0,4.0),'RL'),
      ('ESP32-C3 SuperMini',(22.5,18.0,4.5),'B'),('MPU-6050',(21.0,16.0,3.5),'LR')]
REG={'L':(np.array([-57.0,-17.5,ZC-64.5]),np.array([-15.0,22.4,ZC-38.6])),'R':(np.array([-57.0,-17.5,ZC+38.6]),np.array([-15.0,22.4,ZC+64.5])),
     'B':(np.array([-45.0,-50.7,ZC-44.5]),np.array([-28.5,-24.5,ZC+44.5]))}
def cells(a,b): return (slice(int((a[0]-lo[0])/P),int(np.ceil((b[0]-lo[0])/P))),slice(int((a[1]-lo[1])/P),int(np.ceil((b[1]-lo[1])/P))),slice(int((a[2]-lo[2])/P),int(np.ceil((b[2]-lo[2])/P))))
placed=[]
for name,dims,rr in MODS:
  found=None
  for r in rr:
    a,b=REG[r]
    perms=sorted(set(itertools.permutations(dims)),key=lambda d:-d[0])
    if name.startswith('MPU'): perms=[(dims[0],dims[2],dims[1])]      # flat, X arrow forward
    for d in perms:
        if found: break
        d=np.array(d)
        for x0 in np.arange(a[0],b[0]-d[0]+0.01,1.0):
            for y0 in (np.arange(a[1],b[1]-d[1]+0.01,1.0) if r!='B' else np.arange(a[1],b[1]-d[1]+0.01,1.0)):
                ws=np.arange(a[2],b[2]-d[2]+0.01,1.0)
                if r=='L': ws=ws[::1]
                if r=='R': ws=ws[::-1]
                for z0 in ws:
                    p0=np.array([x0,y0,z0]); c=cells(p0,p0+d)
                    if not occ[c].any(): found=(p0,d); break
                if found: break
            if found: break
        if found: break
  if found:
        p0,d=found; occ[cells(p0-0.5,p0+d+0.5)]=True; placed.append((name,r,p0.tolist(),d.tolist()))
        print('%-24s at x %.1f..%.1f  y %.1f..%.1f  w %.1f..%.1f'%(name,p0[0],p0[0]+d[0],p0[1],p0[1]+d[1],p0[2]-ZC,p0[2]+d[2]-ZC))
  else: print('%-24s DOES NOT FIT in %s'%(name,rr))
json.dump(placed,open('anim/boards_placed.json','w'))
