# Lamp v6.2: v6.1 made ready for the slicer. Nothing moves, nothing is added to the bill; the parts just print.
# The STL check (print_check.py) found what a slicer would have quietly got wrong:
# - Lens frame: the horn pocket's floor was 0.3-0.5 mm, thinner than one line of a 0.4 mm nozzle, and the
#   horn's two little screws had nothing to bite in and would have stuck out into the pocket wall. The
#   floor is now 1.2 mm, standing in a 0.4 mm recess in the housing's wall where the horn swings; the
#   horn is glued in instead of screwed. Printed face down (it had no flat side on the bed before).
# - Housing: a 0.05 mm skin left from v5.4's stop, 0.05-0.2 mm slits beside the lower stop and the handle-screw
#   bosses. Ribs under the
#   lenses' floor, in the duct, so the sealed slabs above and below the duct bridge in short spans instead
#   of needing support that could never come out of the duct; its dead-end outer strips are solid. 45 degree
#   cones under the lid posts.
# - Top plate: knife-edge tips where the bearing's and the servo's arcs met the tongues' sides, 0.1-0.15 mm slits between
#   the tongues and the stop, and a 0.2 mm floor under the M4 inserts.
# - Handle: its webs ended 0.2 mm short of, or 0.2 mm past, the stock leg's faces: slivers. The USB wire's groove
#   left 0.2-0.4 mm walls in the web: it now sits on the channel's exit, in a web 1.5 mm thicker there. Prints
#   lying flat, so its layers run along the legs and the grip.
import numpy as np, trimesh, manifold3d as mf
exec(open('build23.py').read())

# ---- lens frame: a real floor behind the horn ----
HORN_FLOOR_W=32.6                        # inner face of the horn plate (the arms stay at ARM_W0 = 33.3)
def horn_plate(grow=0.0):
    z1=HW3+BOSS3-2.4
    return hull(cw(HUB_R+grow,HORN_FLOOR_W-grow,z1,seg=48),cw(4.5+grow,HORN_FLOOR_W-grow,z1,u=HORN_UV[0],v=HORN_UV[1],seg=48))
def lens_frame7():
    f=lens_frame()
    # the horn screws' holes go: the horn is glued in
    for k in (0.62,0.95): f+=cw(0.8,HORN_FLOOR_W,HW3+BOSS3-2.2,u=HORN_UV[0]*k,v=HORN_UV[1]*k)
    f+=horn_plate()
    # the bridge's back face and the hub only touched at a tangent: a 0.02-0.1 mm crevice (on the left only above
    # the stop lug, which must stay the first thing to meet the stops)
    f+=box(LB_U-5.1,LB_U-4.6,-3.0,3.0,-ARM_W1+0.1,-31.6)+box(LB_U-5.1,LB_U-4.6,-3.0,3.0,31.6,HW3+BOSS3-0.01)
    return f
def horn_recess():   # where the thicker horn plate swings, 0.4 mm clear, cut into the pocket wall; and up to the top,
    p=H6(horn_plate(0.4))                    # the way it comes in with the servo
    swing=hull(*[tilt6(p,a) for a in np.arange(-13.0,13.01,1.0)])          # one convex shape: no slivers between copies
    return swing+hull(p,p.translate([0,40,0]))

# ---- housing ----
RIB_W=(-20.0,-8.6,0.0,8.6,20.0); RIB_T=1.2    # spans of 10 mm or less; the +-8.6 ones carry the button box's roof
def duct_ribs():   # along the flow, from the face's back to the passage's end wall, roof to the lenses' floor
    z=[bx(HOUSE_X0+FACE-0.1,PASS_END[0]+0.1,PASS_Y0-0.1,FLOOR_Y[0]+0.1,ZC+w-RIB_T/2,ZC+w+RIB_T/2) for w in RIB_W]
    for s in (-1,1):   # the passage's outer strips lead nowhere (the trap and the inlet are 58 mm wide): solid
        z0,z1=zw(s*TRAP_IN_W,s*(P3A+0.1)); z.append(bx(HOUSE_X0+FACE-0.1,PASS_END[0]+0.1,PASS_Y0-0.1,FLOOR_Y[0]+0.1,z0,z1))
    return mf.Manifold.batch_boolean(z,mf.OpType.Add)
def housing11():
    h=housing10()
    z0,z1=zw(-36.65,-33.9); h-=bx(-29.95,-21.35,-3.6,-3.45,z0,z1)                 # v5.4 stop's last skin
    z0,z1=zw(-36.6,-36.45)                                                        # slit beside the lower stop
    h+=bx(PX6+STOP6_U[0],PX6+STOP6_U[1],FLOOR_Y[1]-0.1,PY6-STOP6_V,z0,z1)-cw(SEAT_R+0.05,-37.0,-36.5).translate([PX6,PY6,ZC])
    h+=duct_ribs()^bx(-300,300,PASS_Y0-1,FLOOR_Y[0]+1,ZC-P3A-0.05,ZC+P3A+0.05)    # into the partitions, not flush with them
    z0,z1=zw(31.0,33.4); h-=horn_recess()^bx(-300,300,-300,300,z0,z1)
    for s in (-1,1):                                                              # the bar's pads stood 0.1 mm off the inlet's edge
        z0,z1=zw(s*25.0,s*30.5); h+=bx(INLET[0]-0.2,BAR_X0+1.2,FLOOR_Y[1]-0.1,BAR_Y0-0.15,z0,z1)
    for x,w in WEB_SCREWS:                                                        # handle-screw bosses: 0.2 mm off the back wall, joined to it
        h+=bx(x+3.0,HOUSE_X1-WALL+0.1,HOUSE_YS,HOUSE_YS+8,ZC+w-2.0,ZC+w+2.0)
        h-=cylV(1.25,HOUSE_YS-1,HOUSE_YS+7,x,w)
    for x,w in LID_POSTS:                                                         # 45 degree cones under the lid posts' ends
        h+=mf.Manifold.cylinder(4.0,4.0,0.0,48).rotate([-90,0,0]).translate([x,LOW_Y0+10,ZC+w])
    return h

