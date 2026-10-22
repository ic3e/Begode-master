# Headlamp v2: adds a road distance sensor (VL53L1X) and daytime running lights to build_headlamp.
# DRL: a white LED strip behind a printed diffuser in the front of each side block.
# Road sensor: in the front of the electronics block, aimed 15° down at the road ~2 m ahead,
# placed out at the side so neither the head nor an open cup holder is in its view.
# A light sensor (LDR) in the lid tells day from night.
import numpy as np, trimesh, manifold3d as mf
exec(open('build9.py').read().split("\nif __name__=='__main__':")[0])

DRL_Y0,DRL_Y1=2.0,26.0          # window height
DRL_W0,DRL_W1=39.0,67.0         # window across (|w|), each block
RECESS=1.2; LIP=2.0             # diffuser sits flush in a recess, glued
TOF_W=-60.0; TOF_Y=-10.0; TOF_DOWN=15.0
LDR_X,LDR_W=-40.0,-52.0

def zr(s,a,b): z0,z1=sorted((ZC+s*a,ZC+s*b)); return z0,z1
def drl_cut(s):
    # window through the front wall, plus the recess the diffuser sits in
    w0,w1=zr(s,DRL_W0,DRL_W1); r0,r1=zr(s,DRL_W0-LIP,DRL_W1+LIP)
    return bx(BX0-1,BX0+3.01,DRL_Y0,DRL_Y1,w0,w1)+bx(BX0-1,BX0+RECESS,DRL_Y0-LIP,DRL_Y1+LIP,r0,r1)

def servo_block2():
    b=servo_block()-drl_cut(+1)
    w0,w1=zr(+1,DRL_W0,DRL_W1)
    b-=bx(BX0+2.9,BX0+10,DRL_Y0,DRL_Y1,w0,w1)              # light chamber: strip on its back wall
    # strip wires: down from the chamber and across to the servo cable hole
    b-=mf.Manifold.cylinder(DRL_Y0-(-14)+1,2.0,2.0,16).rotate([-90,0,0]).translate([BX0+7,-14,ZC+45])
    b-=mf.Manifold.cylinder(PX-(BX0+7),2.0,2.0,16).rotate([0,90,0]).translate([BX0+7,-14,ZC+45])
    b-=bx(PX-2,PX+2,-16,-12,ZC+40,ZC+45)
    return b

def tof_parts():
    # in sensor coordinates: a = along the view (forward), b = across it, c = lateral; origin on the front face
    mount=box(-12,0,-12,12,-9,9)
    slot=box(-7.2,-3.8,-9.3,9.3,-7.0,16.0)                 # board (13.5 x 18) slides in sideways from inside the box
    tunnel=box(-4.0,3,-4.5,4.5,-5.5,5.5)                    # view out; no glass in front of it
    place=lambda m: m.rotate([0,0,180+TOF_DOWN]).translate([BX0,TOF_Y,ZC+TOF_W])
    return place(mount),place(slot),place(tunnel)

def elec_block2():
    b=elec_block()-drl_cut(-1)
    w0,w1=zr(-1,DRL_W0-LIP,DRL_W1+LIP)
    carrier=bx(BX0+9,BX0+11,DRL_Y0-LIP,DRL_Y1+LIP,ZC-BLK_OUT+3,ZC-BLK_IN-3.5)   # strip glued to its front
    carrier-=bx(BX0+8,BX0+12,DRL_Y0-LIP-1,DRL_Y0+2,ZC-50,ZC-44)                 # wire notch
    mount,slot,tunnel=tof_parts()
    body=box(BX0,BX1,BY0,BY1,ZC-BLK_OUT,ZC-BLK_IN)
    b=b+carrier+(mount^body)
    b-=slot; b-=tunnel
    return b

def lid2():
    return lid()-mf.Manifold.cylinder(6,2.65,2.65,24).rotate([-90,0,0]).translate([LDR_X,BY1-1,ZC+LDR_W])   # 5 mm LDR

def diffuser(s):
    r0,r1=zr(s,DRL_W0-LIP+0.15,DRL_W1+LIP-0.15)
    return bx(BX0,BX0+RECESS,DRL_Y0-LIP+0.15,DRL_Y1+LIP-0.15,r0,r1)

if __name__=='__main__':
    hd=H(head()); sv,_,_=servo_model(); sv=H(sv)
    sb=servo_block2(); eb=elec_block2(); ld=lid2(); df=diffuser(1)+diffuser(-1)
    handle=to_mf(trimesh.load(OUT+'master_handle_v5_lamp_cup.stl'))
    cup_open=to_mf(trimesh.load('v5_cup_open.stl')); cup_f=to_mf(trimesh.load('v5_cup_folded.stl'))
    fixed={'handle':handle,'servo block':sb,'electronics block':eb,'lid':ld,'servo':sv,'diffusers':df}
    for a in (-13,-12,0,12,13):
        t=tilt(hd,a); bad={k:round((t^m).volume(),2) for k,m in fixed.items() if (t^m).volume()>0.01}
        print(f'head {a:4d} deg', bad or 'clear')
    print('servo in block',round((sv^sb).volume(),2),' blocks vs handle',round((sb^handle).volume(),2),round((eb^handle).volume(),2))
    # road sensor's view: a 15° cone (4x4 ROI) out to the ground must miss the head, cup holder and handle
    cone_len=2200; half=np.radians(8.5)
    cone=mf.Manifold.cylinder(cone_len,0.5,cone_len*np.tan(half),48).rotate([0,90,0])   # along +x
    cone=cone.rotate([0,0,180+TOF_DOWN]).translate([BX0-4,TOF_Y,ZC+TOF_W])
    ground=-494.0
    cone=cone^box(-3000,0,ground+5,200,-400,300)            # stop just above the road
    for nm,m in (('head (any tilt)',mf.Manifold.batch_boolean([tilt(hd,a) for a in (-12,0,12)],mf.OpType.Add)),
                 ('cup holder open',cup_open),('cup holder folded',cup_f),('handle',handle),('servo block',sb)):
        print(f'  road sensor view vs {nm}: {(cone^m).volume():.1f} mm3')
    hit=np.array([BX0-4,TOF_Y])+((TOF_Y-ground)/np.tan(np.radians(TOF_DOWN)))*np.array([-1,0])
    print('  hits the road about',round((TOF_Y-ground)/np.sin(np.radians(TOF_DOWN))/1000,2),'m away on the rough model')
    for nm,m in (('servo block',sb),('electronics block',eb),('lid',ld),('diffuser',diffuser(1))):
        t=to_tm(m); print(f'  {nm}: watertight {t.is_watertight}, bodies {len(t.split(only_watertight=False))}')
    def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
    to_tm(flat(sb.rotate([180,0,0]))).export(OUT+'headlamp2_servo_block.stl')
    to_tm(flat(eb.rotate([90,0,0]))).export(OUT+'headlamp2_electronics_block.stl')
    to_tm(flat(ld.rotate([-90,0,0]))).export(OUT+'headlamp2_lid.stl')
    to_tm(flat(diffuser(1).rotate([0,-90,0]))).export(OUT+'headlamp2_drl_diffuser_x2.stl')
    to_tm(sb+eb+ld).export('lamp2_fixed.stl'); to_tm(df).export('lamp2_diffusers.stl')
    to_tm(cone).export('lamp2_tof_cone.stl')
