# Folding cup holder v4 for the Begode Master front handle: compact version.
# Ring folds down and hangs behind the folded basket; basket hinge sits forward and high,
# so the folded pack is short and stays well clear of the tyre.
# Local frame: x forward, y across the wheel, z up; mounting plate front face at x=0.
import numpy as np, trimesh, manifold3d as mf
U='../reference/'
OUT='../build_output/'
SEG=96
def to_mf(t): return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices,np.float32),tri_verts=np.asarray(t.faces,np.uint32)))
def to_tm(m):
    g=m.to_mesh(); return trimesh.Trimesh(g.vert_properties[:,:3],g.tri_verts,process=True)
def box(x0,x1,y0,y1,z0,z1): return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def cyl_y(r,y0,y1,x=0,z=0,seg=SEG): return mf.Manifold.cylinder(y1-y0,r,r,seg).rotate([-90,0,0]).translate([x,y0,z])
def cyl_z(r,z0,z1,x=0,y=0,seg=SEG): return mf.Manifold.cylinder(z1-z0,r,r,seg).translate([x,y,z0])
def hull(*ms): return mf.Manifold.batch_hull(list(ms))
def U2(a): a=np.radians(a); return np.array([np.cos(a),np.sin(a)])
def both(f): m=f(); return m+m.mirror([0,1,0])
def rot_about(m,c,deg): return m.translate([-c[0],0,-c[1]]).rotate([0,-deg,0]).translate([c[0],0,c[1]])

RING_IN=40.0; RING_OUT=44.0; RING_T=8.0; H0=4.0
BASK_OUT=37.0; BASK_WALL=2.5; BASK_D=20.0; BASK_FLOOR=2.5
BASK_DROP=6.4                            # rim below the hinge, so it passes under the lug
A=np.array([10.,0.])
RING_CX=A[0]+6+RING_OUT                  # ring centre, open (6 mm clear of the hinge boss)
B=np.array([35.,-52.])                   # basket hinge: forward and high keeps the pack short
PLATE_W=20.0; CH0,CH1=PLATE_W+0.4,PLATE_W+4.4
AXLE=4.3; TOP=12.0; BOT=B[1]-12
HOLES=[(y,z) for y in (-15,15) for z in (-14,-40)]   # 4x M4 to the hanger

def plate():
    p=box(-5,0,-PLATE_W,PLATE_W,BOT,TOP)
    p+=hull(cyl_y(6,-PLATE_W,PLATE_W,*A),box(-5,0,-PLATE_W,PLATE_W,-6,6))
    # lug carrying the basket hinge out in front of the plate
    p+=hull(cyl_y(6,-PLATE_W,PLATE_W,*B),box(-5,0,-PLATE_W,PLATE_W,B[1]-6,B[1]+6))
    # ears the ring's tail stops against when open; the basket's back rim stops under the lug
    p+=both(lambda: box(-5,0,PLATE_W-1,CH1,-8,10))
    p-=cyl_y(AXLE/2,-40,40,*A); p-=cyl_y(AXLE/2,-40,40,*B)
    for y,z in HOLES: p-=mf.Manifold.cylinder(10,2.2,2.2,32).rotate([0,90,0]).translate([-8,y,z])
    return p

def ring_lever():
    band=(cyl_z(RING_OUT,0,RING_T)-cyl_z(RING_IN,-1,RING_T+1)).translate([RING_CX,0,A[1]+H0])
    def cheek():
        c=hull(cyl_y(6,CH0,CH1,*A),box(A[0]+2,RING_CX-RING_OUT+9,CH0,CH1,A[1]+H0,A[1]+H0+RING_T))
        # tail meets the plate ears: the ring cannot tip up past level
        return c+hull(cyl_y(6,CH0,CH1,*A),cyl_y(2.5,CH0,CH1,*(A+7.6*U2(170))))
    return band+both(cheek)-cyl_y(AXLE/2,-40,40,*A)

def basket_lever():
    cx=RING_CX
    cup=cyl_z(BASK_OUT,-BASK_D,0,cx)-cyl_z(BASK_OUT-BASK_WALL,-BASK_D+BASK_FLOOR,1,cx)
    cup=cup.translate([0,0,B[1]-BASK_DROP])
    fz=B[1]-BASK_DROP-BASK_D
    for i in range(6):
        a=np.radians(60*i); cup-=cyl_z(6,fz-1,fz+BASK_FLOOR+1,cx+20*np.cos(a),20*np.sin(a),40)
    cup-=cyl_z(6,fz-1,fz+BASK_FLOOR+1,cx,0,40)
    def cheek():
        return hull(cyl_y(6,CH0,CH1,*B),box(cx-BASK_OUT+3,B[0]+6,CH0,CH1,B[1]-BASK_DROP-8,B[1]-BASK_DROP+1))
    return cup+both(cheek)-cyl_y(AXLE/2,-40,40,*B)

if __name__=='__main__':
    pl=plate(); ring=ring_lever(); bask=basket_lever()
    def hit(t1,t2):
        r=rot_about(ring,A,t1); b=rot_about(bask,B,t2)
        v={'ring/basket':(r^b).volume(),'ring/plate':(r^pl).volume(),'basket/plate':(b^pl).volume()}
        return {k:round(x,1) for k,x in v.items() if x>0.05}
    T1=list(range(0,-91,-10)); T2=list(range(0,91,10))
    print('      '+''.join(f'{t:5d}' for t in T2)+'   <- basket angle')
    for t1 in T1:
        print(f'{t1:5d} '+''.join('    .' if not hit(t1,t2) else f'{min(sum(hit(t1,t2).values()),9999):5.0f}' for t2 in T2))
    print('fold order: basket up, then ring down')
    bad=[(t2,hit(0,t2)) for t2 in np.arange(0,90.1,2.5) if hit(0,t2)]+[(t1,hit(t1,90)) for t1 in np.arange(0,-90.1,-2.5) if hit(t1,90)]
    print('  collisions:',bad or 'none')
    for t in (1,2,3): print('  ring past level',t,hit(t,0))
    for t in (-2,-3,-4,-5): print('  basket past level',t,hit(0,t))
