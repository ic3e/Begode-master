# v11 (option A): the self-levelling lamp goes into the stock lamp's opening in the top cover.
# Opening (owner's caliper): 134 wide, 36.8 tall, 49.3 deep, top 39.1 above the lowest bolt hole; the old
# lamp's metal underside hung 9.8 lower, under the cover's front lip. Two M4 screws come down through the
# cover's top into the lamp: the new housing takes them, so the handle gets two more mounting points.
# The housing sits on a tray that is part of the handle: the tray is carried by webs that run back to the
# handle's tabs, where the stock lamp's ears used to bolt on.
# To fit the opening and keep the whole lens above the cover's front lip while it tilts ±10°, the head
# uses a 20 mm TIR optic on a 16 mm star and a 25x25x20 heat sink (one LDD-1500L, ~5 W).
import numpy as np, trimesh, manifold3d as mf, types
exec(open('build15.py').read())            # helpers, cup holder parts, M2 (measured wheel)

# ---- measured opening ----
OPEN_TOP=M2.HOLE[1]+39.1; OPEN_BOT=OPEN_TOP-36.8; OPEN_W=134.0; OPEN_BACK=M2.COVER_X+49.3
LIP_BACK=M2.LAMP_X                         # the stock lamp face: the cover's lip is in front of this
HOUSE_X0,HOUSE_X1=LIP_BACK+0.2,OPEN_BACK-0.5
HOUSE_Y0=M2.LAMP_Y+0.2                     # where the old lamp's underside was
HOUSE_YS=M2.LAMP_Y+1.2                     # outer parts: the shell tops rise to just under -20.3 at the front
HOUSE_Y1=OPEN_TOP-0.5; HOUSE_W=OPEN_W/2-0.5
TOP_SCREWS=[(M2.COVER_X+32.8,s*30.4) for s in (-1,1)]
WALL=2.0; FACE=2.5
# ---- head ----
TIR2_D=20.0; TIR2_H=12.0; STAR2=1.6; HS2=25.0; HS2_D=20.0
HW2=HS2/2+1.5; HV2=13.5; HU0_2,HU1_2=-17.0,18.0
TILT2=10.0
PX2=HOUSE_X0+FACE+0.5-HU0_2; PY2=4.0
PIN2_R=4.0
def H2(m): return m.translate([PX2,PY2,ZC])
def tilt2(m,a): return m.translate([-PX2,-PY2,0]).rotate([0,0,a]).translate([PX2,PY2,0])
def head2():
    h=box(HU0_2,HU1_2,-HV2,HV2,-HW2,HW2)
    h-=cu(8.0,HU0_2-1,HU0_2+1.5)                                   # front aperture
    h-=cu(TIR2_D/2+0.2,HU0_2+1.5,HU0_2+1.5+TIR2_H+STAR2+0.2)        # optic + star
    h-=box(HU1_2-HS2_D,HU1_2+1,-HS2/2-0.2,HS2/2+0.2,-HS2/2-0.2,HS2/2+0.2)   # heat sink from the back
    for w in (-7,7): h-=mf.Manifold.cylinder(2*HV2+2,1.4,1.4,16).rotate([-90,0,0]).translate([HU1_2-8,-HV2-1,w])
    h+=box(HU0_2-6,HU0_2+0.5,HV2-2,HV2,-10,10)                      # short visor
    b=hull(cw(7,HW2,HW2+3),cw(4.5,HW2,HW2+3,u=11))                 # servo horn boss
    b-=hull(cw(3.9,HW2+3-2.2,HW2+4),cw(2.5,HW2+3-2.2,HW2+4,u=12))
    b-=cw(3.2,HW2+3-4,HW2+4)
    for u in (6.5,10): b-=cw(0.8,HW2+3-7,HW2+4,u=u)
    h+=b+cw(7,-HW2-3,-HW2)+cw(PIN2_R,-HW2-3-4.5,-HW2-3+0.5)
    h-=cw(2.3,-HW2-3-5.5,-TIR2_D/2+1,u=HU0_2+1.5+TIR2_H+STAR2/2)   # LED + NTC wires out through the pin
    return h
