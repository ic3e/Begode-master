# v12 (lamp v5): no can holder; a brighter self-levelling headlamp in the stock lamp opening.
# Three LEDs (16 mm stars, 20 mm TIR optics: one narrow for reach, two wide for spread) sit on one
# finned heat-sink bar that the servo tilts ±10°. The bar fills the opening's width between the servo
# and the pivot pin. With no can holder under it, the electronics (three LDD-1500L, ESP32-C3, MPU-6050,
# buck, DRL switch) move into a box that hangs down into the bay between the shells, with a lid underneath
# for access. The lamp is held by the cover's two M4 screws and by two webs that run back to the
# handle's tabs.
import numpy as np, trimesh, manifold3d as mf
exec(open('build16.py').read())

PITCH3=21.0                               # optic centres across
OPTIC_W=(-PITCH3,0.0,PITCH3)
HS3_W,HS3_H,HS3_D=64.0,25.0,20.0          # finned bar: the three stars glue to its flat face
HW3=HS3_W/2+1.5; HV3=13.5; HU0_3,HU1_3=-17.0,18.0
BOSS3=2.5
VISOR3=6.0
PIN3_R,BORE3_R=5.0,3.3                   # hollow pivot pin: 6 LED wires + 2 sensor wires (26 AWG) go through it
PX3=HOUSE_X0+FACE+0.5-HU0_3; PY3=2.2
def H3(m): return m.translate([PX3,PY3,ZC])
def tilt3(m,a): return m.translate([-PX3,-PY3,0]).rotate([0,0,a]).translate([PX3,PY3,0])
def head3():
    h=box(HU0_3,HU1_3,-HV3,HV3,-HW3,HW3)
    for w in OPTIC_W:
        h-=cu(8.0,HU0_3-1,HU0_3+1.5,w=w)                                     # apertures
        h-=cu(TIR2_D/2+0.2,HU0_3+1.5,HU0_3+1.5+TIR2_H+STAR2+0.2,w=w)        # optic + star
    h-=box(HU1_3-HS3_D,HU1_3+1,-HS3_H/2-0.2,HS3_H/2+0.2,-HS3_W/2-0.2,HS3_W/2+0.2)   # heat sink bar from the back
    for w in (-27,0,27): h-=mf.Manifold.cylinder(2*HV3+2,1.4,1.4,16).rotate([-90,0,0]).translate([HU1_3-8,-HV3-1,w])
    h+=box(HU0_3-VISOR3,HU0_3+0.5,HV3-2,HV3,-HW3+2,HW3-2)                  # visor over the three
    b=hull(cw(7,HW3,HW3+BOSS3),cw(4.5,HW3,HW3+BOSS3,u=11))                  # servo horn boss
    b-=hull(cw(3.9,HW3+BOSS3-2.2,HW3+BOSS3+1),cw(2.5,HW3+BOSS3-2.2,HW3+BOSS3+1,u=12))
    b-=cw(3.2,HW3+BOSS3-4,HW3+BOSS3+1)
    for u in (6.5,10): b-=cw(0.8,HW3+BOSS3-7,HW3+BOSS3+1,u=u)
    h+=b+cw(7.5,-HW3-BOSS3,-HW3)+cw(PIN3_R,-HW3-BOSS3-4.5,-HW3-BOSS3+0.5)
    h-=cw(BORE3_R,-HW3-BOSS3-5.5,-PITCH3,u=HU0_3+1.5+TIR2_H+STAR2/2)      # LED wires out through the pin
    return h
SV_TOP3=HW3+BOSS3+0.3+SV_BOSS
def servo3():
    cu_=SV_L/2-SV_SHAFT
    body=box(-SV_SHAFT,SV_L-SV_SHAFT,-SV_W/2,SV_W/2,SV_TOP3,SV_TOP3+SV_H)
    tabs=box(cu_-SV_TAB/2,cu_+SV_TAB/2,-SV_W/2,SV_W/2,SV_TOP3+SV_TAB_DOWN-SV_TAB_T,SV_TOP3+SV_TAB_DOWN)
    return body+tabs+cw(3.0,SV_TOP3-SV_BOSS,SV_TOP3)
