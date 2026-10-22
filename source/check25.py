# Lamp v6.2 + handle v17 checks: the v6.1 checks on the print-ready parts (fit, swing, stops, assembly, sealing, duct, drops).
import numpy as np, trimesh, manifold3d as mf
from matplotlib.path import Path
from scipy import ndimage
exec(open('build26.py').read())
handle=handle17()
hs=housing11(); pl=top_plate11(); win=window(); ld=lid10(); gk=lid_tape(); df=mf.Manifold()
bar=led_bar(); cl=mf.Manifold(); sv=servo6(); brg=H6(bearing7()); bt=buttons8()
fr=lambda a: tilt6(H6(lens_frame7()+lenses6()),a)
TOFWIN=mf.Manifold()
lamp=hs+pl
OBL=obstacles3(True); OBR=obstacles3(False)
v=lambda m: round(m.volume(),2)
print('vs wheel (suspension bottomed): housing+plate',v(lamp^OBL),' lid',v(ld^OBL),' gasket',v(gk^OBL),' window',v(win^OBR))
print('lid above the cross plate when bottomed: %.1f mm'%(ld.bounding_box()[1]-M2.PLATE_LOW))
print('vs handle: housing',v(hs^handle),' plate',v(pl^handle))
print('handle vs wheel (bottomed / at rest):',v(handle^OBL),v(handle^OBR),' left-hand version:',v(handle17(-1)^OBL),v(handle17(-1)^OBR))
print('plate fingers on the bar: overlap',v(pl^bar),' gap at the fins %.2f mm'%(min(to_tm(pl).vertices[(to_tm(pl).vertices[:,0]>BAR_X1-0.5)&(to_tm(pl).vertices[:,0]<BAR_X1+4)][:,0])-BAR_X1))
print('parts that must not overlap: plate/housing',v(pl^hs),' lid/gasket',v(ld^gk),' gasket/housing',v(gk^hs),' window/housing',v(win^lamp),
      ' bar/housing',v(bar^hs),' bar/plate',v(bar^pl),' clamp/housing',v(cl^hs),' clamp/bar',v(cl^bar),' servo/housing',v(sv^hs),
      ' bearing/housing',v(brg^hs),' buttons/housing',v(bt^hs),' sensor window/housing',v(TOFWIN^hs))
for a in (-12,-10,0,10,12):
    f=fr(a); print(f'  lenses {a:+3d}°: vs housing {v(f^hs)}  plate {v(f^pl)}  window {v(f^win)}  LED bar {v(f^bar)}  servo {v(f^sv)}')
lug=H6(box(LUG6[0],LUG6[1],-LUG6[2],LUG6[2],-36.2,-ARM_W1+0.1)); stops=stop6_lower()+stop6_upper()
for a in (-13.5,13.5):
    print(f'  lenses pushed to {a:+.1f}°: lug into the stops {v(tilt6(lug,a)^stops)}, rest into anything {v((fr(a)-tilt6(lug,a))^(hs+pl+win+bar+sv))}')
lo=hi=0
for a in np.arange(10,14,0.1):
    if not hi and (tilt6(lug,a)^stops).volume()>0.01: hi=a
    if not lo and (tilt6(lug,-a)^stops).volume()>0.01: lo=a
print(f'  stops meet at +{hi:.1f}° / -{lo:.1f}°')
# lens base vs the stars: the closest approach over the swing
st=mf.Manifold.batch_boolean([mf.Manifold.cylinder(STAR2,8,8,48).rotate([0,-90,0]).translate([BAR_X0,PY3,ZC+w]) for w in OPTIC_W],mf.OpType.Add)
for a in (0,10,12):
    gap=min(((tilt6(H6(lenses6()),s*a)^st.translate([-g,0,0])).volume()>0.001 and g or 9) for s in (-1,1) for g in np.arange(0,2.01,0.05))
    print(f'  lens base to the stars at ±{a}°: {gap:.2f} mm' if gap<9 else f'  lens base to the stars at ±{a}°: over 2 mm')