SV_TOP2=HW2+3+0.5+SV_BOSS
def servo2():   # MG90S lying with its body running back from the shaft
    cu_=SV_L/2-SV_SHAFT
    body=box(-SV_SHAFT,SV_L-SV_SHAFT,-SV_W/2,SV_W/2,SV_TOP2,SV_TOP2+SV_H)
    tabs=box(cu_-SV_TAB/2,cu_+SV_TAB/2,-SV_W/2,SV_W/2,SV_TOP2+SV_TAB_DOWN-SV_TAB_T,SV_TOP2+SV_TAB_DOWN)
    return body+tabs+cw(3.0,SV_TOP2-SV_BOSS,SV_TOP2)
# ---- housing (open at the bottom: the handle's tray closes it) ----
PART0,PART1=HW2+3.5,HW2+5.5           # partitions either side of the head
DRL2_W0,DRL2_W1,DRL2_Y0,DRL2_Y1=PART1+2,PART1+24,OPEN_BOT+16,OPEN_TOP-4
TOF2=(-56.0,OPEN_TOP-14); LDR2=(56.0,OPEN_TOP-14)
TRAY_SCREWS=[(x,s*(PART0+PART1)/2) for x in (HOUSE_X0+9,HOUSE_X1-8) for s in (-1,1)]
def zw(a,b): return sorted((ZC+a,ZC+b))
def housing():
    W=HOUSE_W
    outer=bx(HOUSE_X0,HOUSE_X1,HOUSE_Y0,HOUSE_Y1,ZC-47,ZC+47)+bx(HOUSE_X0,HOUSE_X1,HOUSE_YS,HOUSE_Y1,ZC-W,ZC+W)
    inner=bx(HOUSE_X0+FACE,HOUSE_X1-WALL,HOUSE_Y0-1,HOUSE_Y1-WALL,ZC-W+WALL,ZC+W-WALL)
    h=outer-inner
    for s in (-1,1):
        z0,z1=zw(s*47,s*W); h+=bx(HOUSE_X0,HOUSE_X1,HOUSE_YS,HOUSE_YS+2,z0,z1)
    for s in (-1,1):   # partitions with the head's bearings
        z0,z1=zw(s*PART0,s*PART1); h+=bx(HOUSE_X0+FACE-0.1,HOUSE_X1-WALL+0.1,HOUSE_Y0,HOUSE_Y1-WALL+0.1,z0,z1)
    h-=cw(PIN2_R+0.25,-PART1-1,-PART0+1).translate([PX2,PY2,ZC])                  # pin bearing (-w)
    h-=cw(SV_BOSS+0.6,PART0-1,PART1+1).translate([PX2,PY2,ZC])                    # servo spline boss through (+w)
    h-=hull(cw(7.6,PART0-1,PART0+0.6),cw(5.1,PART0-1,PART0+0.6,u=11)).translate([PX2,PY2,ZC])   # horn swings by the partition
    # head window and the room it tilts in, front face
    h-=bx(HOUSE_X0-1,HOUSE_X0+FACE+1,OPEN_BOT+0.8,HOUSE_Y1-WALL-0.5,ZC-HW2-0.5,ZC+HW2+0.5)
    for s in (-1,1):   # daytime running light windows + recess for the diffusers
        z0,z1=zw(s*DRL2_W0,s*DRL2_W1); r0,r1=zw(s*(DRL2_W0-2),s*(DRL2_W1+2))
        h-=bx(HOUSE_X0-1,HOUSE_X0+FACE+1,DRL2_Y0,DRL2_Y1,z0,z1)+bx(HOUSE_X0-1,HOUSE_X0+1.2,DRL2_Y0-2,DRL2_Y1+2,r0,r1)
    # road sensor: a 9x11 tunnel aimed 15° down, with a slot for the board behind it
    t=box(-6,4,-4.5,4.5,-5.5,5.5).rotate([0,0,180+TOF_DOWN]).translate([HOUSE_X0+1,TOF2[1],ZC+TOF2[0]])
    m=box(-12,0,-12,12,-9,9).rotate([0,0,180+TOF_DOWN]).translate([HOUSE_X0+FACE,TOF2[1],ZC+TOF2[0]])
    sl=box(-7.2,-3.8,-9.3,9.3,-9.3,9.3).rotate([0,0,180+TOF_DOWN]).translate([HOUSE_X0+FACE,TOF2[1],ZC+TOF2[0]])
    h=(h+(m^outer))-t-sl
    h-=mf.Manifold.cylinder(FACE+2,2.65,2.65,24).rotate([0,90,0]).translate([HOUSE_X0-1,LDR2[1],ZC+LDR2[0]])   # 5 mm LDR
    # top: two bosses for the cover's M4 screws, nut slot opening downwards
    for x,w in TOP_SCREWS:
        h+=cylV(6,HOUSE_Y1-9,HOUSE_Y1-0.1,x,w)
        h-=cylV(2.2,HOUSE_Y1-10,HOUSE_Y1+1,x,w)
        h-=bxw(x-3.7,x+3.7,HOUSE_Y1-9.5,HOUSE_Y1-5,w-3.25,w+3.25).translate([0,0,0])
    # servo cradle on the +w side: two posts its tabs screw to
    for du in (-SV_TAB/2+2.4,SV_TAB/2-2.4):
        x=PX2+(SV_L/2-SV_SHAFT)+du; z0,z1=zw(SV_TOP2+SV_TAB_DOWN,W-WALL+0.1)
        p=bx(x-2.2,x+2.2,PY2-3,PY2+3,z0,z1)-mf.Manifold.cylinder(9,0.85,0.85,16).translate([x,PY2,z0-0.1])
        h+=p
    # screw bosses at the bottom of the partitions (M3 from below, through the tray)
    for x,w in TRAY_SCREWS:
        h+=bxw(x-4,x+4,HOUSE_Y0,HOUSE_Y0+8,w-3,w+3)-cylV(1.25,HOUSE_Y0-1,HOUSE_Y0+7,x,w)
    for s in (-1,1):   # servo cable crosses under the head to the electronics side
        z0,z1=zw(s*(PART0-1),s*(PART1+1)); h-=bx(-44,-38,HOUSE_Y0-1,HOUSE_Y0+4,z0,z1)
    # wires: servo cable and the power lead leave at the back
    for w in (-30,30): h-=mf.Manifold.cylinder(WALL+2,3.2,3.2,24).rotate([0,90,0]).translate([HOUSE_X1-WALL-1,HOUSE_Y0+8,ZC+w])
    return h
