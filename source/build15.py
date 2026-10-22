# v10: lamp moved in front of the top cover, can holder that swings up into the bay under it.
# Measured front (master_model2): the stock lamp is built into the top cover, the cover's tip is
# 62 mm in front of the handle bolts and the shells 68 mm, with their tops rising to just above the
# lamp's underside. So the new lamp can't sit where the stock one is: it hangs in front of the cover,
# under the grip, on side plates that grow out of the handle's arms.
# The can holder hangs from two swing arms on a hinge just under the lamp's front. Swung in, it sits
# flat under the lamp shelf with its back half in the bay between the shells, clear of the cross
# plate even when the suspension bottoms out. Swung out, the arms hang just past vertical, so gravity
# holds them against their stop, and the basket hangs in a gimbal (pitch on the arms, roll inside).
import numpy as np, trimesh, manifold3d as mf, types
exec(open('build13.py').read())
_g={}; exec(open('master_model2.py').read().split("\nif __name__=='__main__':")[0],_g); M2=types.SimpleNamespace(**_g)

DX=-56.0                          # lamp module moved forward: its back ends 8 mm in front of the cover tip
X_BACK=-70.0                      # nothing low may come further back than this (shells at -68)
def mv(m): return m.translate([DX,0,0])
def lamp_fixed(): return mv(servo_block2()+elec_block2()+lid2()+H(servo_model()[0])+diffuser(1)+diffuser(-1))
def lamp_head(a=0.0): return mv(tilt(H(head()),a))
TOF0=np.array([BX0-4+DX,TOF_Y])   # road sensor window

# ---- can holder ----
R_IN,R_WALL,R_H=34.25,1.8,16.0   # cup ring: Ø68.5 for a 66 mm can, 16 tall, centred on the gimbal axis
R_OUT=R_IN+R_WALL
G0,G1,G_H=41.0,44.5,3.5          # gimbal ring radii, half height
PB1=49.1                         # pitch bosses run out to here
A0,A1=49.5,55.5                  # swing arms (|w|)
K0,K1=56.0,62.0                  # hinge brackets (|w|)
CORD=80.0                        # ring top edge -> floor top
GS=np.array([-76.0,-38.0])       # gimbal centre swung in (ring top 30 under... pads)
HY=-32.5; R_ARM=52.0
HX=GS[0]-np.sqrt(R_ARM**2-(GS[1]-HY)**2)
HP=np.array([HX,HY])             # hinge
TH_IN=np.degrees(np.arctan2(GS[1]-HY,GS[0]-HX)); TH_OUT=-95.0
def gpos(th): return HP+R_ARM*np.array([np.cos(np.radians(th)),np.sin(np.radians(th))])
GD=gpos(TH_OUT)
FLOOR_Y=R_H/2-CORD               # floor top, relative to the axis

def cup_ring():   # basket coords: x fwd from the axis, y up from the axis, w across (cylV etc. add ZC)
    m=cylV(R_OUT,-R_H/2,R_H/2,0,0)-cylV(R_IN,-R_H/2-1,R_H/2+1,0,0)
    for s in (-1,1):   # roll ears front and back, on the axis
        x0,x1=sorted((s*(R_IN+0.6),s*40.4))
        e=bxw(x0,x1,-4.5,4.5,-5,5)+cylX(4.5,x0,x1,0,0)
        m+=e-cylX(1.25,x0-1,x1+1,0,0)                            # M3 self-tap pilot
    for a in (90,210,330):   # cord holes, horizontal through the wall near the top
        c,s_=np.cos(np.radians(a)),np.sin(np.radians(a))
        m-=mf.Manifold.cylinder(6,1.3,1.3,16).rotate([0,90,0]).translate([-3,0,0]).rotate([0,-a,0]).translate([c*(R_IN+R_WALL/2),R_H/2-3.5,ZC+s_*(R_IN+R_WALL/2)])
    return m
def floor_disc():  # sits up inside the ring when swung in (springy tabs), hangs on 3 cords when out
    R=R_IN-0.65
    def arc(r0,r1,a0,a1,n=24):
        t=np.radians(np.linspace(a0,a1,n))
        return [(r1*np.cos(u),r1*np.sin(u)) for u in t]+[(r0*np.cos(u),r0*np.sin(u)) for u in t[::-1]]
    cs=mf.CrossSection.circle(R,96)
    for i in range(6):
        u=np.radians(60*i+30); cs-=mf.CrossSection.circle(3.5,20).translate([15*np.cos(u),15*np.sin(u)])
    for a in (90,210,330):
        u=np.radians(a); cs-=mf.CrossSection.circle(1.3,16).translate([31.0*np.cos(u),31.0*np.sin(u)])
    for a in (30,150,270):
        # a 28° strip of the rim, cut free on the inside and at one end, with a bump at its free end that
        # stands 0.4 mm proud of the ring's bore: it flexes in and holds the floor up by friction
        cs-=mf.CrossSection([arc(R-2.9,R-1.8,a,a+28.6)]); cs-=mf.CrossSection([arc(R-3.1,R+1,a+28,a+29.4)])
        u=np.radians(a+25); cs+=mf.CrossSection.circle(1.4,20).translate([(R_IN+0.4-1.4)*np.cos(u),(R_IN+0.4-1.4)*np.sin(u)])
    f=mf.Manifold.extrude(cs,2.4).rotate([-90,0,0]).translate([0,-2.4,ZC])
    f+=cylV(30.4,-0.5,3,0,0)-cylV(28.4,-1,4,0,0)                 # locates the can's tapered base
    return f.translate([0,FLOOR_Y,0])
