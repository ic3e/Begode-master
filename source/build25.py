# Handle v15: the USB-C port flush in the leg, no bump. The IP67 panel socket's body is 26 mm long behind its
# flange and the leg is 18 mm thick there, so v13/v14 carried it in a round boss sticking out into the handle's
# opening. v15 takes a bare USB-C receptacle instead (the 8.9 x 3.3 mm shell every USB-C socket has, about
# 7.4 mm deep, with CC1/CC2 brought out for the 22 k resistors). It sits in a slot behind a shallow recess in
# the leg's flat outer face, where the old socket was; the recess takes the cable plug's moulding and a silicone
# dust plug. It goes in from the leg's inner face through a pocket that is then filled with epoxy, which also
# seals the receptacle's back. The lamp is unchanged (v6.2).
exec(open('build24.py').read())
LEG_DIR=np.array([0.69,-0.72,0.0]); LEG_DIR/=np.linalg.norm(LEG_DIR)   # along the leg, in the handle's plane
USB_C=(-59.0,50.0)                     # where the old socket's axis met the leg's outer face (w = USB_FACE)
REC_SLOT=(9.2,3.6,7.6)                 # the receptacle's slot: shell 8.94 x 3.26, about 7.4 deep
REC_RECESS=(12.8,7.0,1.4)              # cable plugs' mouldings are up to 12.35 x 6.5; the receptacle's mouth sits at its floor
REC_POCKET=(13.0,8.0)                  # behind it, room for the solder tabs, the two resistors and the wires
def usb_stadium(L,D,w0,w1,grow=0.0):   # rounded slot, long side along the leg, axis along w
    r=D/2+grow; L=L+2*grow
    a=hull(*[mf.Manifold.cylinder(w1-w0,r,r,48).translate([s*(L/2-r),0,0]) for s in (-1,1)])
    return a.rotate([0,0,np.degrees(np.arctan2(LEG_DIR[1],LEG_DIR[0]))]).translate([USB_C[0],USB_C[1],ZC+w0])
REC_W1=USB_FACE-REC_RECESS[2]; REC_W0=REC_W1-REC_SLOT[2]   # the receptacle's mouth and its back
def usb_pocket():
    return (usb_stadium(REC_RECESS[0],REC_RECESS[1],REC_W1,USB_FACE+1.0)+usb_stadium(REC_SLOT[0],REC_SLOT[1],REC_W0-0.01,REC_W1+0.01)
            +usb_stadium(REC_POCKET[0],REC_POCKET[1],60.0,REC_W0))                          # the pocket opens on the leg's inner face
def usb_receptacle():   # the receptacle as fitted, for the renders
    return usb_stadium(8.94,3.26,REC_W0,REC_W1)-usb_stadium(8.34,2.66,REC_W0+1.0,REC_W1+0.1)+usb_stadium(6.7,0.7,REC_W0+1.0,REC_W1-0.6)
# the wire channel now starts in the pocket's lower end and joins v14's path down the leg
USB_PATH=[(-57.0,47.9,84.0),(-52.0,43.0,89.0)]+USB_PATH[2:]
def handle15(side=1):
    h=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds4()
    h-=usb_pocket()+usb_channel()+usb_groove()
    h-=bx(-9.5,-4.5,WEB_Y0-0.2,-18.9,ZC+66.0,ZC+67.6)   # the channel's mouth against the block (as v14)
    if side<0: h=h.mirror([0,0,1]).translate([0,0,2*ZC])
    return h

# ---- handle v16: the port on the leg's inner face, pressed in from inside ----
# Facing into the handle's opening, the port is out of harm's way when the wheel falls on its side: the leg's
# outer face takes the ground. The receptacle presses into a tight slot from the inside, its wires and the two
# 22 k resistors going ahead of it through the slot into a small chamber and the channel. Straight inward is the
# only way a plug fits: tilted square to the slanted face, the cable runs into the cover.
USB16_C=(-59.0,50.0)
SLOT16=(9.0,3.3,7.6)                    # press fit on the 8.94 x 3.26 shell (printed holes come out a little small)
CHAMBER16=(10.4,5.0,4.0)                # behind it: solder tabs, resistors in heat-shrink, wires
WELL16=(13.6,7.8)                       # the plug's moulding (12.35 x 6.5 at most) sits in this well
def _stadium16(L,D,w0,w1): 
    r=D/2; a=hull(*[mf.Manifold.cylinder(w1-w0,r,r,48).translate([s*(L/2-r),0,0]) for s in (-1,1)])
    return a.rotate([0,0,np.degrees(np.arctan2(LEG_DIR[1],LEG_DIR[0]))]).translate([USB16_C[0],USB16_C[1],ZC+w0])
def _mouth16():   # the deepest point of the slanted inner face under the well: the mouth sits level with it
    t=trimesh.load(U+'euc_master_front_handle.stl'); ws=[]
    for a in np.linspace(-WELL16[0]/2+0.5,WELL16[0]/2-0.5,9):
        for b in np.linspace(-WELL16[1]/2+0.5,WELL16[1]/2-0.5,5):
            q=np.array([USB16_C[0],USB16_C[1],ZC+60.0])+a*LEG_DIR+b*np.array([-LEG_DIR[1],LEG_DIR[0],0])
            loc,ir,it=t.ray.intersects_location([q],[[0,0,1.0]]); ws.append(loc[:,2].min()-ZC)
    return max(ws)+0.3
MOUTH16=_mouth16()
def usb16_cut():
    return (_stadium16(*WELL16,60.0,MOUTH16)+_stadium16(*SLOT16[:2],MOUTH16-0.01,MOUTH16+SLOT16[2])
            +_stadium16(*CHAMBER16[:2],MOUTH16+SLOT16[2]-0.01,MOUTH16+SLOT16[2]+CHAMBER16[2]))
def usb16_receptacle():
    w0,w1=MOUTH16,MOUTH16+7.35
    return _stadium16(8.94,3.26,w0,w1)-_stadium16(8.34,2.66,w0-0.1,w1-1.0)+_stadium16(6.7,0.7,w0+0.6,w1-1.0)
USB16_PATH=[(USB16_C[0]+1.0,USB16_C[1]-1.0,MOUTH16+SLOT16[2]+CHAMBER16[2]/2),(-52.0,43.0,89.0)]+USB_PATH[2:]
def handle16(side=1):
    global USB_PATH
    keep=USB_PATH; USB_PATH=USB16_PATH
    try:
        h=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds4()
        h-=usb16_cut()+usb_channel()+usb_groove()
        h-=bx(-9.5,-4.5,WEB_Y0-0.2,-18.9,ZC+66.0,ZC+67.6)   # the channel's mouth against the block (as v14)
    finally: USB_PATH=keep
    if side<0: h=h.mirror([0,0,1]).translate([0,0,2*ZC])
    return h
