# Lamp v5.4 + handle v13: hard stops for the head, buttons in the chin, a USB-C port in the handle.
# - Stops: in a drop the head's weight wants to keep turning, and before this only the servo's small gears
#   stopped it. A lug on the head's left side now meets a stop just past the firmware's ±10° (contact at
#   about ±12°): the lower stop is part of the housing, the upper one a finger of the top plate, so the
#   head still drops in from above.
# - Buttons: two sealed 8 mm push buttons, one above the other in the middle of the chin (+ aim up,
#   - aim down), so either hand reaches them. They sit 2.5 mm deep in pockets, so a knock or a drop can't
#   press them; the firmware also wants a deliberate half-second press with the wheel standing still.
#   The air intake moves to either side of them, and a pad behind the face gives their threads something
#   to clamp.
# - USB: an IP67 USB-C panel socket (16 mm cutout, the common size) in the outer face of the right leg,
#   near the top, where there's air behind it for the socket's body. Its two wires run down a channel
#   inside the leg, out through the handle's lower block, along a groove in the web's top, and up through
#   a hole in the housing's side floor: never outside the wheel.
import numpy as np, trimesh, manifold3d as mf
exec(open('build20.py').read())

# ---- head stops ----
LUG_U0,LUG_U1,LUG_V=11.0,16.0,2.5                 # lug on the head's left face, behind the axis
LUG_W0,LUG_W1=-HW3-2.6,-HW3+0.1
STOP_A=11.8                                        # the lug's corner meets the stop at about ±12°; firmware stops at 10, trim at ±1.5
STOP_V=LUG_U1*np.sin(np.radians(STOP_A))+LUG_V*np.cos(np.radians(STOP_A))
STOP_U0,STOP_U1=9.5,18.0; STOP_W0,STOP_W1=-P3A+0.05,-HW3-0.5
def head8():
    return head7()+box(LUG_U0,LUG_U1,-LUG_V,LUG_V,LUG_W0,LUG_W1)
def stop_lower():
    z0,z1=zw(STOP_W0-0.1,STOP_W1); return bx(PX3+STOP_U0,PX3+STOP_U1,HOUSE_Y0+3,PY3-STOP_V,z0,z1)
def stop_upper():
    z0,z1=zw(STOP_W0,STOP_W1); return bx(PX3+STOP_U0,PX3+STOP_U1,PY3+STOP_V,PLATE_Y0+0.1,z0,z1)

# ---- chin buttons ----
BTN_Y=(-30.5,-42.5)                                # + above, - below, on the centre line
BTN_HOLE=4.1; BTN_POCKET_R,BTN_POCKET_D=6.5,2.5; BTN_PAD=3.5
GRILLE_W0,GRILLE_W1=9.5,30.0                       # intake either side of the buttons (the road sensor is at -36)
def btn_cyl(r,x0,x1,y): return mf.Manifold.cylinder(x1-x0,r,r,48).rotate([0,90,0]).translate([x0,y,ZC])
def housing8():
    h=housing7()+stop_lower()
    for y0,y1 in GRILLE: h+=bx(LOW_X0,LOW_X0+FACE,y0-0.1,y1+0.1,ZC-GRILLE_W,ZC+GRILLE_W)    # close v5.1's grille
    for y0,y1 in GRILLE:
        for s in (-1,1):
            z0,z1=zw(s*GRILLE_W0,s*GRILLE_W1); h-=bx(LOW_X0-1,LOW_X0+FACE+1,y0,y1,z0,z1)
    h+=bx(LOW_X0+FACE-0.1,LOW_X0+FACE+BTN_PAD,LOW_Y0+1.5,LIP_Y-FACE-0.5,ZC-8.5,ZC+8.5)         # pad behind the buttons
    for y in BTN_Y:
        h-=btn_cyl(BTN_POCKET_R,LOW_X0-1,LOW_X0+BTN_POCKET_D,y)+btn_cyl(BTN_HOLE,LOW_X0-1,LOW_X0+FACE+BTN_PAD+1,y)
    for s in (-1,1): h-=cylV(USB_FLOOR[2],HOUSE_YS-1,HOUSE_YS+3,USB_FLOOR[0],s*USB_FLOOR[1])   # USB wires in (either handle)
    return h
def top_plate8(): return top_plate7()+stop_upper()
def buttons8():   # the two buttons as fitted (head 10 mm, body 8 mm x 18 mm), for checks and renders
    return mf.Manifold.batch_boolean([btn_cyl(5.0,LOW_X0+BTN_POCKET_D-1.5,LOW_X0+BTN_POCKET_D,y)+btn_cyl(4.0,LOW_X0+BTN_POCKET_D-0.1,LOW_X0+BTN_POCKET_D+18,y) for y in BTN_Y],mf.OpType.Add)

# ---- USB-C in the handle (right leg) ----
USB_XY=(-59.0,50.0); USB_R=8.1; USB_FACE=97.5      # 16.2 mm hole in the leg's outer face
USB_BOSS=(69.0,11.0); USB_CAV=(71.0,9.2)           # behind the leg: room for the socket's body (up to 26.5 mm)
USB_PATH=[(-58.5,44.0,74.5),(-59.0,44.0,89.0),(-41.0,31.0,89.5),(-37.0,16.0,90.0),(-18.0,4.0,89.0),
          (-19.0,-3.0,89.5),(-15.0,-11.0,85.0),(-7.0,-19.5,76.0),(-7.0,-21.4,69.0)]     # through the leg's thickest part
CH_R=2.5                                           # 5 mm: the socket's two power wires, 24 AWG
GROOVE=[((-7.0,68.6),(-16.8,68.6)),((-16.8,68.6),(-16.8,62.8))]; GROOVE_W,GROOVE_Y0=3.4,WEB_Y1-2.2
USB_FLOOR=(-16.8,62.8,2.4)
def sph(p,r): return mf.Manifold.sphere(r,24).translate([p[0],p[1],ZC+p[2]])
def usb_channel():
    return mf.Manifold.batch_boolean([hull(sph(a,CH_R),sph(b,CH_R)) for a,b in zip(USB_PATH,USB_PATH[1:])],mf.OpType.Add)
def usb_groove():
    g=[]
    for (x0,w0),(x1,w1) in GROOVE:
        g.append(bx(min(x0,x1)-GROOVE_W/2,max(x0,x1)+GROOVE_W/2,GROOVE_Y0,WEB_Y1+5,ZC+min(w0,w1)-GROOVE_W/2,ZC+max(w0,w1)+GROOVE_W/2))
    return mf.Manifold.batch_boolean(g,mf.OpType.Add)
def usb_socket():  # IP67 USB-C panel socket as fitted: flange 22 x 2.5 mm, body 16 x 26 mm
    x,y=USB_XY
    return cw(11.0,USB_FACE,USB_FACE+2.5,u=x,v=y).translate([0,0,ZC])+cw(7.9,USB_FACE-26,USB_FACE,u=x,v=y).translate([0,0,ZC])
def handle13(side=1):
    h=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds3()
    x,y=USB_XY
    boss=cw(USB_BOSS[1],USB_BOSS[0],USB_FACE-8,u=x,v=y).translate([0,0,ZC])
    h=h+boss
    h-=cw(USB_R,USB_CAV[0],USB_FACE+1,u=x,v=y).translate([0,0,ZC])+cw(USB_CAV[1],USB_CAV[0],USB_FACE-12,u=x,v=y).translate([0,0,ZC])
    h-=usb_channel()+usb_groove()
    if side<0: h=h.mirror([0,0,1]).translate([0,0,2*ZC])
    return h
