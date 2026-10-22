# Rough Begode Master around the handle, for pictures only. Sizes are eyeballed from the photos:
# tyre ~490 mm, its front ~2 cm behind the grip at axle height; seat nose ~4 cm in front of the mounting blocks.
import numpy as np, trimesh, manifold3d as mf, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
exec(open('build8.py').read().split("\nif __name__=='__main__':")[0])
O=OUT
def ex_xy(pts,z0,z1):   # extrude an XY outline along Z
    a=sum(x0*y1-x1*y0 for (x0,y0),(x1,y1) in zip(pts,pts[1:]+pts[:1]))
    cs=mf.CrossSection([pts if a>0 else pts[::-1]])
    return mf.Manifold.extrude(cs,z1-z0).translate([0,0,z0])
def rounded(x0,x1,y0,y1,r,n=8):
    pts=[]
    for cx,cy,a0 in ((x1-r,y1-r,0),(x0+r,y1-r,90),(x0+r,y0+r,180),(x1-r,y0+r,270)):
        for k in range(n+1):
            a=np.radians(a0+90*k/n); pts.append((cx+r*np.cos(a),cy+r*np.sin(a)))
    return pts
TC=np.array([139.,-284.]); TR=210.   # from the side photo, scaled by the Ø25 grip
def ring_z(r0,r1,w,seg=96):  # wheel part: annulus around Z through the tyre centre
    return (mf.Manifold.cylinder(w,r1,r1,seg)-mf.Manifold.cylinder(w+2,r0,r0,seg).translate([0,0,-1])).translate([TC[0],TC[1],ZC-w/2])
tyre=ring_z(TR-38,TR-6,80)+ring_z(TR-30,TR,64)
rim=ring_z(125,TR-37,52); hub=ring_z(0,125,40)
shells=[]
for s in (-1,1):
    z0,z1=sorted((ZC+s*48,ZC+s*130))
    # the shells are frames: top rail, front column, pedal rail; the tyre shows through the middle
    sh=ex_xy(rounded(-50,470,-390,-45,40),z0,z1)-ex_xy(rounded(20,400,-290,-105,30),z0-1,z1+1)
    shells.append(sh)
pedals=[ex_xy(rounded(80,280,-372,-358,6),*sorted((ZC+s*130,ZC+s*235))) for s in (-1,1)]
body=bx(-12,430,-90,28,ZC-66.5,ZC+66.5)
seat=ex_xy([(-55,42),(-55,88),(-38,100),(440,100),(460,78),(460,42)],ZC-85,ZC+85)+bx(-12,430,24,44,ZC-66,ZC+66)
trolley=sum([mf.Manifold.cylinder(260,7,7,24).rotate([-90,0,0]).translate([380,100,ZC+s*45]) for s in (-1,1)],mf.Manifold())+bx(370,392,355,380,ZC-60,ZC+60)

handle=to_tm(to_mf(trimesh.load(O+'master_handle_v5_lamp_cup.stl')))
cap=trimesh.load(U+'euc_master_front_handle_p2.stl')
lampm=lamp(); 
lens=mf.Manifold()
for i in range(4): lens+=cyl_X(12.5,L_FRONT-0.5,L_FRONT+3,(L_BOT+L_TOP)/2,ZC+(i-1.5)*33)
parts=[(to_tm(tyre),'#222222'),(to_tm(rim),'#9a9a9a'),(to_tm(hub),'#666666'),
       (to_tm(shells[0]),'#c8202a'),(to_tm(shells[1]),'#c8202a'),(to_tm(pedals[0]),'#333333'),(to_tm(pedals[1]),'#333333'),
       (to_tm(body),'#2b2b2b'),(to_tm(seat),'#1d1d1d'),(to_tm(trolley),'#b0b0b0'),
       (cap,'#e0303a'),(to_tm(lampm),'#3a3a3a'),(to_tm(lens),'#f4f1d0')]
T=np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1.]])
light=np.array([0.5,-0.4,0.75]); light/=np.linalg.norm(light)
def draw(ax,meshes,el,az,lim):
    tris=[];cols=[]
    for m,c in meshes:
        m=m.copy(); m.apply_transform(T)
        base=np.array(matplotlib.colors.to_rgb(c)); sh=np.clip(np.abs(m.face_normals@light)*0.65+0.35,0,1)
        tris.append(m.triangles); cols.append(base[None,:]*sh[:,None])
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    (x0,x1),(y0,y1),(z0,z1)=lim
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0))
    ax.view_init(el,az); ax.set_axis_off()

fig=plt.figure(figsize=(16,15),facecolor='white'); k=1
for ver,lab in (('v4','before (v4)'),('v5','now (v5, slim)')):
    hd=trimesh.load(O+f'master_handle_{ver}_lamp_cup.stl')
    for st in ('folded','open'):
        cup=trimesh.load(f'{ver}_cup_{st}.stl')
        ax=fig.add_subplot(2,2,k,projection='3d'); k+=1
        draw(ax,parts+[(hd,'#e0303a'),(cup,'#4a4f55')],0,-90,((-200,120),(-330,190),(-200,120)))
        ax.set_title(f'{lab}: cup holder {st}',fontsize=15)
fig.suptitle('Side view, close up',fontsize=17)
plt.tight_layout(); plt.savefig(O+'render_side_before_after.png',dpi=70,facecolor='white')
print('ok')
