# Slide-out, self-levelling cup holder under the headlamp (v8).
# Two C-rails hang under the lamp shelf. Each side has a slider in its rail and an arm through the
# rail's slot; the arms carry the basket on two pivots near its top, so it hangs like a pendulum and
# keeps the cup upright when the wheel pitches (braking, accelerating, tilt-back).
# The basket is four telescoping rings: pushed up they make a 20 mm flat stack that slides in under the
# lamp; pulled out they drop open into a 75 mm deep cup for a 0.33 l can or a coffee cup.
# Stowed, the back of the stack sits in a slot, which stops it swinging.
import numpy as np, trimesh, manifold3d as mf
exec(open('build12.py').read().split("\nif __name__=='__main__':")[0])     # lamp v2, handle helpers

def bxw(x0,x1,y0,y1,w0,w1): return bx(x0,x1,y0,y1,ZC+w0,ZC+w1)            # lateral as w (centre 0)
def cylX(r,x0,x1,y,w,seg=48): return mf.Manifold.cylinder(abs(x1-x0),r,r,seg).rotate([0,90,0]).translate([min(x0,x1),y,ZC+w])
def cylW(r,w0,w1,x,y,seg=48): return mf.Manifold.cylinder(w1-w0,r,r,seg).translate([x,y,ZC+w0])
def cylV(r,y0,y1,x,w,seg=96): return mf.Manifold.cylinder(y1-y0,r,r,seg).rotate([-90,0,0]).translate([x,y0,ZC+w])

YP=-48.0                         # pivot axis height (STL Y)
X_IN,X_OUT=-75.0,-130.0          # pivot X stowed / pulled out
RING_H=20.0; LIP=1.6; WALL=1.6
# telescoping rings, outermost first: (inner radius, outer radius, bottom lip inner radius, top flange outer radius)
RINGS=[(45.4,47.0,43.6,None),(41.6,43.2,39.8,45.0),(37.8,39.4,36.0,41.2),(34.0,35.6,None,37.4)]
R1_TOP=-6.0                      # ring 1 top, relative to the pivot: the pivot sits above the drink's centre of gravity
EAR0,EAR1=45.8,51.0; ARM0,ARM1=51.4,57.6     # ears start inside the ring wall so they join it
RAIL0,RAIL1=55.6,64.0; RAIL_Y0,RAIL_Y1=YP-8,YP+8; RAIL_X0,RAIL_X1=-22.0,-124.0

def ring_tops(extended=True):
    tops=[R1_TOP]
    for k in range(1,4):
        tops.append(tops[-1]-RING_H+2*LIP if extended else R1_TOP)
    return tops
def ring(k,top):   # in basket coords: x fwd (from pivot), y up (from pivot), w across; ring axis vertical
    ri,ro,lip,fl=RINGS[k]
    m=cylV(ro,top-RING_H,top,0,0)-cylV(ri,top-RING_H-1,top+1,0,0)
    if lip: m+=cylV(ri+0.01,top-RING_H,top-RING_H+LIP,0,0)-cylV(lip,top-RING_H-1,top-RING_H+LIP+1,0,0)
    if fl:  m+=cylV(fl,top-LIP,top,0,0)-cylV(ri,top-LIP-1,top+1,0,0)
    if k==3:   # floor with drain holes
        f=cylV(ri+0.01,top-RING_H,top-RING_H+LIP,0,0)
        for i in range(6):
            a=np.radians(60*i); f-=cylV(5,top-RING_H-1,top,18*np.cos(a),18*np.sin(a),24)
        m+=f-cylV(5,top-RING_H-1,top,0,0,24)
    if k==0:   # ears carrying the pivots, above the ring
        for s in (-1,1):
            w0,w1=sorted((s*EAR0,s*EAR1))
            e=bxw(-6,6,top-RING_H,2,w0,w1)+cylW(5,w0,w1,0,0)
            m+=e-cylW(1.25,w0-1,w1+1,0,0)                           # M3 self-tap pilot
    return m
def basket(extended=True):
    return [ring(k,t) for k,t in enumerate(ring_tops(extended))]
def place_basket(parts,xp,swing=0.0):   # +swing = top tips back (wheel pitched nose-down, cup stays upright)
    out=[]
    for p in parts:
        m=p.rotate([0,0,-swing]).translate([xp,YP,0]) if swing else p.translate([xp,YP,0])
        out.append(m)
    return out

def arm(s,xp,detent=True):     # slider + arm, one side
    w0,w1=sorted((s*ARM0,s*ARM1)); v0,v1=sorted((s*(RAIL0+1.6),s*(RAIL1-1.6)))
    b0,b1=sorted((s*ARM0,s*(RAIL0-0.4)))                       # pivot boss stays out of the rail wall
    a=bx(xp-6,xp+40,YP-3,YP+3,ZC+w0,ZC+w1)+cylW(5,b0,b1,xp,YP)
    a+=bx(xp+10,xp+40,YP-6.4,YP+6.4,ZC+v0,ZC+v1)                 # slider in the rail
    b0,b1=sorted((s*(RAIL0+1.6),s*(RAIL1-1.6)))
    if detent: a+=cylV(1.0,YP+6.4,YP+7.0,xp+25,s*(RAIL0+RAIL1)/2,16)   # click bump on top of the slider
    return a-cylW(1.65,w0-1,w1+1,xp,YP)                          # M3 pivot, clearance
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
    # back cross piece, with the slot that holds the stowed stack level
    back=bxw(RAIL_X0-4,RAIL_X0,RAIL_Y0,RAIL_Y1,-RAIL1,RAIL1)
    top=YP+R1_TOP; bot=YP+R1_TOP-RING_H
    slot=bxw(RAIL_X0-12,RAIL_X0,bot-3,top+3,-30,30)-bxw(RAIL_X0-13,RAIL_X0-3.9,bot-0.4,top+0.4,-31,31)
    slot-=hull(bxw(RAIL_X0-13,RAIL_X0-11.9,bot-0.4,top+0.4,-31,31),bxw(RAIL_X0-13.1,RAIL_X0-13,bot-2.5,top+2.5,-31,31))  # lead-in
    # ledge under the back of the flat stack: holds the inner rings up while stowed; its sloped front
    # pushes hanging rings back up as the basket slides in
    ledge=hull(bxw(-46,RAIL_X0-4,bot-3,bot-0.4,-30,30),bxw(-56,-46,bot-3,bot-2.9,-30,30))
    return mf.Manifold.batch_boolean(out+[back,slot,ledge],mf.OpType.Add)

def holder8():
    parts=[]
    for s in (-1,1):
        zin=ZC+s*EAR_OUT; zout=zin+s*(PLATE_T+2); z0,z1=sorted((zin,zout))
        prof=hull(bx(-60,-12,SHELF_Y0,EAR_TOP-8,z0,z1),cyl_Z(8,z0,z1,-52,EAR_TOP-8),cyl_Z(8,z0,z1,-20,EAR_TOP-8))
        for hx,hy in EAR_HOLES:
            prof-=hull(cyl_Z(2.2,z0-1,z1+1,hx,hy-4,24),cyl_Z(2.2,z0-1,z1+1,hx,hy+4,24))
        parts.append(prof)
    shelf=bx(-60,-12,SHELF_Y0,SHELF_Y1,ZC-EAR_OUT-1,ZC+EAR_OUT+1)
    shelf-=bx(-48,-24,SHELF_Y0-1,SHELF_Y1+1,ZC-45,ZC+45)
    return mf.Manifold.batch_boolean(parts+[shelf,rails()],mf.OpType.Add)
