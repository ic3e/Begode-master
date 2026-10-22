import numpy as np, trimesh, manifold3d as mf
exec(open('build18.py').read())
orig=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))
handle=orig+handle_adds3()
hs=housing5(); win=window(); ld=lid3(); sv=H3(servo3()); df=diffuser5(1)+diffuser5(-1)
OBL=obstacles3(True); OBR=obstacles3(False)
print('housing vs wheel (suspension bottomed):',round((hs^OBL).volume(),2),' window vs wheel:',round((win^OBR).volume(),2),' lid:',round((ld^OBL).volume(),2))
print('vs handle: housing',round((hs^handle).volume(),2),' window',round((win^handle).volume(),2),' window vs housing',round((win^hs).volume(),2),' diffusers vs housing',round((df^hs).volume(),2))
print('window front X',round(win.bounding_box()[0],2),' cover tip',round(M2.COVER_X,2),' -> sits',round(win.bounding_box()[0]-M2.COVER_X,2),'mm behind it')
for a in (-TILT2,0,TILT2):
    hd=tilt3(H3(head3()),a); print(f'  head {a:+.0f}°: vs housing {(hd^hs).volume():.2f}  servo {(hd^sv).volume():.2f}  window {(hd^win).volume():.2f}')
cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
cone=cone.rotate([0,0,180+TOF_DOWN]).translate([LOW_X0-1,TOF5[1],ZC+TOF5[0]])^box(-3000,LOW_X0-1.5,M2.GROUND+5,300,-400,300)
print('road sensor view vs wheel/handle/lamp:',round((cone^OBR).volume(),1),round((cone^handle).volume(),1),round((cone^(hs+win+ld)).volume(),1))
# drops: for a flat ground meeting the wheel from direction d, the first contact is the support point of
# wheel + handle; the lamp is safe if its own support along d stays behind that by a margin.
W=np.vstack([m.vertices for m,c in model3()]+[to_tm(handle).vertices])
L=np.vstack([to_tm(m).vertices for m in (hs,win,ld,df)])
def margin(d): d=np.array(d,float); d/=np.linalg.norm(d); return (W@d).max()-(L@d).max()
named={'front':(-1,0,0),'front, 45° down':(-1,-1,0),'front, 45° up':(-1,1,0),'front-left':(-1,0,-1),'front-right':(-1,0,1),
       'left side':(0,0,-1),'right side':(0,0,1),'top (upside down)':(0,1,0),'back':(1,0,0)}
for k,d in named.items(): print(f'  fall {k:18s}: lamp sits {margin(d):6.1f} mm behind the first contact')
rng=np.random.default_rng(1); D=rng.normal(size=(20000,3)); D/=np.linalg.norm(D,axis=1)[:,None]
D=D[D[:,1]>-0.85]                                  # leave out "standing on the tyre"
m=(W@D.T).max(0)-(L@D.T).max(0); i=m.argmin()
print('worst of',len(D),'fall directions: lamp',round(m[i],1),'mm behind the first contact, direction',np.round(D[i],2))
for nm,mm in (('housing',hs),('window',win),('head',head3()),('lid',ld),('handle v12',handle)):
    t=to_tm(mm); print(nm,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
