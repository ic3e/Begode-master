# Lamp v6: sealed against rain, tyre spray and sand. The tyre sits a few cm under the lamp and throws
# water and sand up at it even on a merely wet road, so nothing that minds water may sit in the cooling air.
# The LEDs no longer tilt: the three stars stay on the heat-sink bar, and the bar is clamped behind a
# bulkhead with its face (and the LEDs) on the dry side and its fins in a duct of their own. Only a light
# frame with the three lenses tilts, about the line through the three LED chips, so the beam follows the
# lens. The lens base stands 2 mm off the stars so it can swing ±12° without touching (it costs some light).
# The duct: chin slots -> a trap with drains in the lid (water and sand drop out) -> a passage under the
# lenses -> up through the fins -> down the back into the bay. Everything else is dry and sealed: the
# lenses and the inside of the window, the servo and bearing, the electronics (a box with a gasketed lid),
# the road sensor (its own pocket behind a small window).
import numpy as np, trimesh, manifold3d as mf
exec(open('build21.py').read())

# ---- the fixed LED bar and the tilting lens frame ----
BAR_W=62.0                                           # 64 mm bar cut to 62: room for the lens frame's pivots
BAR_X0=PX3+HU1_3-HS3_D+0.8; BAR_X1=BAR_X0+HS3_D        # face -40.6 .. fin tips -20.6: the lens fronts stay behind the face
BAR_Y0,BAR_Y1=PY3-HS3_H/2,PY3+HS3_H/2
DOME=0.8; LENS_GAP=2.0
PX6=BAR_X0-STAR2-DOME; PY6=PY3                         # pivot = the LED chips
LB_U=DOME-LENS_GAP; LF_U=LB_U-TIR2_H                   # lens base / front, in the pivot frame (u = x - PX6)
LR=TIR2_D/2
def H6(m): return m.translate([PX6,PY6,ZC])
def tilt6(m,a): return m.translate([-PX6,-PY6,0]).rotate([0,0,a]).translate([PX6,PY6,0])
HUB_R=6.1; ARM_W0,ARM_W1=33.3,34.6; ARM_U0=-11.5     # arms stay behind the face (the face opening is ±34.5 wide)
HORN_UV=(-4.0,10.5)                                  # the servo horn's arm points up and a little forward
def lens_frame():
    box_=box(LF_U-0.6,LB_U-5.0,-(LR+1.2),LR+1.2,-(21+LR+1.2),21+LR+1.2)
    for w in OPTIC_W:
        box_-=cu(LR+0.15,LF_U,LB_U+1,w=w)+cu(LR-1.0,LF_U-1,LF_U+0.1,w=w)       # bore from the back, lip at the front
    f=box_
    for s in (-1,1):
        z0,z1=sorted((s*(21+LR+0.5),s*ARM_W1)); f+=box(ARM_U0,LB_U-5.0,-8,8,z0,z1)       # bridge to the arm
        z0,z1=sorted((s*ARM_W0,s*ARM_W1)); f+=box(ARM_U0,0.5,-5,5,z0,z1)                 # arm back to the pivot
        z0,z1=sorted((s*ARM_W0,s*(HW3+BOSS3))); f+=cw(HUB_R,z0,z1)                       # hub
    f+=cw(BRG_ID/2+1.0,BRG_W1,-HW3-BOSS3+0.1)+cw(BRG_ID/2,BRG_W0,BRG_W1+0.1)              # shoulder and pin (left)
    # right: servo horn in a recess, its arm pointing forward
    b=hull(cw(HUB_R,HW3+BOSS3-2.5,HW3+BOSS3),cw(4.5,HW3+BOSS3-2.5,HW3+BOSS3,u=HORN_UV[0],v=HORN_UV[1]))
    f+=b
    f-=hull(cw(3.9,HW3+BOSS3-2.2,HW3+BOSS3+1),cw(2.5,HW3+BOSS3-2.2,HW3+BOSS3+1,u=HORN_UV[0]*1.1,v=HORN_UV[1]*1.1))
    f-=cw(3.2,HW3+BOSS3-4,HW3+BOSS3+1)
    for k in (0.62,0.95): f-=cw(0.8,HW3+BOSS3-7,HW3+BOSS3+1,u=HORN_UV[0]*k,v=HORN_UV[1]*k)
    f+=box(LUG6[0],LUG6[1],-LUG6[2],LUG6[2],-36.2,-ARM_W1+0.1)                              # stop lug
    return f
