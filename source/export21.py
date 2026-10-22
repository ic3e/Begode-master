exec(open('build21.py').read())
import glob, os
os.makedirs(OUT,exist_ok=True)
handle=handle13(1)
to_tm(handle).export(OUT+'master_handle_v13_usb_right.stl')
to_tm(handle13(-1)).export(OUT+'master_handle_v13_usb_left.stl')
def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
to_tm(flat(housing8().rotate([-90,0,0]))).export(OUT+'lamp54_housing.stl')
to_tm(flat(top_plate8().rotate([-90,0,0]))).export(OUT+'lamp54_top_plate.stl')
to_tm(flat(head8().rotate([0,90,0]))).export(OUT+'lamp54_head.stl')
to_tm(flat(lid3().rotate([90,0,0]))).export(OUT+'lamp54_lid.stl')
to_tm(flat(diffuser5(1).rotate([0,90,0]))).export(OUT+'lamp54_drl_diffuser_right.stl')
to_tm(flat(diffuser5(-1).rotate([0,90,0]))).export(OUT+'lamp54_drl_diffuser_left.stl')
# window: 1.5 mm clear polycarbonate, cut to this outline (SVG at 1:1, millimetres)
pts=window_outline(); W_=2*WIN_W; H_=WIN_Y1-WIN_Y0
path=' '.join(('M' if i==0 else 'L')+f'{w+WIN_W:.2f},{WIN_Y1-y:.2f}' for i,(w,y) in enumerate(pts))+' Z'
open(OUT+'lamp54_window_1.5mm_polycarbonate.svg','w').write(
 f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_:.1f}mm" height="{H_:.1f}mm" viewBox="0 0 {W_:.2f} {H_:.2f}">'
 f'<path d="{path}" fill="none" stroke="black" stroke-width="0.2"/></svg>')
print('window',round(W_,1),'x',round(H_,1),'mm, corners chamfered',WIN_CH)
for f in sorted(glob.glob(OUT+'lamp54_*.stl')+glob.glob(OUT+'master_handle_v13_*.stl')):
    t=trimesh.load(f); print(f.split('/')[-1],'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)),'size',np.round(t.extents,1))