P3A,P3B=HW3+BOSS3+0.6,HW3+BOSS3+2.6        # partitions
DRL3_W0,DRL3_W1=P3B+1.5,HOUSE_W-3.5
TOF3=(-30.0,-34.0)                          # road sensor in the lower box's front, left of centre
LDR3=(56.0,OPEN_TOP-6)
LOW_W=46.5; LOW_X0,LOW_X1=M2.SHELL_X+0.5,-27.0; LOW_Y0=M2.PLATE_LOW+7.0
LIP_Y=M2.LAMP_Y-0.8
LID_POSTS=[(x,s*(LOW_W-WALL-3)) for x in (LOW_X0+FACE+3,LOW_X1-WALL-3) for s in (-1,1)]                         # under the cover's lip, in front of the old lamp face
def housing3():
    W=HOUSE_W
    up=bx(HOUSE_X0,HOUSE_X1,HOUSE_Y0,HOUSE_Y1,ZC-47,ZC+47)+bx(HOUSE_X0,HOUSE_X1,HOUSE_YS,HOUSE_Y1,ZC-W,ZC+W)
    lo=bx(LOW_X0,LOW_X1,LOW_Y0,HOUSE_Y0+0.5,ZC-LOW_W,ZC+LOW_W)-bx(LOW_X0-1,HOUSE_X0,LIP_Y,HOUSE_Y0+1,ZC-LOW_W-1,ZC+LOW_W+1)
    outer=up+lo
    inner=bx(HOUSE_X0+FACE,HOUSE_X1-WALL,HOUSE_Y0-1,HOUSE_Y1-WALL,ZC-W+WALL,ZC+W-WALL)
    inner+=bx(LOW_X0+FACE,LOW_X1-WALL,LOW_Y0-1,HOUSE_Y0+1,ZC-LOW_W+WALL,ZC+LOW_W-WALL)-bx(LOW_X0-1,HOUSE_X0+FACE,LIP_Y-FACE,HOUSE_Y0+2,ZC-50,ZC+50)
    h=outer-inner
    for s in (-1,1):   # floors under the side compartments (beside the bay, over the shells)
        z0,z1=zw(s*LOW_W,s*W); h+=bx(HOUSE_X0,HOUSE_X1,HOUSE_YS,HOUSE_YS+2,z0,z1)
    for s in (-1,1):
        z0,z1=zw(s*P3A,s*P3B); h+=bx(HOUSE_X0+FACE-0.1,HOUSE_X1-WALL+0.1,HOUSE_Y0+3,HOUSE_Y1-WALL+0.1,z0,z1)
    h-=cw(PIN3_R+0.25,-P3B-1,-P3A+1).translate([PX3,PY3,ZC])
    h-=cw(SV_BOSS+0.6,P3A-1,P3B+1).translate([PX3,PY3,ZC])
    h-=hull(cw(7.6,P3A-1,P3A+0.6),cw(5.1,P3A-1,P3A+0.6,u=11)).translate([PX3,PY3,ZC])
    h-=bx(HOUSE_X0-1,HOUSE_X0+FACE+1,OPEN_BOT+0.8,HOUSE_Y1-WALL-0.5,ZC-HW3-0.5,ZC+HW3+0.5)      # head window (air comes in here too)
    for s in (-1,1):   # running lights either side
        z0,z1=zw(s*DRL3_W0,s*DRL3_W1); r0,r1=zw(s*(DRL3_W0-2),s*(DRL3_W1+2))
        h-=bx(HOUSE_X0-1,HOUSE_X0+FACE+1,DRL2_Y0,DRL2_Y1,z0,z1)+bx(HOUSE_X0-1,HOUSE_X0+1.2,DRL2_Y0-2,DRL2_Y1+2,r0,r1)
    t=box(-6,4,-4.5,4.5,-5.5,5.5).rotate([0,0,180+TOF_DOWN]).translate([LOW_X0+1,TOF3[1],ZC+TOF3[0]])
    m=box(-12,0,-12,12,-9,9).rotate([0,0,180+TOF_DOWN]).translate([LOW_X0+FACE,TOF3[1],ZC+TOF3[0]])
    sl=box(-7.2,-3.8,-9.3,9.3,-9.3,9.3).rotate([0,0,180+TOF_DOWN]).translate([LOW_X0+FACE,TOF3[1],ZC+TOF3[0]])
    h=(h+(m^outer))-t-sl
    h-=mf.Manifold.cylinder(FACE+2,2.65,2.65,24).rotate([0,90,0]).translate([HOUSE_X0-1,LDR3[1],ZC+LDR3[0]])
    for x,w in TOP_SCREWS:   # short bosses over the head: M4 heat-set inserts (5.7 long, 5.6 OD) for the cover's screws
        h+=cylV(6,HOUSE_Y1-6,HOUSE_Y1-0.1,x,w)
        h-=cylV(2.8,HOUSE_Y1-5.8,HOUSE_Y1+1,x,w)
    for du in (-SV_TAB/2+2.4,SV_TAB/2-2.4):
        x=PX3+(SV_L/2-SV_SHAFT)+du; z0,z1=zw(SV_TOP3+SV_TAB_DOWN,W-WALL+0.1)
        h+=bx(x-2.2,x+2.2,PY3-3,PY3+3,z0,z1)-mf.Manifold.cylinder(9,0.85,0.85,16).translate([x,PY3,z0-0.1])
    # warm air out of the back of the lower box, into the back of the bay
    for k in range(5):
        z=-28+k*14; h-=bx(LOW_X1-WALL-1,LOW_X1+1,LOW_Y0+6,HOUSE_Y0-4,ZC+z-4,ZC+z+4)
    # lid corner posts (M3 self-tap), and the screw bosses that sit on the handle's webs
    for x,w in LID_POSTS: h+=cylV(4,LOW_Y0,LOW_Y0+10,x,w)
    for x,w in WEB_SCREWS: h+=cylV(4,HOUSE_YS,HOUSE_YS+8,x,w)
    for x,w in LID_POSTS: h-=cylV(1.25,LOW_Y0-1,LOW_Y0+9,x,w)
    for x,w in WEB_SCREWS: h-=cylV(1.25,HOUSE_YS-1,HOUSE_YS+7,x,w)
    # wires: power lead in at the back of the side compartment
    h-=mf.Manifold.cylinder(WALL+2,3.2,3.2,24).rotate([0,90,0]).translate([HOUSE_X1-WALL-1,HOUSE_YS+8,ZC-56])
    return h