LUG6=(-11.0,-6.5,2.2)
STOP6_V=-LUG6[0]*np.sin(np.radians(12))+LUG6[2]*np.cos(np.radians(12))
STOP6_U=(-12.5,-6.0); STOP6_W=(-36.5,-34.8)
def stop6_lower():
    z0,z1=zw(*STOP6_W); return bx(PX6+STOP6_U[0],PX6+STOP6_U[1],FLOOR_Y[1]-0.1,PY6-STOP6_V,z0,z1)
def stop6_upper():
    z0,z1=zw(*STOP6_W); return bx(PX6+STOP6_U[0],PX6+STOP6_U[1],PY6+STOP6_V,PLATE_Y0+0.1,z0,z1)
def lenses6():   # the three optics, for checks and renders
    return mf.Manifold.batch_boolean([cu(LR-0.2,LF_U,LB_U,w=w) for w in OPTIC_W],mf.OpType.Add)
def led_bar():   # bar with its fins (as a block) and the three stars
    m=bx(BAR_X0,BAR_X1,BAR_Y0,BAR_Y1,ZC-BAR_W/2,ZC+BAR_W/2)
    for w in OPTIC_W: m+=mf.Manifold.cylinder(STAR2,8,8,48).rotate([0,-90,0]).translate([BAR_X0,PY3,ZC+w])
    return m
def servo6(): return H6(servo3())

