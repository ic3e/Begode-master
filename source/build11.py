# Headlamp v3: lamp and folding cup holder as one unit.
# The lamp's side blocks carry two legs down the front; the cup ring and tray hinge between them on
# long side arms (like the motorcycle holders) and fold flat between the legs, right under the lamp.
# The road sensor moves into the front of the left leg. The handle loses its hanger (handle v6) and
# gains a second bolt per side, because the blocks now carry the cup too.
import numpy as np, trimesh, manifold3d as mf
exec(open('build10.py').read().split("\nif __name__=='__main__':")[0])   # lamp v2 + handle v5 parts

# ---- cup holder, in its own frame: x forward from the legs' back (STL X = -60 - x),
#      y across (STL Z = ZC + y), z up (STL Y = YA + z) ----
CX0=BX0                         # x = 0 at the blocks' front face
YAc=L_BOT-1-(H0+RING_T)         # ring hinge height: open ring top just under the lamp
LEG0,LEG1=47.0,BLK_OUT          # legs, |y|: outer face flush with the block, so each prints flat on its side
ARM0,ARM1=LEG0-4.4,LEG0-0.4     # ring and tray side arms, just inside the legs
LEG_X1=30.0                     # legs reach forward to frame the folded pack
LEG_BOT=B[1]-14
def c2s(m): return m.transform([[-1,0,0,CX0],[0,0,1,YAc],[0,1,0,ZC]])
def legs_local():
    out=[]
    for s in (-1,1):
        y0,y1=sorted((s*LEG0,s*LEG1))
        top=(DRL_Y0-LIP-2)-YAc                           # leg top, local z: just under the DRL recess
        leg=box(0,LEG_X1,y0,y1,LEG_BOT,top)+box(-3,0,y0,y1,L_BOT-YAc,top)   # back strip fuses into the block's front wall
        # stop ears for the ring and tray tails, on the legs' inner faces
        e0,e1=sorted((s*ARM0,s*(LEG0+0.5)))
        leg+=box(-5,EAR_A,e0,e1,6.5,14)+box(-5,B[0]-2.7,e0,e1,B[1]-14,B[1]-6.3)
        out.append(leg)
    m=out[0]+out[1]
    for p in (A,B): m-=cyl_y(AXLE/2,-LEG1-1,LEG1+1,*p)   # M4 stub axles from outside, nyloc inside
    return m

def ring_local():
    band=(cyl_z(RING_OUT,0,RING_T)-cyl_z(RING_IN,-1,RING_T+1)).translate([RING_CX,0,A[1]+H0])
    def arm():
        # short hull at the hinge, then a straight bar: a hull along the whole arm would fill in a
        # triangle underneath that hits the folded tray
        c=hull(cyl_y(6,ARM0,ARM1,*A),box(A[0]+2,A[0]+14,ARM0,ARM1,A[1]+H0,A[1]+H0+RING_T))
        c+=box(A[0]+2,RING_CX+12,ARM0,ARM1,A[1]+H0,A[1]+H0+RING_T)
        c+=box(RING_CX-12,RING_CX+12,RING_OUT-6,ARM1,A[1]+H0,A[1]+H0+RING_T)        # web onto the ring
        return c+hull(cyl_y(4,ARM0,ARM1,*A),cyl_y(2.5,ARM0,ARM1,*(A+9*U2(100))))   # stop tail
    return band+both(arm)-cyl_y(AXLE/2,-LEG1,LEG1,*A)

def tray_local():
    cx=B[0]+44.0
    cup=cyl_z(BASK_OUT,-BASK_D,0,cx)-cyl_z(BASK_OUT-BASK_WALL,-BASK_D+BASK_FLOOR,1,cx)
    cup=cup.translate([0,0,B[1]-BASK_DROP]); fz=B[1]-BASK_DROP-BASK_D
    for i in range(6):
        a=np.radians(60*i); cup-=cyl_z(6,fz-1,fz+BASK_FLOOR+1,cx+20*np.cos(a),20*np.sin(a),40)
    cup-=cyl_z(6,fz-1,fz+BASK_FLOOR+1,cx,0,40)
    z0,z1=B[1]-BASK_DROP-BASK_D,B[1]-BASK_DROP
    def arm():
        c=hull(cyl_y(6,ARM0,ARM1,*B),box(B[0]+2,B[0]+14,ARM0,ARM1,z0,z1))
        c+=box(B[0]+2,cx+12,ARM0,ARM1,z0,z1)
        c+=box(cx-12,cx+12,BASK_OUT-3,ARM1,z0,z1)                                   # web onto the tray
        return c+hull(cyl_y(3,ARM0,ARM1,*B),cyl_y(2.5,ARM0,ARM1,*(B+8*U2(270))))
    return cup+both(arm)-cyl_y(AXLE/2,-LEG1,LEG1,*B)

