# Handle v17: the lamp tabs braced. The first printed v16 snapped both tabs at the root, where they leave the leg:
# a 4 mm plate bending about that line with the lamp's weight and every bump on its screws, and on the USB side
# the wire's groove ran right along the root and cut it to 1.8 mm. v17 keeps the tabs' 4 mm and adds:
# - a triangular gusset under each tab, 5 mm deep at the root and tapering out under the screw (the shells are
#   7-12 mm below; it keeps 2 mm off them), its root carried back under the foot;
# - a sloped fillet over the root, in the gap between the lamp's side wall and the leg;
# - the USB wire in a closed channel through that thicker root instead of the open groove, coming up through the
#   tab under the housing's grommet. The screws get a counterbore from below, so the same M3 x 10 still reach.
exec(open('build25.py').read())
GUS_D=5.0                                  # gusset depth under the tab at its root
GUS_W=(50.0,66.5,80.5)                     # the taper starts at w 50, full depth from 66.5 out into the leg (80.5)
FIL_TOP=-12.0                              # the fillet over the root rises to here, clear of the cover's edge
def _wy(pts,x0,x1,s):   # (w, y) polygon -> solid between x0 and x1, on side s
    return hull(*[mf.Manifold.cube([x1-x0,0.01,0.01]).translate([x0,y,ZC+s*w]) for w,y in pts])
def tab_braces():
    out=[]
    for s in (-1,1):
        y0=WEB_Y0
        # gusset under the tab: full depth near the leg, tapering to nothing at w 50; carried back under the foot
        # (the gap between the tab's end, w 70.5, and the leg's lower inner face, w 75-80, is filled too: the gusset
        # braces against the leg itself, and the wire runs inside)
        out.append(_wy([(GUS_W[0],y0),(70.5,y0),(70.5,WEB_Y1),(GUS_W[2],WEB_Y1),(GUS_W[2],y0-GUS_D),(GUS_W[1],y0-GUS_D)],-25.0,-10.0,s))
        out.append(_wy([(66.6,y0+0.4),(GUS_W[2],y0+0.4),(GUS_W[2],y0-GUS_D),(66.6,y0-GUS_D)],-11.0,4.0,s))   # up into the foot (its underside is at -23.6)
        # fillet over the root, outside the lamp's side wall (w 66.5) and up the leg's inner face
        out.append(_wy([(67.0,WEB_Y1-0.01),(80.0,WEB_Y1-0.01),(80.0,FIL_TOP)],-25.0,-10.5,s))
    return mf.Manifold.batch_boolean(out,mf.OpType.Add)
# the USB wire: down the leg as before, then inside the braced root to the grommet at (-16.8, 62.8), up through the tab
USB17_PATH=USB16_PATH[:-2]+[(-16.8,-18.0,77.0),(-16.8,-23.0,70.0),(-16.8,-23.0,62.8),(-16.8,-18.5,62.8)]
def handle17(side=1):
    global USB_PATH
    keep=USB_PATH; USB_PATH=USB17_PATH
    try:
        h=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds4()+tab_braces()
        h-=usb16_cut()+usb_channel()
        for x,w in WEB_SCREWS:
            h-=cylV(1.7,WEB_Y0-GUS_D-1,WEB_Y1+1,x,w)                     # the screw's hole through tab and gusset
            h-=cylV(3.2,WEB_Y0-GUS_D-1,WEB_Y0,x,w)                       # its head up to where the tab began: M3 x 10 as before
    finally: USB_PATH=keep
    if side<0: h=h.mirror([0,0,1]).translate([0,0,2*ZC])
    return h
