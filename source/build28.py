# Lamp v6.4 + handle v18: the lamp sees hills, and the rider can dip it.
# - Hills: an EUC balances to gravity, not to the road, so on a steady hill the shell stays level and the gyro and
#   accelerometer see nothing: v6.1-v6.3 "followed hills" only by the rider's pedal angle, and a 2 deg-down beam hit
#   a 10 % climb about 4.5 m ahead, or never came down on a 10 % descent. A VL53L1X distance sensor (Pololu carrier,
#   12.7 x 17.8 mm) now looks 25 deg down at the road about 1.3 m ahead, from the left side of the face, through the
#   main window: if the window is too dirty for it, it is too dirty for the light as well (v6's sensor under the
#   lamp was in the tyre's spray). Tilted 25 deg, the window's reflection goes down and away from its receiver.
#   It sits in a hood behind the face, on foam tape, where the LED drivers' front ends were (they move back 8 mm).
# - Dipping: the stock opening is 36.8 mm tall and a 33 mm cut-off lens (LEDiL FILIPPA) swinging +-12 deg needs about
#   40, so the beam still has no cut-off. The servo dips it instead: two sealed switches on the inner face of the
#   handle's right leg, under the USB port, step the beam between dipped, main and high, and hold for a flash.
exec(open('build27.py').read())

# ---- the road sensor ----
TOF_BOARD=(12.7,17.8,1.6)                  # Pololu VL53L1X carrier: tall (in its plane), wide (along w), board thickness
TOF_DOWN6=25.0                             # its view, below the lamp's level
TOF_TOP=(-55.1,9.0)                        # (x, y) of the board's top front edge: 1.8 mm behind the face for the parts on its front
TOF_W=(-62.0,-44.2)                        # across: between the window tape (63.1) and the bearing block (41.6)
TOF_RIM,TOF_TAPE=1.5,0.5                  # the hood's rim under the board's front edge (its wall), and the foam tape on it
_c,_s=np.cos(np.radians(TOF_DOWN6)),np.sin(np.radians(TOF_DOWN6))
TOF_N=np.array([-_c,-_s,0.0]); TOF_U=np.array([-_s,_c,0.0])   # the way it looks; up its board (the top leans forward)
def _tof_rect(inset,d0,d1):   # the board's outline, shrunk by inset, swept along the view from d0 to d1 (from the board's front)
    a=np.array([TOF_TOP[0],TOF_TOP[1],0.0])
    pts=[]
    for d in (d0,d1):
        for uu in (-inset,-(TOF_BOARD[0]-inset)):
            for w in (TOF_W[0]+inset,TOF_W[1]-inset):
                p=a+uu*TOF_U+d*TOF_N; pts.append(mf.Manifold.cube([0.01,0.01,0.01]).translate([p[0],p[1],ZC+w]))
    return hull(*pts)
def tof_board():   # for checks and renders: the board, and the sensor chip on the middle of its front
    a=np.array([TOF_TOP[0],TOF_TOP[1]])
    corners=[]
    for uu in (0,TOF_BOARD[0]):
        for d in (0,TOF_BOARD[2]):
            p=a-uu*TOF_U[:2]-d*TOF_N[:2]
            for w in TOF_W: corners.append(mf.Manifold.cube([0.01,0.01,0.01]).translate([p[0],p[1],ZC+w]))
    b=hull(*corners)
    m=a-TOF_BOARD[0]/2*TOF_U[:2]; wm=(TOF_W[0]+TOF_W[1])/2
    chip=mf.Manifold.cube([1.56,2.5,4.9],center=True).translate([-0.78,0,0]).rotate([0,0,TOF_DOWN6]).translate([m[0],m[1],ZC+wm])
    return b,chip
def tof_hood():    # a tube from the board's front edge to the face: the board sits on its back rim on foam tape
    return _tof_rect(0.0,TOF_TAPE,9.0)^bx(HOUSE_X0+0.5,0,-30,30,ZC-80,ZC)
def tof_tunnel():  # the view through the hood and the face
    return _tof_rect(TOF_RIM,-1.0,14.0)
def housing13():
    h=housing12()+tof_hood()
    h-=tof_tunnel()
    return h