# ---- the housing: dry front, wet duct, sealed box ----
BULK_X0,BULK_X1=BAR_X0-2.0,BAR_X0                      # bulkhead; the bar presses on its back
BULK_OPEN=(29.6,PY6-11.0,PY6+11.0)                     # stars and lens rims pass through
JOG_W=(31.2,32.9); STEP_X=(-36.5,-35.4)                # walls round the pivot pockets (dry)
FLOOR_Y=(-14.5,-12.5)                                  # floor under the lenses and the fins
PASS_Y0=-22.5                                          # passage floor = electronics box roof (top face)
ROOF_T=2.0
DIV_X=(-47.0,-45.0)                                    # trap | electronics box (the drivers live in the dry side bays)
TRAP_IN_W=29.0                                         # passage inlet width (the road sensor pocket is beside it)
INLET=(-39.7,-31.7,28.5)                               # floor holes under the fins
PASS_END=(-31.5,-29.5)
TOF_POCKET=(-44.5,-29.5)
CUT_Y0=-7.0                                            # face opening's bottom: 3.4 mm of face below it for the window tape
TAPE_W=3.4
def housing9():
    W=HOUSE_W; h=housing8()
    # take out v5.4's pivot fittings, posts, stops, the baffle and the box's exhaust slots
    z0,z1=zw(-P3B-BEAR_T-1.1,-P3B); h-=bx(HOUSE_X0+FACE+0.5,HOUSE_X1-WALL-0.5,HOUSE_Y0+3-0.1,PLATE_Y0+0.1,z0,z1)  # old bearing block off
    for s in (-1,1):
        z0,z1=zw(s*(P3A-0.05),s*P3B)
        h+=bx(HOUSE_X0+FACE-0.05,HOUSE_X1-WALL+0.05,HOUSE_Y0+3,PLATE_Y0,z0,z1)            # partitions whole again
    for x in SV_POSTS:
        z0,z1=zw(TAB_W0-2.3,W-WALL); h-=bx(x-2.3,x+2.3,SV_Y0-3.1,SV_Y1+5.1,z0,z1)
    h-=stop_lower().translate([0,-0.05,0])
    h-=bx(PX3-1.05,PX3+1.05,LOW_Y0+0.05,HOUSE_Y0-0.55,ZC-LOW_W+WALL+0.05,ZC+LOW_W-WALL-0.05)
    for k in range(5):
        z=-28+k*14; h+=bx(LOW_X1-WALL-0.05,LOW_X1,LOW_Y0+5.9,HOUSE_Y0-3.9,ZC+z-4.1,ZC+z+4.1)
    # new pivot: bearing block on the left, servo slot on the right, servo posts
    dX=PX6-PX3
    z0,z1=zw(BLK_W0,-P3A); h+=bx(PX6-12.5,PX6+12.5,HOUSE_Y0+3,PLATE_Y0,z0,z1)
    z0,z1=zw(BRG_W0-0.1,-P3A+0.1)
    h-=cw(SEAT_R,BRG_W0-0.1,-P3A+0.1).translate([PX6,PY6,ZC])+bx(PX6-SEAT_R,PX6+SEAT_R,PY6,PLATE_Y0+1,z0,z1)
    z0,z1=zw(BLK_W0-1,BRG_W0)
    h-=cw(WIRE_R,BLK_W0-1,BRG_W0).translate([PX6,PY6,ZC])+bx(PX6-WIRE_R,PX6+WIRE_R,PY6,PLATE_Y0+1,z0,z1)
    z0,z1=zw(P3A-1,P3B+1)
    h-=cw(SV_BOSS+0.6,P3A-1,P3B+1).translate([PX6,PY6,ZC])+bx(PX6-SV_BOSS-0.6,PX6+SV_BOSS+0.6,PY6,PLATE_Y0+1,z0,z1)
    h-=cw(HUB_R+0.6,P3A-1,P3A+0.6).translate([PX6,PY6,ZC])
    for x in SV_POSTS:
        x+=dX; z0,z1=zw(TAB_W0-2.2,W-WALL+0.1); g0,g1=zw(TAB_W0-0.2,TAB_W1+0.2)
        h+=bx(x-2.2,x+2.2,SV_Y0-3,SV_Y1+5,z0,z1)-bx(x-2.3,x+2.3,SV_Y0-0.2,PLATE_Y0+1,g0,g1)
    h+=stop6_lower()
    z0,z1=zw(-HW3-0.6,HW3+0.6); h+=bx(HOUSE_X0,HOUSE_X0+FACE,OPEN_BOT+0.7,CUT_Y0,z0,z1)
    # bulkhead with the bar's window, the walls round the pivot pockets, the floor
    z0,z1=zw(-JOG_W[1],JOG_W[1]); bulk=bx(BULK_X0,BULK_X1,FLOOR_Y[0],PLATE_Y0,z0,z1)
    z0,z1=zw(-BULK_OPEN[0],BULK_OPEN[0]); bulk-=bx(BULK_X0-1,BULK_X1+1,BULK_OPEN[1],BULK_OPEN[2],z0,z1)
    h+=bulk
    for s in (-1,1):
        z0,z1=zw(s*JOG_W[0],s*JOG_W[1]); h+=bx(BULK_X0,STEP_X[1],FLOOR_Y[0],PLATE_Y0,z0,z1)
        z0,z1=zw(s*JOG_W[0],s*P3A); h+=bx(STEP_X[0],STEP_X[1],FLOOR_Y[0],PLATE_Y0,z0,z1)
    z0,z1=zw(-P3A-0.1,P3A+0.1)
    fl=bx(HOUSE_X0+FACE-0.1,LOW_X1,FLOOR_Y[0],FLOOR_Y[1],z0,z1)
    z0,z1=zw(-INLET[2],INLET[2]); fl-=bx(INLET[0],INLET[1],FLOOR_Y[0]-1,FLOOR_Y[1]+1,z0,z1)
    h+=fl
    for s in (-1,1):                                    # the bar rests on two pads
        z0,z1=zw(s*25.0,s*30.5); h+=bx(BAR_X0+1,BAR_X0+12,FLOOR_Y[1]-0.1,BAR_Y0-0.15,z0,z1)
    # passage: partitions down to the box roof, the roof, the end wall
    for s in (-1,1):
        z0,z1=zw(s*P3A,s*P3B); h+=bx(HOUSE_X0+FACE-0.1,PASS_END[1],PASS_Y0-ROOF_T,HOUSE_Y0+3.1,z0,z1)
    z0,z1=zw(-P3B,P3B); h+=bx(DIV_X[0],LOW_X1-WALL+0.1,PASS_Y0-ROOF_T,PASS_Y0,z0,z1)
    z0,z1=zw(-P3A-0.1,P3A+0.1); h+=bx(PASS_END[0],PASS_END[1],PASS_Y0-0.1,FLOOR_Y[0]+0.1,z0,z1)
    # over the trap, beside the inlet: roof pieces (the side bays and the sensor pocket stay dry)
    for s in (-1,1):
        z0,z1=zw(s*TRAP_IN_W,s*(LOW_W-WALL+0.1)); h+=bx(HOUSE_X0+FACE-0.1,DIV_X[1],PASS_Y0-ROOF_T,PASS_Y0,z0,z1)
    # trap | box divider; road-sensor pocket walls
    z0,z1=zw(-LOW_W+WALL-0.1,LOW_W-WALL+0.1); h+=bx(DIV_X[0],DIV_X[1],LOW_Y0,PASS_Y0,z0,z1)
    z0,z1=zw(TOF_POCKET[1],TOF_POCKET[1]+1.5); h+=bx(LOW_X0+FACE-0.1,DIV_X[0]+0.1,LOW_Y0,PASS_Y0,z0,z1)
    # chin intake narrowed so it clears the sensor pocket
    for y0,y1 in GRILLE:
        z0,z1=zw(-GRILLE_W1-0.1,TOF_POCKET[1]+1.6); h+=bx(LOW_X0,LOW_X0+FACE,y0-0.1,y1+0.1,z0,z1)
        z0,z1=zw(-TOF_POCKET[1]-1.6,GRILLE_W1+0.1); h+=bx(LOW_X0,LOW_X0+FACE,y0-0.1,y1+0.1,z0,z1)
    h-=btn_cyl(3.0,DIV_X[0]-1,DIV_X[1]+1,-36.0).translate([0,0,-37.0])         # sensor cable: pocket -> box
    z0,z1=zw(-LOW_W+WALL-0.1,TOF_POCKET[1]+0.1); h+=bx(LOW_X0+FACE-0.1,HOUSE_X0+0.3,-25.7,-23.1,z0,z1)   # closed corner above the sensor mount
    z0,z1=zw(-30.2,-29.4); h+=bx(LOW_X0+FACE-0.1,LOW_X0+FACE+1.1,LOW_Y0+1,PASS_Y0,z0,z1)                  # old intake slot ends inside the mount
    h-=cw(2.2,BLK_W0-0.5,-P3A+0.6,u=-40.0,v=-10.3).translate([0,0,ZC])                     # LED and NTC wires: left pocket -> left side bay
    # road sensor: a recess for its small window over the tunnel
    t=box(-0.01,1.3,-7.0,7.0,-6.8,6.8).rotate([0,0,TOF_DOWN]).translate([LOW_X0,TOF5[1],ZC+TOF5[0]])
    h-=t
    # button box: the buttons' backs and nuts stay dry in a closed box behind the pad, open only to the electronics box
    BW=7.6
    z0,z1=zw(-BW-1.6,BW+1.6); bb=bx(LOW_X0+FACE+BTN_PAD-0.1,DIV_X[0]+0.1,LOW_Y0,PASS_Y0,z0,z1)
    z0,z1=zw(-BW,BW); bb-=bx(LOW_X0+FACE+BTN_PAD,DIV_X[0]+0.2,LOW_Y0+2.0,PASS_Y0-ROOF_T,z0,z1)
    h+=bb
    for y in BTN_Y: h-=btn_cyl(BTN_HOLE,LOW_X0-1,LOW_X0+FACE+BTN_PAD+1,y)
    z0,z1=zw(-BW,BW); h-=bx(DIV_X[0]-0.5,DIV_X[1]+0.5,LOW_Y0+2.0,PASS_Y0-ROOF_T,z0,z1)
    # side bays closed at the back (they used to open to the bay behind the box), and along the box's sides
    for s in (-1,1):
        z0,z1=zw(s*P3B,s*(LOW_W+0.1)); h+=bx(LOW_X1-WALL,HOUSE_X1-WALL+0.1,HOUSE_Y0,HOUSE_Y0+2,z0,z1)
        z0,z1=zw(s*P3A,s*P3B); h+=bx(PASS_END[0],HOUSE_X1-WALL+0.1,HOUSE_Y0,HOUSE_Y0+3.1,z0,z1)
        z0,z1=zw(s*P3A,s*P3B); h+=bx(PASS_END[0],LOW_X1+0.1,PASS_Y0-ROOF_T,HOUSE_Y0+0.1,z0,z1)
        # the box's walls stop 1 mm short of the side floors (the upper housing's inside trims them): close that slot
        z0,z1=zw(s*(LOW_W-WALL),s*(LOW_W+0.5)); h+=bx(LOW_X0+FACE,LOW_X1,PASS_Y0-0.1,HOUSE_YS+2.0,z0,z1)
    z0,z1=zw(-LOW_W-0.5,LOW_W+0.5); h+=bx(LOW_X1-WALL,LOW_X1,PASS_Y0-ROOF_T,HOUSE_Y0+0.1,z0,z1)
    z0,z1=zw(56.0,W-WALL); h-=cylV(3.6,PLATE_Y0-10.2,PLATE_Y0+0.1,*PS_OLD)^bx(-80,0,-30,30,z0,z1)
    h+=cylV(2.4,17.0,PLATE_Y0,*PS_NEW); h-=cylV(1.25,17.4,PLATE_Y0+0.1,*PS_NEW)   # short boss: above the running-light strip
    # the bar clamp's posts on the duct's side walls
    for s in (-1,1):
        z0,z1=zw(s*(P3A-4.6),s*P3A+s*0.1); h+=bx(CLAMP_X-2.5,CLAMP_X+2.5,BAR_Y1-6,BAR_Y1+4,z0,z1)
        h-=cylV(1.25,BAR_Y1-5,BAR_Y1+4.1,CLAMP_X,s*(P3A-2.3))
    return h
