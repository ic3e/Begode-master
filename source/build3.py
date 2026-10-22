# Folding cup holder for the Begode Master front handle (v3).
# Like the motorcycle ones: the ring folds down, the basket folds up into it,
# Fold the basket up first, then the ring down over it: folded, the ring keeps the basket in.
# (A linkage that moves both at once would have to pass the basket crossways through the ring.)
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

# --- linkage (found by link2.py): pivots and pin points in the x-z plane ---
A=np.array([10.,0.]); B=np.array([18.,-100.])
R_PIN=10.0; AL=40.0; BE=130.0            # pin angles on ring / basket levers, open position
P0=A+R_PIN*U2(AL); Q0=B+R_PIN*U2(BE); LINK=np.linalg.norm(P0-Q0)
H0=16.0                                  # ring sits this far above its pivot: folded, it clears the links
RING_IN=42.0; RING_OUT=48.0; RING_T=8.0; RING_CX=A[0]+54.0
BASK_OUT=38.0; BASK_WALL=2.5; BASK_D=23.0; BASK_FLOOR=2.5
PLATE_W=20.0                             # half width
CH0,CH1=PLATE_W+0.4,PLATE_W+4.4          # lever cheeks
AXLE=4.3                                 # M4 axles
BTAIL=8.0

def both(f):  # mirror a part built on the +y side
    m=f(); return m+m.mirror([0,1,0])

def plate():
    p=box(-5,0,-PLATE_W,PLATE_W,-114,14)
    p+=hull(cyl_y(6,-PLATE_W,PLATE_W,*A),box(-5,0,-PLATE_W,PLATE_W,-6,6))
    p+=hull(cyl_y(6,-PLATE_W,PLATE_W,*B),box(-5,0,-PLATE_W,PLATE_W,B[1]-6,B[1]+6))
    # ears the ring lever's tail stops against when open
    p+=both(lambda: box(-5,0,PLATE_W-1,CH1,-8,10))
    p+=both(lambda: box(-5,B[0]-2.7,PLATE_W-1,CH1,B[1]-14,B[1]-6.3))
    p-=cyl_y(AXLE/2,-40,40,*A); p-=cyl_y(AXLE/2,-40,40,*B)
    # saves plastic and lets rain out
    p-=box(-6,1,-12,12,-80,-24)
    # 4x M4 to bolt it under the lamp bracket (30 x 45 pattern), heads clear of the folded parts
    for y in (-15,15):
        for z in (-30,-75): p-=mf.Manifold.cylinder(10,2.2,2.2,32).rotate([0,90,0]).translate([-8,y,z])
    return p

def ring_lever():
    band=(cyl_z(RING_OUT,0,RING_T)-cyl_z(RING_IN,-1,RING_T+1)).translate([RING_CX,0,A[1]+H0])
    def cheek():
        c=hull(cyl_y(6,CH0,CH1,*A),box(A[0]+2,A[0]+12,CH0,CH1,A[1]+H0,A[1]+H0+RING_T))
        # tail that meets the plate ears: the ring cannot tip up past level
        return c+hull(cyl_y(6,CH0,CH1,*A),cyl_y(2.5,CH0,CH1,*(A+7.6*U2(170))))
    m=band+both(cheek)
    return m-cyl_y(AXLE/2,-40,40,*A)

def basket_lever():
    cx=A[0]+54.0
    cup=cyl_z(BASK_OUT,-BASK_D,0,cx)-cyl_z(BASK_OUT-BASK_WALL,-BASK_D+BASK_FLOOR,1,cx)
    cup=cup.translate([0,0,B[1]])
    # drain holes in the floor, like the motorcycle basket
    for i in range(6):
        a=np.radians(60*i); cup-=cyl_z(7,B[1]-BASK_D-1,B[1]-BASK_D+BASK_FLOOR+1,cx+21*np.cos(a),21*np.sin(a),40)
    cup-=cyl_z(6,B[1]-BASK_D-1,B[1]-BASK_D+BASK_FLOOR+1,cx,0,40)
    def cheek():
        # joins the basket near its rim only: folded, the rest of the wall sits inside the ring
        c=hull(cyl_y(6,CH0,CH1,*B),box(B[0]+2,B[0]+16,CH0,CH1,B[1]-7.5,B[1]+2))
        # tail that meets the lower ears: a cup's weight holds the basket level
        return c+hull(cyl_y(3,CH0,CH1,*B),cyl_y(2.5,CH0,CH1,*(B+BTAIL*U2(270))))
    m=cup+both(cheek)
    return m-cyl_y(AXLE/2,-40,40,*B)

def link_bar():
    l=hull(cyl_y(5,LK0,LK1,*P0),cyl_y(5,LK0,LK1,*Q0))
    l=l-cyl_y(PINH/2,LK0-1,LK1+1,*P0)-cyl_y(PINH/2,LK0-1,LK1+1,*Q0)
    return l

def solve_q(t1,prev):
    P=A+R_PIN*U2(AL+t1)
    cand=np.linspace(prev-15,prev+15,3001)
    Q=B[None,:]+R_PIN*np.stack([np.cos(np.radians(BE+cand)),np.sin(np.radians(BE+cand))],1)
    f=np.linalg.norm(Q-P,axis=1)-LINK
    s=np.where(np.sign(f[:-1])!=np.sign(f[1:]))[0]
    k=s[np.argmin(np.abs(cand[s]-prev))]
    return cand[k]-f[k]*(cand[k+1]-cand[k])/(f[k+1]-f[k])

def rot_about(m,c,deg):  # rotate in the x-z plane about point c, +deg = counter-clockwise (x towards z)
    return m.translate([-c[0],0,-c[1]]).rotate([0,-deg,0]).translate([c[0],0,c[1]])

def pose(t1,t2,ring,bask,link):
    r=rot_about(ring,A,t1); b=rot_about(bask,B,t2)
    P=A+R_PIN*U2(AL+t1); Q=B+R_PIN*U2(BE+t2)
    a0=np.degrees(np.arctan2(*(Q0-P0)[::-1])); a1=np.degrees(np.arctan2(*(Q-P)[::-1]))
    l=rot_about(link,P0,a1-a0).translate([P[0]-P0[0],0,P[1]-P0[1]])
    l=l+l.mirror([0,1,0])
    return r,b,l

if __name__=='__main__':
    pl=plate(); ring=ring_lever(); bask=basket_lever()
    def hit(t1,t2):
        r=rot_about(ring,A,t1); b=rot_about(bask,B,t2)
        return {k:round(v,2) for k,v in {'ring/basket':(r^b).volume(),'ring/plate':(r^pl).volume(),'basket/plate':(b^pl).volume()}.items() if v>0.02}
    print('step 1: basket up, ring open')
    for t2 in np.arange(0,90.1,5): 
        h=hit(0,t2); 
        if h: print('  basket',t2,h)
    print('step 2: ring down over the folded basket')
    for t1 in np.arange(0,-90.1,-2.5):
        h=hit(t1,90)
        if h: print('  ring',t1,h)
    for t in (1,2,3): print('ring past level',t,hit(t,0))
    for t in (-1,-2,-3): print('basket past level',t,hit(0,t))
    print('basket tipping out of the folded ring:',[ (a,sum(hit(-90,a).values())) for a in (88,85,80)])
    print('ring',ring.genus(),'basket',bask.genus(),'plate',pl.genus())