def gimbal_ring():
    g=cylV(G1,-G_H,G_H,0,0)-cylV(G0,-G_H-1,G_H+1,0,0)
    for s in (-1,1):
        w0,w1=sorted((s*G0,s*PB1)); g+=cylW(5,w0,w1,0,0)-cylW(1.25,w0-1,w1+1,0,0)   # pitch: M3 pilot
        x0,x1=sorted((s*(G0-0.5),s*G1)); g+=cylX(4.5,x0,x1,0,0)
        x0,x1=sorted((s*(G0-1),s*(G1+1))); g-=cylX(1.65,x0,x1,0,0)               # roll: M3 clearance
    return g^bxw(-80,80,-G_H,10,-80,80)
def place(m,g,pitch=0.0,roll=0.0):   # basket coords -> STL with the gimbal centre at g
    if roll: m=m.translate([0,0,-ZC]).rotate([roll,0,0]).translate([0,0,ZC])
    if pitch: m=m.rotate([0,0,-pitch])
    return m.translate([g[0],g[1],0])
def basket_parts(floor_up):
    f=floor_disc()
    if floor_up: f=f.translate([0,-R_H/2+2.4+0.5-FLOOR_Y,0])
    return cup_ring(),f
def place_holder(th,pitch=0.0,roll=0.0,floor_up=None):
    g=gpos(th); up=(th>TH_IN-1) if floor_up is None else floor_up
    ring_,fl=basket_parts(up)
    return [place(gimbal_ring(),g,pitch)]+[place(m,g,pitch,roll) for m in (ring_,fl)]

def arm_local(s):   # in the arm's own frame: hinge at the origin, gimbal pin at +R_ARM along x
    w0,w1=sorted((s*A0,s*A1))
    a=hull(cylW(6,w0,w1,0,0),cylW(6,w0,w1,R_ARM,0))
    a-=cylW(2.2,w0-1,w1+1,0,0)                                    # M4 hinge bolt
    a-=cylW(1.65,w0-1,w1+1,R_ARM,0)                               # M3 pitch screw, clearance
    return a
def arm(s,th): return arm_local(s).translate([0,-0,0]).rotate([0,0,th]).translate([HP[0],HP[1],0])
STOP_R=20.0
STOP_A=TH_OUT-np.degrees(np.arcsin(6/STOP_R))-np.degrees(np.arcsin(3.4/STOP_R))-1.0
def brackets():
    out=[]
    for s in (-1,1):
        w0,w1=sorted((s*K0,s*K1))
        c=HP+STOP_R*np.array([np.cos(np.radians(STOP_A)),np.sin(np.radians(STOP_A))])
        b=hull(bxw(HP[0]-6,-100,HP[1],SHELF_Y1,w0,w1),cylW(6,w0,w1,HP[0],HP[1]))
        b+=hull(cylW(6,w0,w1,HP[0],HP[1]),cylW(4.5,w0,w1,c[0],c[1]))          # leg down to the stop
        b-=cylW(2.2,w0-1,w1+1,HP[0],HP[1])
        s0,s1=sorted((s*(A0+0.2),s*(K0+0.5)))
        b+=cylW(3.2,s0,s1,c[0],c[1])          # the arm's front edge comes to rest on this at -95°
        out.append(b)
    return out

def holder10():
    parts=[]
    for s in (-1,1):   # side plates: the lamp blocks bolt to them; they climb back into the handle's arms
        zin=ZC+s*EAR_OUT; zout=zin+s*(PLATE_T+2); z0,z1=sorted((zin,zout))
        pts=[(-60+DX,SHELF_Y0),(X_BACK,SHELF_Y0),(X_BACK,-8),(-64,8),(-64,45),(-78,62),(-100,60),(-60+DX,EAR_TOP-8)]
        prof=M2.ex(pts,z0,z1)
        for hx,hy in EAR_HOLES:
            prof-=hull(cyl_Z(2.2,z0-1,z1+1,hx+DX,hy-4,24),cyl_Z(2.2,z0-1,z1+1,hx+DX,hy+4,24))
        parts.append(prof)
    shelf=bx(-60+DX,X_BACK,SHELF_Y0,SHELF_Y1,ZC-EAR_OUT-1,ZC+EAR_OUT+1)
    shelf+=bx(X_BACK-1,-64,SHELF_Y0,SHELF_Y1,ZC-46,ZC+46)                 # reaches over the bay's mouth
    shelf-=bx(-48+DX,-24+DX,SHELF_Y0-1,SHELF_Y1+1,ZC-26,ZC+26)            # cable window (lamp power, servo)
    # felt pads the swung-in ring presses up against: front, and either side
    rt=GS[1]+R_H/2
    pads=[bxw(GS[0]-R_OUT-2,GS[0]-R_OUT+6,rt,SHELF_Y0+0.5,-7,7)]
    for s in (-1,1):
        w0,w1=sorted((s*28,s*40)); pads.append(bxw(GS[0]-5,GS[0]+5,rt,SHELF_Y0+0.5,w0,w1))
    return mf.Manifold.batch_boolean(parts+[shelf]+pads+brackets(),mf.OpType.Add)
