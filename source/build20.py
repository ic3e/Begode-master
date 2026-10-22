# Lamp v5.3: a real bearing for the head's pivot. A printed pin turning in a printed slot works on load
# (friction is a few % of the servo's torque) but binds if the print comes out tight, grinds with road dust
# from the chin vent, and wears into play that makes the beam shiver over bumps. A sealed 6800-2RS
# (10 x 19 x 5) presses onto the 10 mm pin, which now has a shoulder for the inner race. The outer race
# drops into a seat in a 6 mm bearing block, behind a lip that only touches the outer race, and the
# top plate's tongue holds it down.
# Also: the wire hole ran off the pin's axis (aimed at the stars) and broke out of the pin's side as an
# open groove. It now runs on the axis through the pin and turns towards the stars inside the head.
import numpy as np, trimesh, manifold3d as mf
exec(open('build19.py').read())

BRG_ID,BRG_OD,BRG_B=10.0,19.0,5.0
BRG_W1=-P3A; BRG_W0=BRG_W1-BRG_B                 # inner face of the left wall to 5 mm outboard: -41.6..-36.6
SEAT_R=BRG_OD/2+0.2; LIP_T=0.9; LIP_R=8.0          # lip clears the inner race and its seal
BLK_W0=BRG_W0-0.1-LIP_T
WIRE_R=4.0                                          # wires leave the pin's end through the lip
def head7():
    h=head3()-cw(PIN3_R+0.5,-HW3-BOSS3-6,-HW3-BOSS3)                 # v5.2's pin off: the new one would sit on its surface
    h+=cw(BORE3_R+0.1,-HW3-BOSS3-0.5,-HW3+2,u=HU0_3+1.5+TIR2_H+STAR2/2)  # close the off-axis hole in the hub
    h+=cw(BRG_ID/2+1.0,BRG_W1,-HW3-BOSS3+0.1)                         # shoulder for the inner race
    h+=cw(BRG_ID/2,BRG_W0,BRG_W1+0.1)                                  # the pin, as long as the bearing
    h-=cw(BORE3_R,BRG_W0-1,-HW3+3)                                     # wire hole on the axis, meeting the old one to the stars
    return h
def bearing7():
    return cw(BRG_OD/2,BRG_W0,BRG_W1)-cw(BRG_ID/2,BRG_W0-1,BRG_W1+1)
def housing7():
    h=housing6()
    z0,z1=zw(BLK_W0,-P3A); h+=bx(PX3-12.5,PX3+12.5,HOUSE_Y0+3,PLATE_Y0,z0,z1)
    z0,z1=zw(BRG_W0-0.1,-P3A+0.1)
    h-=cw(SEAT_R,BRG_W0-0.1,-P3A+0.1).translate([PX3,PY3,ZC])+bx(PX3-SEAT_R,PX3+SEAT_R,PY3,PLATE_Y0+1,z0,z1)
    z0,z1=zw(BLK_W0-1,BRG_W0)
    h-=cw(WIRE_R,BLK_W0-1,BRG_W0).translate([PX3,PY3,ZC])+bx(PX3-WIRE_R,PX3+WIRE_R,PY3,PLATE_Y0+1,z0,z1)
    return h
def top_plate7():
    p=top_plate6()
    z0,z1=zw(-P3B-BEAR_T-0.5,-P3A+0.5); p-=bx(PX3-PIN3_R-0.5,PX3+PIN3_R+0.5,PY3-1,PLATE_Y0,z0,z1)   # v5.2's pin tongue
    z0,z1=zw(BRG_W0-0.05,-P3A-0.05)
    p+=bx(PX3-SEAT_R+0.05,PX3+SEAT_R-0.05,PY3,PLATE_Y0+0.1,z0,z1)-cw(SEAT_R+0.05,BRG_W0-1,-P3A+1).translate([PX3,PY3,ZC])
    z0,z1=zw(BLK_W0+0.05,BRG_W0-0.15)
    p+=bx(PX3-WIRE_R+0.1,PX3+WIRE_R-0.1,PY3,PLATE_Y0+0.1,z0,z1)-cw(WIRE_R+0.2,BLK_W0-1,BRG_W0+1).translate([PX3,PY3,ZC])
    return p
