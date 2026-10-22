# Rough Begode Master for pictures, traced from side photos and scaled to its ~510 mm tyre.
# Anchors: the tyre front ~2 cm behind the grip (owner's photo), the shell tops just under the
# blocks the handle bolts to (owner's ruler photo). Same STL frame as the handle: -X forward, +Y up.
import numpy as np, manifold3d as mf, trimesh
ZC=-70.5
def to_tm(m):
    g=m.to_mesh(); return trimesh.Trimesh(g.vert_properties[:,:3],g.tri_verts,process=True)
def bx(x0,x1,y0,y1,z0,z1): return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def ex(pts,z0,z1):
    a=sum(x0*y1-x1*y0 for (x0,y0),(x1,y1) in zip(pts,pts[1:]+pts[:1]))
    return mf.Manifold.extrude(mf.CrossSection([pts if a>0 else pts[::-1]]),z1-z0).translate([0,0,z0])
def ex_soft(pts,z0,z1,r=14,bevel=7,outer=+1):
    # rounded outline, with the outer face (+z if outer>0, else -z) stepped in twice
    # so the edges read as moulded plastic rather than a flat cut-out
    a=sum(x0*y1-x1*y0 for (x0,y0),(x1,y1) in zip(pts,pts[1:]+pts[:1]))
    cs=mf.CrossSection([pts if a>0 else pts[::-1]]).offset(-r,mf.JoinType.Round).offset(r,mf.JoinType.Round)
    h=bevel/2
    if outer>0: spans=[(cs,z0,z1-bevel),(cs.offset(-h),z1-bevel,z1-h),(cs.offset(-bevel),z1-h,z1)]
    else:       spans=[(cs,z0+bevel,z1),(cs.offset(-h),z0+h,z0+bevel),(cs.offset(-bevel),z0,z0+h)]
    return mf.Manifold.batch_boolean([mf.Manifold.extrude(c,zb-za).translate([0,0,za]) for c,za,zb in spans if zb>za],mf.OpType.Add)
def both(z0,z1,f):  # a part on each side of the wheel, z measured outwards from the centre plane
    return [f(ZC+z0,ZC+z1),f(ZC-z1,ZC-z0)]
def P(x,y): return (-70+(x-165)*0.872, -26-(y-133)*0.872)   # photo pixels -> mm

TC=np.array(P(457,590)); TR=255.0; TW=95.0
GROUND=TC[1]-TR

def ring(r0,r1,w,c=TC,seg=128):
    m=mf.Manifold.cylinder(w,r1,r1,seg)
    if r0>0: m-=mf.Manifold.cylinder(w+2,r0,r0,seg).translate([0,0,-1])
    return m.translate([c[0],c[1],ZC-w/2])

def tyre():
    t=ring(TR-55,TR-8,TW)+ring(TR-45,TR-2,TW-16)
    blocks=[]
    for row,(z,off) in enumerate(((-24,0),(24,0.5))):
        for i in range(64):
            a=2*np.pi*(i+off)/64
            b=bx(-7,7,-5,5,-13,13).translate([0,TR-5,z]).rotate([0,0,np.degrees(a)])
            blocks.append(b.translate([TC[0],TC[1],ZC]))
    return mf.Manifold.batch_boolean([t]+blocks,mf.OpType.Add)

def rim():
    r=ring(TR-62,TR-50,70)
    spokes=[]
    for i in range(12):
        s=bx(60,TR-58,-3,3,-30,30).rotate([0,0,30*i+8]).translate([TC[0],TC[1],ZC])
        spokes.append(s)
    return mf.Manifold.batch_boolean([r]+spokes,mf.OpType.Add)
def hub(): return ring(0,TR-60,58)+ring(0,62,90)