CLAMP_X=BAR_X1+2.4
PS_OLD=(-51.0,61.2); PS_NEW=(-53.0,62.6)              # right-front plate screw: the servo (now 4 mm further forward) passes the old boss
PLATE_SCREWS9=[PS_NEW if (x,w)==PS_OLD else (x,w) for x,w in PLATE_SCREWS]
def bar_clamp():   # presses the bar's fins forward onto the bulkhead's gasket
    z0,z1=zw(-P3A+0.2,P3A-0.2)
    c=bx(CLAMP_X-2.5,CLAMP_X+2.5,BAR_Y1+4.1,BAR_Y1+7.1,z0,z1)
    for w in (-20,0,20): c+=bx(BAR_X1,CLAMP_X+2.5,BAR_Y0+2,BAR_Y1+7.1,ZC+w-3,ZC+w+3)
    for s in (-1,1): c-=cylV(1.7,BAR_Y1+3,BAR_Y1+8,CLAMP_X,s*(P3A-2.3))
    return c
def top_plate9():
    p=top_plate8()
    # move the pivot tongues and the stop to the new pivot
    z0,z1=zw(BLK_W0-0.6,-P3A+0.6); p-=bx(PX3-SEAT_R-0.6,PX3+SEAT_R+0.6,PY3-1,PLATE_Y0,z0,z1)
    z0,z1=zw(P3A-0.6,P3B+0.6); p-=bx(PX3-SV_BOSS-1.2,PX3+SV_BOSS+1.2,PY3-1,PLATE_Y0,z0,z1)
    z0,z1=zw(STOP_W0-0.1,STOP_W1+0.1); p-=bx(PX3+STOP_U0-0.1,PX3+STOP_U1+0.1,PY3+STOP_V-0.1,PLATE_Y0,z0,z1)
    for x in SV_POSTS:
        z0,z1=zw(TAB_W0-0.6,TAB_W1+0.6); p-=bx(x-2.6,x+2.6,SV_Y1-1,PLATE_Y0,z0,z1)
    dX=PX6-PX3
    z0,z1=zw(BRG_W0-0.05,-P3A-0.05)
    p+=bx(PX6-SEAT_R+0.05,PX6+SEAT_R-0.05,PY6,PLATE_Y0+0.1,z0,z1)-cw(SEAT_R+0.05,BRG_W0-1,-P3A+1).translate([PX6,PY6,ZC])
    z0,z1=zw(BLK_W0+0.05,BRG_W0-0.15)
    p+=bx(PX6-WIRE_R+0.1,PX6+WIRE_R-0.1,PY6,PLATE_Y0+0.1,z0,z1)-cw(WIRE_R+0.2,BLK_W0-1,BRG_W0+1).translate([PX6,PY6,ZC])
    z0,z1=zw(P3A+0.05,P3B-0.05)
    p+=bx(PX6-SV_BOSS-0.5,PX6+SV_BOSS+0.5,PY6,PLATE_Y0+0.1,z0,z1)-cw(SV_BOSS+0.7,P3A-1,P3B+1).translate([PX6,PY6,ZC])
    for x in SV_POSTS:
        x+=dX; z0,z1=zw(TAB_W0-0.1,TAB_W1+0.1); p+=bx(x-2.1,x+2.1,SV_Y1+0.05,PLATE_Y0+0.1,z0,z1)
    p+=stop6_upper()
    p+=cylV(3.5,PLATE_Y0,HOUSE_Y1,*PS_OLD)^bx(HOUSE_X0,HOUSE_X1,PLATE_Y0,HOUSE_Y1,ZC-HOUSE_W,ZC+HOUSE_W)
    p-=cylV(1.7,PLATE_Y0-1,HOUSE_Y1+1,*PS_NEW)
    p-=mf.Manifold.cylinder(1.6,1.7,3.3,48).rotate([-90,0,0]).translate([PS_NEW[0],HOUSE_Y1-1.55,ZC+PS_NEW[1]])
    for x,w in TOP_SCREWS: p+=cylV(6,HOUSE_Y1-6,PLATE_Y0+0.1,x,w); p-=cylV(2.8,HOUSE_Y1-5.8,HOUSE_Y1+1,x,w)   # bosses whole again
    return p
