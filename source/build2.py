# Begode Master front handle v2 + folding cup holder.
# Orientation from the photo: STL +Y = up, -X = forward, Z = across the wheel.
# The grip is the Ø25 bar at X-80 Y70 running along Z; the original handle is kept untouched.
import numpy as np, trimesh, manifold3d as mf
U='../reference/'
OUT='../build_output/'
SEG=96

def to_mf(t): return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices,np.float32),tri_verts=np.asarray(t.faces,np.uint32)))
def to_tm(m):
    g=m.to_mesh(); return trimesh.Trimesh(g.vert_properties[:,:3],g.tri_verts,process=True)
def box(x0,x1,y0,y1,z0,z1): return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def cyl_x(r,x0,x1,y=0,z=0): return mf.Manifold.cylinder(x1-x0,r,r,SEG).rotate([0,90,0]).translate([x0,y,z])
def hull(*ms): return mf.Manifold.batch_hull(list(ms))
def poly(pts):
    a=sum(x0*y1-x1*y0 for (x0,y0),(x1,y1) in zip(pts,pts[1:]+pts[:1]))
    return mf.CrossSection([pts if a>0 else pts[::-1]])

# Hinge frame: x' across the wheel (x' = -70.5 - Z), y' forward (-X), z' up (+Y); axis on x'.
AX_X=-104.5; AX_Y=62.0; ZC=-70.5    # axis 12 mm in front of the grip, below its centre line
CLEVIS=70.5                          # clevises sit in the grip's two corners, grip itself stays free
R_K=9.0; T_TONGUE=10.0; GAP=0.4; T_KNUCKLE=7.0
BOLT=5.4; PIN=5.3; R_PIN=13.0        # Ø5 ball-lock pin or M5 bolt locks open / folded
NUT_AF=8.1; NUT_DEPTH=3.2
RING_IN=46.0; RING_WALL=3.0; RING_H=50.0; RING_BACK=12.0; RING_BOT=-9.0

xt=T_TONGUE/2; xk0=xt+GAP; xk1=xk0+T_KNUCKLE
PIN_OPEN=(R_PIN,0.0); PIN_FOLD=(0.0,-R_PIN)

def knuckle_profile(x0,x1,lock):
    k=cyl_x(R_K,x0,x1)
    if lock:
        k=hull(k,cyl_x(6,x0,x1,*PIN_OPEN),cyl_x(6,x0,x1,*PIN_FOLD))
    return k+box(x0,x1,-30,0,-R_K,R_K)   # base reaches back into the grip

def clevis(cx,lock,outer_sign):
    parts=[knuckle_profile(cx+s*xk0 if s>0 else cx-xk1, cx+xk1 if s>0 else cx-xk0, lock) for s in (+1,-1)]
    c=parts[0]+parts[1]
    c=c-cyl_x(BOLT/2,cx-xk1-1,cx+xk1+1)
    if lock:
        for p in (PIN_OPEN,PIN_FOLD): c=c-cyl_x(PIN/2,cx-xk1-1,cx+xk1+1,*p)
    # hex pocket for the nyloc on the outer knuckle
    r=NUT_AF/np.sqrt(3)
    hx=mf.Manifold.cylinder(NUT_DEPTH+0.01,r,r,6).rotate([0,90,0]).rotate([30,0,0])
    hx=hx.translate([cx+xk1-NUT_DEPTH,0,0]) if outer_sign>0 else hx.translate([cx-xk1-0.01,0,0])
    return c-hx

def cup_part():
    ro=RING_IN+RING_WALL; cy=RING_BACK+ro
    top=RING_BOT+RING_H
    # (radius, height); 45° floor cone, open centre drains rain
    prof=[(29,0),(32,0),(ro,17),(ro,RING_H),(RING_IN,RING_H),(RING_IN,20),(29,3)]
    ring=mf.Manifold.revolve(poly(prof),SEG)
    fingers=[]
    for i in range(6):
        # leaf springs rising from the floor: a 66 mm can is held, a 90 mm coffee cup pushes them out
        fp=[(45.9,19),(47.5,19),(36.5,47),(34.9,47)]
        f=mf.Manifold.extrude(poly(fp),16).translate([0,0,-8]).rotate([90,0,0]).rotate([0,0,30+60*i])
        fingers.append(f)
    ring=mf.Manifold.batch_boolean([ring]+fingers,mf.OpType.Add)
    # ring axis vertical (z'), centred across the wheel, in front of the axis
    ring=ring.translate([0,cy,RING_BOT])
    parts=[ring]
    for s,lock in ((-1,True),(+1,False)):
        cx=s*CLEVIS
        t=cyl_x(R_K,cx-xt,cx+xt)
        if lock: t=hull(t,cyl_x(6,cx-xt,cx+xt,*PIN_OPEN))
        # straight out of the slot until clear of the knuckles, then in to the ring floor
        reach=(R_PIN+6 if lock else R_K)+0.8+4   # the turn inward starts past the knuckles' reach
        a1=box(cx-xt,cx+xt,0,reach,RING_BOT,3)
        px=s*34; py=cy-np.sqrt(40**2-34**2)
        a2=hull(box(cx-xt,cx+xt,reach-4,reach,RING_BOT,3),box(px-6,px+6,py-6,py+6,RING_BOT,3))
        p=hull(t,a1)+a2
        p=p-cyl_x(BOLT/2,cx-xt-1,cx+xt+1)
        if lock: p=p-cyl_x(PIN/2,cx-xt-1,cx+xt+1,*PIN_OPEN)
        parts.append(p)
    return mf.Manifold.batch_boolean(parts,mf.OpType.Add)

def to_world(m):
    # x'->-Z, y'->-X, z'->+Y  (proper rotation)
    M=[[0,-1,0,AX_X],[0,0,1,AX_Y],[-1,0,0,ZC]]
    return m.transform(M)
def fold(m,deg): return m.rotate([deg,0,0])

handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))
cl=clevis(-CLEVIS,True,-1)+clevis(CLEVIS,False,+1)
cup=cup_part()
fixed=handle+to_world(cl)
print('handle genus',fixed.genus(),'vol cm3',round(fixed.volume()/1000,1))
print('cup vol cm3',round(cup.volume()/1000,1),'bbox',np.round(cup.bounding_box(),1))
for a in (0,-10,-20,-30,-45,-60,-75,-90,-95):
    print(f'fold {a:4d}: overlap {(fixed^to_world(fold(cup,a))).volume():.2f} mm3')
to_tm(fixed).export(OUT+'master_handle_v2.stl')
to_tm(to_world(cup)).export('v2_cup_open.stl'); to_tm(to_world(fold(cup,-90))).export('v2_cup_fold.stl')
b=cup.bounding_box(); to_tm(cup.translate([0,0,-b[2]])).export(OUT+'cup_holder_v2.stl')
