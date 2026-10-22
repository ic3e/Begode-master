import numpy as np, trimesh, manifold3d as mf, itertools
exec(open('build15.py').read())
U_=lambda ms: mf.Manifold.batch_boolean(ms,mf.OpType.Add)
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder10()
lamp=lamp_fixed(); hd0=lamp_head(0)
OBL=M2.obstacles(True); OBR=M2.obstacles(False)
arms=lambda th: arm(1,th)+arm(-1,th)
print('hinge',np.round(HP,1),'swung in at',round(TH_IN,1),'deg, out at',TH_OUT,' gimbal centre in',GS,'out',np.round(GD,1))
print('--- lamp and handle vs the measured wheel ---')
print('handle v10 vs wheel:',round((handle^OBR).volume(),1),' lamp vs wheel:',round((lamp^OBR).volume(),1),' lamp vs handle:',round((lamp^handle).volume(),1))
print('lamp head ±13 vs wheel/handle/lamp:',[round((lamp_head(a)^(OBR+handle+lamp)).volume(),2) for a in (-13,13)])
print('cover tip to the lamp module back:',round(M2.COVER_X-(BX1+DX),1),'mm')
# cover lifting on a rear hinge: check the nose against the lamp for a few hinge guesses
print('--- holder ---')
for th in np.linspace(TH_IN,TH_OUT,7):
    a=arms(th); print(f'  arms at {th:6.1f}: vs handle {(a^handle).volume():6.2f}  lamp {(a^lamp).volume():5.2f}  wheel(rest) {(a^OBR).volume():5.2f}')
st=U_(place_holder(TH_IN))
print('swung in: vs wheel at full suspension',round((st^OBL).volume(),2),' vs handle',round((st^handle).volume(),2),' vs lamp',round((st^lamp).volume(),2),' vs arms',round((st^arms(TH_IN)).volume(),2))
b=st.bounding_box(); print('  swung in, basket X',round(b[0],1),'..',round(b[3],1),' Y',round(b[1],1),'..',round(b[4],1),' width',round(b[5]-b[2],1))
print('  gap to the cross plate at full suspension:',round(b[1]-M2.PLATE_LOW,1),' to the cable:',round(M2.CABLE_X-b[3],1))
print('  tipping when swung in (ring pressed on the pads):',[(d,round((U_(place_holder(TH_IN,d,0))^handle).volume(),1)) for d in (-2,2)],
      [(d,round((U_(place_holder(TH_IN,0,d))^handle).volume(),1)) for d in (-2,2)])
worst=0; bad=[]
for th in np.linspace(TH_IN-3,TH_OUT,10):
    v=(U_(place_holder(th,floor_up=True))^(handle+lamp+OBR)).volume()+(U_(place_holder(th,floor_up=True))^arms(th)).volume(); worst=max(worst,v)
    if v>0.05: bad.append((round(th),round(v,1)))
print('swinging out (floor up, wheel at rest): worst',round(worst,2),bad)
print('arm stop: overlap with the arm at',[(t,round((arms(t)^handle).volume(),2)) for t in (TH_OUT+3,TH_OUT,TH_OUT-1,TH_OUT-2.5)])
worst=0; bad=[]
for p,r in itertools.product(range(-25,26,5),range(-20,21,5)):
    ex_=U_(place_holder(TH_OUT,p,r,False)); v=(ex_^(handle+lamp+OBR)).volume()+(ex_^arms(TH_OUT)).volume(); worst=max(worst,v)
    if v>0.05: bad.append((p,r,round(v,1)))
print('out, pitch ±25 x roll ±20: worst',round(worst,2),bad[:10])
# the can
fl=GD[1]+FLOOR_Y; can=cylV(33,FLOOR_Y,FLOOR_Y+115,0,0)
print('can: floor Y',round(fl,1),' top Y',round(fl+115,1),' CoG',round(FLOOR_Y+57.5,1),'mm from the axis')
worst=0; bad=[]
for p,r in itertools.product((-25,-15,0,15,25),(-20,0,20)):
    v=(place(can,GD,p,r)^(handle+lamp+arms(TH_OUT)+OBR)).volume()
    if v>0.05: bad.append((p,r,round(v,1)))
print('can vs everything, pitch ±25/±15 x roll ±20:',bad if bad else 'clear')
cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
cone=cone.rotate([0,0,180+TOF_DOWN]).translate([TOF0[0],TOF0[1],ZC+TOF_W])^box(-3000,TOF0[0]+1,M2.GROUND+5,300,-400,300)
print('road sensor view vs handle+holder in/out:',round((cone^(handle+st+arms(TH_IN))).volume(),1),round((cone^U_(place_holder(TH_OUT)+[arms(TH_OUT)])).volume(),1),
      ' vs can (worst):',max(round((cone^place(can,GD,p,r)).volume(),1) for p in (-25,0,25) for r in (-20,0,20)),' vs wheel:',round((cone^OBR).volume(),1))
beam=lambda X: PY-np.tan(np.radians(7))*(PX+HU0+DX-X)
print('beam lower edge over the can front (X',round(GD[0]-33),'): Y',round(beam(GD[0]-33),1),' can top',round(fl+115,1))
for nm,m in (('handle v10',handle),('arm',arm(1,0)),('gimbal ring',gimbal_ring()),('cup ring',cup_ring()),('floor',floor_disc())):
    t=to_tm(m); print(nm,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
