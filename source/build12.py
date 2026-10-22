# Minimal cup holder that folds away under the headlamp (v7).
# Just a ring with springy fingers on two short arms. The arms' pins ride in a short sloped slot in two
# small brackets under the lamp shelf. Open: the pins sit at the back of the slot and the arms' tails
# are trapped between two lugs, so a cup's weight can't fold it. To fold: lift and pull the ring
# forward 8 mm (tails come out from between the lugs), then let it swing down to hang flat.
# The slot slopes down towards the back, so gravity keeps it locked.
import numpy as np, trimesh, manifold3d as mf
exec(open('build10.py').read().split("\nif __name__=='__main__':")[0])   # lamp v2 + handle helpers

def poly(pts):
    a=sum(x0*y1-x1*y0 for (x0,y0),(x1,y1) in zip(pts,pts[1:]+pts[:1]))
    return mf.CrossSection([pts if a>0 else pts[::-1]])

PIV_Y=-40.0                      # pivot height (STL Y), locked
PIN0=np.array([6.0,0.0])         # locked pin position (x forward of the blocks' front, z up from PIV_Y)
PIN1=np.array([14.0,1.5])        # pulled forward (slot rises 1.5 mm)
R_IN,R_OUT,R_H=40.0,43.0,22.0    # ring: Ø80 inside, Ø86 outside, 22 tall
RCX=PIN0[0]+12+R_OUT             # ring centre, x
ARM0,ARM1=41.0,45.6              # arms, |y|
CHK0,CHK1=46.0,52.0              # brackets, |y|
TAIL=12.0
def c7(m):              # local (x fwd, y across, z up) -> STL
    return m.transform([[-1,0,0,BX0],[0,0,1,PIV_Y],[0,1,0,ZC]])
def brackets_local():
    out=[]
    for s in (-1,1):
        y0,y1=sorted((s*CHK0,s*CHK1))
        b=box(-6,18,y0,y1,-14,L_BOT-1-PIV_Y+6)               # reaches up into the handle shelf
        b-=hull(cyl_y(2.25,y0-1,y1+1,*PIN0),cyl_y(2.25,y0-1,y1+1,*PIN1))   # sloped slot for the M4 pin
        l0,l1=sorted((s*(ARM0-0.4),s*(CHK0+0.5)))
        # upper lug: holds the tail down when open; its underside rises with the slot so the tail can slide out
        rise=(PIN1[1]-PIN0[1])/(PIN1[0]-PIN0[0])
        x0=-TAIL+PIN0[0]-1
        lug=mf.Manifold.extrude(poly([(x0,4.3),(-1,4.3+rise*(-1-x0)+0.2),(-1,12),(x0,12)]),l1-l0).rotate([90,0,0]).translate([0,l1,0])
        b+=lug
        b+=box(-TAIL+PIN0[0]-1,-1,l0,l1,-12,-4.3)              # lower lug: stops the ring tipping up
        out.append(b)
    return out[0]+out[1]
def ring_local():
    # ring bottom flush with the arms' bottom: the whole part prints flat, no supports
    band=cyl_z(R_OUT,-4,-4+R_H,RCX)-cyl_z(R_IN,-5,R_H,RCX)
    fingers=[]
    for i in range(6):
        # springy fingers rising inward from the bottom edge: a 66 mm can is gripped, a coffee cup wedges
        fp=[(R_IN+1.5,-4),(R_IN-0.2,-4),(32.3,-4+R_H-4),(33.9,-4+R_H-4)]
        f=mf.Manifold.extrude(poly(fp),14).translate([0,0,-7]).rotate([90,0,0]).rotate([0,0,30+60*i]).translate([RCX,0,0])
        fingers.append(f)
    def arm():
        boss=cyl_y(5,ARM0,ARM1,*PIN0)^box(PIN0[0]-6,PIN0[0]+6,ARM0-1,ARM1+1,-4,6)   # flat-bottomed, so the part lies flat
        a=box(PIN0[0]-TAIL,RCX+14,ARM0,ARM1,-4,4)+boss
        return a
    m=mf.Manifold.batch_boolean([band]+fingers+[both(arm)],mf.OpType.Add)
    return m-cyl_y(2.15,-ARM1-1,ARM1+1,*PIN0)
def pose(ring,pin,deg):  # ring with its pin at `pin`, rotated deg (+ = front up) about the pin
    return rot_about(ring.translate([pin[0]-PIN0[0],0,pin[1]-PIN0[1]]),pin,deg)

