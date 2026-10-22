exec(open('build23.py').read())
import glob, os
os.makedirs(OUT,exist_ok=True)
def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
to_tm(handle13(1)).export(OUT+'master_handle_v13_usb_right.stl')
to_tm(handle13(-1)).export(OUT+'master_handle_v13_usb_left.stl')
to_tm(flat(housing10().rotate([-90,0,0]))).export(OUT+'lamp61_housing.stl')           # open top on the bed
to_tm(flat(top_plate10().rotate([-90,0,0]))).export(OUT+'lamp61_top_plate.stl')       # top face on the bed, tongues and fingers up
to_tm(flat(lens_frame().rotate([0,90,0]))).export(OUT+'lamp61_lens_frame.stl')        # back on the bed
to_tm(flat(lid10().rotate([90,0,0]))).export(OUT+'lamp61_lid.stl')
pts=window_outline(); W_=2*WIN_W; H_=WIN_Y1-WIN_Y0
path=' '.join(('M' if i==0 else 'L')+f'{w+WIN_W:.2f},{WIN_Y1-y:.2f}' for i,(w,y) in enumerate(pts))+' Z'
open(OUT+'lamp61_window_1.5mm_polycarbonate.svg','w').write(
 f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_:.1f}mm" height="{H_:.1f}mm" viewBox="0 0 {W_:.2f} {H_:.2f}">'
 f'<path d="{path}" fill="none" stroke="black" stroke-width="0.2"/></svg>')
for f in sorted(glob.glob(OUT+'lamp61_*.stl')+glob.glob(OUT+'master_handle_v13_*.stl')):
    t=trimesh.load(f); print(f.split('/')[-1],'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)),'size',np.round(t.extents,1))
