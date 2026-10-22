# Self-levelling headlamp for the Begode Master front handle (replaces the stock lamp).
# One LED + TIR lens on an aluminium heat sink, in a head that a servo tilts ±12° to keep the beam
# steady. Two side blocks bolt into the handle's lamp slots: one holds the servo, the other the
# electronics (ESP32-C3 + MPU-6050 + LED driver). The LED wires run through the hollow pivot pin.
# STL frame of the handle: +Y up, -X forward, Z across the wheel (centre Z = -70.5).
import numpy as np, trimesh, manifold3d as mf
exec(open('build8.py').read().split("\nif __name__=='__main__':")[0])   # handle v5 + cup holder

# ---- bought parts (nominal sizes: check yours) ----
TIR_D=26.5; TIR_H=15.0          # 26.5 mm TIR optic for a 20 mm LED star
STAR_T=1.6
HS=40.0; HS_D=20.0              # 40x40x20 aluminium heat sink
SV_L,SV_W,SV_H=22.8,12.2,22.5   # MG90S body
SV_TAB=32.5; SV_TAB_T=2.5; SV_TAB_DOWN=6.5   # tab span, thickness, distance below body top
SV_SHAFT=6.0                    # shaft centre from the body end
SV_BOSS=4.5                     # gear boss height above the body top
SV_HOLE=27.8                    # tab hole spacing

# ---- layout ----
PX,PY=-36.0,7.0                 # pivot axis (lateral), STL X/Y
TILT=12.0                       # firmware limit; the head clears everything to ±13°
HW=26.0                         # head half width (w)
HU0,HU1=-19.0,19.0              # head front/back (u = X - PX, back positive)
HV=23.0                         # head half height
BOSS_R=9.0; BOSS_W=3.0
PIN_R=4.0; PIN_L=5.5; WIRE_R=2.3
BLK_IN=31.0; BLK_OUT=LW/2+EAR_T # block inner / outer faces (|w|); outer matches the stock ear
BX0,BX1,BY0,BY1=-60.0,-14.0,L_BOT,30.0
LID_SCREWS=[(x,z) for x in (BX0+6,BX1-6) for z in (ZC-BLK_OUT+6.75,ZC-BLK_IN-7)]

def H(m):  # head-local (u,v,w) -> STL
    return m.translate([PX,PY,ZC])
def cu(r,u0,u1,v=0,w=0,seg=64): return mf.Manifold.cylinder(u1-u0,r,r,seg).rotate([0,90,0]).translate([u0,v,w])
def cw(r,w0,w1,u=0,v=0,seg=64): return mf.Manifold.cylinder(w1-w0,r,r,seg).translate([u,v,w0])

def head():
    h=box(HU0,HU1,-HV,HV,-HW,HW)
    h-=cu(11.0,HU0-1,HU0+2.5)                               # front aperture (TIR flange stops on it)
    h-=cu(TIR_D/2+0.2,HU0+2.5,0.01)                          # TIR + star pocket
    h-=box(0,HU1+1,-HS/2-0.2,HS/2+0.2,-HS/2-0.2,HS/2+0.2)    # heat sink slides in from the back
    for w in (-10,10):                                       # M3 self-tappers pinch the outer fins
        h-=mf.Manifold.cylinder(2*HV+2,1.4,1.4,16).rotate([-90,0,0]).translate([10,-HV-1,w])
    # servo side: boss with a recess for the MG90S single-arm horn (arm pointing back)
    b=hull(cw(BOSS_R,HW,HW+BOSS_W),cw(5,HW,HW+BOSS_W,u=13))
    b-=hull(cw(3.9,HW+BOSS_W-2.2,HW+BOSS_W+1),cw(2.5,HW+BOSS_W-2.2,HW+BOSS_W+1,u=14))
    b-=cw(3.2,HW+BOSS_W-4,HW+BOSS_W+1)                       # room for the spline boss
    for u in (7.5,11.5): b-=cw(0.8,HW+BOSS_W-8,HW+BOSS_W+1,u=u)   # M2 screws through the horn
    h+=b
    # other side: boss and hollow pivot pin; the LED and NTC wires leave through it
    h+=cw(BOSS_R,-HW-BOSS_W,-HW)+cw(PIN_R,-HW-BOSS_W-PIN_L,-HW-BOSS_W+0.5)
    h-=cw(WIRE_R,-HW-BOSS_W-PIN_L-1,-TIR_D/2+1,u=-STAR_T/2)
    # visor: shades the upper part of the beam, so the levelled cut-off doesn't dazzle
    vis=box(HU0-14,HU0+0.5,13.5,15.5,-15,15)
    h+=vis
    return h

def servo_model():  # MG90S, in head-local coords, shaft on the pivot axis pointing -w
    top=HW+BOSS_W+0.5+SV_BOSS
    cy=SV_SHAFT-SV_L/2          # body centre in v (body runs down from the shaft)
    body=box(-SV_W/2,SV_W/2,-(SV_L-SV_SHAFT),SV_SHAFT,-0,SV_H).translate([0,0,top])
    tabs=box(-SV_W/2,SV_W/2,cy-SV_TAB/2,cy+SV_TAB/2,0,SV_TAB_T).translate([0,0,top+SV_TAB_DOWN-SV_TAB_T])
    boss=cw(3.0,top-SV_BOSS,top)
    return body+tabs+boss, top, cy