# ---- road sensor, now in the front of the left (electronics) leg ----
TOF3_Y=-36.0; TOF3_W=-(LEG0+LEG1)/2
def tof3_cuts():
    slot=box(-7.2,-3.8,-9.3,9.3,-7.0,20.0)       # board slides in from the leg's inner face
    tunnel=box(-4.0,3,-4.5,4.5,-5.5,5.5)
    place=lambda m: m.rotate([0,0,180+TOF_DOWN]).translate([CX0-LEG_X1,TOF3_Y,ZC+TOF3_W])
    # wires: up the leg, then back through the block wall into the box
    ch=mf.Manifold.cylinder(-8-TOF3_Y+1,3.0,3.0,20).rotate([-90,0,0]).translate([CX0-12,TOF3_Y,ZC+TOF3_W])
    ch+=mf.Manifold.cylinder(25,3.0,3.0,20).rotate([0,90,0]).translate([CX0-15,-8,ZC+TOF3_W])
    ch+=mf.Manifold.cylinder(LEG_X1-12+4,3.0,3.0,20).rotate([0,90,0]).translate([CX0-LEG_X1+4-0,TOF3_Y,ZC+TOF3_W])   # from the slot back to the riser
    return place(slot)+place(tunnel)+ch

def servo_block3():
    b=servo_block2()+c2s(legs_local()^box(-10,LEG_X1+1,0,LEG1+1,-500,500))
    return b-lower_bolts(+1)
def elec_block3():
    e=elec_block()-drl_cut(-1)
    w0,w1=zr(-1,DRL_W0-LIP,DRL_W1+LIP)
    carrier=bx(BX0+9,BX0+11,DRL_Y0-LIP,DRL_Y1+LIP,ZC-BLK_OUT+3,ZC-BLK_IN-3.5)
    carrier-=bx(BX0+8,BX0+12,DRL_Y0-LIP-1,DRL_Y0+2,ZC-50,ZC-44)
    e=e+carrier+c2s(legs_local()^box(-10,LEG_X1+1,-LEG1-1,0,-500,500))
    e-=tof3_cuts()
    return e-lower_bolts(-1)
def lower_bolts(s):
    # a second M4 per side into the handle's side plates, low down; nut slots open from the bottom
    c=mf.Manifold()
    for hx in (EAR_HOLES[0][0],EAR_HOLES[3][0]):
        hy=-10.0
        z0,z1=sorted((ZC+s*(BLK_OUT+1),ZC+s*(BLK_OUT-14)))
        c+=cyl_Z(2.2,z0,z1,hx,hy,24)
        n0,n1=sorted((ZC+s*(BLK_OUT-8.5),ZC+s*(BLK_OUT-8.5-3.4)))
        c+=bx(hx-3.6,hx+3.6,BY0-1,hy+3.6,n0,n1)
    return c

def holder6():
    # handle v6: side plates and shelf as v5, no hanger, round holes for the lower bolts
    parts=[]
    for s in (-1,1):
        zin=ZC+s*EAR_OUT; zout=zin+s*(PLATE_T+2); z0,z1=sorted((zin,zout))
        prof=hull(bx(-60,-12,SHELF_Y0,EAR_TOP-8,z0,z1),cyl_Z(8,z0,z1,-52,EAR_TOP-8),cyl_Z(8,z0,z1,-20,EAR_TOP-8))
        for hx,hy in EAR_HOLES:
            prof-=hull(cyl_Z(2.2,z0-1,z1+1,hx,hy-4,24),cyl_Z(2.2,z0-1,z1+1,hx,hy+4,24))
        for hx in (EAR_HOLES[0][0],EAR_HOLES[3][0]): prof-=cyl_Z(2.2,z0-1,z1+1,hx,-10.0,24)
        parts.append(prof)
    shelf=bx(-60,-12,SHELF_Y0,SHELF_Y1,ZC-EAR_OUT-1,ZC+EAR_OUT+1)
    shelf-=bx(-48,-24,SHELF_Y0-1,SHELF_Y1+1,ZC-45,ZC+45)
    return mf.Manifold.batch_boolean(parts+[shelf],mf.OpType.Add)

