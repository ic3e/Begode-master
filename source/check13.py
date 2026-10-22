import numpy as np, trimesh, manifold3d as mf, types
exec(open('build13.py').read())
_g={}; exec(open('master_model.py').read().split("\nif __name__=='__main__':")[0],_g); MM=types.SimpleNamespace(**_g)
def M(t): return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices,np.float32),tri_verts=np.asarray(t.faces,np.uint32)))
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder8()
lamp=servo_block2()+elec_block2()+lid2()+H(servo_model()[0])+diffuser(1)+diffuser(-1)
hd=H(head())
fixed=handle+lamp
U_=lambda ms: mf.Manifold.batch_boolean(ms,mf.OpType.Add)
arms=lambda xp: arm(1,xp,False)+arm(-1,xp,False)
bc=basket(False); be=basket(True)
print('rings overlap each other: collapsed',round(sum((bc[i]^bc[j]).volume() for i in range(4) for j in range(i+1,4)),2),
      ' extended',round(sum((be[i]^be[j]).volume() for i in range(4) for j in range(i+1,4)),2))
for xp in np.linspace(X_IN,X_OUT,6):
    a=arms(xp); print(f'  pivot at X {xp:6.1f}: arms vs handle {(a^handle).volume():.2f}  vs lamp {(a^lamp).volume():.2f}')
st=U_(place_basket(bc,X_IN))
print('stowed (flat stack) vs handle/lamp/arms:',round((st^fixed).volume(),2),round((st^arms(X_IN)).volume(),2))
print('stowed, trying to swing:',[(d,round((U_(place_basket(bc,X_IN,d))^handle).volume(),1)) for d in (-3,-2,2,3)])
print('sliding out with the stack flat:',[(round(xp),round((U_(place_basket(bc,xp))^fixed).volume(),1)) for xp in np.linspace(X_IN,X_OUT,6)])
worst=0
for d in range(-25,26,5):
    ex=U_(place_basket(be,X_OUT,d)); v=(ex^fixed).volume()+(ex^arms(X_OUT)).volume(); worst=max(worst,v)
    if v>0.05: print('  out, swing',d,'deg: hits',round(v,1))
print('out, opened, swinging -25..25 deg: worst overlap',round(worst,2))
# road sensor and lamp head
cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
cone=cone.rotate([0,0,180+TOF_DOWN]).translate([BX0-4,TOF_Y,ZC+TOF_W])^box(-3000,-60,MM.GROUND+5,300,-400,300)
new=handle+arms(X_OUT)+U_(place_basket(be,X_OUT))
print('road sensor view vs rails/arms/basket (out):',round((cone^new).volume(),1),' stowed:',round((cone^(arms(X_IN)+st)).volume(),1))
print('lamp head ±13 vs basket/rails:',[round((tilt(hd,a)^(new+st)).volume(),2) for a in (-13,13)])
# the wheel
wheel=U_([M(m) for m,c in MM.model()])
print('wheel vs handle+rails:',round((wheel^handle).volume(),1),' vs basket out/stowed:',round((wheel^new).volume(),1),round((wheel^(st+arms(X_IN))).volume(),1))
# drinks: can 66x115, coffee cup 90/60x110; where they sit and where their centre of gravity is
floor=YP+ring_tops(True)[3]-RING_H+LIP
print('floor at Y',round(floor,1),' pivot at Y',YP)
print('  can top Y',round(floor+115,1),' centre of gravity',round(floor+57.5-YP,1),'mm from the pivot (negative = below = stable)')
print('  coffee cup top Y',round(floor+110,1),' full cup centre of gravity about',round(floor+45-YP,1),'mm from the pivot')
lens_y=PY; 
for X,nm in ((X_OUT-33,'can front edge'),(X_OUT-45,'cup front edge')):
    beam_low=lens_y-np.tan(np.radians(7))*(PX+HU0-X)
    print(f'  beam lower edge at {nm} (X {X:.0f}): Y {beam_low:.1f}')
print('click bump: snaps in stowed/out, rubs in between:',[(round(xp),round(((arm(1,xp)^handle).volume()),2)) for xp in (X_IN,(X_IN+X_OUT)/2,X_OUT)])
for nm,m in (('handle v8',handle),('arm',arm(1,X_IN))): t=to_tm(m); print(nm,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
for k,r in enumerate(be): t=to_tm(r); print('ring',k+1,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
