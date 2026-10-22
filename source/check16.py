import numpy as np, trimesh, manifold3d as mf, itertools
exec(open('build16.py').read())
U_=lambda ms: mf.Manifold.batch_boolean(ms,mf.OpType.Add)
orig=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))
handle=orig+handle_adds()
hs=housing(); sv=H2(servo2()); df=diffuser2(1)+diffuser2(-1)
tr=tray(); lamp=hs+sv+df+tr
OBL=obstacles3(True); OBR=obstacles3(False)
arms=lambda th: arm(1,th)+arm(-1,th)
print('--- lamp in the opening ---')
print('housing vs wheel (cover, shells, controller):',round((hs^OBR).volume(),2),' vs handle:',round((hs^handle).volume(),2),' servo vs housing:',round((sv^hs).volume(),2))
print('handle v11 vs wheel:',round((handle^OBR).volume(),2),' tray vs wheel',round((tr^OBR).volume(),2),' tray vs housing',round((tr^hs).volume(),2),' tray vs handle',round((tr^handle).volume(),2))
for a in (-TILT2,-5,0,5,TILT2):
    hd=tilt2(H2(head2()),a)
    print(f'  head at {a:+.0f}°: vs housing {(hd^hs).volume():.2f}  servo {(hd^sv).volume():.2f}  cover {(hd^OBR).volume():.2f}')
for a in (-TILT2,TILT2):   # lowest point of the lens opening must stay above the cover's lip
    p=np.array([HU0_2,-8.0]); c,s=np.cos(np.radians(a)),np.sin(np.radians(a))
    print(f'  lens bottom at {a:+.0f}°: Y {PY2+p[0]*s+p[1]*c:.1f}  (lip top {OPEN_BOT:.1f})')
print('head clearance to the housing top / floor at ±10°:',[(a,round(HOUSE_Y1-WALL-(tilt2(H2(head2()),a).bounding_box()[4]),1),round(tilt2(H2(head2()),a).bounding_box()[1]-TRAY_Y1,1)) for a in (-TILT2,TILT2)])
print('--- can holder ---')
print('hinge',HP,'R',round(R_ARM,1),'in',round(TH_IN,1),'out',TH_OUT,'GS',GS,'GD',np.round(GD,1))
for th in np.linspace(TH_IN,TH_OUT,6):
    a=arms(th); print(f'  arms at {th:6.1f}: vs handle {(a^handle).volume():6.2f}  lamp {(a^lamp).volume():5.2f}  wheel {(a^OBR).volume():5.2f}')
st=U_(place_holder(TH_IN))
print('swung in vs wheel at full suspension',round((st^OBL).volume(),2),' handle',round((st^handle).volume(),2),' lamp',round((st^lamp).volume(),2),' arms',round((st^arms(TH_IN)).volume(),2))
b=st.bounding_box(); print('  swung in X',round(b[0],1),'..',round(b[3],1),' Y',round(b[1],1),'..',round(b[4],1),' gap to the plate (bottomed)',round(b[1]-M2.PLATE_LOW,1),' to the cable',round(M2.CABLE_X-b[3],1))
print('  tip test:',[(d,round((U_(place_holder(TH_IN,d,0))^(handle+tr)).volume(),1)) for d in (-2,2)],[(d,round((U_(place_holder(TH_IN,0,d))^(handle+tr)).volume(),1)) for d in (-2,2)])
worst=0; bad=[]
for th in np.linspace(TH_IN-3,TH_OUT,10):
    g=U_(place_holder(th,floor_up=True)); v=(g^(handle+lamp+OBR)).volume()+(g^arms(th)).volume(); worst=max(worst,v)
    if v>0.05: bad.append((round(th),round(v,1)))
print('swinging (wheel at rest): worst',round(worst,2),bad)
print('arm stop:',[(t,round((arms(t)^handle).volume(),2)) for t in (TH_OUT+3,TH_OUT,TH_OUT-1,TH_OUT-2.5)])
worst=0; bad=[]
for p,r in itertools.product(range(-25,26,5),range(-20,21,5)):
    e=U_(place_holder(TH_OUT,p,r,False)); v=(e^(handle+lamp+OBR)).volume()+(e^arms(TH_OUT)).volume(); worst=max(worst,v)
    if v>0.05: bad.append((p,r,round(v,1)))
print('out, pitch ±25 x roll ±20: worst',round(worst,2),bad[:8])
can=cylV(33,FLOOR_Y,FLOOR_Y+115,0,0); fl=GD[1]+FLOOR_Y
bad=[]
for p,r in itertools.product((-25,-15,0,15,25),(-20,0,20)):
    v=(place(can,GD,p,r)^(handle+lamp+arms(TH_OUT)+OBR)).volume()
    if v>0.05: bad.append((p,r,round(v,1)))
print('can: top Y',round(fl+115,1),' vs everything ±25/±20:',bad if bad else 'clear')
cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
cone=cone.rotate([0,0,180+TOF_DOWN]).translate([HOUSE_X0-1,TOF2[1],ZC+TOF2[0]])^box(-3000,HOUSE_X0-1.5,M2.GROUND+5,300,-400,300)
print('road sensor vs handle/holder in/out/wheel:',round((cone^(handle+st+arms(TH_IN))).volume(),1),round((cone^U_(place_holder(TH_OUT)+[arms(TH_OUT)])).volume(),1),
      round((cone^OBR).volume(),1),' can worst',max(round((cone^place(can,GD,p,r)).volume(),1) for p in (-25,0,25) for r in (-20,0,20)))
beam=lambda X: PY2-10-np.tan(np.radians(7))*(PX2+HU0_2-X)
print('beam lower edge over the can front: Y',round(beam(GD[0]-33),1),' can top',round(fl+115,1))
for nm,m in (('handle v11',handle),('tray',tr),('housing',hs),('head',head2()),('arm',arm_local(1))):
    t=to_tm(m); print(nm,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