# putting it together
unit=fr(0)+sv+brg
print('lens frame + servo lifted straight out:',max(v(unit.translate([0,d,0])^hs) for d in np.arange(0.5,45,0.5)))
barin=max(v(bar.translate([2.5,d,0])^hs) for d in np.arange(0,40,0.5))
print('LED bar lowered in 2.5 mm back from the bulkhead, then pushed forward:',barin,' pushed home:',v(bar^hs))
print('plate lifted off:',max(v(pl.translate([0,d,0])^(hs+unit+bar+cl)) for d in np.arange(0.5,20,0.5)))
# ---- sealing: flood the air reachable from outside and look where it gets ----
P=0.5
asm=mf.Manifold.batch_boolean([hs,pl,ld,gk,win,df,TOFWIN,bt,bar,cl,sv,brg,fr(0)]+
    [cylV(2.5,HOUSE_YS-1,HOUSE_YS+3,USB_FLOOR[0],s*USB_FLOOR[1]) for s in (-1,1)]+                      # grommets
    [cylV(1.8,PLATE_Y0-1,HOUSE_Y1+0.1,x,w) for x,w in PLATE_SCREWS9]+                                   # plate screws
    [cylV(1.8,LOW_Y0-6,LOW_Y0+2,x,w) for x,w in LID_POSTS]+                                            # lid screws
    [tape_frame(),mf.Manifold.cylinder(WALL+2,3.4,3.4,24).rotate([0,90,0]).translate([HOUSE_X1-WALL-1,HOUSE_YS+8,ZC-56])],  # window tape, power-cable grommet
    mf.OpType.Add)
t=to_tm(asm); b=t.bounds; b0=b[0]-2; b1=b[1]+2
xs=np.arange(b0[0],b1[0],P); zs=np.arange(b0[2],b1[2],P); ys=np.arange(b0[1],b1[1],P)
X,Z=np.meshgrid(xs,zs,indexing='ij'); pts=np.c_[X.ravel(),Z.ravel()]
solid=np.zeros((len(xs),len(ys),len(zs)),bool)
for j,y in enumerate(ys):
    sec=t.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
    if sec is None: continue
    occ=np.zeros(len(pts),int)
    for e in sec.discrete:
        occ^=Path(e[:,[0,2]]).contains_points(pts)
    solid[:,j,:]=occ.reshape(len(xs),len(zs)).astype(bool)
air=~solid; lab,n=ndimage.label(air)
outside=lab[0,0,0]
def at(x,y,w): return lab[int((x-b0[0])/P),int((y-b0[1])/P),int((ZC+w-b0[2])/P)]
probes={'trap (wet)':(-60,-40,20),'passage (wet)':(-45,-18,4),'fins (wet)':(-30,18,0),'rear exit (wet)':(-20,-17,0),
        'lens bay / inside of the window':(-58.3,18,0),'left pivot pocket':(-40.5,15,-35),'left side bay':(-30,0,-55),
        'right side bay':(-35,15,55),'electronics box':(-37,-35,0),'button box':(-50,-36,0)}
for k,p in probes.items():
    l=at(*p); print(f'  {k:34s}: '+('reached from outside' if l==outside else ('solid' if l==0 else 'sealed')))
# airflow cross-sections along the duct (mm^2)
def area_x(x,y0,y1,w0,w1):
    i=int((x-b0[0])/P); j0,j1=int((y0-b0[1])/P),int((y1-b0[1])/P); k0,k1=int((ZC+w0-b0[2])/P),int((ZC+w1-b0[2])/P)
    return (lab[i,j0:j1,k0:k1]==outside).sum()*P*P
def area_y(y,x0,x1,w0,w1):
    j=int((y-b0[1])/P); i0,i1=int((x0-b0[0])/P),int((x1-b0[0])/P); k0,k1=int((ZC+w0-b0[2])/P),int((ZC+w1-b0[2])/P)
    return (lab[i0:i1,j,k0:k1]==outside).sum()*P*P
print('duct sections: chin slots %.0f, trap -> passage %.0f, passage %.0f, into the fins %.0f, rear exit %.0f mm2'%(
    area_x(LOW_X0+1.2,LOW_Y0,LIP_Y,-40,40),area_y(PASS_Y0-1.0,HOUSE_X0+FACE,DIV_X[0],-40,40),area_x(-52,PASS_Y0,FLOOR_Y[0],-37,37),
    area_y(FLOOR_Y[0]+1,-42,-30,-37,37),area_y(HOUSE_Y0+1,LOW_X1,HOUSE_X1-WALL,-37,37)))
# drops
W=np.vstack([m.vertices for m,c in model3()]+[to_tm(handle).vertices])
L=np.vstack([to_tm(m).vertices for m in (hs,pl,win,ld,df)])
rng=np.random.default_rng(1); D=rng.normal(size=(20000,3)); D/=np.linalg.norm(D,axis=1)[:,None]; D=D[D[:,1]>-0.85]
m=(W@D.T).max(0)-(L@D.T).max(0)
fwd=(W@[-1,0,0]).max()-(L@[-1,0,0]).max()
print('drops: worst of',len(D),'directions %.1f mm, straight forward %.1f mm'%(m.min(),fwd))
for nm,mm in (('housing',hs),('top plate',pl),('lens frame',lens_frame7()),('lid',ld),('lid tape',gk),('handle v17',handle)):
    tt=to_tm(mm); print(nm,'watertight',tt.is_watertight,'bodies',len(tt.split(only_watertight=False)))