GASKET_T=1.5
DRAIN_W=(-27.0,38.0)
def lid9():   # flat lid under a full gasket sheet; drain slots under the trap
    l=bx(LOW_X0,LOW_X1,LOW_Y0-GASKET_T-2.5,LOW_Y0-GASKET_T,ZC-LOW_W,ZC+LOW_W)
    for x,w in LID_POSTS: l-=cylV(1.7,LOW_Y0-6,LOW_Y0,x,w)
    for k in range(4):
        x=LOW_X0+FACE+3.0+k*3.6
        for w0,w1 in ((DRAIN_W[0],-9.6),(9.6,DRAIN_W[1])):
            z0,z1=zw(w0,w1); l-=bx(x,x+1.8,LOW_Y0-6,LOW_Y0,z0,z1)
    return l
def gasket9():   # TPU sheet over the whole underside: it seals under every wall; windows over the drains
    g=bx(LOW_X0,LOW_X1,LOW_Y0-GASKET_T,LOW_Y0,ZC-LOW_W,ZC+LOW_W)
    for w0,w1 in ((TOF_POCKET[1]+1.9,-9.6),(9.6,LOW_W-WALL-0.4)):
        z0,z1=zw(w0,w1); g-=bx(LOW_X0+FACE+0.4,DIV_X[0]-0.4,LOW_Y0-2,LOW_Y0+1,z0,z1)
    for x,w in LID_POSTS: g-=cylV(1.9,LOW_Y0-3,LOW_Y0+1,x,w)
    return g
def tape_frame():   # the window's foam tape, as a ring round its edge
    o=poly(window_outline()); r=o-o.offset(-TAPE_W,mf.JoinType.Miter)
    return mf.Manifold.extrude(r,TAPE).rotate([0,-90,0]).translate([HOUSE_X0,0,ZC])
def tof_window():   # 1 mm clear polycarbonate over the road sensor, glued into its recess
    return box(0.15,1.3,-7.0,7.0,-6.8,6.8).rotate([0,0,TOF_DOWN]).translate([LOW_X0,TOF5[1],ZC+TOF5[0]])   # glued: fills its recess
