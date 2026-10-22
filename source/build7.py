# Folding cup holder v5 for the Begode Master front handle: slim version.
# The basket is a flat tray (floor + low lip) hinged right at the plate. Fold the tray up flat,
# then the ring down in front of it: the ring keeps the tray shut and the pack is ~35 mm deep.
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

RING_IN=40.0; RING_OUT=44.0; RING_T=8.0; H0=13.0   # folded, the ring lies just in front of the tray
BASK_OUT=37.0; BASK_WALL=2.5; BASK_D=10.5; BASK_FLOOR=2.5
BASK_DROP=2.0                            # lip just below the hinge: folded, the tray sits flat on the plate
A=np.array([8.,0.])
RING_CX=A[0]+4+RING_OUT                  # ring centre, open
B=np.array([8.,-92.])                    # tray hinge at the plate
PLATE_W=20.0; CH0,CH1=PLATE_W+0.4,PLATE_W+4.4
AXLE=4.3; TOP=12.0; EAR_A=3.79; BOT=B[1]-14
HOLES=[(y,z) for y in (-15,15) for z in (-20,-62)]   # 4x M4 to the hanger

def plate():
    p=box(-5,0,-PLATE_W,PLATE_W,BOT,TOP)
    p+=hull(cyl_y(6,-PLATE_W,PLATE_W,*A),box(-5,0,-PLATE_W,PLATE_W,-6,6))
    p+=hull(cyl_y(6,-PLATE_W,PLATE_W,*B),box(-5,0,-PLATE_W,PLATE_W,B[1]-6,B[1]+6))
    # ears the levers' tails stop against when open
    p+=both(lambda: box(-5,EAR_A,PLATE_W-1,CH1,6.5,14))
    p+=both(lambda: box(-5,B[0]-2.7,PLATE_W-1,CH1,B[1]-14,B[1]-6.3))
    p-=cyl_y(AXLE/2,-40,40,*A); p-=cyl_y(AXLE/2,-40,40,*B)
    for y,z in HOLES: p-=mf.Manifold.cylinder(10,2.2,2.2,32).rotate([0,90,0]).translate([-8,y,z])
    return p

def ring_lever():
    band=(cyl_z(RING_OUT,0,RING_T)-cyl_z(RING_IN,-1,RING_T+1)).translate([RING_CX,0,A[1]+H0])
    def cheek():
        c=hull(cyl_y(6,CH0,CH1,*A),box(A[0]+2,RING_CX-RING_OUT+9,CH0,CH1,A[1]+H0,A[1]+H0+RING_T))
        # tail meets the plate ears: the ring cannot tip up past level
        return c+hull(cyl_y(4,CH0,CH1,*A),cyl_y(2.5,CH0,CH1,*(A+9*U2(100))))
    return band+both(cheek)-cyl_y(AXLE/2,-40,40,*A)

def basket_lever():
    cx=B[0]+44.0                         # tray clear of the hinge boss
    cup=cyl_z(BASK_OUT,-BASK_D,0,cx)-cyl_z(BASK_OUT-BASK_WALL,-BASK_D+BASK_FLOOR,1,cx)
    cup=cup.translate([0,0,B[1]-BASK_DROP])
    fz=B[1]-BASK_DROP-BASK_D
    for i in range(6):
        a=np.radians(60*i); cup-=cyl_z(6,fz-1,fz+BASK_FLOOR+1,cx+20*np.cos(a),20*np.sin(a),40)
    cup-=cyl_z(6,fz-1,fz+BASK_FLOOR+1,cx,0,40)
    def cheek():
        c=hull(cyl_y(6,CH0,CH1,*B),box(B[0]+2,cx-BASK_OUT+9,CH0,CH1,B[1]-BASK_DROP-BASK_D,B[1]-BASK_DROP))
        # tail meets the lower ears: a cup's weight holds the tray level
        return c+hull(cyl_y(3,CH0,CH1,*B),cyl_y(2.5,CH0,CH1,*(B+8*U2(270))))
    return cup+both(cheek)-cyl_y(AXLE/2,-40,40,*B)

if __name__=='__main__':
    pl=plate(); ring=ring_lever(); bask=basket_lever()
    def hit(t1,t2):
        r=rot_about(ring,A,t1); b=rot_about(bask,B,t2)
        v={'ring/tray':(r^b).volume(),'ring/plate':(r^pl).volume(),'tray/plate':(b^pl).volume()}
        return {k:round(x,1) for k,x in v.items() if x>0.05}
    T1=list(range(0,-91,-10)); T2=list(range(0,91,10))
    print('      '+''.join(f'{t:5d}' for t in T2)+'   <- tray angle')
    for t1 in T1:
        print(f'{t1:5d} '+''.join('    .' if not hit(t1,t2) else f'{min(sum(hit(t1,t2).values()),9999):5.0f}' for t2 in T2))
    print('fold order: tray up, then ring down')
    bad=[(t2,hit(0,t2)) for t2 in np.arange(0,90.1,2.5) if hit(0,t2)]+[(t1,hit(t1,90)) for t1 in np.arange(0,-90.1,-2.5) if hit(t1,90)]
    print('  collisions:',bad or 'none')
    for t in (1,2,3): print('  ring past level',t,hit(t,0))
    for t in (-1,-2,-3): print('  tray past level',t,hit(0,t))
    print('  tray trying to open while ring folded:',[(a,sum(hit(-90,a).values())) for a in (88,85,80)])
    f=pl+rot_about(ring,A,-90)+rot_about(bask,B,90); bb=f.bounding_box()
    o=pl+ring+bask; ob=o.bounding_box()
    print('  folded pack (deep x wide x tall) mm',round(bb[3]-bb[0]),round(bb[4]-bb[1]),round(bb[5]-bb[2]))
    print('  open (deep x tall) mm',round(ob[3]-ob[0]),round(ob[5]-ob[2]),' ring top to tray floor',round(H0+RING_T-(B[1]-BASK_DROP-BASK_D+BASK_FLOOR)))
