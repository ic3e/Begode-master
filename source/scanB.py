src=open('build5.py').read().split("if __name__")[0]
import numpy as np
for bx in (33,35,37,39,41):
    for bz in (-50,-55,-60):
        g={}; exec(src.replace("B=np.array([31.,-50.])",f"B=np.array([{bx}.,{bz}.])"),g)
        pl=g['plate'](); ring=g['ring_lever'](); bask=g['basket_lever'](); rot=g['rot_about']; A=g['A']; B=g['B']
        worst=0
        for t2 in np.arange(0,90.1,5):
            b=rot(bask,B,t2); worst=max(worst,(b^pl).volume())
        bf=rot(bask,B,90)
        for t1 in np.arange(0,-90.1,2.5*-1):
            r=rot(ring,A,t1); worst=max(worst,(r^bf).volume(),(r^pl).volume() if t1<0 else 0)
        bb=bf.bounding_box(); rb=rot(ring,A,-90).bounding_box()
        print(f'B=({bx},{bz}) worst overlap {worst:6.1f}  folded basket z {bb[2]:.0f}..{bb[5]:.0f} x..{bb[3]:.0f}  folded bottom {min(bb[2],rb[2],bz-12):.0f}  open floor {bz-7-20}')
