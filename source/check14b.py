import numpy as np, trimesh, manifold3d as mf
exec(open('build14.py').read())
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder8()
gc=gimbal(False)
# stowed: drop each inner ring 1 mm - the ledge must catch it
for k in (1,2,3):
    r=place(gc[1][k].translate([0,-1,0]),X_IN); print('stowed ring',k+1,'dropped 1 mm hits the ledge:',round((r^handle).volume(),1))
print('gimbal ring re-check vs ring1 roll ±20:',[round((gc[0]^rollm(gc[1][0],r)).volume(),2) for r in (-20,20)])
b=gc[0].bounding_box(); print('gimbal ring size',round(b[3]-b[0],1),round(b[4]-b[1],1),round(b[5]-b[2],1))
b=gimbal(True)[1][0].bounding_box(); print('ring1 size',round(b[3]-b[0],1),round(b[5]-b[2],1),'  fits through gimbal inner Ø',2*OR0)