def shell_outline(): return [P(*p) for p in [(225,135),(650,140),(655,225),(420,235),(398,260),(398,440),(380,490),(320,500),(240,492),(222,460)]]
def shells():
    out=[]
    out+=[ex_soft(shell_outline(),ZC+62,ZC+140,16,9,+1),ex_soft(shell_outline(),ZC-140,ZC-62,16,9,-1)]
    # the raised panel the BEGODE letters sit on
    pan=[P(*p) for p in [(240,255),(380,255),(380,465),(240,465)]]
    out+=[ex_soft(pan,ZC+138,ZC+141,10,1.5,+1),ex_soft(pan,ZC-141,ZC-138,10,1.5,-1)]
    return out
def lower_boxes():
    box=[P(250,520),P(530,520),P(530,600),P(420,690),P(250,690)]
    rail=[P(520,520),P(790,515),P(790,555),P(520,565)]
    return [ex_soft(box,ZC+62,ZC+130,14,8,+1),ex_soft(box,ZC-130,ZC-62,14,8,-1)]+both(70,115,lambda a,b: ex(rail,a,b))
def pedals():
    x0,y0=P(285,470); x1,y1=P(640,630)
    def ped(a,b):
        p=bx(x0,x1,y1,y0,a,b)
        cx,cy=(x0+x1)/2,(y0+y1)/2
        for i,(dx,dy) in enumerate([(-110,30),(-110,-30),(-60,55),(-60,0),(-60,-55),(60,55),(60,0),(60,-55),(110,30),(110,-30)]):
            p-=mf.Manifold.cylinder(b-a+2,19,19,6).translate([cx+dx,cy+dy,a-1])   # the honeycomb
        return p
    return both(143,158,ped)
def frame():
    arms=both(48,56,lambda a,b: bx(TC[0]-22,TC[0]+22,TC[1],-30,a,b))
    panels=both(50,61,lambda a,b: ex([P(260,240),P(640,240),P(640,470),P(400,480),P(260,470)],a,b))
    return arms,panels
def top_body():
    side=[(-50,74),(-2,100),(360,100),(392,86),(392,38),(-6,36),(-52,56)]
    t=ex_soft(side,ZC,ZC+78,8,10,+1)+ex_soft(side,ZC-78,ZC,8,10,-1)
    t+=ex_soft([(20,100),(330,100),(330,103),(20,103)],ZC-55,ZC+55,1,0.01,+1)        # seat pad
    t+=ex([(340,96),(392,92),(392,70),(340,70)],ZC-40,ZC+40).translate([4,0,0])      # tail light housing
    return t
def centre_block():
    # the black block under the seat: controller, and what the handle's tabs bolt to (its sides at w = +-66.5)
    return ex_soft([(-10,-60),(350,-60),(350,40),(-10,40)],ZC-66.5,ZC+66.5,6,0.01,+1)
def tail_light(): return bx(396,398,74,90,ZC-30,ZC+30)
def mudguard():
    return ex([P(612,255),P(800,330),P(800,345),P(612,272)],ZC-38,ZC+38)
def rear_bracket():
    return both(56,70,lambda a,b: ex([P(600,120),P(712,140),P(712,250),P(600,250)],a,b))

def model():
    arms,panels=frame()
    parts=[(tyre(),'#1e1e1e'),(rim(),'#b8bcc2'),(hub(),'#2a2a2a')]
    parts+=[(m,'#c8202a') for m in shells()]
    parts+=[(m,'#1a1a1a') for m in lower_boxes()]
    parts+=[(m,'#151515') for m in pedals()]
    parts+=[(m,'#c9ccd1') for m in arms]+[(m,'#202020') for m in panels]
    parts+=[(centre_block(),'#232323'),(top_body(),'#1b1b1b'),(tail_light(),'#3b7bff'),(mudguard(),'#161616')]
    parts+=[(m,'#c8202a') for m in rear_bracket()]
    return [(to_tm(m),c) for m,c in parts]

if __name__=='__main__':
    print('tyre centre',np.round(TC,1),'ground',round(GROUND,1),'tyre front X',round(TC[0]-TR,1),'top',round(TC[1]+TR,1))
    print('shell outline',np.round(shell_outline(),0).tolist())
    ms=model(); print('parts',len(ms),'faces',sum(len(m.faces) for m,_ in ms))
