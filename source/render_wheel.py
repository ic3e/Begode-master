# A better-looking Master for the pictures only. The checks keep using the measured model (model3 /
# obstacles3): this one is dressed on top of the same measured outline (shells, cover, tyre at rest), with the
# details traced from the owner's 360 turntable GIF: faceted side pads, the silver suspension rail over the
# axle, the rear battery pack, a knobby tyre, a spoked rim, spiked pedals, the rear fender, the red rear
# linkage and the tail light. Run after build16+ (needs M2, bx, ZC, cover3).
import numpy as np, manifold3d as mf
def _cs(pts):
    a=sum(x0*y1-x1*y0 for (x0,y0),(x1,y1) in zip(pts,pts[1:]+pts[:1]))
    return mf.CrossSection([pts if a>0 else pts[::-1]])
def _slab(cs,w0,w1,b=0.0,steps=6):   # extruded at w0..w1 (outwards from the centre plane), outer edge chamfered by b
    out=[mf.Manifold.extrude(cs,w1-w0-b).translate([0,0,w0])]
    for k in range(steps):
        c=cs.offset(-b*(k+1)/steps,mf.JoinType.Round)
        if c.area()<=1: break
        out.append(mf.Manifold.extrude(c,b/steps).translate([0,0,w1-b+k*b/steps]))
    return mf.Manifold.batch_boolean(out,mf.OpType.Add)
def _side(m,s): return m.translate([0,0,ZC]) if s>0 else m.mirror([0,0,1]).translate([0,0,ZC])
HUB=tuple(M2.TC); TR=M2.TR; TW=47.5                  # tyre at rest: centre, radius, half width
def _ring(r0,r1,w0,w1,seg=128):
    return (mf.Manifold.cylinder(w1-w0,r1,r1,seg)-mf.Manifold.cylinder(w1-w0+2,r0,r0,seg).translate([0,0,-1])).translate([HUB[0],HUB[1],ZC+w0])
def _about_hub(m,deg): return m.rotate([0,0,deg]).translate([HUB[0],HUB[1],ZC])
def wheel_parts():   # (name, manifold, colour, roughness, metalness)
    R=TR-11
    # carcass: rounded section (stacked rings), then three rows of knobs, staggered like the stock off-road tyre
    tyre=_ring(R-62,R,-TW+5,TW-5)+_ring(R-62,R-6,-TW,TW)+_ring(R-62,R-2,-TW+2,TW-2)
    kn=[]
    N=56
    for i in range(N):
        for w,dw,off,l in ((-31,15,0.0,13),(0,22,0.5,11),(31,15,0.0,13)):
            k=mf.Manifold.cube([8,l,dw],True).translate([R+2,0,w+(4 if (i%2 and w) else 0)*np.sign(w)])
            kn.append(_about_hub(k,360*(i+off)/N))
        for s in (-1,1):   # shoulder lugs down the sidewall
            k=mf.Manifold.cube([14,8,3],True).translate([R-9,0,s*(TW-1)])
            kn.append(_about_hub(k,360*(i+0.25)/N))
    tyre+=mf.Manifold.batch_boolean(kn,mf.OpType.Add)
    parts=[('tyre',tyre,'#141517',0.95,0.0)]
    parts.append(('rim',_ring(R-80,R-60,-31,31)+_ring(R-63,R-59,-36,36),'#c9ccd1',0.22,0.9))
    sp=[]
    for i in range(12):   # Y-spokes in pairs, like the stock rim
        for d in (-4,4):
            sp.append(_about_hub(mf.Manifold.cube([R-80-95,9,10],True).translate([95+(R-80-95)/2,0,0]).rotate([0,0,d]),30*i))
    parts.append(('spokes',mf.Manifold.batch_boolean(sp,mf.OpType.Add),'#26282c',0.35,0.7))
    motor=mf.Manifold.cylinder(60,100,100,96).translate([0,0,-30])+mf.Manifold.cylinder(68,94,94,96).translate([0,0,-34])
    motor=motor.translate([HUB[0],HUB[1],ZC])
    parts.append(('motor',motor,'#1a1b1e',0.5,0.4))
    parts.append(('axle',mf.Manifold.cylinder(124,24,24,48).translate([HUB[0],HUB[1],ZC-62]),'#9aa0a8',0.3,0.85))
    return parts