def servo_block():
    b=box(BX0,BX1,BY0,BY1,ZC+BLK_IN,ZC+BLK_OUT)
    _,top,cy=servo_model()
    # pocket open towards the head: body, tabs, and the ledge the tabs screw to
    pk=box(-SV_W/2-0.25,SV_W/2+0.25,-(SV_L-SV_SHAFT)-0.25,SV_SHAFT+0.25,BLK_IN-1,top+SV_H+0.6)
    pk+=box(-SV_W/2-0.25,SV_W/2+0.25,cy-SV_TAB/2-0.3,cy+SV_TAB/2+0.3,BLK_IN-1,top+SV_TAB_DOWN+0.2)
    for s in (-1,1): pk+=cw(0.85,top+SV_TAB_DOWN,top+SV_TAB_DOWN+8,v=cy+s*SV_HOLE/2)
    pk+=cw(BOSS_R+1.0,BLK_IN-1,top)                         # horn and spline boss swing here
    pk+=cw(2.0,BLK_IN-1,top).translate([14,0,0])
    b-=H(pk)
    # servo cable drops out of the bottom, through the shelf window, and across to the electronics
    b-=mf.Manifold.cylinder(15,3.0,3.0,24).rotate([-90,0,0]).translate([PX,BY0-1,ZC+40])
    return b-bolts_cut(+1)

def bolts_cut(s):
    # 2x M4 into the handle's lamp slots (the outer two), nut slots open from the top
    c=mf.Manifold()
    for hx in (EAR_HOLES[0][0],EAR_HOLES[3][0]):
        hy=EAR_HOLES[0][1]
        z0,z1=sorted((ZC+s*(BLK_OUT+1),ZC+s*(BLK_OUT-14)))
        c+=cyl_Z(2.2,z0,z1,hx,hy,24)
        n0,n1=sorted((ZC+s*(BLK_OUT-8.5),ZC+s*(BLK_OUT-8.5-3.4)))
        c+=bx(hx-3.6,hx+3.6,hy-3.6,BY1+1,n0,n1)
    return c

def elec_block():
    b=box(BX0,BX1,BY0,BY1,ZC-BLK_OUT,ZC-BLK_IN)
    b-=bx(BX0+3,BX1-3,BY0+3,BY1+1,ZC-BLK_OUT+3.75,ZC-BLK_IN-4)          # compartment, lid on top
    for x,z in LID_SCREWS:                                    # corner posts, M3 self-tappers for the lid
        b+=bx(x-3,x+3,BY1-12,BY1,z-3,z+3)
        b-=mf.Manifold.cylinder(11,1.25,1.25,16).rotate([-90,0,0]).translate([x,BY1-10,z])
    b-=cyl_Z(PIN_R+0.25,ZC-BLK_IN-5,ZC-BLK_IN+1,PX,PY)                 # pivot pin bearing
    b-=mf.Manifold.cylinder(5,3.0,3.0,24).rotate([-90,0,0]).translate([PX,BY0-1,ZC-40])   # servo cable in
    b-=mf.Manifold.cylinder(5,3.5,3.5,24).rotate([-90,0,0]).translate([PX+8,BY0-1,ZC-40])   # power cable in, over the shelf window too
    return b-bolts_cut(-1)

def lid():
    l=bx(BX0,BX1,BY1,BY1+3,ZC-BLK_OUT,ZC-BLK_IN)
    for x,z in LID_SCREWS:
        l-=mf.Manifold.cylinder(5,1.7,1.7,16).rotate([-90,0,0]).translate([x,BY1-1,z])
    return l

def tilt(m,deg_up):  # beam up = front (-X) up
    return m.translate([-PX,-PY,0]).rotate([0,0,deg_up]).translate([PX,PY,0])

if __name__=='__main__':
    hd=H(head()); sv,_,_=servo_model(); sv=H(sv)
    sb=servo_block(); eb=elec_block(); ld=lid()
    handle=to_mf(trimesh.load(OUT+'master_handle_v5_lamp_cup.stl'))
    cup_open=to_mf(trimesh.load('v5_cup_open.stl'))
    fixed={'handle':handle,'servo block':sb,'electronics block':eb,'lid':ld,'servo':sv,'cup (open)':cup_open}
    print('head vs fixed parts while tilting:')
    for a in (-13,-12,-6,0,6,12,13):
        t=tilt(hd,a)
        bad={k:round((t^m).volume(),2) for k,m in fixed.items() if (t^m).volume()>0.01}
        print(f'  {a:4d} deg', bad or 'clear')
    print('servo in its block:',round((sv^sb).volume(),2),' blocks vs handle:',round((sb^handle).volume(),2),round((eb^handle).volume(),2),' lid vs handle',round((ld^handle).volume(),2))
    for nm,m in (('head',head()),('servo block',sb),('electronics block',eb),('lid',ld)):
        t=to_tm(m); print(f'  {nm}: watertight {t.is_watertight}, bodies {len(t.split(only_watertight=False))}, size {np.round(t.extents,1)}, {round(t.volume/1000,1)} cm3')
    # print orientations
    def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
    to_tm(flat(head().rotate([0,90,0]))).export(OUT+'headlamp_head.stl')            # open back on the bed
    to_tm(flat(sb.rotate([180,0,0]))).export(OUT+'headlamp_servo_block.stl')  # outer face on the bed
    to_tm(flat(eb.rotate([90,0,0]))).export(OUT+'headlamp_electronics_block.stl')  # bottom on the bed
    to_tm(flat(ld.rotate([-90,0,0]))).export(OUT+'headlamp_lid.stl')
    # assembly pieces for the renders
    to_tm(sb+eb+ld).export('lamp_fixed.stl'); to_tm(sv).export('lamp_servo.stl')
    for a in (-12,-8,0,6,8,12): to_tm(tilt(hd,a)).export(f'lamp_head_{a}.stl')
