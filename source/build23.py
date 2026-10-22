# Lamp v6.1: v6 with fewer parts. "The best part is no part."
# - No road sensor: dirty most of the time down there anyway. The gyro and accelerometer still cancel braking,
#   accelerating and bumps and follow long hills partly. Its window, pocket and cable hole go too, and the chin
#   gets its full air intake back.
# - No bar clamp: three fingers on the top plate hold the LED bar against the bulkhead as the plate goes on.
# - No diffusers: the running-light strips shine through their slots and the main window; sand the window's
#   inside over the slots to spread the light.
# - No TPU gasket: the window's foam tape, laid on the electronics box's wall edges, seals the lid.
import numpy as np, trimesh, manifold3d as mf
exec(open('build22.py').read())

LID_TAPE=0.5
DRAIN10=((-LOW_W+WALL+0.6,-9.6),(9.6,LOW_W-WALL-0.6))
def housing10():
    W=HOUSE_W; h=housing9()
    # bar clamp's posts off
    for s in (-1,1):
        z0,z1=zw(s*(P3A-4.65),s*(P3A-0.05)); h-=bx(CLAMP_X-2.6,CLAMP_X+2.6,BAR_Y1-6.1,BAR_Y1+4.1,z0,z1)
    # road sensor out: chin face whole again, its mount, slot, pocket wall and cable hole gone
    z0,z1=zw(-LOW_W+0.6,-9.0); h+=bx(LOW_X0,LOW_X0+FACE,LOW_Y0+0.5,LIP_Y-0.6,z0,z1)
    z0,z1=zw(-LOW_W+WALL,-9.25); h-=bx(LOW_X0+FACE,DIV_X[0],LOW_Y0-1,PASS_Y0-ROOF_T,z0,z1)
    h+=btn_cyl(3.1,DIV_X[0]-0.05,DIV_X[1]+0.05,-36.0).translate([0,0,-37.0])
    x,w=LID_POSTS[0]; h+=cylV(4,LOW_Y0,LOW_Y0+10,x,w); h-=cylV(1.25,LOW_Y0-1,LOW_Y0+9,x,w)
    for y0,y1 in GRILLE:                                  # full intake both sides
        for s in (-1,1):
            z0,z1=zw(s*GRILLE_W0,s*GRILLE_W1); h-=bx(LOW_X0-1,LOW_X0+FACE+1,y0,y1,z0,z1)
    # running-light slots without diffusers: the diffusers' rebates filled
    for s in (-1,1): h+=drl_prism(s,grow=1.2,x0=HOUSE_X0,x1=HOUSE_X0+1.0)-drl_prism(s)
    return h
FING_W=9.0
def top_plate10():   # fingers behind the fins hold the bar forward
    p=top_plate9()
    for w in (-20.0,0.0,20.0):
        z0,z1=ZC+w-FING_W/2,ZC+w+FING_W/2
        p+=hull(bx(BAR_X1,BAR_X1+3.0,BAR_Y0+6,PLATE_Y0+0.1,z0,z1),bx(BAR_X1+1.6,BAR_X1+3.0,BAR_Y0+2,BAR_Y0+2.1,z0,z1))
    return p
def lid10():   # flat lid on foam tape; drain slots under the trap
    l=bx(LOW_X0,LOW_X1,LOW_Y0-LID_TAPE-2.5,LOW_Y0-LID_TAPE,ZC-LOW_W,ZC+LOW_W)
    for x,w in LID_POSTS: l-=cylV(1.7,LOW_Y0-6,LOW_Y0,x,w)
    for k in range(4):
        x=LOW_X0+FACE+3.0+k*3.6
        for w0,w1 in DRAIN10:
            z0,z1=zw(w0,w1); l-=bx(x,x+1.8,LOW_Y0-6,LOW_Y0,z0,z1)
    return l
def lid_tape():   # foam tape under the electronics box's walls: divider, both sides, back
    t=bx(DIV_X[0],LOW_X1,LOW_Y0-LID_TAPE,LOW_Y0,ZC-LOW_W,ZC+LOW_W)
    t-=bx(DIV_X[1],LOW_X1-WALL,LOW_Y0-1,LOW_Y0+1,ZC-LOW_W+WALL,ZC+LOW_W-WALL)
    for x,w in LID_POSTS: t-=cylV(1.9,LOW_Y0-2,LOW_Y0+1,x,w)
    return t