# ---- top plate ----
def top_plate11():
    p=top_plate10()
    # knife-edge tips of the bearing tongue (arc r 9.75 against sides at 9.65) and the wire tongue (4.2 / 3.9)
    z0,z1=zw(BRG_W0-0.2,-P3A+0.1); p-=bx(PX6-SEAT_R-0.5,PX6+SEAT_R+0.5,PY6-1,PY6+5.0,z0,z1)
    z0,z1=zw(BLK_W0-0.2,BRG_W0-0.1); p-=bx(PX6-WIRE_R-0.5,PX6+WIRE_R+0.5,PY6-1,PY6+3.0,z0,z1)
    z0,z1=zw(P3A,P3B); p-=bx(PX6-SV_BOSS-1.0,PX6+SV_BOSS+1.0,PY6-1,PY6+3.0,z0,z1)
    # one tongue, not two with a 0.1 mm slit (only beyond the bearing's outside, r > 9.75)
    z0,z1=zw(BRG_W0-0.2,BRG_W0); p+=bx(PX6-WIRE_R+0.1,PX6+WIRE_R-0.1,PY6,PLATE_Y0+0.1,z0,z1)-cw(SEAT_R+0.05,BRG_W0-1,BRG_W0+1).translate([PX6,PY6,ZC])
    # the upper stop joined to the bearing tongue
    z0,z1=zw(-36.7,-36.45); p+=bx(PX6-SEAT_R+0.05,PX6+STOP6_U[1],PY6+STOP6_V,PLATE_Y0+0.1,z0,z1)-cw(SEAT_R+0.05,-37.0,-36.0).translate([PX6,PY6,ZC])
    # M4 inserts: 1.0 mm floor under them (the boss comes 0.8 mm lower)
    for x,w in TOP_SCREWS: p+=cylV(6,HOUSE_Y1-6.8,HOUSE_Y1-5.9,x,w)
    return p

# ---- handle: webs that overlap the stock leg instead of stopping 0.2 mm short of it ----
GROOVE=[((-7.0,69.0),(-16.8,69.0)),((-16.8,69.0),(-16.8,62.8))]   # on the channel's exit (w 69), not 0.2 mm from the web's face
USB_PATH=USB_PATH[:-1]+[(-7.0,-20.8,69.0)]                           # its end 0.6 mm higher: it broke through the foot's underside
def handle_adds4():
    p=[]
    for s in (-1,1):
        z0,z1=zw(s*48.0,s*70.5); p.append(bx(-25,-10.5,WEB_Y0,WEB_Y1,z0,z1))
        z0,z1=zw(s*66.5,s*71.5); p.append(bx(-11,4,WEB_Y0,-17,z0,z1))
        z0,z1=zw(s*66.5,s*72.0); p.append(bx(-18.8,-5.0,WEB_Y0,WEB_Y1,z0,z1))   # room for the groove's outer wall
    m=mf.Manifold.batch_boolean(p,mf.OpType.Add)
    for x,w in WEB_SCREWS: m-=cylV(1.7,WEB_Y0-1,WEB_Y1+1,x,w)
    return m
def handle14(side=1):
    h=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds4()
    x,y=USB_XY
    h=h+cw(USB_BOSS[1],USB_BOSS[0],USB_FACE-8,u=x,v=y).translate([0,0,ZC])
    h-=cw(USB_R,USB_CAV[0],USB_FACE+1,u=x,v=y).translate([0,0,ZC])+cw(USB_CAV[1],USB_CAV[0],USB_FACE-12,u=x,v=y).translate([0,0,ZC])
    h-=usb_channel()+usb_groove()
    h-=bx(-9.5,-4.5,WEB_Y0-0.2,-18.9,ZC+66.0,ZC+67.6)   # the channel's mouth left a 0.1 mm skin on the face against the block: open
    if side<0: h=h.mirror([0,0,1]).translate([0,0,2*ZC])
    return h

def clean_tm(t):   # zero-area triangles (three points in a line, left by the booleans): split the neighbour across
    F=t.faces.copy(); V=t.vertices              # the long edge at the middle point and drop the flat one, so the
    for _ in range(50):                          # mesh stays closed and no slicer has anything to "repair"
        a=np.linalg.norm(np.cross(V[F[:,1]]-V[F[:,0]],V[F[:,2]]-V[F[:,0]]),axis=1)/2
        bad=np.flatnonzero(a<1e-6)
        if not len(bad): break
        f=F[bad[0]]; L=[np.linalg.norm(V[f[(i+1)%3]]-V[f[i]]) for i in range(3)]; i=int(np.argmax(L))
        p,q,m=f[i],f[(i+1)%3],f[(i+2)%3]
        g=np.flatnonzero(((F==q).any(1))&((F==p).any(1))); g=[k for k in g if k!=bad[0]]
        if len(g)!=1: break
        G=F[g[0]]; j=int(np.flatnonzero(G==q)[0])
        if G[(j+1)%3]!=p: break
        x=G[(j+2)%3]
        F=np.delete(np.vstack([F,[[q,m,x],[m,p,x]]]),[bad[0],g[0]],axis=0)
    return trimesh.Trimesh(V,F,process=False)