# side body, in (x, y) mm; outwards w from the centre plane
SHELL=M2.shell_pts()
REAR_PACK=[(150,-110),(300,-110),(300,-300),(268,-332),(196,-338),(196,-150)]   # behind the rail (photo px 200-290)
RAIL=(138,192)                                                                    # the silver rail, x span, above the axle
PAD_CUT=[(-150,60),(420,60),(420,-96),(132,-100),(120,-246),(48,-284),(-150,-294)] # upper pad region (photo)
LOWER_CUT=[(-150,-300),(48,-290),(120,-252),(132,-300),(132,-500),(-150,-500)]      # lower pad, below it
def body_parts():
    parts=[]
    shell=_cs(SHELL).offset(-6,mf.JoinType.Round).offset(6,mf.JoinType.Round)
    rear=_cs(REAR_PACK)
    pad=shell.offset(-2.5,mf.JoinType.Round)^_cs(PAD_CUT)
    low=shell.offset(-2.5,mf.JoinType.Round)^_cs(LOWER_CUT)
    ribs=[]
    for x in range(204,296,7): ribs.append(mf.Manifold.cube([3.2,176,3],False).translate([x,-322,0]))
    rib=mf.Manifold.batch_boolean(ribs,mf.OpType.Add)
    for s in (1,-1):
        parts.append((f'shell{s}',_side(_slab(shell,M2.BAY_W/2,120,4),s),'#1b1d21',0.7,0.1))
        parts.append((f'pack{s}',_side(_slab(rear,M2.BAY_W/2,124,3)+rib.translate([0,0,121]),s),'#1f2125',0.55,0.25))
        parts.append((f'rail{s}',_side(_slab(_cs([(RAIL[0],-60),(RAIL[1],-60),(RAIL[1],-345),(RAIL[0],-345)]),M2.BAY_W/2,118,2),s),'#b9bdc3',0.25,0.9))
        parts.append((f'pad{s}',_side(_slab(pad,119,135,9),s),'#202227',0.85,0.0))
        parts.append((f'lowpad{s}',_side(_slab(low,119,132,7),s),'#17181b',0.85,0.0))
        # the long lower arm beside the tyre (photo: rear-high to the pedal), and the pedal on it
        arm=_cs([(470,-250),(486,-262),(120,-372),(96,-372),(96,-352),(120,-352)])
        parts.append((f'arm{s}',_side(_slab(arm,TW+3,TW+17,3),s),'#18191c',0.6,0.2))
        pd=mf.Manifold.cube([300,10,92],False).translate([-8,-382,124])
        for i in range(5):
            for j in range(2):
                pd-=mf.Manifold.cylinder(14,11,11,6).rotate([90,0,0]).translate([30+i*60,-375,150+j*40])
        sp=[mf.Manifold.cylinder(6,1.8,0.5,8).rotate([-90,0,0]).translate([2+i*29.5,-372,130+j*80]) for i in range(10) for j in range(2)]
        pd+=mf.Manifold.batch_boolean(sp,mf.OpType.Add)
        pd+=mf.Manifold.cube([300,30,8],False).translate([-8,-382,116])   # hinge edge against the shell
        parts.append((f'pedal{s}',_side(pd,s),'#232529',0.5,0.35))
    # rear linkage (red) and fender, tail light on the cover's back
    link=_cs([(336,22),(372,22),(392,-14),(386,-62),(364,-70),(344,-36)])
    for d in (-1,1):   # two plates with lightening holes, the shock's bolts between them
        for c in ((360,0),(372,-40)): link=link-_cs([(c[0]+7*np.cos(a),c[1]+7*np.sin(a)) for a in np.linspace(0,2*np.pi,20,endpoint=False)])
    link=_slab(link,17,23,1.5)
    link=link+link.mirror([0,0,1])+mf.Manifold.cylinder(40,4,4,24).translate([360,0,-20])+mf.Manifold.cylinder(40,4,4,24).translate([372,-40,-20])
    parts.append(('link',link.translate([0,0,ZC]),'#c0262d',0.45,0.35))
    fender=(_ring(TR+12,TR+16,-56,56,96)^bx(HUB[0]+60,HUB[0]+400,HUB[1]+150,HUB[1]+400,ZC-60,ZC+60))
    parts.append(('fender',fender,'#16171a',0.55,0.1))
    parts.append(('tail',bx(388,394,30,70,ZC-56,ZC+56),'#e0262d',0.3,0.1))
    return parts
