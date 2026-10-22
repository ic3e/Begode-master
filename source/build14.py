# Slide-out cup holder v9: a two-axis gimbal (pitch and roll), like a ship's compass.
# The basket (four telescoping rings, as in v8) hangs on front and back pins inside a gimbal ring,
# so it can swing side to side; the gimbal ring hangs on left and right pins from the slide arms,
# so it can swing forward and back. Both axes meet in one point above the drink's centre of gravity.
# Roll is for the kickstand (the wheel leans ~10-15° on it), cambered roads and carrying the wheel;
# in turns the wheel already leans with the apparent gravity, so roll stays near zero there.
exec(open('build13.py').read())

YP=-60.0                         # 12 mm lower than v8: the wider gimbal ring stays out of the road sensor's view
RAIL_Y0,RAIL_Y1=YP-8,YP+8        #   even pitched 25°, and the drink sits further below the beam
R1_TOP=-8.0
OR0,OR1,OR_H=52.4,56.0,3.5       # gimbal ring: inner/outer radius, half height. 52.4 lets ring 1 roll ±20°
BOSS1=57.4                       # pitch bosses run out to here (5 mm of thread for the M3)
ARM0,ARM1=57.8,64.0
RAIL0,RAIL1=62.0,70.4            # 6.4 mm further out than v8, still well inside the side plates (74)
X_IN=-86.0                       # stowed: the gimbal ring's back screw head stays clear of the back cross piece
ROLL=20.0; PITCH=25.0

def ring(k,top):   # basket coords: x fwd from the pivot, y up from the pivot, w across
    ri,ro,lip,fl=RINGS[k]
    m=cylV(ro,top-RING_H,top,0,0)-cylV(ri,top-RING_H-1,top+1,0,0)
    if lip: m+=cylV(ri+0.01,top-RING_H,top-RING_H+LIP,0,0)-cylV(lip,top-RING_H-1,top-RING_H+LIP+1,0,0)
    if fl:  m+=cylV(fl,top-LIP,top,0,0)-cylV(ri,top-LIP-1,top+1,0,0)
    if k==3:   # floor with drain holes
        f=cylV(ri+0.01,top-RING_H,top-RING_H+LIP,0,0)
        for i in range(6):
            a=np.radians(60*i); f-=cylV(5,top-RING_H-1,top,18*np.cos(a),18*np.sin(a),24)
        m+=f-cylV(5,top-RING_H-1,top,0,0,24)
    if k==0:   # roll ears, front and back, rising above the ring to the gimbal axis
        for s in (-1,1):
            x0,x1=sorted((s*45.8,s*51.0))
            e=bxw(x0,x1,top-8,0,-6,6)+cylX(5,x0,x1,0,0)
            m+=e-cylX(1.25,x0-1,x1+1,0,0)                           # M3 self-tap pilot
    return m
def gimbal_ring():
    g=cylV(OR1,-OR_H,OR_H,0,0)-cylV(OR0,-OR_H-1,OR_H+1,0,0)
    for s in (-1,1):
        w0,w1=sorted((s*OR0,s*BOSS1)); g+=cylW(5,w0,w1,0,0)-cylW(1.25,w0-1,w1+1,0,0)        # pitch: M3 pilot
    for s in (-1,1):
        x0,x1=sorted((s*OR0,s*OR1)); g+=cylX(5,x0,x1,0,0)
    for s in (-1,1):
        x0,x1=sorted((s*(OR0-1),s*(OR1+1))); g-=cylX(1.65,x0,x1,0,0)                     # roll: M3 clearance
    return g^bxw(-80,80,-OR_H,10,-80,80)            # bosses flush with the band's underside: prints flat, no supports
def gimbal(extended=True):
    return gimbal_ring(),basket(extended)
def rollm(m,roll): return m.translate([0,0,-ZC]).rotate([roll,0,0]).translate([0,0,ZC]) if roll else m
def place(m,xp,pitch=0.0,roll=0.0):   # +pitch = top tips back (wheel nose-down, cup stays upright)
    m=rollm(m,roll)
    if pitch: m=m.rotate([0,0,-pitch])
    return m.translate([xp,YP,0])
def place_gimbal(g,xp,pitch=0.0,roll=0.0):
    ring_,rings=g
    return [place(ring_,xp,pitch)]+[place(r,xp,pitch,roll) for r in rings]

def rails():
    out=[]
    for s in (-1,1):
        w0,w1=sorted((s*RAIL0,s*RAIL1))
        r=bxw(RAIL_X1,RAIL_X0,RAIL_Y0,RAIL_Y1,w0,w1)
        c0,c1=sorted((s*(RAIL0+1.4),s*(RAIL1-1.4)))
        r-=bxw(RAIL_X1-1,RAIL_X0-3,YP-6.6,YP+6.6,c0,c1)          # cavity for the slider (open at the front)
        g0,g1=sorted((s*(RAIL0-1),s*(RAIL0+1.5)))
        r-=bxw(RAIL_X1-1,RAIL_X0-3,YP-3.4,YP+3.4,g0,g1)          # slot the arm runs in
        for xp in (X_IN,X_OUT):                                    # detent dimples, stowed and out
            r-=cylV(1.2,YP+6.0,YP+7.2,xp+25,s*(RAIL0+RAIL1)/2,16)
        r-=cylV(1.25,YP+5,YP+RAIL_Y1-YP+1,RAIL_X1+3,s*(RAIL0+RAIL1)/2,16)   # M3 front stop screw
        web=bxw(-60,RAIL_X0,RAIL_Y1-1,SHELF_Y0+1,w0,w1)            # hangs it from the lamp shelf
        out.append(r+web)
    back=bxw(RAIL_X0-4,RAIL_X0,RAIL_Y0,RAIL_Y1,-RAIL1,RAIL1)
    top=YP+R1_TOP; bot=YP+R1_TOP-RING_H
    # stowed, the back of ring 1 sits in a slot either side of its back ear: that holds both pitch and
    # roll, and with ring 1 held the gimbal ring can't turn either
    XS=-47.0
    slot=bxw(XS,RAIL_X0-2,bot-3,top+3,-30,30)-bxw(XS-1,-36.5,bot-0.4,top+0.4,-31,31)
    slot-=hull(bxw(XS-1,XS+1.1,bot-0.4,top+0.4,-31,31),bxw(XS-1.1,XS-1,bot-2.5,top+2.5,-31,31))     # lead-in
    slot-=bxw(XS-1,RAIL_X0+1,bot-0.4,top+4,-8,8)                   # notch for the back ear and the gimbal's back pin
    # ledge under the back of the flat stack: holds the inner rings up while stowed; its sloped front
    # pushes hanging rings back up as the basket slides in
    ledge=hull(bxw(-57,RAIL_X0-2,bot-3,bot-0.4,-30,30),bxw(-67,-57,bot-3,bot-2.9,-30,30))
    return mf.Manifold.batch_boolean(out+[back,slot,ledge],mf.OpType.Add)
