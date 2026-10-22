import numpy as np, trimesh, manifold3d as mf, types, itertools
exec(open('build14.py').read())
_g={}; exec(open('master_model.py').read().split("\nif __name__=='__main__':")[0],_g); MM=types.SimpleNamespace(**_g)
def M(t): return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices,np.float32),tri_verts=np.asarray(t.faces,np.uint32)))
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder8()
lamp=servo_block2()+elec_block2()+lid2()+H(servo_model()[0])+diffuser(1)+diffuser(-1)
hd=H(head()); fixed=handle+lamp
U_=lambda ms: mf.Manifold.batch_boolean(ms,mf.OpType.Add)
arms=lambda xp: arm(1,xp,False)+arm(-1,xp,False)
gc=gimbal(False); ge=gimbal(True); G=gc[0]
be=ge[1]; bc=gc[1]
print('gimbal ring vs ring1, roll -20..20:',[round((G^rollm(bc[0],r)).volume(),2) for r in (-ROLL,-10,0,10,ROLL)],
      ' extended basket',[round((G^U_([rollm(r,ro) for r in be])).volume(),2) for ro in (-ROLL,ROLL)])
print('how far ring1 can roll before it touches the gimbal ring:',next(r for r in range(15,60) if (G^rollm(bc[0],r)).volume()>0.01 or (G^rollm(bc[0],-r)).volume()>0.01),'deg')
print('gimbal ring vs arms (pitch -25..25):',[round((place(G,X_OUT,p)^arms(X_OUT)).volume(),2) for p in (-PITCH,0,PITCH)])
for xp in np.linspace(X_IN,X_OUT,5):
    a=arms(xp); print(f'  pivot at X {xp:6.1f}: arms vs handle {(a^handle).volume():.2f}  vs lamp {(a^lamp).volume():.2f}')
st=U_(place_gimbal(gc,X_IN))
print('stowed vs handle/lamp/arms:',round((st^fixed).volume(),2),round((st^arms(X_IN)).volume(),2))
print('stowed, trying to pitch:',[(d,round((U_(place_gimbal(gc,X_IN,d))^handle).volume(),1)) for d in (-3,-2,2,3)])
print('stowed, trying to roll: ',[(d,round((U_(place_gimbal(gc,X_IN,0,d))^handle).volume(),1)) for d in (-3,-2,2,3)])
print('sliding out flat:',[(round(xp),round((U_(place_gimbal(gc,xp))^fixed).volume(),1)) for xp in np.linspace(X_IN,X_OUT,6)])
worst=0; bad=[]
for p,r in itertools.product(range(-25,26,5),range(-20,21,5)):
    ex=U_(place_gimbal(ge,X_OUT,p,r)); v=(ex^fixed).volume()+(ex^arms(X_OUT)).volume(); worst=max(worst,v)
    if v>0.05: bad.append((p,r,round(v,1)))
print('out, opened, pitch -25..25 x roll -20..20: worst overlap',round(worst,2),bad[:12])
cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
cone=cone.rotate([0,0,180+TOF_DOWN]).translate([BX0-4,TOF_Y,ZC+TOF_W])^box(-3000,-60,MM.GROUND+5,300,-400,300)
new=handle+arms(X_OUT)+U_(place_gimbal(ge,X_OUT))
print('road sensor view vs holder out:',round((cone^new).volume(),1),' stowed:',round((cone^(arms(X_IN)+st)).volume(),1),
      ' out, pitched/rolled:',max(round((cone^U_(place_gimbal(ge,X_OUT,p,r))).volume(),1) for p in (-25,25) for r in (-20,20)))
print('lamp head ±13 vs holder:',[round((tilt(hd,a)^(new+st)).volume(),2) for a in (-13,13)])
wheel=U_([M(m) for m,c in MM.model()])
print('wheel vs handle+rails:',round((wheel^handle).volume(),1),' vs holder out/stowed:',round((wheel^new).volume(),1),round((wheel^(st+arms(X_IN))).volume(),1))
print('wheel vs holder out, pitched/rolled:',max(round((wheel^U_(place_gimbal(ge,X_OUT,p,r))).volume(),1) for p in (-25,25) for r in (-20,20)))
floor=YP+ring_tops(True)[3]-RING_H+LIP
print('floor Y',round(floor,1),' can top Y',round(floor+115,1),' can CoG',round(floor+57.5-YP,1),' coffee CoG',round(floor+45-YP,1),'mm from the pivots')
for X,nm in ((X_OUT-33,'can front edge'),(X_OUT-45,'cup front edge')):
    print(f'  beam lower edge at {nm} (X {X:.0f}): Y {PY-np.tan(np.radians(7))*(PX+HU0-X):.1f}')
b=st.bounding_box(); print('stowed stack: X',round(b[0],1),'..',round(b[3],1),' Y',round(b[1],1),'..',round(b[4],1),' width',round(b[5]-b[2],1))
b=handle.bounding_box(); print('handle width',round(b[5]-b[2],1))
print('click bump:',[(round(xp),round(((arm(1,xp)^handle).volume()),2)) for xp in (X_IN,(X_IN+X_OUT)/2,X_OUT)])
for nm,m in (('handle v9',handle),('arm',arm(1,X_IN)),('gimbal ring',G)): t=to_tm(m); print(nm,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
for k,r in enumerate(be): t=to_tm(r); print('ring',k+1,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
