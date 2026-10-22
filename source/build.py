# Begode Master front handle + folding cup holder.
# The original handle (holes, tabs, grip) is kept untouched; the hinge is fused onto it.
import numpy as np, trimesh, manifold3d as mf
U='../reference/'
OUT='../build_output/'
SEG=96

def to_mf(t): return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices,np.float32),tri_verts=np.asarray(t.faces,np.uint32)))
def to_tm(m):
    g=m.to_mesh(); return trimesh.Trimesh(g.vert_properties[:,:3],g.tri_verts,process=True)
def box(x0,x1,y0,y1,z0,z1): return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def cyl_x(r,x0,x1,y=0,z=0):  # cylinder along x
    return mf.Manifold.cylinder(x1-x0,r,r,SEG).rotate([0,90,0]).translate([x0,y,z])

# ---------------- parameters (mm) ----------------
U_HINGE=65.0          # along the arm, from the mounting holes toward the grip
Z_AXIS=-160.5         # middle of the bottom arm (arm is Z -168..-153)
FACE={+1:21.9,-1:-8.5}# side faces of the bottom arm at U_HINGE
OFFSET=14.0           # hinge axis distance out from the arm face
R_K=9.0               # knuckle radius
T_TONGUE=10.0; GAP=0.4; T_KNUCKLE=7.0
BOLT=5.4              # M5 clearance
NUT_AF=8.1; NUT_DEPTH=3.2
SHELF_TOP=-9.15       # stop the ring rests on when open
RING_IN=46.0; RING_WALL=3.0; RING_H=50.0
ARM_GAP=10.0          # axis to nearest point of the ring (> R_K so it swings past the knuckles)

xt=T_TONGUE/2; xk0=xt+GAP; xk1=xk0+T_KNUCKLE

# ---------------- fixed clevis, built in hinge frame ----------------
# x' = along arm, y' = out from the side face (axis at y'=0), z' = up (axis at z'=0)
def clevis():
    parts=[]
    for s in (+1,-1):
        a,b=sorted((s*xk0,s*xk1))
        # knuckles reach down to the stop shelf so it is one piece with the handle
        k=cyl_x(R_K,a,b)+box(a,b,-OFFSET-6,0,SHELF_TOP-7,R_K)
        parts.append(k)
    shelf=box(-xk1,xk1,-OFFSET-6,R_K-0.0,SHELF_TOP-7,SHELF_TOP)
    # keep the shelf clear of the tongue's swing
    shelf=shelf-cyl_x(R_K+0.15,-xk0,xk0)
    c=mf.Manifold.batch_boolean(parts+[shelf],mf.OpType.Add)
    c=c-cyl_x(BOLT/2,-xk1-1,xk1+1)
    # hex pocket for the nyloc on the +x' knuckle
    hexn=mf.Manifold.cylinder(NUT_DEPTH+0.01,NUT_AF/np.sqrt(3),NUT_AF/np.sqrt(3),6).rotate([0,90,0]).translate([xk1-NUT_DEPTH,0,0])
    hexn=hexn.rotate([30,0,0])
    return c-hexn


def poly(pts):
    a=sum(x0*y1-x1*y0 for (x0,y0),(x1,y1) in zip(pts,pts[1:]+pts[:1]))
    return mf.CrossSection([pts if a>0 else pts[::-1]])

# ---------------- moving part: tongue + arm + ring ----------------
def ring_part():
    ro=RING_IN+RING_WALL; cy=ARM_GAP+ro
    # profile as (radius, depth below the rim); 45 degree floor cone prints without support rim-down
    prof=[(RING_IN,0),(RING_IN,30),(29,47),(29,RING_H),(32,RING_H),(ro,33),(ro,0)]
    ring=mf.Manifold.revolve(poly(prof),SEG)
    fingers=[]
    for i in range(6):
        # leaf springs: hold a 66 mm can, open to 90 mm for a coffee cup
        fp=[(47.5,0),(36.5,28),(34.9,28),(45.9,0)]
        f=mf.Manifold.extrude(poly(fp),16).translate([0,0,-8]).rotate([90,0,0]).rotate([0,0,30+60*i])
        fingers.append(f)
    ring=mf.Manifold.batch_boolean([ring]+fingers,mf.OpType.Add).mirror([0,0,1]).translate([0,cy,0])
    tongue=cyl_x(R_K,-xt,xt)+box(-xt,xt,0,ARM_GAP+4,-9.0,0)
    gus=box(-9,9,R_K+0.6,ARM_GAP+4,-24,0)
    part=mf.Manifold.batch_boolean([ring,tongue,gus],mf.OpType.Add)
    return part-cyl_x(BOLT/2,-xt-1,xt+1)

def place(m,s):
    d=np.array([-1,1,0])/np.sqrt(2); p=np.array([-d[1],d[0],0]); z=np.array([0,0,1.])
    if s<0: m=m.mirror([1,0,0]); cx,cy=-d,-p
    else: cx,cy=d,p
    t=U_HINGE*d+(FACE[s]+s*OFFSET)*p+Z_AXIS*z
    M=np.column_stack([cx,cy,z,t])
    return m.transform(M.tolist())

def rot(m,deg): return m.rotate([deg,0,0])

handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))
cap=trimesh.load(U+'euc_master_front_handle_p2.stl')
cl=clevis(); cup=ring_part()
print('cup volume cm3',round(cup.volume()/1000,1),'bbox',np.round(cup.bounding_box(),1))
for s,name in ((+1,'A'),(-1,'B')):
    fixed=handle+place(cl,s)
    print(name,'handle genus',fixed.genus(),'vol',round(fixed.volume()/1000,1))
    for a in (0,10,30,45,60,80,90,95,100,110):
        hit=(fixed^place(rot(cup,a),s)).volume()
        print(f'  side {name} fold {a:3d} deg: overlap {hit:.2f} mm3')
    to_tm(fixed).export(OUT+f'master_handle_cupside_{name}.stl')
    to_tm(place(cup,s)).export(f'cup_open_{name}.stl'); to_tm(place(rot(cup,90),s)).export(f'cup_fold_{name}.stl')
# cup holder printed rim-down
pc=cup.mirror([0,0,1]); b=pc.bounding_box(); pc=pc.translate([0,0,-b[2]])
to_tm(pc).export(OUT+'cup_holder_ring.stl')
cap.export(OUT+'master_handle_top_cap_p2.stl')
for a in (-1,-2,-4):
    print('open past level',a,'overlap with stop',round((cl^rot(cup,a)).volume(),2))