def lid3():
    l=bx(LOW_X0,LOW_X1,LOW_Y0-2.5,LOW_Y0,ZC-LOW_W,ZC+LOW_W)
    l+=bx(LOW_X0+FACE+0.3,LOW_X1-WALL-0.3,LOW_Y0,LOW_Y0+2,ZC-LOW_W+WALL+0.3,ZC+LOW_W-WALL-0.3)-bx(LOW_X0+FACE+2,LOW_X1-WALL-2,LOW_Y0-1,LOW_Y0+3,ZC-LOW_W+WALL+2,ZC+LOW_W-WALL-2)
    for x,w in LID_POSTS: l-=cylV(4.3,LOW_Y0-0.1,LOW_Y0+3,x,w); l-=cylV(1.7,LOW_Y0-4,LOW_Y0+1,x,w)
    return l
def diffuser3(s):
    r0,r1=zw(s*(DRL3_W0-2+0.15),s*(DRL3_W1+2-0.15))
    return bx(HOUSE_X0,HOUSE_X0+1.2,DRL2_Y0-2+0.15,DRL2_Y1+2-0.15,r0,r1)
# handle v12: the original handle + two webs back to its tabs (the lamp's back corners screw onto them)
WEB_Y1=HOUSE_YS-0.2; WEB_Y0=WEB_Y1-4.0
WEB_SCREWS=[(-19.5,s*57.0) for s in (-1,1)]
def handle_adds3():
    p=[]
    for s in (-1,1):
        z0,z1=zw(s*48.0,s*70.5); p.append(bx(-25,-10.5,WEB_Y0,WEB_Y1,z0,z1))
        z0,z1=zw(s*66.7,s*70.5); p.append(bx(-11,4,WEB_Y0,-17,z0,z1))
    m=mf.Manifold.batch_boolean(p,mf.OpType.Add)
    for x,w in WEB_SCREWS: m-=cylV(1.7,WEB_Y0-1,WEB_Y1+1,x,w)
    return m
