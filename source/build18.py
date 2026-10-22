# Lamp v5.1: lamp v5 dressed for the Master. A clear 1.5 mm polycarbonate window sits flush in the stock
# opening, just behind the cover's front edge, over a black face: the lamp reads as part of the wheel,
# and rain and grit stay off the optics. The running lights become two angled light lines that follow the
# Master's faceted lines. With the front sealed, cooling air comes in through a chin vent in the
# electronics box between the shells, rises under the head, passes the heat sink and leaves at the back.
# Drops: the window, the face and the chin all sit behind the handle grip, the cover's tip and the shells,
# so when the wheel falls forward or onto a side, those touch the ground first (check18 measures it).
import numpy as np, trimesh, manifold3d as mf
exec(open('build17.py').read())

VISOR3=0.0                                 # no visor: the head front swings forward 2 mm at +10°, the window is 3 mm away
WIN_T,TAPE=1.5,0.5
WIN_X1=HOUSE_X0-TAPE; WIN_X0=WIN_X1-WIN_T
WIN_Y0,WIN_Y1=OPEN_BOT+0.5,OPEN_TOP-0.5; WIN_W=OPEN_W/2-0.5; WIN_CH=4.0
def window_outline():   # (w, y) corners, chamfered like the cover's facets
    c=WIN_CH
    return [(-WIN_W+c,WIN_Y0),(WIN_W-c,WIN_Y0),(WIN_W,WIN_Y0+c),(WIN_W,WIN_Y1-c),(WIN_W-c,WIN_Y1),(-WIN_W+c,WIN_Y1),(-WIN_W,WIN_Y1-c),(-WIN_W,WIN_Y0+c)]
def window():
    # 2D (w, y) extruded along -X: rotate([0,-90,0]) sends 2D x -> Z (across) and the extrusion -> -X
    return mf.Manifold.extrude(poly(window_outline()),WIN_T).rotate([0,-90,0]).translate([WIN_X1,0,ZC])
# angled running-light slots (w, y), one per side, mirrored
DRL_SLOT=[(41.0,20.5),(62.5,15.0),(62.5,11.0),(41.0,16.5)]
TOF5=(-36.0,-38.0)
GRILLE_W=24.0; GRILLE=[(-46.0+k*3.6,-46.0+k*3.6+2.2) for k in range(6)]
def drl_prism(s,grow=0.0,x0=None,x1=None):
    cs=poly([(w*s,y) for w,y in DRL_SLOT])
    if grow: cs=cs.offset(grow,mf.JoinType.Miter)
    x0=HOUSE_X0-1 if x0 is None else x0; x1=HOUSE_X0+FACE+1 if x1 is None else x1
    return mf.Manifold.extrude(cs,x1-x0).rotate([0,-90,0]).translate([x1,0,ZC])
def housing5():
    h=housing3()
    # undo v5's square running-light windows and the old sensor openings, then cut the new face
    for s in (-1,1):
        z0,z1=zw(s*DRL3_W0,s*DRL3_W1); r0,r1=zw(s*(DRL3_W0-2),s*(DRL3_W1+2))
        h+=bx(HOUSE_X0,HOUSE_X0+FACE,DRL2_Y0-2,DRL2_Y1+2,r0,r1)
    h+=bx(LOW_X0,LOW_X0+FACE,LOW_Y0+1,LIP_Y-0.5,ZC-LOW_W+WALL,ZC+LOW_W-WALL)           # rebuild the chin face
    h+=bx(HOUSE_X0,HOUSE_X0+FACE,LDR3[1]-4,LDR3[1]+4,ZC+LDR3[0]-4,ZC+LDR3[0]+4)
    h-=bx(HOUSE_X0-1,HOUSE_X0+FACE+1,OPEN_BOT+0.8,HOUSE_Y1-WALL-0.5,ZC-HW3-0.5,ZC+HW3+0.5)
    for s in (-1,1):
        h-=drl_prism(s)                                                           # light line
        h-=drl_prism(s,grow=1.2,x0=HOUSE_X0-1,x1=HOUSE_X0+1.0)                    # rebate for its diffuser
    h-=mf.Manifold.cylinder(FACE+2,2.65,2.65,24).rotate([0,90,0]).translate([HOUSE_X0-1,22.0,ZC+50.0])   # LDR, behind the window
    # chin: vent slots (air in) and the road sensor's tunnel
    for y0,y1 in GRILLE: h-=bx(LOW_X0-1,LOW_X0+FACE+1,y0,y1,ZC-GRILLE_W,ZC+GRILLE_W)
    t=box(-6,4,-4.5,4.5,-5.5,5.5).rotate([0,0,180+TOF_DOWN]).translate([LOW_X0+1,TOF5[1],ZC+TOF5[0]])
    m=box(-12,0,-12,12,-9,9).rotate([0,0,180+TOF_DOWN]).translate([LOW_X0+FACE,TOF5[1],ZC+TOF5[0]])
    sl=box(-7.2,-3.8,-9.3,9.3,-9.3,9.3).rotate([0,0,180+TOF_DOWN]).translate([LOW_X0+FACE,TOF5[1],ZC+TOF5[0]])
    outer=bx(LOW_X0,LOW_X1,LOW_Y0,LIP_Y,ZC-LOW_W,ZC+LOW_W)
    h=(h+(m^outer))-t-sl
    # baffle: fresh air rises under the front half of the head, warm air drops behind it to the back slots
    h+=bx(PX3-1,PX3+1,LOW_Y0+0.1,HOUSE_Y0-0.6,ZC-LOW_W+WALL-0.5,ZC+LOW_W-WALL+0.5)
    for s in (-1,1):   # wires pass the baffle at its bottom corners
        z0,z1=zw(s*(LOW_W-WALL-9),s*(LOW_W-WALL-1)); h-=bx(PX3-2,PX3+2,LOW_Y0-1,LOW_Y0+6,z0,z1)
    return h
def diffuser5(s):
    return drl_prism(s,grow=1.05,x0=HOUSE_X0,x1=HOUSE_X0+1.0)
