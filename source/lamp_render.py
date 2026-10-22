import numpy as np, trimesh, manifold3d as mf, matplotlib
src=open('master_render.py').read().split("for st in ('open','folded'):")[0]
exec(src)                                  # rough Master + helpers (draw, T, light)
exec(open('build9.py').read().split("\nif __name__=='__main__':")[0])
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
wheel=[(to_tm(tyre),'#222222'),(to_tm(rim),'#9a9a9a'),(to_tm(hub),'#666666'),
       (to_tm(shells[0]),'#c8202a'),(to_tm(shells[1]),'#c8202a'),(to_tm(pedals[0]),'#333333'),(to_tm(pedals[1]),'#333333'),
       (to_tm(body),'#2b2b2b'),(to_tm(seat),'#1d1d1d'),(to_tm(trolley),'#b0b0b0'),
       (trimesh.load(O+'master_handle_v5_lamp_cup.stl'),'#e0303a'),(cap,'#e0303a'),
       (trimesh.load('v5_cup_folded.stl'),'#4a4f55'),
       (trimesh.load('lamp_fixed.stl'),'#3b3f44'),(trimesh.load('lamp_servo.stl'),'#2f6fd6')]
def head_parts(a):
    hs=H(box(0,HS_D,-HS/2,HS/2,-HS/2,HS/2))                 # heat sink
    lens=H(cu(TIR_D/2-0.5,HU0-0.5,HU0+2.6))
    return [(to_tm(tilt(H(head()),a)),'#3b3f44'),(to_tm(tilt(hs,a)),'#c9ccd1'),(to_tm(tilt(lens,a)),'#fff6c8')]
CONTACT=np.array([TC[0],TC[1]-TR])
def pitch_mat(phi):   # whole wheel pitched about the tyre contact point; + = nose down
    c,s=np.cos(np.radians(phi)),np.sin(np.radians(phi))
    M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]
    M[:2,3]=CONTACT-M[:2,:2]@CONTACT
    return M
def beam(phi,a):     # translucent wedge from the lens, in the wheel's centre plane
    elev=np.radians(a-phi); half=np.radians(5)
    # lens centre after head tilt and wheel pitch
    p=np.array([PX+HU0,PY,1.0]); r=np.radians(a)
    rp=np.array([[np.cos(r),-np.sin(r)],[np.sin(r),np.cos(r)]])@np.array([p[0]-PX,p[1]-PY])+[PX,PY]
    M=pitch_mat(phi); q=M[:2,:2]@rp+M[:2,3]
    L=420
    pts=[q]+[q+L*np.array([-np.cos(elev+d),np.sin(elev+d)]) for d in (half,-half)]
    v=np.array([[x,y,ZC] for x,y in pts]); return trimesh.Trimesh(v,[[0,1,2]],process=False)
def scene(phi,a):
    out=[]
    for m,c in wheel+head_parts(a):
        m=m.copy(); m.apply_transform(pitch_mat(phi)); out.append((m,c))
    return out
def draw2(ax,meshes,beams,el,az,lim):
    tris=[];cols=[]
    for m,c in meshes:
        m=m.copy(); m.apply_transform(T)
        base=np.array(matplotlib.colors.to_rgb(c)); sh=np.clip(np.abs(m.face_normals@light)*0.65+0.35,0,1)
        tris.append(m.triangles); cols.append(np.c_[base[None,:]*sh[:,None],np.ones(len(sh))])
    for b in beams:
        b=b.copy(); b.apply_transform(T); tris.append(b.triangles); cols.append(np.array([[1,0.9,0.3,0.35]]))
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    (x0,x1),(y0,y1),(z0,z1)=lim
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0))
    ax.view_init(el,az); ax.set_axis_off()
cases=[(0,0,'wheel level: beam 2° down (aim)'),(8,8,'braking, nose 8° down: head tilts 8° up'),(-6,-6,'tilt-back, nose 6° up: head tilts 6° down')]
AIM=-2
fig=plt.figure(figsize=(21,8),facecolor='white')
for i,(phi,a,tt) in enumerate(cases):
    ax=fig.add_subplot(1,3,i+1,projection='3d')
    draw2(ax,scene(phi,a+AIM),[beam(phi,a+AIM)],0,-90,((-560,300),(-330,190),(-520,140)))
    ax.set_title(tt,fontsize=14)
fig.suptitle('Self-levelling headlamp: the beam (yellow) stays put while the wheel pitches',fontsize=16)
plt.tight_layout(); plt.savefig(O+'render_headlamp_levelling.png',dpi=65,facecolor='white')
fig=plt.figure(figsize=(18,9),facecolor='white')
for i,(el,az,tt) in enumerate(((6,0,'front'),(22,-35,'front, from the side'))):
    ax=fig.add_subplot(1,2,i+1,projection='3d')
    draw2(ax,scene(0,AIM),[],el,az,((-120,120),(-200,60),(-130,110)))
    ax.set_title(tt,fontsize=15)
fig.suptitle('Self-levelling headlamp on the front handle (cup holder folded)',fontsize=16)
plt.tight_layout(); plt.savefig(O+'render_headlamp_front.png',dpi=65,facecolor='white')
print('ok')
