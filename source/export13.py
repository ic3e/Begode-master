exec(open('build13.py').read())
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder8()
to_tm(handle).export(OUT+'master_handle_v8.stl'); to_tm(handle).export('handle8.stl')
def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
# arms: lie flat on their outer side
to_tm(flat(arm(1,0).rotate([180,0,0]))).export(OUT+'cup_slide_arm_right.stl')
to_tm(flat(arm(-1,0))).export(OUT+'cup_slide_arm_left.stl')
# rings: upright, bottom lip on the bed (basket coords have Y up -> rotate so Y is up in the print)
for k,r in enumerate(basket(True)):
    to_tm(flat(r.rotate([90,0,0]))).export(OUT+f'cup_gimbal_ring{k+1}.stl')
print('exported')