# ---- handle v18: two buttons on the right leg, beside the USB port ----
# Asked for on the leg's inner face, by the port; but under the port the cover leaves 9-15 mm in front of that face
# (no room for a gloved finger), and over it the face curves away into the grip's inside corner. So they sit on
# the leg's rounded back, at the port's height: it faces the rider, nothing is in front of it, and a fall onto
# the side or the front never reaches it. The USB wire's channel runs down the leg's middle (w 89, across the leg
# at b 0); the switches stop 3.8 mm short of it, and a short hole takes their wires into it.
LEG_N=np.array([-LEG_DIR[1],LEG_DIR[0],0.0])   # across the leg in the handle's plane: up and back, towards the rider
HB_S=(6.0,17.0)                            # along the leg from the USB port's centre: ▲ the upper, ▼ the lower
HB_W=90.5                                  # across the back's crown (it is about 12 mm wide, w 84-97)
KSC=(6.2,7.7)                              # C&K KSC6 sealed (IP67) tact switch: 6.2 mm square, 7.7 mm to the top of the actuator
HB_RECESS=1.0                              # the actuator's top under the face: a knock or a knee doesn't press it
HB_DISH=(6.0,3.6)                          # a dish round it that leads a gloved finger in: radius 1 mm out, at the actuator
def _leg_pt(s,b): return np.array(USB16_C)+s*LEG_DIR[:2]+b*LEG_N[:2]
def _back_b(s,w):   # where the leg's back is, across the leg, at (s, w)
    p=np.array([*_leg_pt(s,40.0),ZC+w]); l,_,_=trimesh.load(U+'euc_master_front_handle.stl').ray.intersects_location([p],[-LEG_N])
    q=l[np.argmin(np.linalg.norm(l-p,axis=1))]; return float(np.dot(q[:2]-np.array(USB16_C),LEG_N[:2]))
HB_FACE=[_back_b(s,HB_W) for s in HB_S]
def _frame(s,b,w):   # local axes: along the leg, along w, into the leg (-N); origin on the leg's back
    M=np.eye(4); M[:3,0]=LEG_DIR; M[:3,1]=[0,0,1.0]; M[:3,2]=-LEG_N; M[:3,3]=[*_leg_pt(s,b),ZC+w]; return M
def _place(m,s,b): return m.transform(_frame(s,b,HB_W)[:3,:])
def _sq(d0,d1,half): return mf.Manifold.cube([2*half,2*half,d1-d0]).translate([-half,-half,d0])
def hb_cut():
    out=[]
    for s,f in zip(HB_S,HB_FACE):
        base=HB_RECESS+KSC[1]                                                     # depth into the leg from its back
        loc=mf.Manifold.cylinder(1.0+HB_RECESS,HB_DISH[0],HB_DISH[1],48).translate([0,0,-1.0])   # the dish
        loc+=_sq(-1.0,base,KSC[0]/2+0.2)+_sq(base-1.6,base,KSC[0]/2+1.3)            # the switch, its feet
        out.append(_place(loc,s,f))
        a=_frame(s,f,HB_W)[:3,:]@np.r_[0,0,base-0.8,1]; c=np.array([*_leg_pt(s+2.0,0.3),ZC+89.6])   # 2 mm on: past the USB chamber's end
        out.append(hull(mf.Manifold.sphere(1.1,24).translate(a.tolist()),mf.Manifold.sphere(1.1,24).translate(c.tolist())))   # wires into the channel
    return mf.Manifold.batch_boolean(out,mf.OpType.Add)
def hb_switches():   # for renders: body and actuator as fitted
    out=[]
    for s,f in zip(HB_S,HB_FACE):
        loc=_sq(HB_RECESS+3.5,HB_RECESS+KSC[1],KSC[0]/2)+mf.Manifold.cylinder(3.5,1.75,1.75,32).translate([0,0,HB_RECESS])
        out.append(_place(loc,s,f))
    return mf.Manifold.batch_boolean(out,mf.OpType.Add)
def handle18(side=1):
    h=handle17(1)-hb_cut()
    if side<0: h=h.mirror([0,0,1]).translate([0,0,2*ZC])
    return h