def holder7():
    parts=[]
    for s in (-1,1):
        zin=ZC+s*EAR_OUT; zout=zin+s*(PLATE_T+2); z0,z1=sorted((zin,zout))
        prof=hull(bx(-60,-12,SHELF_Y0,EAR_TOP-8,z0,z1),cyl_Z(8,z0,z1,-52,EAR_TOP-8),cyl_Z(8,z0,z1,-20,EAR_TOP-8))
        for hx,hy in EAR_HOLES:
            prof-=hull(cyl_Z(2.2,z0-1,z1+1,hx,hy-4,24),cyl_Z(2.2,z0-1,z1+1,hx,hy+4,24))
        parts.append(prof)
    shelf=bx(-60,-12,SHELF_Y0,SHELF_Y1,ZC-EAR_OUT-1,ZC+EAR_OUT+1)
    shelf-=bx(-48,-24,SHELF_Y0-1,SHELF_Y1+1,ZC-45,ZC+45)
    shelf+=bx(-60,-48,SHELF_Y0-8,SHELF_Y0,ZC-55,ZC+55)                     # a lip the brackets hang from
    return mf.Manifold.batch_boolean(parts+[shelf,c7(brackets_local())],mf.OpType.Add)

if __name__=='__main__':
    handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder7()
    sb=servo_block2(); eb=elec_block2(); ld=lid2(); hd=H(head()); sv=H(servo_model()[0])
    fixed=handle+sb+eb+ld+sv+diffuser(1)+diffuser(-1)
    ring=ring_local()
    def hit(pin,deg): return round((c7(pose(ring,pin,deg))^fixed).volume(),2)
    print('locked, open:',hit(PIN0,0))
    print('locked: tries to fold ->',[(d,hit(PIN0,-d)) for d in (2,3,4,5,6)],'  tries to tip up ->',[(d,hit(PIN0,d)) for d in (2,3,4,5,6)])
    print('slide forward to unlock:',[ (round(t,2),hit(PIN0+(PIN1-PIN0)*t,0)) for t in np.linspace(0,1,5)])
    print('fold down from the front of the slot:',[(d,hit(PIN1,-d)) for d in range(0,91,10)])
    print('hanging, pin dropped to the back of the slot:',hit(PIN0,-90))
    for a in (-13,0,13): print(f'head {a} deg vs ring open/folded:',round((tilt(hd,a)^(c7(ring)+c7(pose(ring,PIN0,-90)))).volume(),2))
    cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
    cone=cone.rotate([0,0,180+TOF_DOWN]).translate([BX0-4,TOF_Y,ZC+TOF_W])^box(-3000,-60,-679+5,300,-400,300)
    print('road sensor view vs ring open / folded / brackets:',round((cone^c7(ring)).volume(),1),round((cone^c7(pose(ring,PIN0,-90))).volume(),1),round((cone^c7(brackets_local())).volume(),1))
    for nm,m in (('ring',ring),('handle v7',handle)):
        t=to_tm(m); print(f'{nm}: watertight {t.is_watertight}, bodies {len(t.split(only_watertight=False))}')
    fo=c7(pose(ring,PIN0,-90)).bounding_box(); op=c7(ring).bounding_box()
    print('open: front X',round(op[0]),' top Y',round(op[4]),'   folded: X',round(fo[0]),'..',round(fo[3]),' bottom Y',round(fo[1]),' thickness',round(fo[3]-fo[0]))
    to_tm(handle).export(OUT+'master_handle_v7.stl'); to_tm(handle).export('handle7.stl')
    b0=ring.bounding_box(); to_tm(ring.translate([0,0,-b0[2]])).export(OUT+'cup_ring_minimal.stl')
    to_tm(sb+eb+ld).export('lamp2_fixed.stl')
    to_tm(c7(ring)).export('v7_cup_open.stl'); to_tm(c7(pose(ring,PIN0,-90))).export('v7_cup_folded.stl')

# ---------------- fold-flat foot (v7b) ----------------
# A U-shaped foot on two M3 friction pivots on the outside of the ring's arms. Open, it hangs straight
# down and its crossbar sits under the cup. Folded, it swings forward and lies just under the ring,
# the crossbar tucked under the ring's front edge, so the ring still folds away under the lamp.
FOOT_P=np.array([RCX,0.0])      # pivot on each arm, at the ring's centre line
FOOT_L=40.0; FOOT_BACK=9.0      # leg length; crossbar set back so it clears the ring when folded
FT0,FT1=ARM1+0.4,ARM1+3.4       # foot legs, |y|
def foot_local():
    px,pz=FOOT_P
    def leg():
        l=box(px-4,px+4,FT0,FT1,pz-FOOT_L,pz+5)+cyl_y(5,FT0,FT1,px,pz)
        l+=box(px-4-FOOT_BACK,px+4,FT0,FT1,pz-FOOT_L-3,pz-FOOT_L)            # elbow back to the crossbar
        return l-cyl_y(1.65,FT0-1,FT1+1,px,pz)                               # M3 pivot
    bar=box(px-4-FOOT_BACK,px+4-FOOT_BACK,-FT1,FT1,pz-FOOT_L-3,pz-FOOT_L)
    return both(leg)+bar
def ring_with_pilots():
    r=ring_local()
    return r-cyl_y(1.25,ARM0-0.5,ARM1+1,*FOOT_P)-cyl_y(1.25,-ARM1-1,-ARM0+0.5,*FOOT_P)   # M3 self-tap pilots
def foot_pose(f,deg): return rot_about(f,FOOT_P,deg)   # +90 = folded forward, flat under the ring
