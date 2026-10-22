# Stills of lamp v5 (no can holder): three-quarter front, straight front, and a section through the middle.
import numpy as np, trimesh, manifold3d as mf, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
exec(open('build17.py').read())
O=OUT; RED='#d9343d'
T=np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1.]])
light=np.array([0.45,-0.35,0.8]); light/=np.linalg.norm(light)
handle=to_tm(to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds3()); cap=trimesh.load(U+'euc_master_front_handle_p2.stl')
def parts(a=0.0,night=False,section=False):
    wheel=model3()
    hs=housing3(); ld=lid3(); sv=H3(servo3()); df=diffuser3(1)+diffuser3(-1)
    hd=tilt3(H3(head3()),a); sink=tilt3(H3(box(HU1_3-HS3_D,HU1_3,-HS3_H/2,HS3_H/2,-HS3_W/2,HS3_W/2)),a)
    lens=tilt3(H3(mf.Manifold.batch_boolean([cu(TIR2_D/2-0.5,HU0_3-0.5,HU0_3+1.6,w=w) for w in OPTIC_W],mf.OpType.Add)),a)
    cut=(lambda m: m^box(-500,500,-500,500,ZC,500)) if section else (lambda m: m)
    ps=[(m,c,False) for m,c in wheel]
    if section: ps=[(to_tm(cut(to_mf(m))),c,False) for m,c in wheel[2:] if len(m.faces)]
    ps+=[(handle,RED,False),(cap,RED,False),(to_tm(cut(hs)),'#2c3036',False),(to_tm(cut(ld)),'#2c3036',False),(to_tm(sv),'#2f6fd6',False),
         (to_tm(df),'#ffffff',True),(to_tm(cut(hd) if section else hd),'#565d68',False),(to_tm(cut(sink) if section else sink),'#c9ccd1',False),
         (to_tm(lens),'#fff3a0' if night else '#d9dde2',night)]
    if section: ps=[p for p in ps if p[0] is not handle and p[0] is not cap]
    return [p for p in ps if len(p[0].faces)]
def draw(ax,meshes,el,az,lim,zoom,title):
    tris=[];cols=[]
    for m,c,em in meshes:
        m=m.copy(); m.apply_transform(T); base=np.array(matplotlib.colors.to_rgb(c))
        sh=np.ones(len(m.faces)) if em else np.clip(np.abs(m.face_normals@light)*0.65+0.35,0,1)
        tris.append(m.triangles); cols.append(np.c_[base[None,:]*sh[:,None],np.ones(len(sh))])
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    (x0,x1),(y0,y1),(z0,z1)=lim
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0),zoom=zoom)
    ax.view_init(el,az); ax.set_axis_off(); ax.set_title(title,fontsize=22)
def lim_at(c,h): q=T@np.array([c[0],c[1],ZC,1]); return tuple((q[i]-h[i],q[i]+h[i]) for i in range(3))
fig=plt.figure(figsize=(21,8.5),facecolor='white')
draw(fig.add_subplot(1,3,1,projection='3d'),parts(),16,-35,lim_at((-60,-10),(150,150,120)),1.5,'Three-quarter front')
draw(fig.add_subplot(1,3,2,projection='3d'),parts(night=True),4,0,lim_at((-60,-10),(120,120,95)),1.55,'Front: three LEDs on one tilting bar')
draw(fig.add_subplot(1,3,3,projection='3d'),parts(-8,section=True),2,-90,lim_at((-40,-15),(80,80,62)),1.5,'Section: head tilted 8°, electronics box below')
plt.tight_layout(); fig.savefig(O+'render_v9_lamp.png',dpi=75,facecolor='white'); print('ok')
