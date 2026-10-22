# Lamp v5.2: v5.1 made possible to put together. In v5.1 the housing was one closed print, and the head
# (72 mm across its bosses) had no way in: the electronics box and the baffle block it from below, the
# light opening is 68 mm wide, the pivot pin and the servo shaft sat in closed round holes in the
# partitions, and the servo's tab screws pointed into a 6 mm gap no screwdriver reaches.
# Now the housing is open on top and a 3 mm top plate closes it. Head and servo are joined on the bench
# (horn screwed to the head, spline pressed into the horn) and lowered in from above as one unit: the pin
# into a slot in the left partition (thickened into a 4 mm bearing), the servo shaft into a slot in the
# right one, the servo's tabs into grooves in its two posts. The plate's tongues fill those slots and
# grooves, so the pin and the servo can't lift out. The plate takes the cover's M4 inserts and is held
# by 4 countersunk M3 screws, flush under the cover.
import numpy as np, trimesh, manifold3d as mf
exec(open('build18.py').read())

PLATE_T=3.0; PLATE_Y0=HOUSE_Y1-PLATE_T
SV_CU=SV_L/2-SV_SHAFT
SV_POSTS=[PX3+SV_CU+du for du in (-(SV_TAB/2-2.4),SV_TAB/2-2.4)]     # under the tab holes
TAB_W0,TAB_W1=SV_TOP3+SV_TAB_DOWN-SV_TAB_T,SV_TOP3+SV_TAB_DOWN       # the tabs, across
SV_Y0,SV_Y1=PY3-SV_W/2,PY3+SV_W/2
BEAR_T=2.0                                                            # left partition thickened to a 4 mm bearing
PLATE_SCREWS=[(x,s*61.2) for x in (-51.0,-18.0) for s in (-1,1)]     # clear of the servo, the tabs and the light strips
def housing6():
    W=HOUSE_W; h=housing5()
    h-=bx(HOUSE_X0-1,HOUSE_X1+1,PLATE_Y0,HOUSE_Y1+1,ZC-W-1,ZC+W+1)                    # open top
    for x,w in TOP_SCREWS: h-=cylV(6.3,HOUSE_Y1-6.5,PLATE_Y0+0.1,x,w)                 # the M4 bosses move to the plate
    for x in SV_POSTS:                                                                 # v5's posts (screws along w)
        z0,z1=zw(TAB_W1-0.1,W-WALL); h-=bx(x-2.3,x+2.3,PY3-3.1,PY3+3.1,z0,z1)
    z0,z1=zw(-P3B-BEAR_T,-P3B); h+=bx(PX3-9,PX3+9,HOUSE_Y0+3,PLATE_Y0,z0,z1)
    z0,z1=zw(-P3B-BEAR_T-1,-P3A+1)
    h-=cw(PIN3_R+0.25,-P3B-BEAR_T-1,-P3A+1).translate([PX3,PY3,ZC])+bx(PX3-PIN3_R-0.25,PX3+PIN3_R+0.25,PY3,PLATE_Y0+1,z0,z1)
    z0,z1=zw(P3A-1,P3B+1); h-=bx(PX3-SV_BOSS-0.6,PX3+SV_BOSS+0.6,PY3,PLATE_Y0+1,z0,z1)  # servo shaft slot (the round hole is already there)
    for x in SV_POSTS:
        z0,z1=zw(TAB_W0-2.2,W-WALL+0.1); g0,g1=zw(TAB_W0-0.2,TAB_W1+0.2)
        h+=bx(x-2.2,x+2.2,SV_Y0-3,SV_Y1+5,z0,z1)-bx(x-2.3,x+2.3,SV_Y0-0.2,PLATE_Y0+1,g0,g1)
    for x,w in PLATE_SCREWS:
        h+=cylV(3.5,PLATE_Y0-10,PLATE_Y0,x,w); h-=cylV(1.25,PLATE_Y0-9.5,PLATE_Y0+0.1,x,w)
    return h
def top_plate6():
    W=HOUSE_W; p=bx(HOUSE_X0,HOUSE_X1,PLATE_Y0,HOUSE_Y1,ZC-W,ZC+W)
    for x,w in TOP_SCREWS: p+=cylV(6,HOUSE_Y1-6,PLATE_Y0+0.1,x,w)
    # tongues: fill the slots and grooves above the pin, the servo shaft and the tabs
    z0,z1=zw(-P3B-BEAR_T+0.05,-P3A-0.05)
    p+=bx(PX3-PIN3_R-0.2,PX3+PIN3_R+0.2,PY3,PLATE_Y0+0.1,z0,z1)-cw(PIN3_R+0.3,-P3B-BEAR_T-1,-P3A+1).translate([PX3,PY3,ZC])
    z0,z1=zw(P3A+0.05,P3B-0.05)
    p+=bx(PX3-SV_BOSS-0.5,PX3+SV_BOSS+0.5,PY3,PLATE_Y0+0.1,z0,z1)-cw(SV_BOSS+0.7,P3A-1,P3B+1).translate([PX3,PY3,ZC])
    for x in SV_POSTS:
        z0,z1=zw(TAB_W0-0.1,TAB_W1+0.1); p+=bx(x-2.1,x+2.1,SV_Y1+0.05,PLATE_Y0+0.1,z0,z1)
    for x,w in TOP_SCREWS: p-=cylV(2.8,HOUSE_Y1-5.8,HOUSE_Y1+1,x,w)
    for x,w in PLATE_SCREWS:   # countersunk M3, heads flush under the cover
        p-=cylV(1.7,PLATE_Y0-1,HOUSE_Y1+1,x,w)
        p-=mf.Manifold.cylinder(1.6,1.7,3.3,48).rotate([-90,0,0]).translate([x,HOUSE_Y1-1.55,ZC+w])
    return p
def horn6():   # the MG90S single-arm horn, in its recess on the head's right boss (for the renders)
    return hull(cw(3.6,HW3+BOSS3-2.0,HW3+BOSS3,seg=32),cw(2.2,HW3+BOSS3-2.0,HW3+BOSS3,u=12,seg=32))
