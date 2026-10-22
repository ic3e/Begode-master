import numpy as np, trimesh, manifold3d as mf
exec(open('build17.py').read())
orig=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))
handle=orig+handle_adds3()
hs=housing3(); ld=lid3(); sv=H3(servo3()); df=diffuser3(1)+diffuser3(-1)
lamp=hs+ld+sv+df
OBL=obstacles3(True); OBR=obstacles3(False)
print('housing vs wheel at full suspension:',round((hs^OBL).volume(),2),' lid:',round((ld^OBL).volume(),2),' vs handle:',round((hs^handle).volume(),2),round((ld^handle).volume(),2))
print('handle v12 vs wheel:',round((handle^OBR).volume(),2),'  servo vs housing:',round((sv^hs).volume(),2),'  lid vs housing:',round((ld^hs).volume(),2))
for a in (-TILT2,-5,0,5,TILT2):
    hd=tilt3(H3(head3()),a)
    print(f'  head {a:+.0f}°: vs housing {(hd^hs).volume():.2f}  servo {(hd^sv).volume():.2f}  wheel {(hd^OBR).volume():.2f}')
bb=[tilt3(H3(head3()),a).bounding_box() for a in (-TILT2,TILT2)]
print('head room top / bottom at ±10°:',[(round(HOUSE_Y1-WALL-b[4],1),round(b[1]-HOUSE_Y0,1)) for b in bb])
for a in (-TILT2,TILT2):
    c,s=np.cos(np.radians(a)),np.sin(np.radians(a)); print(f'  lens bottom at {a:+.0f}°: Y {PY3+HU0_3*s-8*c:.1f} (lip {OPEN_BOT:.1f})')
b=ld.bounding_box(); print('lid bottom Y',round(b[1],1),' cross plate when bottomed',M2.PLATE_LOW,' gap',round(b[1]-M2.PLATE_LOW,1))
b=hs.bounding_box(); print('housing front X',round(b[0],1),'(shell fronts',M2.SHELL_X,', cover tip',M2.COVER_X,')  back',round(b[3],1),' cable at',M2.CABLE_X)
cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
cone=cone.rotate([0,0,180+TOF_DOWN]).translate([LOW_X0-1,TOF3[1],ZC+TOF3[0]])^box(-3000,LOW_X0-1.5,M2.GROUND+5,300,-400,300)
print('road sensor view vs wheel/handle/lamp:',round((cone^OBR).volume(),1),round((cone^handle).volume(),1),round((cone^lamp).volume(),1))
print('road sensor hits the road about',round((TOF3[1]-M2.GROUND)/np.sin(np.radians(TOF_DOWN))/1000,2),'m ahead')
for nm,m in (('handle v12',handle),('housing',hs),('lid',ld),('head',head3())):
    t=to_tm(m); print(nm,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
