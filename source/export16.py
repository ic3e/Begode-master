exec(open('build16.py').read())
import glob
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds()
to_tm(handle).export(OUT+'master_handle_v11.stl'); to_tm(handle).export('handle11.stl')
def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
to_tm(flat(housing().rotate([180,0,0]))).export(OUT+'lamp4_housing.stl')             # top on the bed
to_tm(flat(head2().rotate([0,90,0]))).export(OUT+'lamp4_head.stl')                    # open back on the bed
to_tm(flat(tray().rotate([180,0,0]))).export(OUT+'lamp4_tray.stl')                    # pads up
to_tm(flat(diffuser2(1).rotate([0,90,0]))).export(OUT+'lamp4_drl_diffuser_x2.stl')
to_tm(flat(arm_local(1).rotate([180,0,0]))).export(OUT+'cup4_swing_arm_right.stl')
to_tm(flat(arm_local(-1))).export(OUT+'cup4_swing_arm_left.stl')
for f in sorted(glob.glob(OUT+'lamp4_*.stl'))+sorted(glob.glob(OUT+'cup4_*.stl'))+[OUT+'master_handle_v11.stl']:
    t=trimesh.load(f); print(f.split('/')[-1],'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)),'size',np.round(t.extents,1))