def diffuser2(s):
    r0,r1=zw(s*(DRL2_W0-2+0.15),s*(DRL2_W1+2-0.15))
    return bx(HOUSE_X0,HOUSE_X0+1.2,DRL2_Y0-2+0.15,DRL2_Y1+2-0.15,r0,r1)
def lamp2_parts(a=0.0):
    return housing(),tilt2(H2(head2()),a),tilt2(H2(servo2()),a*0)
# ---- handle additions (webs back to the tabs, front crossbar, hinge brackets) and the bolt-on tray ----
# Fitting order: housing up into the opening from below, held by the cover's two M4 screws; then the
# handle; then the tray, which closes the housing's bottom and screws to it and to the handle.
TRAY_T=4.0; TRAY_Y1=HOUSE_Y0-0.2; TRAY_Y0=TRAY_Y1-TRAY_T
SUP_Y1=TRAY_Y0; SUP_Y0=SUP_Y1-4.0        # webs and crossbar sit under the tray
XB0,XB1=-88.0,-82.0
GS=np.array([-76.0,SUP_Y0-1.0-R_H/2])   # swung in: ring top 1 mm under the crossbar, pressed on the tray's pads
HY=GS[1]; HX=-118.0; HP=np.array([HX,HY]); R_ARM=float(np.hypot(GS[0]-HX,GS[1]-HY))
TH_IN=np.degrees(np.arctan2(GS[1]-HY,GS[0]-HX)); TH_OUT=-95.0
GD=gpos(TH_OUT)
STOP_A=TH_OUT-np.degrees(np.arcsin(6/STOP_R))-np.degrees(np.arcsin(3.4/STOP_R))-1.0
WEB_X0,WEB_X1=HOUSE_X1-12,-10.5
SUP_SCREWS=[((XB0+XB1)/2,s*40) for s in (-1,1)]+[((WEB_X0+WEB_X1)/2-2,s*38) for s in (-1,1)]
def handle_adds():
    p=[]
    for s in (-1,1):   # webs back to the handle's tabs (where the stock lamp's ears bolted on)
        z0,z1=zw(s*30,s*70.5); p.append(bx(WEB_X0,WEB_X1,SUP_Y0,SUP_Y1,z0,z1))
        z0,z1=zw(s*66.7,s*70.5); p.append(bx(-11,4,SUP_Y0,-17,z0,z1))
    p.append(bx(XB0,XB1,SUP_Y0,SUP_Y1,ZC-K1,ZC+K1))
    for s in (-1,1):   # side rails tie the crossbar back to the webs, inside the bay's 95 mm
        z0,z1=zw(s*43.8,s*46.8); p.append(bx(XB0,WEB_X0+1,SUP_Y0,SUP_Y1,z0,z1))
    for s in (-1,1):
        w0,w1=sorted((s*K0,s*K1))
        c=HP+STOP_R*np.array([np.cos(np.radians(STOP_A)),np.sin(np.radians(STOP_A))])
        b=hull(bxw(XB0,XB1,SUP_Y0,SUP_Y1,w0,w1),cylW(6,w0,w1,HP[0],HP[1]))
        b+=hull(cylW(6,w0,w1,HP[0],HP[1]),cylW(4.5,w0,w1,c[0],c[1]))
        b-=cylW(2.2,w0-1,w1+1,HP[0],HP[1])
        s0,s1=sorted((s*(A0+0.2),s*(K0+0.5))); b+=cylW(3.2,s0,s1,c[0],c[1])
        p.append(b)
    m=mf.Manifold.batch_boolean(p,mf.OpType.Add)
    for x,w in SUP_SCREWS: m-=cylV(1.25,SUP_Y0-1,SUP_Y1+1,x,w)          # M3 self-tap pilots for the tray
    return m
