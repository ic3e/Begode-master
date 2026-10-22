# Handle v3: stock Master headlamp held under the grip, folding cup holder hung below it.
# The lamp is a rough model from Begode's photos (only its 141.5 mm width was measured), so its
# ear holes are slots in the side plates: line them up with the real lamp when there is one.
# STL frame of the handle: +Y up, -X forward, Z across the wheel (centre Z = -70.5).
import numpy as np, trimesh, manifold3d as mf
exec(open('build3.py').read().split("if __name__")[0])   # cup holder parts + helpers
ZC=-70.5
def bx(x0,x1,y0,y1,z0,z1): return box(x0,x1,y0,y1,z0,z1)
def cyl_X(r,x0,x1,y,z,seg=48): return mf.Manifold.cylinder(x1-x0,r,r,seg).rotate([0,90,0]).translate([x0,y,z])
def cyl_Z(r,z0,z1,x,y,seg=48): return mf.Manifold.cylinder(z1-z0,r,r,seg).translate([x,y,z0])

# ---- rough stock lamp ----
LW=141.5; LH=40.0; LD=38.0; EAR_T=3.0
L_BACK=-14.0; L_FRONT=L_BACK-LD; L_BOT=-20.0; L_TOP=L_BOT+LH
EAR_X0,EAR_X1=-46.0,-14.0; EAR_TOP=32.0
EAR_HOLES=[(-42,24),(-34,24),(-26,24),(-18,24)]   # guessed: two slots, two round holes in a row
def lamp():
    z0,z1=ZC-LW/2,ZC+LW/2
    b=bx(L_FRONT,L_BACK,L_BOT,L_TOP,z0,z1)
    for i in range(4):
        z=ZC+(i-1.5)*33
        b-=cyl_X(14.5,L_FRONT-1,L_FRONT+3,(L_BOT+L_TOP)/2,z)
        b+=cyl_X(12.5,L_FRONT+1,L_FRONT+3,(L_BOT+L_TOP)/2,z)   # lens
    for s in (-1,1):
        ze=ZC+s*(LW/2+EAR_T/2)
        e=hull(bx(EAR_X0,EAR_X1,L_BOT,EAR_TOP-6,ze-EAR_T/2,ze+EAR_T/2),
               cyl_Z(6,ze-EAR_T/2,ze+EAR_T/2,EAR_X0+6,EAR_TOP-6),cyl_Z(6,ze-EAR_T/2,ze+EAR_T/2,EAR_X1-6,EAR_TOP-6))
        for hx,hy in EAR_HOLES: e-=cyl_Z(2.1,ze-3,ze+3,hx,hy,24)
        b+=e
    return b

# ---- holder fused to the handle ----
EAR_OUT=LW/2+EAR_T+0.3        # half gap between the side plates
PLATE_T=8.5
SHELF_Y0,SHELF_Y1=L_BOT-6,L_BOT
CUP_X0=-67.0                  # cup holder plate front face (its back sits on the hanger at X-62)
CUP_TOP_Y=-32.0               # keeps the open ring below the lamp's beam
def holder():
    parts=[]
    for s in (-1,1):
        zin=ZC+s*EAR_OUT; zout=zin+s*(PLATE_T+2)   # 2 mm into the arm so it fuses
        z0,z1=sorted((zin,zout))
        prof=hull(bx(-60,-12,SHELF_Y0,EAR_TOP-8,z0,z1),cyl_Z(8,z0,z1,-52,EAR_TOP-8),cyl_Z(8,z0,z1,-20,EAR_TOP-8))
        # slots for the ear bolts, long up/down so a real lamp can be lined up
        for hx,hy in EAR_HOLES:
            prof-=hull(cyl_Z(2.2,z0-1,z1+1,hx,hy-4,24),cyl_Z(2.2,z0-1,z1+1,hx,hy+4,24))
        parts.append(prof)
    shelf=bx(-60,-12,SHELF_Y0,SHELF_Y1,ZC-EAR_OUT-1,ZC+EAR_OUT+1)
    shelf-=bx(-48,-24,SHELF_Y0-1,SHELF_Y1+1,ZC-45,ZC+45)      # lighter, lets water out
    hy0=CUP_TOP_Y-14-75-7                                     # hanger reaches below the lower bolts
    hanger=bx(-62,-54,hy0,SHELF_Y1,ZC-22,ZC+22)
    hanger+=hull(bx(-62,-54,SHELF_Y0-14,SHELF_Y0,ZC-22,ZC+22),bx(-62,-40,SHELF_Y0-1,SHELF_Y0,ZC-22,ZC+22))
    YA=CUP_TOP_Y-14
    for dz in (-15,15):
        for zl in (-30,-75):
            hanger-=cyl_X(2.2,-70,-50,YA+zl,ZC+dz,24)
            hanger-=mf.Manifold.cylinder(3.3,4.0,4.0,6).rotate([0,90,0]).translate([-57.3,YA+zl,ZC+dz])  # M4 nut trap
    return mf.Manifold.batch_boolean(parts+[shelf,hanger],mf.OpType.Add)

def cup_to_stl(m):
    YA=CUP_TOP_Y-14
    # local x fwd, y across, z up  ->  X=-x+CUP_X0, Y=z+YA, Z=y+ZC
    return m.transform([[-1,0,0,CUP_X0],[0,0,1,YA],[0,1,0,ZC]])

if __name__=='__main__':
    handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))
    h=handle+holder(); L=lamp()
    pl=cup_to_stl(plate()); ring=ring_lever(); bask=basket_lever()
    print('handle v3 genus',h.genus(),'vol cm3',round(h.volume()/1000,1))
    print('lamp in holder overlap',round((h^L).volume(),2))
    print('cup plate vs hanger overlap',round((h^pl).volume(),2))
    for nm,t1,t2 in (('open',0,0),('basket up',0,90),('folded',-90,90)):
        r=cup_to_stl(rot_about(ring,A,t1)); b=cup_to_stl(rot_about(bask,B,t2))
        print(f'{nm:10s} ring/handle {(r^h).volume():.2f}  basket/handle {(b^h).volume():.2f}  ring/lamp {(r^L).volume():.2f}  basket/lamp {(b^L).volume():.2f}')
    to_tm(h).export(OUT+'master_handle_v3_lamp_cup.stl'); to_tm(L).export(OUT+'rough_stock_lamp.stl')
    for nm,t1,t2 in (('open',0,0),('basketup',0,90),('folded',-90,90)):
        a=cup_to_stl(plate())+cup_to_stl(rot_about(ring,A,t1))+cup_to_stl(rot_about(bask,B,t2))
        to_tm(a).export(f'v3_cup_{nm}.stl')