if __name__=='__main__':
    sb=servo_block3(); eb=elec_block3(); ld=lid2()
    handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder6()
    hd=H(head()); sv,_,_=servo_model(); sv=H(sv)
    ring=ring_local(); tray=tray_local()
    fixed=sb+eb+ld+handle+sv+diffuser(1)+diffuser(-1)
    def hit(t1,t2):
        r=c2s(rot_about(ring,A,t1)); b=c2s(rot_about(tray,B,t2))
        v={'ring/tray':(r^b).volume(),'ring/fixed':(r^fixed).volume(),'tray/fixed':(b^fixed).volume()}
        return {k:round(x,1) for k,x in v.items() if x>0.05}
    T1=list(range(0,-91,-10)); T2=list(range(0,91,10))
    print('      '+''.join(f'{t:5d}' for t in T2)+'   <- tray angle')
    for t1 in T1:
        print(f'{t1:5d} '+''.join('    .' if not hit(t1,t2) else f'{min(sum(hit(t1,t2).values()),9999):5.0f}' for t2 in T2))
    bad=[(t2,hit(0,t2)) for t2 in np.arange(0,90.1,2.5) if hit(0,t2)]+[(t1,hit(t1,90)) for t1 in np.arange(0,-90.1,-2.5) if hit(t1,90)]
    print('fold order tray up, then ring down: collisions',bad or 'none')
    for t in (1,2,3): print('  ring past level',t,hit(t,0))
    for t in (-1,-2,-3): print('  tray past level',t,hit(0,t))
    print('  tray trying to open while ring folded:',[(a,sum(hit(-90,a).values())) for a in (88,85,80)])
    for a in (-13,0,13):
        t=tilt(hd,a); print(f'  head {a:3d} deg vs everything: {(t^(fixed-sv)).volume():.2f}  vs ring/tray open: {(t^(c2s(ring)+c2s(tray))).volume():.2f}')
    # road sensor view
    cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
    cone=cone.rotate([0,0,180+TOF_DOWN]).translate([CX0-LEG_X1-4,TOF3_Y,ZC+TOF3_W])
    cone=cone^box(-3000,-60,-679+5,300,-400,300)
    for nm,m in (('ring+tray open',c2s(ring)+c2s(tray)),('ring+tray folded',c2s(rot_about(ring,A,-90))+c2s(rot_about(tray,B,90))),
                 ('blocks+legs',sb+eb),('handle',handle),('head',mf.Manifold.batch_boolean([tilt(hd,a) for a in (-12,0,12)],mf.OpType.Add))):
        print(f'  road sensor view vs {nm}: {(cone^m).volume():.1f} mm3')
    for nm,m in (('servo block',sb),('electronics block',eb),('ring',ring),('tray',tray),('handle v6',handle)):
        t=to_tm(m); print(f'  {nm}: watertight {t.is_watertight}, bodies {len(t.split(only_watertight=False))}')
    f=c2s(rot_about(ring,A,-90))+c2s(rot_about(tray,B,90)); fb=f.bounding_box()
    print('  folded pack X',round(fb[0],1),'..',round(fb[3],1),' lowest Y',round(min(fb[1],(sb+eb).bounding_box()[1]),1))
    def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
    to_tm(handle).export(OUT+'master_handle_v6.stl')
    to_tm(flat(sb.rotate([180,0,0]))).export(OUT+'headlamp3_servo_block_leg.stl')
    to_tm(flat(eb)).export(OUT+'headlamp3_electronics_block_leg.stl')                 # outer face on the bed
    r=ring.mirror([0,0,1]); b0=r.bounding_box(); to_tm(r.translate([0,0,-b0[2]])).export(OUT+'headlamp3_cup_ring.stl')
    b0=tray.bounding_box(); to_tm(tray.translate([0,0,-b0[2]])).export(OUT+'headlamp3_cup_tray.stl')
    to_tm(sb+eb+ld).export('lamp3_fixed.stl'); to_tm(handle).export('handle6.stl')
    for nm,t1,t2 in (('open',0,0),('folded',-90,90)): to_tm(c2s(rot_about(ring,A,t1))+c2s(rot_about(tray,B,t2))).export(f'v6_cup_{nm}.stl')
    to_tm(cone).export('lamp3_tof_cone.stl')