def tray():
    t=bx(XB0,HOUSE_X1,TRAY_Y0,TRAY_Y1,ZC-47,ZC+47)
    t-=bx(M2.CABLE_X-3,HOUSE_X1+1,TRAY_Y0-1,TRAY_Y1+1,ZC-26,ZC+26)        # clears the motor cable
    t-=bx(-36,-26,TRAY_Y0-1,TRAY_Y1+1,ZC-14,ZC+14)                          # warm air out from behind the head
    for x,w in TRAY_SCREWS+SUP_SCREWS: t-=cylV(1.7,TRAY_Y0-1,TRAY_Y1+1,x,w)
    rt=GS[1]+R_H/2
    pads=[bxw(GS[0]+R_OUT-2,GS[0]+R_OUT+3,rt,TRAY_Y0+0.5,-6,6)]
    for s in (-1,1):
        w0,w1=sorted((s*29,s*40)); pads.append(bxw(GS[0]-5,GS[0]+5,rt,TRAY_Y0+0.5,w0,w1))
    return mf.Manifold.batch_boolean([t]+pads,mf.OpType.Add)
# ---- wheel with the stock lamp out ----
def cover3():
    side=[(M2.COVER_X,OPEN_BOT),(M2.COVER_X,22),(-45,58),(-5,86),(355,86),(392,72),(392,24),(M2.BLOCK_X,24),(M2.BLOCK_X,OPEN_BOT)]
    c=M2.ex_soft(side,ZC,ZC+73,6,6,+1)+M2.ex_soft(side,ZC-73,ZC,6,6,-1)
    return c-bx(M2.COVER_X-1,OPEN_BACK,OPEN_BOT,OPEN_TOP,ZC-OPEN_W/2,ZC+OPEN_W/2)
def obstacles3(low=True):
    o=M2.shells(True)+[cover3(),M2.box_ctrl(),M2.cable()]
    if low: o.append(bx(M2.SHELL_X-2,200,-400,M2.PLATE_LOW,ZC-M2.BAY_W/2,ZC+M2.BAY_W/2))
    return mf.Manifold.batch_boolean(o,mf.OpType.Add)
def model3():
    parts=[(m,'#2b2d31') for m in M2.shells()]+[(cover3(),'#232427'),(M2.box_ctrl(),'#1b1c1e'),(M2.cable(),'#111111'),(M2.plate(),'#9ea3a9')]+M2.lower()
    return [(to_tm(m),c) for m,c in parts]
